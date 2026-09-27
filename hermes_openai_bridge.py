#!/usr/bin/env python3
"""
Hermes OpenAI Bridge Server (v2 - Media & Tool Support)
Exposes an OpenAI-compatible /v1/chat/completions and /v1/models API
backed by Hermes Agent running in Docker (hermes-agent-wt0scunahpdffuupawgm2ssy).
Automatically intercepts MEDIA:<path> tags from Hermes (images, audio, docs)
and serves them seamlessly in Aegis AI / Open WebUI as rendered markdown.
"""

import http.server
import json
import logging
import os
import re
import subprocess
import sys
import time
import uuid

PORT = int(os.environ.get("PORT", "8999"))
CONTAINER_NAME = os.environ.get("HERMES_CONTAINER", "hermes-agent-wt0scunahpdffuupawgm2ssy")
HERMES_BIN = os.environ.get("HERMES_BIN", "/opt/hermes/.venv/bin/hermes")
OPENWEBUI_CONTAINER = "open-webui-h12tpteo8o8edtqh5p9fql0b"
STATIC_MEDIA_DEST = "/app/backend/open_webui/static/media"
HERMES_HOME_VOL = "/var/lib/docker/volumes/wt0scunahpdffuupawgm2ssy_hermes-home/_data"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("hermes-bridge")

MODELS_LIST = [
    {
        "id": "hermes-agent",
        "object": "model",
        "created": 1727190000,
        "owned_by": "aegis-ai",
        "permission": [],
        "root": "hermes-agent",
        "parent": None,
        "name": "Aegis Agent",
        "description": "Aegis Autonomous Agent • Multi-Step Execution, Tool Use & Research by Maudy Network",
        "profile_image_url": "/static/aegis-agent-avatar.png?v=agent1"
    }
]

def format_hermes_prompt(messages):
    """
    Format Open WebUI chat messages into a natural prompt for Hermes Agent.
    Preserves Takok's native persona and avoids robotic brackets.
    """
    if not messages:
        return "Halo"
    
    msgs = [m for m in messages if isinstance(m, dict) and m.get("content")]
    if not msgs:
        return "Halo"
    
    # If single turn query, pass raw user prompt directly
    if len(msgs) == 1:
        return str(msgs[0].get("content", "")).strip() or "Halo"

    history = []
    custom_system = []

    for m in msgs[:-1]:
        role = str(m.get("role", "user")).lower()
        content = str(m.get("content", "")).strip()
        if not content:
            continue
        if role == "system":
            # Only include if user defined specific system instructions
            if "You are an AI assistant" not in content:
                custom_system.append(content)
        elif role == "user":
            history.append(f"User: {content}")
        elif role in ("assistant", "model"):
            history.append(f"Takok: {content}")

    last_msg = msgs[-1]
    last_content = str(last_msg.get("content", "")).strip()

    parts = []
    if custom_system:
        parts.append("Instruksi: " + " ".join(custom_system))
    
    if history:
        # Keep last 8 turns for natural conversation continuity
        parts.append("\n".join(history[-8:]))
    
    if parts:
        parts.append(f"User: {last_content}\nTakok:")
        return "\n\n".join(parts)
    else:
        return last_content

def resolve_and_publish_media(text):
    """
    Find MEDIA:/path/to/file patterns in Hermes output,
    copy the files to Open WebUI's static media directory,
    and replace the MEDIA tag with proper markdown image/audio tags.
    """
    media_pattern = re.compile(r'MEDIA:\s*([^\s\n\r]+)')
    matches = media_pattern.findall(text)
    if not matches:
        return text

    logger.info("Found %d MEDIA reference(s) in response: %s", len(matches), matches)

    # Ensure static/media directory exists in open-webui
    subprocess.run(
        ["docker", "exec", OPENWEBUI_CONTAINER, "mkdir", "-p", STATIC_MEDIA_DEST],
        capture_output=True
    )

    for raw_match in matches:
        raw_path = raw_match.rstrip(')].,;\"\'')
        filename = os.path.basename(raw_path)
        host_src = None

        if raw_path.startswith("/home/hermes/.hermes/"):
            rel = raw_path[len("/home/hermes/.hermes/"):]
            candidate = os.path.join(HERMES_HOME_VOL, rel)
            if os.path.exists(candidate):
                host_src = candidate

        if host_src and os.path.exists(host_src):
            res = subprocess.run(
                ["docker", "cp", host_src, f"{OPENWEBUI_CONTAINER}:{STATIC_MEDIA_DEST}/{filename}"],
                capture_output=True, text=True
            )
            logger.info("Copied from host volume %s -> %s (code %d)", host_src, filename, res.returncode)
        else:
            # Fallback copy directly from container
            tmp_local = f"/tmp/{filename}"
            subprocess.run(
                ["docker", "cp", f"{CONTAINER_NAME}:{raw_path}", tmp_local],
                capture_output=True
            )
            if os.path.exists(tmp_local):
                subprocess.run(
                    ["docker", "cp", tmp_local, f"{OPENWEBUI_CONTAINER}:{STATIC_MEDIA_DEST}/{filename}"],
                    capture_output=True
                )
                try:
                    os.remove(tmp_local)
                except OSError:
                    pass
                logger.info("Copied via temp file from container: %s", filename)

        ext = os.path.splitext(filename)[1].lower()
        media_url = f"/static/media/{filename}"
        if ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'):
            replacement = f"\n\n![Gambar]({media_url})\n\n"
        elif ext in ('.mp3', '.wav', '.ogg', '.m4a'):
            replacement = f'\n\n<audio controls src="{media_url}"></audio>\n\n'
        elif ext in ('.mp4', '.webm'):
            replacement = f'\n\n<video controls src="{media_url}" style="max-width:100%; border-radius:8px;"></video>\n\n'
        else:
            replacement = f"\n\n[📄 Unduh Berkas: {filename}]({media_url})\n\n"

        text = text.replace(f"MEDIA:{raw_match}", replacement).replace(f"MEDIA: {raw_match}", replacement)
        if raw_match != raw_path:
            text = text.replace(f"MEDIA:{raw_path}", replacement).replace(f"MEDIA: {raw_path}", replacement)

    return text

class HermesBridgeHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")
        if not path:
            path = "/"

        if path in ("", "/", "/health"):
            data = {"status": "ok", "service": "hermes-openai-bridge", "version": "2.0-media", "models": ["hermes-agent"]}
            self._send_json(200, data)
            return

        if path in ("/v1/models", "/models"):
            data = {"object": "list", "data": MODELS_LIST}
            self._send_json(200, data)
            return

        if path.startswith("/v1/models/") or path.startswith("/models/"):
            model_id = path.split("/")[-1]
            if model_id in ("hermes-agent", "aegis-agent"):
                self._send_json(200, MODELS_LIST[0])
                return
            for m in MODELS_LIST:
                if m["id"] == model_id:
                    self._send_json(200, m)
                    return
            self._send_json(404, {"error": {"message": f"Model {model_id} not found", "type": "invalid_request_error"}})
            return

        self._send_json(404, {"error": {"message": "Not Found", "type": "invalid_request_error"}})

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        if path not in ("/v1/chat/completions", "/chat/completions"):
            self._send_json(404, {"error": {"message": "Not Found", "type": "invalid_request_error"}})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {"error": {"message": "Empty request body"}})
            return

        try:
            body_bytes = self.rfile.read(content_length)
            body = json.loads(body_bytes.decode("utf-8"))
        except Exception as e:
            logger.error("Failed to parse request JSON: %s", e)
            self._send_json(400, {"error": {"message": f"Malformed JSON: {str(e)}"}})
            return

        messages = body.get("messages", [])
        stream = bool(body.get("stream", False))
        model_name = body.get("model", "hermes-agent")
        chat_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created_time = int(time.time())

        prompt = format_hermes_prompt(messages)
        logger.info("Executing Hermes with prompt: %s (stream=%s)", prompt[:100].replace("\n", " "), stream)

        cmd = [
            "docker", "exec", "-i",
            CONTAINER_NAME,
            HERMES_BIN,
            "-z",
            prompt
        ]

        if stream:
            self._handle_streaming(cmd, chat_id, created_time, model_name)
        else:
            self._handle_non_streaming(cmd, chat_id, created_time, model_name, prompt)

    def _handle_streaming(self, cmd, chat_id, created_time, model_name):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.send_header("X-Accel-Buffering", "no")
        self._send_cors_headers()
        self.end_headers()

        # Send initial role chunk
        role_chunk = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": ""},
                    "finish_reason": None
                }
            ]
        }
        self.wfile.write(f"data: {json.dumps(role_chunk)}\n\n".encode("utf-8"))
        self.wfile.flush()

        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            out, err = p.communicate(timeout=180)
            if p.returncode != 0 and not out:
                logger.error("Hermes stream execution failed (%d): %s", p.returncode, err)
                out = f"[Hermes Error: Container execution failed with code {p.returncode}: {err}]"

            # Transform any MEDIA tags before streaming to user
            transformed_content = resolve_and_publish_media(out.strip())

            # Stream words/lines naturally with tiny delay for smooth typing animation
            words = transformed_content.split(" ")
            for i, word in enumerate(words):
                chunk_text = word if i == len(words) - 1 else word + " "
                delta_chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": model_name,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": chunk_text},
                            "finish_reason": None
                        }
                    ]
                }
                self.wfile.write(f"data: {json.dumps(delta_chunk)}\n\n".encode("utf-8"))
                self.wfile.flush()
                # Fast typing cadence: 8ms per token
                time.sleep(0.008)

            # Final finish reason chunk
            finish_chunk = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }
                ]
            }
            self.wfile.write(f"data: {json.dumps(finish_chunk)}\n\n".encode("utf-8"))
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            self.close_connection = True
            logger.info("Streaming completed successfully for %s", chat_id)

        except (BrokenPipeError, ConnectionResetError):
            logger.warning("Client disconnected during stream %s", chat_id)
            if 'p' in locals() and p.poll() is None:
                p.terminate()
        except Exception as e:
            logger.error("Error in streaming execution: %s", e)

    def _handle_non_streaming(self, cmd, chat_id, created_time, model_name, prompt):
        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            out, err = p.communicate(timeout=180)
            if p.returncode != 0 and not out:
                logger.error("Hermes execution failed (%d): %s", p.returncode, err)
                out = f"[Hermes Error: Execution failed with code {p.returncode}: {err}]"

            content = resolve_and_publish_media(out.strip())
            prompt_toks = max(1, len(prompt.split()))
            comp_toks = max(1, len(content.split()))

            resp = {
                "id": chat_id,
                "object": "chat.completion",
                "created": created_time,
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_toks,
                    "completion_tokens": comp_toks,
                    "total_tokens": prompt_toks + comp_toks
                }
            }
            self._send_json(200, resp)
            logger.info("Non-streaming completed for %s", chat_id)
        except subprocess.TimeoutExpired:
            p.kill()
            self._send_json(504, {"error": {"message": "Hermes execution timed out after 180s"}})
        except Exception as e:
            logger.error("Error during execution: %s", e)
            self._send_json(500, {"error": {"message": str(e)}})

    def _send_json(self, status, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        logger.debug("%s - %s", self.address_string(), format % args)

def main():
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), HermesBridgeHandler)
    logger.info("🚀 Hermes OpenAI Bridge (v2) listening on 0.0.0.0:%d", PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping Hermes OpenAI Bridge...")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()

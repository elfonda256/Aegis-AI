#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import time

print("[1/5] Creating /opt/hermes-bridge directory...")
os.makedirs("/opt/hermes-bridge", exist_ok=True)
shutil.copy2("/tmp/hermes_openai_bridge.py", "/opt/hermes-bridge/hermes_openai_bridge.py")
os.chmod("/opt/hermes-bridge/hermes_openai_bridge.py", 0o755)

print("[2/5] Writing systemd service unit...")
service_content = """[Unit]
Description=Hermes OpenAI Bridge Server
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /opt/hermes-bridge/hermes_openai_bridge.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1
Environment=PORT=8999

[Install]
WantedBy=multi-user.target
"""

with open("/etc/systemd/system/hermes-openai-bridge.service", "w") as f:
    f.write(service_content)

print("[3/5] Reloading and starting systemd service...")
subprocess.run(["systemctl", "daemon-reload"], check=True)
subprocess.run(["systemctl", "enable", "hermes-openai-bridge.service"], check=True)
subprocess.run(["systemctl", "restart", "hermes-openai-bridge.service"], check=True)

time.sleep(2)
res = subprocess.run(["systemctl", "is-active", "hermes-openai-bridge.service"], capture_output=True, text=True)
print(f"Service status: {res.stdout.strip()}")

print("[4/5] Testing local endpoint...")
curl_res = subprocess.run(["curl", "-s", "http://127.0.0.1:8999/v1/models"], capture_output=True, text=True)
print("curl /v1/models:", curl_res.stdout)

print("[5/5] Testing from inside open-webui container...")
docker_curl = subprocess.run([
    "docker", "exec", "open-webui-h12tpteo8o8edtqh5p9fql0b",
    "curl", "-s", "http://10.0.7.1:8999/v1/models"
], capture_output=True, text=True)
print("docker curl /v1/models:", docker_curl.stdout)

print("Installation completed successfully!")

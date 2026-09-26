#!/usr/bin/env python3
"""
Deploy Hermes OpenAI Bridge to the VPS and configure Open WebUI.
"""

import os
import subprocess
import sys
import time

def run_ssh(cmd):
    exp_script = "/Users/mymac/.gemini/antigravity-ide/scratch/aegis-ai-brand-system/run_ssh.exp"
    res = subprocess.run([exp_script, cmd], capture_output=True, text=True)
    return res.stdout

def run_scp(src, dst):
    exp_script = "/Users/mymac/.gemini/antigravity-ide/scratch/aegis-ai-brand-system/run_scp.exp"
    res = subprocess.run([exp_script, src, dst], capture_output=True, text=True)
    return res.stdout

def main():
    print("=== Step 1: Uploading hermes_openai_bridge.py to VPS ===")
    src_file = "/Users/mymac/.gemini/antigravity-ide/scratch/aegis-ai-brand-system/hermes_openai_bridge.py"
    scp_out = run_scp(src_file, "efi@192.168.25.83:/tmp/hermes_openai_bridge.py")
    print(scp_out)

    print("=== Step 2: Installing hermes-openai-bridge on VPS ===")
    server_pass = os.environ.get("SERVER_PASS", "")
    sudo_prefix = f"echo {server_pass} | sudo -S " if server_pass else "sudo -S "

    setup_commands = f"""
{sudo_prefix}mkdir -p /opt/hermes-bridge
{sudo_prefix}cp /tmp/hermes_openai_bridge.py /opt/hermes-bridge/hermes_openai_bridge.py
{sudo_prefix}chmod +x /opt/hermes-bridge/hermes_openai_bridge.py

cat << 'EOF' | {sudo_prefix}tee /etc/systemd/system/hermes-openai-bridge.service > /dev/null
[Unit]
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
EOF

{sudo_prefix}systemctl daemon-reload
{sudo_prefix}systemctl enable hermes-openai-bridge.service
{sudo_prefix}systemctl restart hermes-openai-bridge.service
sleep 2
{sudo_prefix}systemctl status hermes-openai-bridge.service --no-pager
"""
    ssh_out = run_ssh(setup_commands)
    print(ssh_out)

    print("=== Step 3: Verifying bridge from host & from Open WebUI container ===")
    test_commands = """
curl -s http://127.0.0.1:8999/v1/models
echo ""
echo Elvan0 | sudo -S docker exec open-webui-h12tpteo8o8edtqh5p9fql0b curl -s http://10.0.7.1:8999/v1/models
echo ""
"""
    test_out = run_ssh(test_commands)
    print(test_out)

if __name__ == "__main__":
    main()

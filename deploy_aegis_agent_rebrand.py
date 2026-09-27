#!/usr/bin/env python3
import subprocess
import sys
import os

print("=== Deploying Aegis Agent Rebranding & Custom Avatar ===")

LOCAL_DIR = "/Users/mymac/.gemini/antigravity-ide/scratch/aegis-ai-brand-system"
CONTAINER = "open-webui-h12tpteo8o8edtqh5p9fql0b"

files_to_upload = [
    ("aegis-agent-avatar.png", "/tmp/aegis-agent-avatar.png"),
    ("loader.js", "/tmp/loader.js"),
    ("openwebui/aegis-openwebui-theme.css", "/tmp/custom.css"),
    ("hermes_openai_bridge.py", "/tmp/hermes_openai_bridge.py")
]

for src_rel, dst_path in files_to_upload:
    src_path = os.path.join(LOCAL_DIR, src_rel)
    print(f"Uploading {src_rel} -> {dst_path}...")
    res = subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), src_path, dst_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error uploading {src_rel}:", res.stderr)
        sys.exit(1)
print("All files uploaded to VPS /tmp successfully.")

remote_deploy_script = f"""#!/bin/bash
set -e

echo "1. Copying avatar and frontend assets into {CONTAINER}..."
docker cp /tmp/aegis-agent-avatar.png {CONTAINER}:/app/backend/open_webui/static/aegis-agent-avatar.png
docker cp /tmp/aegis-agent-avatar.png {CONTAINER}:/app/build/static/aegis-agent-avatar.png
docker cp /tmp/aegis-agent-avatar.png {CONTAINER}:/app/build/aegis-agent-avatar.png

docker cp /tmp/loader.js {CONTAINER}:/app/backend/open_webui/static/loader.js
docker cp /tmp/loader.js {CONTAINER}:/app/build/static/loader.js

docker cp /tmp/custom.css {CONTAINER}:/app/backend/open_webui/static/custom.css
docker cp /tmp/custom.css {CONTAINER}:/app/build/static/custom.css

echo "2. Updating Open WebUI Database (webui.db) with Aegis Agent..."
docker exec {CONTAINER} python3 -c "
import sqlite3, json

conn = sqlite3.connect('/app/backend/data/webui.db')
c = conn.cursor()

meta_data = {{
    'profile_image_url': '/static/aegis-agent-avatar.png?v=agent1',
    'description': 'Aegis Autonomous Agent • Multi-Step Execution, Tool Use & Research by Maudy Network',
    'capabilities': {{'vision': True, 'file_context': True}}
}}
meta_json = json.dumps(meta_data)

# Update hermes-agent entry to Aegis Agent
c.execute('''
    UPDATE model 
    SET name = 'Aegis Agent', 
        meta = ? 
    WHERE id = 'hermes-agent'
''', (meta_json,))

# Remove legacy duplicate aegis-agent entry if present
c.execute('DELETE FROM model WHERE id = \\'aegis-agent\\'')
print('Cleaned up duplicate aegis-agent model row!')

conn.commit()
conn.close()
print('webui.db updated successfully for Aegis Agent!')
"

echo "3. Updating Hermes OpenAI Bridge service..."
cp /tmp/hermes_openai_bridge.py /opt/hermes-bridge/hermes_openai_bridge.py
chmod 755 /opt/hermes-bridge/hermes_openai_bridge.py
systemctl restart hermes-openai-bridge.service
sleep 1
systemctl is-active hermes-openai-bridge.service

echo "4. Updating index.html cache-busting to v=aegis8..."
docker exec {CONTAINER} python3 -c "
with open('/app/build/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'loader\\.js\\?v=[^\\"]*', 'loader.js?v=aegis8', c)
c = re.sub(r'custom\\.css\\?v=[^\\"]*', 'custom.css?v=aegis8', c)

with open('/app/build/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.html to v=aegis8 successfully!')
"

echo "5. Setting correct permissions..."
docker exec {CONTAINER} chmod 644 /app/backend/open_webui/static/aegis-agent-avatar.png /app/backend/open_webui/static/loader.js /app/backend/open_webui/static/custom.css

echo "Aegis Agent deployment completed successfully!"
"""

deploy_sh_local = os.path.join(LOCAL_DIR, "deploy_agent.sh")
with open(deploy_sh_local, "w", encoding="utf-8") as f:
    f.write(remote_deploy_script)

scp_sh = subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), deploy_sh_local, "/tmp/deploy_agent.sh"], capture_output=True, text=True)
if scp_sh.returncode != 0:
    print("Failed to scp deploy_agent.sh:", scp_sh.stderr)
    sys.exit(1)

print("Executing remote deployment script...")
ssh_proc = subprocess.run([os.path.join(LOCAL_DIR, "run_ssh.exp"), "bash /tmp/deploy_agent.sh"], capture_output=True, text=True)
print(ssh_proc.stdout)
if ssh_proc.returncode != 0:
    print("Remote execution error:", ssh_proc.stderr)
    sys.exit(1)

print("=== Aegis Agent Rebranding & Avatar Deployment Complete! ===")

#!/usr/bin/env python3
import subprocess
import sys
import os

print("=== Deploying Aegis AI Enterprise UI Enhancements (Points 2-5) ===")

LOCAL_DIR = "/Users/mymac/.gemini/antigravity-ide/scratch/aegis-ai-brand-system"
CONTAINER = "open-webui-h12tpteo8o8edtqh5p9fql0b"

# Step 1: Copy files to remote server /tmp
print("1. Uploading loader.js and custom.css to VPS /tmp...")
loader_local = os.path.join(LOCAL_DIR, "loader.js")
css_local = os.path.join(LOCAL_DIR, "openwebui", "aegis-openwebui-theme.css")

scp_loader = subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), loader_local, "/tmp/loader.js"], capture_output=True, text=True)
if scp_loader.returncode != 0:
    print("Failed to scp loader.js:", scp_loader.stderr)
    sys.exit(1)
print("Uploaded loader.js successfully.")

scp_css = subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), css_local, "/tmp/custom.css"], capture_output=True, text=True)
if scp_css.returncode != 0:
    print("Failed to scp custom.css:", scp_css.stderr)
    sys.exit(1)
print("Uploaded custom.css successfully.")

# Step 2: Upload deployment script to VPS
deploy_sh_content = f"""#!/bin/bash
set -e
echo "Injecting into {CONTAINER}..."
docker cp /tmp/loader.js {CONTAINER}:/app/backend/open_webui/static/loader.js
docker cp /tmp/loader.js {CONTAINER}:/app/build/static/loader.js
docker cp /tmp/custom.css {CONTAINER}:/app/backend/open_webui/static/custom.css
docker cp /tmp/custom.css {CONTAINER}:/app/build/static/custom.css

echo "Updating cache-busting in index.html to v=aegis7..."
docker exec {CONTAINER} python3 -c "
with open('/app/build/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'loader\\.js\\?v=[^\\"]*', 'loader.js?v=aegis7', c)
c = re.sub(r'custom\\.css\\?v=[^\\"]*', 'custom.css?v=aegis7', c)

with open('/app/build/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.html cache-buster successfully!')
"

echo "Checking static permissions..."
docker exec {CONTAINER} chmod 644 /app/backend/open_webui/static/loader.js /app/backend/open_webui/static/custom.css /app/build/static/loader.js /app/build/static/custom.css

echo "Deployment into container finished successfully!"
"""

deploy_sh_local = os.path.join(LOCAL_DIR, "deploy_ui.sh")
with open(deploy_sh_local, "w", encoding="utf-8") as f:
    f.write(deploy_sh_content)

scp_sh = subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), deploy_sh_local, "/tmp/deploy_ui.sh"], capture_output=True, text=True)
if scp_sh.returncode != 0:
    print("Failed to scp deploy_ui.sh:", scp_sh.stderr)
    sys.exit(1)

print("2. Executing remote deployment script via sudo bash...")
ssh_proc = subprocess.run([os.path.join(LOCAL_DIR, "run_ssh.exp"), "bash /tmp/deploy_ui.sh"], capture_output=True, text=True)
print(ssh_proc.stdout)
if ssh_proc.returncode != 0:
    print("Error during remote execution:", ssh_proc.stderr)
    sys.exit(1)

print("=== Deployment Completed Successfully! ===")

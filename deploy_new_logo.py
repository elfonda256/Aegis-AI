#!/usr/bin/env python3
import subprocess
import os
import sys

LOCAL_DIR = "/Users/mymac/.gemini/antigravity-ide/scratch/aegis-ai-brand-system"
CONTAINER = "open-webui-h12tpteo8o8edtqh5p9fql0b"

print("=== Deploying New Aegis Shield & Emblem Logos to Open WebUI ===")

# 1. Upload tarball and loader.js to server
print("1. Uploading assets to VPS...")
res1 = subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), "/tmp/aegis_logo_pack.tar.gz", "/tmp/aegis_logo_pack.tar.gz"], check=True)
res2 = subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), os.path.join(LOCAL_DIR, "loader.js"), "/tmp/loader.js"], check=True)
print("Uploaded tarball and loader.js successfully.")

# 2. Prepare remote deployment script
deploy_sh = f"""#!/bin/bash
set -e

echo "Extracting logo pack on VPS..."
rm -rf /tmp/new_logo_pack
mkdir -p /tmp/new_logo_pack
tar -xzf /tmp/aegis_logo_pack.tar.gz -C /tmp/new_logo_pack/

echo "Copying logo pack to container {CONTAINER}..."
# Copy all static assets
for f in favicon.png favicon-96x96.png apple-touch-icon.png web-app-manifest-192x192.png web-app-manifest-512x512.png favicon.ico favicon.svg splash.png splash-dark.png aegis-agent-avatar.png logo.png aegis-seal.png; do
    if [ -f "/tmp/new_logo_pack/$f" ]; then
        docker cp "/tmp/new_logo_pack/$f" "{CONTAINER}:/app/backend/open_webui/static/$f"
        docker cp "/tmp/new_logo_pack/$f" "{CONTAINER}:/app/build/static/$f"
    fi
done

# Copy root favicon
docker cp /tmp/new_logo_pack/favicon.png "{CONTAINER}:/app/build/favicon.png"

# Copy updated loader.js
docker cp /tmp/loader.js "{CONTAINER}:/app/backend/open_webui/static/loader.js"
docker cp /tmp/loader.js "{CONTAINER}:/app/build/static/loader.js"

# Update index.html cache-buster to v=aegis12
echo "Updating index.html cache-buster to v=aegis12..."
docker exec {CONTAINER} python3 -c "
with open('/app/build/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'loader\\.js\\?v=[^\\"]*', 'loader.js?v=aegis12', c)
c = re.sub(r'custom\\.css\\?v=[^\\"]*', 'custom.css?v=aegis12', c)

with open('/app/build/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.html to v=aegis12 successfully!')
"

echo "Setting permissions..."
docker exec {CONTAINER} chmod -R 644 /app/backend/open_webui/static/ /app/build/static/ /app/build/favicon.png

echo "Deployment complete!"
"""

deploy_sh_path = os.path.join(LOCAL_DIR, "deploy_remote_logo.sh")
with open(deploy_sh_path, "w", encoding="utf-8") as f:
    f.write(deploy_sh)

print("2. Uploading deployment script to VPS...")
subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), deploy_sh_path, "/tmp/deploy_remote_logo.sh"], check=True)

print("3. Executing deployment on server...")
res = subprocess.run([os.path.join(LOCAL_DIR, "run_ssh.exp"), "bash /tmp/deploy_remote_logo.sh"], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("Stderr:", res.stderr)

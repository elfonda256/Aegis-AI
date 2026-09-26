#!/usr/bin/env python3
import subprocess
import os

LOCAL_DIR = "/Users/mymac/.gemini/antigravity-ide/scratch/aegis-ai-brand-system"
CONTAINER = "open-webui-h12tpteo8o8edtqh5p9fql0b"

deploy_sh_content = f"""#!/bin/bash
set -e

echo "Copying assets into container..."
docker cp /tmp/loader.js {CONTAINER}:/app/backend/open_webui/static/loader.js
docker cp /tmp/loader.js {CONTAINER}:/app/build/static/loader.js

docker cp /tmp/custom.css {CONTAINER}:/app/backend/open_webui/static/custom.css
docker cp /tmp/custom.css {CONTAINER}:/app/build/static/custom.css

echo "Updating index.html to v=aegis11..."
docker exec {CONTAINER} python3 -c "
with open('/app/build/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'loader\\.js\\?v=[^\\"]*', 'loader.js?v=aegis11', c)
c = re.sub(r'custom\\.css\\?v=[^\\"]*', 'custom.css?v=aegis11', c)

with open('/app/build/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.html to v=aegis11 successfully!')
"

docker exec {CONTAINER} chmod 644 /app/backend/open_webui/static/loader.js /app/backend/open_webui/static/custom.css /app/build/static/loader.js /app/build/static/custom.css
echo "Done!"
"""

deploy_sh_local = os.path.join(LOCAL_DIR, "deploy_footer.sh")
with open(deploy_sh_local, "w", encoding="utf-8") as f:
    f.write(deploy_sh_content)

subprocess.run([os.path.join(LOCAL_DIR, "run_scp.exp"), deploy_sh_local, "/tmp/deploy_footer.sh"], check=True)
res = subprocess.run([os.path.join(LOCAL_DIR, "run_ssh.exp"), "bash /tmp/deploy_footer.sh"], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)

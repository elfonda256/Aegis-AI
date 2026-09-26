#!/bin/bash
set -e

echo "Extracting logo pack on VPS..."
rm -rf /tmp/new_logo_pack
mkdir -p /tmp/new_logo_pack
tar -xzf /tmp/aegis_logo_pack.tar.gz -C /tmp/new_logo_pack/

echo "Copying logo pack to container open-webui-h12tpteo8o8edtqh5p9fql0b..."
# Copy all static assets
for f in favicon.png favicon-96x96.png apple-touch-icon.png web-app-manifest-192x192.png web-app-manifest-512x512.png favicon.ico favicon.svg splash.png splash-dark.png aegis-agent-avatar.png logo.png aegis-seal.png; do
    if [ -f "/tmp/new_logo_pack/$f" ]; then
        docker cp "/tmp/new_logo_pack/$f" "open-webui-h12tpteo8o8edtqh5p9fql0b:/app/backend/open_webui/static/$f"
        docker cp "/tmp/new_logo_pack/$f" "open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/static/$f"
    fi
done

# Copy root favicon
docker cp /tmp/new_logo_pack/favicon.png "open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/favicon.png"

# Copy updated loader.js
docker cp /tmp/loader.js "open-webui-h12tpteo8o8edtqh5p9fql0b:/app/backend/open_webui/static/loader.js"
docker cp /tmp/loader.js "open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/static/loader.js"

# Update index.html cache-buster to v=aegis12
echo "Updating index.html cache-buster to v=aegis12..."
docker exec open-webui-h12tpteo8o8edtqh5p9fql0b python3 -c "
with open('/app/build/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'loader\.js\?v=[^\"]*', 'loader.js?v=aegis12', c)
c = re.sub(r'custom\.css\?v=[^\"]*', 'custom.css?v=aegis12', c)

with open('/app/build/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.html to v=aegis12 successfully!')
"

echo "Setting permissions..."
docker exec open-webui-h12tpteo8o8edtqh5p9fql0b chmod -R 644 /app/backend/open_webui/static/ /app/build/static/ /app/build/favicon.png

echo "Deployment complete!"

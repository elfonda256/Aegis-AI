#!/bin/bash
set -e

echo "Copying assets into container..."
docker cp /tmp/loader.js open-webui-h12tpteo8o8edtqh5p9fql0b:/app/backend/open_webui/static/loader.js
docker cp /tmp/loader.js open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/static/loader.js

docker cp /tmp/custom.css open-webui-h12tpteo8o8edtqh5p9fql0b:/app/backend/open_webui/static/custom.css
docker cp /tmp/custom.css open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/static/custom.css

echo "Updating index.html to v=aegis11..."
docker exec open-webui-h12tpteo8o8edtqh5p9fql0b python3 -c "
with open('/app/build/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'loader\.js\?v=[^\"]*', 'loader.js?v=aegis11', c)
c = re.sub(r'custom\.css\?v=[^\"]*', 'custom.css?v=aegis11', c)

with open('/app/build/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.html to v=aegis11 successfully!')
"

docker exec open-webui-h12tpteo8o8edtqh5p9fql0b chmod 644 /app/backend/open_webui/static/loader.js /app/backend/open_webui/static/custom.css /app/build/static/loader.js /app/build/static/custom.css
echo "Done!"

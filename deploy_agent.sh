#!/bin/bash
set -e

echo "1. Copying avatar and frontend assets into open-webui-h12tpteo8o8edtqh5p9fql0b..."
docker cp /tmp/aegis-agent-avatar.png open-webui-h12tpteo8o8edtqh5p9fql0b:/app/backend/open_webui/static/aegis-agent-avatar.png
docker cp /tmp/aegis-agent-avatar.png open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/static/aegis-agent-avatar.png
docker cp /tmp/aegis-agent-avatar.png open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/aegis-agent-avatar.png

docker cp /tmp/loader.js open-webui-h12tpteo8o8edtqh5p9fql0b:/app/backend/open_webui/static/loader.js
docker cp /tmp/loader.js open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/static/loader.js

docker cp /tmp/custom.css open-webui-h12tpteo8o8edtqh5p9fql0b:/app/backend/open_webui/static/custom.css
docker cp /tmp/custom.css open-webui-h12tpteo8o8edtqh5p9fql0b:/app/build/static/custom.css

echo "2. Updating Open WebUI Database (webui.db) with Aegis Agent..."
docker exec open-webui-h12tpteo8o8edtqh5p9fql0b python3 -c "
import sqlite3, json

conn = sqlite3.connect('/app/backend/data/webui.db')
c = conn.cursor()

meta_data = {
    'profile_image_url': '/static/aegis-agent-avatar.png?v=agent1',
    'description': 'Aegis Autonomous Agent • Multi-Step Execution, Tool Use & Research by Maudy Network',
    'capabilities': {'vision': True, 'file_context': True}
}
meta_json = json.dumps(meta_data)

# Update hermes-agent entry to Aegis Agent
c.execute('''
    UPDATE model 
    SET name = 'Aegis Agent', 
        meta = ? 
    WHERE id = 'hermes-agent'
''', (meta_json,))

# Remove legacy duplicate aegis-agent entry if present
c.execute('DELETE FROM model WHERE id = \'aegis-agent\'')
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
docker exec open-webui-h12tpteo8o8edtqh5p9fql0b python3 -c "
with open('/app/build/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'loader\.js\?v=[^\"]*', 'loader.js?v=aegis8', c)
c = re.sub(r'custom\.css\?v=[^\"]*', 'custom.css?v=aegis8', c)

with open('/app/build/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.html to v=aegis8 successfully!')
"

echo "5. Setting correct permissions..."
docker exec open-webui-h12tpteo8o8edtqh5p9fql0b chmod 644 /app/backend/open_webui/static/aegis-agent-avatar.png /app/backend/open_webui/static/loader.js /app/backend/open_webui/static/custom.css

echo "Aegis Agent deployment completed successfully!"

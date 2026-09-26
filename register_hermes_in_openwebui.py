#!/usr/bin/env python3
"""
Register Hermes Agent in Open WebUI config and model tables.
"""

import json
import sqlite3
import time

DB_PATH = "/app/backend/data/webui.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

now = int(time.time())

# 1. Update config table
configs = {
    "openai.enable": "true",
    "openai.api_base_urls": json.dumps(["http://10.0.7.1:8999/v1"]),
    "openai.api_keys": json.dumps(["hermes"]),
    "openai.api_configs": json.dumps({"0": {"enable": True}})
}

for k, v in configs.items():
    cursor.execute("""
        INSERT INTO config (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
    """, (k, v, now))

print("Config table updated successfully.")

# 2. Register hermes-agent in model table
model_id = "hermes-agent"
user_id = "e5c1cae2-207d-45b4-84f6-71cc28933ec2"
name = "Hermes Agent (Takok AI)"
params = json.dumps({})
meta = json.dumps({
    "profile_image_url": "/static/favicon.png?v=aegis3",
    "description": "Hermes Autonomous Agent with Takok AI backend & specialized tool capabilities",
    "capabilities": {
        "file_context": True,
        "vision": False,
        "file_upload": True,
        "web_search": True,
        "code_interpreter": True,
        "memory": True,
        "citations": True
    },
    "suggestion_prompts": [
        {"title": ["Halo Hermes", "Perkenalkan kemampuanmu"], "content": "Halo Hermes Agent! Apa saja tugas dan kapabilitas yang bisa kamu bantu?"},
        {"title": ["Analisis & Rencana", "Buat rancangan kerja"], "content": "Bantu saya menyusun langkah strategis untuk proyek implementasi AI."}
    ],
    "tags": ["agent", "hermes", "autonomous"]
})

cursor.execute("""
    INSERT INTO model (id, user_id, base_model_id, name, params, meta, updated_at, created_at, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    ON CONFLICT(id) DO UPDATE SET
        name=excluded.name,
        params=excluded.params,
        meta=excluded.meta,
        updated_at=excluded.updated_at,
        is_active=1
""", (model_id, user_id, model_id, name, params, meta, now, now))

conn.commit()
print("Model table registered successfully.")

# Verify
cursor.execute("SELECT id, name, is_active FROM model")
print("Current models:", cursor.fetchall())

cursor.execute("SELECT key, value FROM config WHERE key LIKE 'openai%'")
print("OpenAI config:", cursor.fetchall())

conn.close()

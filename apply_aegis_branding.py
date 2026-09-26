#!/usr/bin/env python3
import os
import shutil
import re
from PIL import Image

SRC_DIR = "/tmp/aegis_brand"
BACKEND_STATIC = "/app/backend/open_webui/static"
BUILD_STATIC = "/app/build/static"
BUILD_DIR = "/app/build"
ENV_FILE = "/app/backend/open_webui/env.py"
INDEX_FILE = "/app/build/index.html"

print("=== Starting Aegis AI Brand Deployment ===")

# 1. Backup original directories
for d in [BACKEND_STATIC, BUILD_STATIC]:
    backup = d + "_backup"
    if not os.path.exists(backup):
        print(f"Creating backup of {d} -> {backup}")
        shutil.copytree(d, backup)

# 2. Generate resized icons from aegis-logo-symbol.png
symbol_src = os.path.join(SRC_DIR, "aegis-logo-symbol.png")
primary_src = os.path.join(SRC_DIR, "aegis-logo-primary.png")
favicon_svg_src = os.path.join(SRC_DIR, "aegis-favicon.svg")
custom_css_src = os.path.join(SRC_DIR, "custom.css")

img = Image.open(symbol_src)

# Generate icon sizes
sizes = {
    "favicon-96x96.png": (96, 96),
    "favicon.png": (256, 256),
    "apple-touch-icon.png": (180, 180),
    "web-app-manifest-192x192.png": (192, 192),
    "web-app-manifest-512x512.png": (512, 512),
    "logo.png": (512, 512)
}

temp_gen = "/tmp/aegis_gen"
os.makedirs(temp_gen, exist_ok=True)

for name, size in sizes.items():
    resized = img.resize(size, Image.Resampling.LANCZOS)
    out_path = os.path.join(temp_gen, name)
    resized.save(out_path, format="PNG")
    print(f"Generated {name} ({size[0]}x{size[1]})")

# Generate favicon.ico (multi-resolution)
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
img.save(os.path.join(temp_gen, "favicon.ico"), format="ICO", sizes=ico_sizes)
print("Generated favicon.ico with multi-resolution")

# 3. Copy assets to both BACKEND_STATIC and BUILD_STATIC
target_dirs = [BACKEND_STATIC, BUILD_STATIC]

for target in target_dirs:
    for name in sizes.keys():
        shutil.copy2(os.path.join(temp_gen, name), os.path.join(target, name))
    
    shutil.copy2(os.path.join(temp_gen, "favicon.ico"), os.path.join(target, "favicon.ico"))
    shutil.copy2(favicon_svg_src, os.path.join(target, "favicon.svg"))
    
    # Splash screens
    shutil.copy2(primary_src, os.path.join(target, "splash.png"))
    shutil.copy2(primary_src, os.path.join(target, "splash-dark.png"))
    
    # Custom CSS
    shutil.copy2(custom_css_src, os.path.join(target, "custom.css"))
    print(f"Copied all icons & CSS to {target}")

# Also copy favicon.png to BUILD_DIR root
shutil.copy2(os.path.join(temp_gen, "favicon.png"), os.path.join(BUILD_DIR, "favicon.png"))
print(f"Copied favicon.png to {BUILD_DIR}/favicon.png")

# 4. Create loader.js with Title & Branding enforcement
loader_js_content = """// Aegis AI Runtime Branding Injector
(function() {
    'use strict';
    
    const BRAND_NAME = 'Aegis AI';
    const FULL_TITLE = 'Aegis AI — Enterprise Intelligence Platform';
    
    // Enforce document title
    function updateTitle() {
        if (!document.title.includes('Aegis AI')) {
            document.title = FULL_TITLE;
        }
    }
    
    // Observer for dynamic title changes by SvelteKit
    const titleObserver = new MutationObserver(function() {
        if (document.title.includes('Open WebUI')) {
            document.title = document.title.replace('Open WebUI', BRAND_NAME);
        }
    });
    
    const titleEl = document.querySelector('title');
    if (titleEl) {
        titleObserver.observe(titleEl, { childList: true, characterData: true, subtree: true });
    }
    
    // Style and brand observer for UI components
    function enforceBranding() {
        updateTitle();
        
        // Ensure top-left logo and icons have no color inversion
        const logos = document.querySelectorAll('img[alt="logo"], img[alt="favicon"], #sidebar-toggle-button img, nav button[aria-label="Home"] img');
        logos.forEach(img => {
            img.style.filter = 'none';
            img.style.webkitFilter = 'none';
        });
        
        // Update any visible text nodes that say Open WebUI in headers
        const walkers = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while (node = walkers.nextNode()) {
            if (node.nodeValue && node.nodeValue.includes('Open WebUI') && !node.parentElement.closest('code, pre')) {
                node.nodeValue = node.nodeValue.replace(/Open WebUI/g, BRAND_NAME);
            }
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', enforceBranding);
    } else {
        enforceBranding();
    }
    
    setInterval(enforceBranding, 1500);
})();
"""

for target in target_dirs:
    loader_path = os.path.join(target, "loader.js")
    with open(loader_path, "w", encoding="utf-8") as f:
        f.write(loader_js_content)
    print(f"Written loader.js to {loader_path}")

# 5. Patch env.py to default WEBUI_NAME to 'Aegis AI' without appending ' (Open WebUI)'
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        env_content = f.read()
    
    # Replace WEBUI_NAME definition
    old_pattern = r"WEBUI_NAME = os\.getenv\('WEBUI_NAME', 'Open WebUI'\)\s*\nif WEBUI_NAME != 'Open WebUI':\s*\n\s*WEBUI_NAME \+= ' \(Open WebUI\)'"
    new_code = "WEBUI_NAME = os.getenv('WEBUI_NAME', 'Aegis AI')"
    
    if re.search(old_pattern, env_content):
        env_content = re.sub(old_pattern, new_code, env_content)
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(env_content)
        print("Successfully patched env.py for clean Aegis AI branding!")
    else:
        # Fallback direct replacement
        env_content = env_content.replace("WEBUI_NAME = os.getenv('WEBUI_NAME', 'Open WebUI')", "WEBUI_NAME = os.getenv('WEBUI_NAME', 'Aegis AI')")
        env_content = env_content.replace("WEBUI_NAME += ' (Open WebUI)'", "# WEBUI_NAME += ' (Open WebUI)'")
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(env_content)
        print("Applied fallback patch to env.py")

# 6. Update index.html for title & cache busting
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Replace title
    html = re.sub(r"<title>.*?</title>", "<title>Aegis AI — Enterprise Intelligence Platform</title>", html)
    
    # Add cache-busting query params to favicon links
    html = html.replace('href="/static/favicon.png"', 'href="/static/favicon.png?v=aegis2"')
    html = html.replace('href="/static/favicon-96x96.png"', 'href="/static/favicon-96x96.png?v=aegis2"')
    html = html.replace('href="/static/favicon.svg"', 'href="/static/favicon.svg?v=aegis2"')
    html = html.replace('href="/static/favicon.ico"', 'href="/static/favicon.ico?v=aegis2"')
    html = html.replace('href="/static/custom.css"', 'href="/static/custom.css?v=aegis2"')
    html = html.replace('src="/static/loader.js"', 'src="/static/loader.js?v=aegis2"')
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully updated index.html with cache-busting and Aegis AI title!")

print("=== Aegis AI Brand Deployment Completed Successfully ===")

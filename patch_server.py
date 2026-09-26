#!/usr/bin/env python3
import os
import glob
import re

print("=== Starting Advanced Aegis Brand & Cache Fix ===")

MODELS_ROUTER = "/app/backend/open_webui/routers/models.py"
MAIN_PY = "/app/backend/open_webui/main.py"
STATIC_FAVICON = "/app/backend/open_webui/static/favicon.png"

# 1. Patch routers/models.py to serve favicon.png directly without requiring auth
if os.path.exists(MODELS_ROUTER):
    with open(MODELS_ROUTER, "r", encoding="utf-8") as f:
        code = f.read()
    
    # Allow optional auth on get_model_profile_image so <img> tags work without Bearer header
    code = code.replace(
        "async def get_model_profile_image(\n    request: Request,\n    id: str,\n    user=Depends(get_verified_user),",
        "async def get_model_profile_image(\n    request: Request,\n    id: str,\n    user=Depends(get_optional_user),"
    )
    
    # Also if no profile_image_url, return FileResponse of STATIC_DIR/favicon.png instead of redirect
    fallback_old = "    return RedirectResponse(\n        url='/static/favicon.png',\n        status_code=status.HTTP_302_FOUND,\n    )"
    fallback_new = """    return FileResponse(
        f'{STATIC_DIR}/favicon.png',
        media_type='image/png',
        headers={'Cache-Control': 'no-cache, must-revalidate'}
    )"""
    if fallback_old in code:
        code = code.replace(fallback_old, fallback_new)
        print("Updated fallback image in models.py to FileResponse")
    
    with open(MODELS_ROUTER, "w", encoding="utf-8") as f:
        f.write(code)
    print("Patched routers/models.py successfully!")

# 2. Patch main.py to stop popping profile_image_url
if os.path.exists(MAIN_PY):
    with open(MAIN_PY, "r", encoding="utf-8") as f:
        code = f.read()
    
    code = code.replace(
        "model['info']['meta'].pop('profile_image_url', None)",
        "# model['info']['meta'].pop('profile_image_url', None)  # Preserved for Aegis AI"
    )
    with open(MAIN_PY, "w", encoding="utf-8") as f:
        f.write(code)
    print("Patched main.py to preserve profile_image_url!")

# 3. Patch compiled JS bundles for cache-busting and removal of dark:invert
js_files = glob.glob("/app/build/_app/immutable/**/*.js", recursive=True)
patched_count = 0

for jf in js_files:
    with open(jf, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    orig_len = len(content)
    # Replace static asset paths with cache-busted versions
    content = content.replace("static/favicon.png", "static/favicon.png?v=aegis3")
    content = content.replace("static/splash.png", "static/splash.png?v=aegis3")
    content = content.replace('"/favicon.png"', '"/static/favicon.png?v=aegis3"')
    content = content.replace("'/favicon.png'", "'/static/favicon.png?v=aegis3'")
    
    # Disable dark:invert on logo img
    content = content.replace("dark:invert p-0.5", "dark:invert-0 p-0.5")
    
    if len(content) != orig_len or "aegis3" in content:
        with open(jf, "w", encoding="utf-8") as f:
            f.write(content)
        patched_count += 1

print(f"Patched {patched_count} JavaScript bundle files with cache-busting (?v=aegis3)!")

# 4. Clean up custom.css (remove content: url(...) that breaks Safari/Chromium)
CUSTOM_CSS_PATHS = [
    "/app/backend/open_webui/static/custom.css",
    "/app/build/static/custom.css"
]

for css_path in CUSTOM_CSS_PATHS:
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        
        # Replace the content: url(...) replacement block with pure styling
        content_rule_pattern = r"(#[^\{]+\{[^\}]*content:\s*url\([^\}]+\}[^\}]*\})"
        css = re.sub(
            r"#sidebar-toggle-button img,[\s\S]*?#logo-her\s*\{[\s\S]*?\}",
            """/* Aegis AI Logo Styling */
img[alt="logo"],
img[alt="favicon"],
nav button[aria-label="Home"] img,
nav button[aria-label="Chat"] img,
#sidebar-toggle-button img,
button[id*="model-selector"] img,
div[id*="model"] img,
#logo,
#logo-her {
  filter: none !important;
  -webkit-filter: none !important;
  border-radius: 8px !important;
  object-fit: contain !important;
}""",
            css
        )
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css)
        print(f"Cleaned up {css_path}")

# 5. Enhance loader.js with aggressive runtime image swap
LOADER_PATHS = [
    "/app/backend/open_webui/static/loader.js",
    "/app/build/static/loader.js"
]

enhanced_loader = """// Aegis AI Runtime Branding Injector v3
(function() {
    'use strict';
    
    const BRAND_NAME = 'Aegis AI';
    const FULL_TITLE = 'Aegis AI — Enterprise Intelligence Platform';
    const AEGIS_LOGO_SRC = '/static/favicon.png?v=aegis3';
    
    function updateBranding() {
        // Document Title
        if (!document.title.includes('Aegis AI')) {
            document.title = FULL_TITLE;
        }
        
        // Find all logo and avatar images
        const logoSelectors = [
            'img[alt="logo"]',
            'img[alt="favicon"]',
            '#sidebar-toggle-button img',
            'nav button[aria-label="Home"] img',
            'nav button[aria-label="Chat"] img',
            'button[id*="model-selector"] img',
            'img.assistant-message-profile-image'
        ];
        
        const imgs = document.querySelectorAll(logoSelectors.join(', '));
        imgs.forEach(img => {
            img.style.filter = 'none';
            img.style.webkitFilter = 'none';
            // If image is still pointing to default un-busted or old favicon, swap it
            if (!img.src || img.src.includes('favicon.png') && !img.src.includes('v=aegis3')) {
                img.src = AEGIS_LOGO_SRC;
            }
        });
        
        // Update header & text nodes
        const titleEl = document.querySelector('title');
        if (titleEl && titleEl.innerText.includes('Open WebUI')) {
            titleEl.innerText = titleEl.innerText.replace('Open WebUI', BRAND_NAME);
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateBranding);
    } else {
        updateBranding();
    }
    
    // Continuous brand enforcement
    setInterval(updateBranding, 1000);
})();
"""

for lp in LOADER_PATHS:
    with open(lp, "w", encoding="utf-8") as f:
        f.write(enhanced_loader)
    print(f"Updated loader.js at {lp}")

print("=== Advanced Aegis Brand & Cache Fix Completed Successfully ===")

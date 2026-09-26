// Aegis AI Runtime Branding & Enterprise UI Enhancer v8
// Enterprise Standards for Executive Pitching & Rebranded Aegis Agent
(function() {
    'use strict';
    
    const BRAND_NAME = 'Aegis AI';
    const FULL_TITLE = 'Aegis AI — Enterprise Intelligence Platform';
    const AEGIS_LOGO_SRC = '/static/favicon.png?v=aegis_brand2';
    const AEGIS_AGENT_AVATAR_SRC = '/static/aegis-agent-avatar.png?v=agent_brand2';
    
    const COPYRIGHT_HTML = `
        <div class="aegis-enterprise-footer-inner">
            <span class="aegis-cr-text">© 2026 <strong>Aegis AI</strong> • Maudy Network</span>
        </div>
    `;

    const SECURITY_BADGE_HTML = `
        <div class="aegis-sec-badge-inner" title="Enterprise Zero-Trust Cluster • 256-Bit TLS Secured">
            <span class="aegis-sec-lock">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
            </span>
            <span class="aegis-sec-text aegis-sec-enc">End-to-End Encrypted</span>
            <span class="aegis-sec-divider">•</span>
            <span class="aegis-sec-pulse-dot"></span>
            <span class="aegis-sec-text aegis-sec-node">Sovereign Node: <strong class="aegis-sec-node-id">exac-cluster-01</strong></span>
        </div>
    `;

    // 1. Master Update Loop
    function updateAll() {
        updateBranding();
        updateAuthPage();
        dismissUpdateToast();
        updateAgentBrandingAndAvatars();
        updateSecurityBadge();
        removeModelStatusPill();
        updateMacCodeBlocks();
        updateMessageBubbles();
        updateCopyrightBar();
        initOmnibarGlow();
    }

    // 1b. Auth Portal Presentation Enhancer
    function updateAuthPage() {
        const authCard = document.querySelector('#auth-login-card');
        if (!authCard) return;

        const isDark = document.documentElement.classList.contains('dark');

        authCard.style.maxWidth = '450px';
        authCard.style.padding = '40px 36px 36px 36px';
        authCard.style.borderRadius = '24px';
        if (isDark) {
            authCard.style.background = 'radial-gradient(ellipse at top, rgba(13, 31, 56, 0.88) 0%, rgba(5, 12, 22, 0.96) 100%)';
            authCard.style.border = '1px solid rgba(56, 189, 248, 0.25)';
            authCard.style.boxShadow = '0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 50px -10px rgba(11, 52, 102, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
        } else {
            authCard.style.background = '#FFFFFF';
            authCard.style.border = '1px solid #E2E8F0';
            authCard.style.boxShadow = '0 20px 40px -15px rgba(0, 0, 0, 0.08), 0 0 25px -5px rgba(37, 99, 235, 0.1)';
        }
        authCard.style.backdropFilter = 'blur(24px)';
        authCard.style.webkitBackdropFilter = 'blur(24px)';

        if (!authCard.querySelector('.aegis-login-branding')) {
            const form = authCard.querySelector('form');
            if (form) {
                const brandDiv = document.createElement('div');
                brandDiv.className = 'aegis-login-branding';
                brandDiv.style = 'margin-bottom: 24px; display: flex; flex-direction: column; align-items: center; justify-content: center;';
                const logoSrc = isDark ? '/static/splash-dark.png?v=aegis_brand2' : '/static/splash.png?v=aegis_brand2';
                brandDiv.innerHTML = `
                    <div style="margin-bottom: 14px; position: relative;">
                        <img src="${logoSrc}" alt="Aegis AI" style="height: 52px; width: auto; max-width: 260px; object-fit: contain; filter: drop-shadow(0 4px 18px rgba(0, 163, 255, 0.25));" />
                    </div>
                    <div style="font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: #0284c7; font-weight: 600; display: flex; align-items: center; gap: 7px; background: rgba(56, 189, 248, 0.08); padding: 5px 12px; border-radius: 9999px; border: 1px solid rgba(56, 189, 248, 0.2);">
                        <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #0284c7; box-shadow: 0 0 10px #0284c7;"></span>
                        Enterprise Zero-Trust Platform
                    </div>
                `;
                form.insertBefore(brandDiv, form.firstChild);
            }
        }
    }

    // 1c. Clean Presentation Mode (Dismiss Update Banner safely)
    function dismissUpdateToast() {
        // Target only the specific update toast link or its container safely
        const updateLinks = document.querySelectorAll('a[href*="github.com/open-webui/open-webui/releases"]');
        updateLinks.forEach(link => {
            const toast = link.closest('.fixed, .absolute');
            if (toast && toast !== document.body && !toast.contains(document.querySelector('main')) && !toast.contains(document.querySelector('nav'))) {
                toast.style.display = 'none';
            }
        });

        // Safeguard: Ensure SvelteKit root container is NEVER hidden
        const svelteRoot = document.querySelector('body > div:first-child');
        if (svelteRoot && svelteRoot.style.display === 'none') {
            svelteRoot.style.display = 'contents';
        }
    }

    // 2. Core Global Branding
    function updateBranding() {
        if (!document.title.includes('Aegis AI')) {
            document.title = FULL_TITLE;
        }
        
        const aegisSelectors = [
            '#sidebar-toggle-button img',
            'nav button[aria-label="Home"] img',
            'nav button[aria-label="Chat"] img',
            'img[alt="logo"]',
            'img[alt="favicon"]'
        ];
        
        document.querySelectorAll(aegisSelectors.join(', ')).forEach(img => {
            img.style.filter = 'none';
            img.style.webkitFilter = 'none';
            if (!img.src || !img.src.includes('v=aegis_brand2')) {
                img.src = AEGIS_LOGO_SRC;
            }
        });
        
        const titleEl = document.querySelector('title');
        if (titleEl && titleEl.innerText.includes('Open WebUI')) {
            titleEl.innerText = titleEl.innerText.replace(/Open WebUI/g, BRAND_NAME);
        }
    }

    // 3. Aegis Agent Avatars & Text Rebranding
    function updateAgentBrandingAndAvatars() {
        // Rebrand text inside model-selector and model headers safely WITHOUT mutating general text nodes
        const modelLabels = document.querySelectorAll(
            '#model-selector, button[id*="model-selector"], #response-message-model-name, .model-item, [data-model-name]'
        );
        modelLabels.forEach(el => {
            if (el.innerText && el.innerText.includes('Hermes Agent')) {
                Array.from(el.childNodes).forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE && node.nodeValue.includes('Hermes Agent')) {
                        node.nodeValue = node.nodeValue.replace(/Hermes Agent(\s*\(Takok AI\))?/g, 'Aegis Agent');
                    }
                });
            }
        });

        // Dropdown options & model selector items
        document.querySelectorAll('button[id*="model-selector"], #model-selector, .model-item').forEach(el => {
            const txt = (el.innerText || '').toLowerCase();
            if (txt.includes('aegis agent') || txt.includes('hermes agent') || txt.includes('hermes-agent')) {
                const img = el.querySelector('img');
                if (img && !img.src.includes('v=agent_brand2')) {
                    img.src = AEGIS_AGENT_AVATAR_SRC;
                    img.style.borderRadius = '50%';
                    img.style.objectFit = 'cover';
                }
            }
        });

        // Chat message profile pictures for Agent
        document.querySelectorAll('img.assistant-message-profile-image, .chat-message img').forEach(img => {
            const msgContainer = img.closest('[data-message-id]') || img.closest('.chat-message') || img.closest('.group');
            if (msgContainer) {
                const text = (msgContainer.innerText || '').toLowerCase();
                const modelEl = msgContainer.querySelector('#response-message-model-name');
                const modelTxt = modelEl ? modelEl.innerText.toLowerCase() : '';

                if (modelTxt.includes('agent') || modelTxt.includes('hermes') || text.includes('takok') || text.includes('aegis agent')) {
                    if (!img.src.includes('v=agent_brand2')) {
                        img.src = AEGIS_AGENT_AVATAR_SRC;
                        img.style.borderRadius = '50%';
                        img.style.objectFit = 'cover';
                    }
                }
            }
        });
    }

    // 4. Point 3: Header Security & Sovereignty Badge
    function updateSecurityBadge() {
        if (document.querySelector('#aegis-security-badge')) {
            return;
        }

        const navRightTarget = document.querySelector('nav .mr-1.flex.flex-none') || 
                               document.querySelector('nav button#temporary-chat-button')?.parentElement ||
                               document.querySelector('nav button[aria-label="Controls"]')?.parentElement ||
                               document.querySelector('nav .flex.items-center.w-full') ||
                               document.querySelector('nav');
        
        if (navRightTarget) {
            const badge = document.createElement('div');
            badge.id = 'aegis-security-badge';
            badge.className = 'aegis-security-badge';
            badge.innerHTML = SECURITY_BADGE_HTML;

            if (navRightTarget.classList.contains('flex-none') || navRightTarget.classList.contains('gap-2')) {
                navRightTarget.insertBefore(badge, navRightTarget.firstChild);
            } else {
                navRightTarget.appendChild(badge);
            }
        }
    }

    // 5. Clean Omnibar Header (Pill removed per user request)
    function removeModelStatusPill() {
        const pills = document.querySelectorAll('#aegis-model-status-pill, .aegis-model-status-pill');
        pills.forEach(p => p.remove());
    }

    // 6. Point 4: Luxury macOS-Style Code Blocks
    function updateMacCodeBlocks() {
        const codeCopyButtons = document.querySelectorAll('button.copy-code-button');
        codeCopyButtons.forEach(btn => {
            const headerRow = btn.closest('div.flex') || btn.parentElement;
            if (!headerRow || headerRow.querySelector('.aegis-mac-controls')) {
                return;
            }

            const macControls = document.createElement('div');
            macControls.className = 'aegis-mac-controls';
            macControls.innerHTML = `
                <span class="aegis-mac-dot dot-close" title="Close"></span>
                <span class="aegis-mac-dot dot-min" title="Minimize"></span>
                <span class="aegis-mac-dot dot-max" title="Zoom"></span>
            `;

            headerRow.insertBefore(macControls, headerRow.firstChild);
            headerRow.classList.add('aegis-mac-code-header');

            const parentBlock = headerRow.parentElement;
            if (parentBlock) {
                parentBlock.classList.add('aegis-mac-code-window');
            }
        });
    }

    // 7. Point 2: Chat Message Left-Border & Accent Distinction
    function updateMessageBubbles() {
        const messageBodies = document.querySelectorAll('.markdown-prose, .markdown-prose-sm');
        messageBodies.forEach(el => {
            const row = el.closest('[data-message-id]') || el.closest('.chat-message') || el.closest('.group');
            if (!row || row.classList.contains('aegis-bubble-tagged')) {
                return;
            }

            row.classList.add('aegis-bubble-tagged');
            const rowText = (row.innerText || '').toLowerCase();
            const modelNameEl = row.querySelector('#response-message-model-name');
            const modelName = modelNameEl ? modelNameEl.innerText.toLowerCase() : '';

            if (modelName.includes('agent') || modelName.includes('hermes') || rowText.includes('takok') || rowText.includes('aegis agent')) {
                row.classList.add('aegis-msg-bubble-agent', 'aegis-msg-bubble-hermes');
            } else {
                row.classList.add('aegis-msg-bubble-aegis');
            }
        });
    }

    // 8. Point 5: Omnibar Focus Glow
    function initOmnibarGlow() {
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(ta => {
            if (ta.dataset.aegisGlowBound) return;
            ta.dataset.aegisGlowBound = 'true';

            const card = ta.closest('form') || ta.closest('div.border') || ta.parentElement;
            if (!card) return;

            card.classList.add('aegis-omnibar-card');

            ta.addEventListener('focus', () => {
                card.classList.add('aegis-omnibar-focused');
            });
            ta.addEventListener('blur', () => {
                card.classList.remove('aegis-omnibar-focused');
            });
        });
    }

    // 9. Enterprise Copyright Bar at Page Bottom
    function updateCopyrightBar() {
        // Only target the specific disclaimer below chat input box (never touch chat history or messages)
        const disclaimerEls = document.querySelectorAll('form + div.text-xs, div[class*="text-xs"][class*="text-gray-500"][class*="text-center"], .aegis-disclaimer-replaced');
        disclaimerEls.forEach(el => {
            if (el.closest('.chat-message') || el.closest('#messages-container') || el.closest('.sidebar') || el.closest('nav')) {
                return;
            }
            const text = (el.innerText || '').toLowerCase();
            if (text.includes('make mistakes') || text.includes('verify') || el.classList.contains('aegis-disclaimer-replaced')) {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.style.height = '0';
                el.style.margin = '0';
                el.style.padding = '0';
            }
        });

        // Ensure single persistent copyright footer is anchored directly to document.body at page bottom
        let footerEl = document.querySelector('#aegis-persistent-footer');
        if (!footerEl) {
            footerEl = document.createElement('div');
            footerEl.id = 'aegis-persistent-footer';
            document.body.appendChild(footerEl);
        } else if (footerEl.parentElement !== document.body) {
            document.body.appendChild(footerEl);
        }

        if (footerEl.innerHTML !== COPYRIGHT_HTML) {
            footerEl.innerHTML = COPYRIGHT_HTML;
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateAll);
    } else {
        updateAll();
    }
    
    // Continuous enforcement every 500ms
    setInterval(updateAll, 500);
})();

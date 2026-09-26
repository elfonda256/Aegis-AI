/**
 * AEGIS AI — Interactive Chat Workspace & Agent Dashboard Simulator
 */

document.addEventListener('DOMContentLoaded', () => {
  // Tab Switcher (Chat vs Dashboard)
  const tabBtns = document.querySelectorAll('.workspace-tab-btn');
  const chatView = document.getElementById('chatWorkspaceView');
  const dashboardView = document.getElementById('dashboardWorkspaceView');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.dataset.tab;

      if (target === 'chat') {
        chatView.style.display = 'flex';
        dashboardView.style.display = 'none';
      } else {
        chatView.style.display = 'none';
        dashboardView.style.display = 'flex';
      }
    });
  });

  // Chat Simulator State
  const chatInput = document.getElementById('simChatInput');
  const chatSendBtn = document.getElementById('simChatSendBtn');
  const chatMessages = document.getElementById('simChatMessages');
  const activeModelDisplay = document.getElementById('simActiveModel');
  const modelSelectDropdown = document.getElementById('simModelSelect');
  const agentSelectDropdown = document.getElementById('simAgentSelect');

  // Realistic Autonomous AI Responses
  const responses = {
    "security": "🛡️ **Aegis Security Sentinel Analysis Complete**:\n- Active Perimeter: Secured with zero-trust encryption (AES-256-GCM).\n- Threat Telemetry: No unverified outbound API egress detected.\n- Compliance: GDPR & SOC2 Type II controls verified across all 14 nodes.",
    "automation": "⚡ **Aegis Autonomous Workflow Dispatched**:\n- Task: Cross-system document classification & ERP synch.\n- Estimated Completion: 1.4s.\n- Autonomous Agent #04 has verified 128 invoice records with 99.98% confidence score.",
    "knowledge": "📚 **Aegis Knowledge Intelligence (RAG)**:\n- Retrieved 4 authoritative internal documents across encrypted vector indices.\n- Semantic match confidence: 0.942.\n- Summary: Enterprise data isolation confirmed. No model training on tenant data.",
    "default": "Hello! I am **Aegis AI**, your intelligent AI guardian. Your session is end-to-end encrypted with dedicated enterprise hardware isolation. How can I assist your team with autonomous workflows, code verification, or data analysis today?"
  };

  function appendMessage(role, text) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;
    
    if (role === 'assistant') {
      bubble.innerHTML = `
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:0.75rem; color:#00E5FF; font-weight:700;">
          <span class="status-dot"></span> AEGIS AI GUARDIAN (${activeModelDisplay.textContent})
        </div>
        <div>${text.replace(/\n/g, '<br/>')}</div>
      `;
    } else {
      bubble.textContent = text;
    }

    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function handleSend() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    chatInput.value = '';

    // Show simulated typing indicator
    const typingBubble = document.createElement('div');
    typingBubble.className = 'chat-bubble assistant';
    typingBubble.id = 'simTypingIndicator';
    typingBubble.innerHTML = `<span style="color:#00E5FF;">Aegis AI is synthesizing neural response...</span>`;
    chatMessages.appendChild(typingBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    setTimeout(() => {
      const indicator = document.getElementById('simTypingIndicator');
      if (indicator) indicator.remove();

      let reply = responses.default;
      const lower = text.toLowerCase();
      if (lower.includes('security') || lower.includes('threat') || lower.includes('audit')) {
        reply = responses.security;
      } else if (lower.includes('workflow') || lower.includes('auto') || lower.includes('task')) {
        reply = responses.automation;
      } else if (lower.includes('knowledge') || lower.includes('doc') || lower.includes('search')) {
        reply = responses.knowledge;
      }

      appendMessage('assistant', reply);
    }, 750);
  }

  if (chatSendBtn && chatInput) {
    chatSendBtn.addEventListener('click', handleSend);
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleSend();
    });
  }

  // Model & Agent Dropdown changes
  if (modelSelectDropdown) {
    modelSelectDropdown.addEventListener('change', (e) => {
      activeModelDisplay.textContent = e.target.value;
      appendMessage('assistant', `Active neural model switched to **${e.target.value}**. Memory cache purged for zero-retention privacy.`);
    });
  }

  // Modal Controls
  const loginModal = document.getElementById('loginModal');
  const openLoginBtns = document.querySelectorAll('.open-login-modal');
  const closeModalBtns = document.querySelectorAll('.close-modal-btn');

  openLoginBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (loginModal) loginModal.classList.add('active');
    });
  });

  closeModalBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-overlay');
      if (modal) modal.classList.remove('active');
    });
  });

  // Close on outside click
  window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
      e.target.classList.remove('active');
    }
  });

  // Prompt Pill Quick Clicks
  const promptPills = document.querySelectorAll('.prompt-suggestion-pill');
  promptPills.forEach(pill => {
    pill.addEventListener('click', () => {
      if (chatInput) {
        chatInput.value = pill.textContent.trim();
        handleSend();
      }
    });
  });
});

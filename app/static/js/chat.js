// ========================================
// Chat Widget – Fliesen Showroom Frankfurt
// ========================================

document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('chat-toggle');
    const chatWindow = document.getElementById('chat-window');
    const closeBtn = document.getElementById('chat-close');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');
    const messages = document.getElementById('chat-messages');

    if (!toggle) return;

    // Toggle chat window
    toggle.addEventListener('click', function () {
        const isVisible = chatWindow.style.display !== 'none';
        chatWindow.style.display = isVisible ? 'none' : 'flex';
        if (!isVisible) input.focus();
    });

    closeBtn.addEventListener('click', function () {
        chatWindow.style.display = 'none';
    });

    // Send message
    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        // Add user message
        addMessage(text, 'user');
        input.value = '';

        // Show typing indicator
        const typingId = showTyping();

        // Send to API
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => {
            removeTyping(typingId);
            addMessage(data.response, 'bot');
        })
        .catch(() => {
            removeTyping(typingId);
            addMessage('Entschuldigung, es gab einen Fehler. Bitte versuchen Sie es später.', 'bot');
        });
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') sendMessage();
    });

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = sender === 'user' ? 'chat-user-msg mb-2' : 'chat-bot-msg mb-2';
        const bgClass = sender === 'user' ? 'bg-accent text-white' : 'bg-light';
        div.innerHTML = `<small class="${bgClass} rounded px-3 py-2 d-inline-block">${escapeHtml(text)}</small>`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    function showTyping() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.className = 'chat-bot-msg mb-2';
        div.id = id;
        div.innerHTML = '<small class="bg-light rounded px-3 py-2 d-inline-block text-muted"><i class="bi bi-three-dots"></i> Wird geschrieben...</small>';
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return id;
    }

    function removeTyping(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});

// ========================================
// MENTAL HEALTH CHATBOT - SIMPLE VERSION
// ========================================

let currentSessionId = null;
let currentToken = localStorage.getItem('auth_token');
let messageCount = 0;

const API = 'http://localhost:5000';

// DOM
const chat = document.getElementById('chatContainer');
const input = document.getElementById('messageInput');
const btn = document.getElementById('sendBtn');
const form = document.getElementById('chatForm');
const startBtn = document.getElementById('startChatBtn');
const spinner = document.getElementById('spinner');

// ===== INIT =====

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 App loaded');
    console.log('Token:', currentToken ? '✅ Found' : '❌ Not found');
    
    if (startBtn) startBtn.onclick = createSession;
    if (form) form.onsubmit = sendMessage;
});

// ===== CREATE SESSION =====

async function createSession() {
    try {
        console.log('📝 Creating session...');
        
        if (!currentToken) {
            alert('Please login first!');
            return;
        }

        const res = await fetch(`${API}/api/chat/session/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: '{}'
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const data = await res.json();
        console.log('Response:', data);
        
        if (!data.data?.session_id) {
            throw new Error('No session_id in response');
        }

        currentSessionId = data.data.session_id;
        messageCount = 0;
        
        console.log('✅ Session created:', currentSessionId);
        
        // Clear chat
        chat.innerHTML = '';
        addBotMessage('Hello! I\'m here to listen. How are you feeling?');
        
        // Enable input
        input.disabled = false;
        btn.disabled = false;
        
    } catch (e) {
        console.error('❌ Session error:', e);
        alert('Error: ' + e.message);
    }
}

// ===== SEND MESSAGE =====

async function sendMessage(e) {
    e.preventDefault();

    if (!currentSessionId) {
        alert('Start a session first!');
        return;
    }

    const msg = input.value.trim();
    if (!msg) return;

    // Show user message
    addUserMessage(msg);
    input.value = '';
    btn.disabled = true;

    try {
        console.log('📤 Sending:', msg);
        
        spinner.style.display = 'block';

        const res = await fetch(`${API}/api/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: msg
            })
        });

        console.log('Response status:', res.status);

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || `HTTP ${res.status}`);
        }

        const data = await res.json();
        console.log('📥 Response:', data);

        if (!data.success) {
            throw new Error(data.error || 'Request failed');
        }

        if (!data.response) {
            throw new Error('No response field');
        }

        // Show bot message
        addBotMessage(data.response);
        
        // Update mood
        if (data.analysis) {
            updateMood(data.analysis);
        }

        messageCount++;
        const cnt = document.getElementById('messageCount');
        if (cnt) cnt.textContent = messageCount;

    } catch (e) {
        console.error('❌ Send error:', e);
        addBotMessage(`❌ Error: ${e.message}`);
    } finally {
        spinner.style.display = 'none';
        btn.disabled = false;
        input.focus();
    }
}

// ===== UI HELPERS =====

function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message user';
    div.innerHTML = `
        <div class="message-content">${escapeHtml(text)}</div>
        <div class="message-time">${getTime()}</div>
    `;
    chat.appendChild(div);
    scroll();
}

function addBotMessage(text) {
    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = `
        <div class="message-content">${escapeHtml(text)}</div>
        <div class="message-time">${getTime()}</div>
    `;
    chat.appendChild(div);
    scroll();
}

function updateMood(analysis) {
    const emotion = analysis.primary_emotion || 'unknown';
    const score = analysis.sentiment_score || 0;
    
    console.log('Emotion:', emotion, 'Score:', score);
    
    const el = document.getElementById('currentMood');
    if (el) {
        const emoji = getEmoji(emotion);
        el.textContent = `${emoji} ${emotion}`;
    }
}

function getEmoji(emotion) {
    const map = {
        sadness: '😢',
        anxiety: '😰',
        anger: '😠',
        fear: '😨',
        joy: '😊',
        neutral: '😐'
    };
    return map[emotion] || '😐';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scroll() {
    setTimeout(() => chat.scrollTop = chat.scrollHeight, 50);
}

console.log('✅ App ready!');
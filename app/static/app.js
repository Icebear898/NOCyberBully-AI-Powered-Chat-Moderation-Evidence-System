let ws = null;
let myUsername = null;
let peerUsername = null;

function appendBubble(text, type = 'other') {
  const win = document.getElementById('chatWindow');
  const row = document.createElement('div');
  row.className = 'row';
  const bubble = document.createElement('div');
  bubble.className = `bubble ${type}`;
  bubble.textContent = text;
  row.appendChild(bubble);
  win.appendChild(row);
  win.scrollTop = win.scrollHeight;
}

function connect() {
  myUsername = document.getElementById('username').value.trim();
  peerUsername = document.getElementById('peer').value.trim();
  const sensitivity = document.getElementById('sensitivity').value;
  if (!myUsername || !peerUsername) {
    alert('Enter both usernames');
    return;
  }
  // Set sensitivity for this user
  const form = new FormData();
  form.append('username', myUsername);
  form.append('sensitivity', sensitivity);
  fetch('/settings', { method: 'POST', body: form }).catch(() => {});
  ws = new WebSocket(`ws://${location.host}/ws/${encodeURIComponent(myUsername)}`);

  ws.onopen = () => {
    document.getElementById('chatArea').classList.remove('hidden');
    appendBubble('Connected. Start chatting...', 'system');
  };

  ws.onmessage = async (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === 'message') {
      const isMe = msg.from === myUsername;
      appendBubble(`${msg.from}: ${msg.message}`, isMe ? 'me' : 'other');
    } else if (msg.type === 'bot') {
      appendBubble(`BOT: ${msg.message}`, 'bot');
    } else if (msg.type === 'bot_info') {
      appendBubble(`INFO: ${msg.message}`, 'system');
    } else if (msg.type === 'capture_screenshot') {
      try {
        const chatEl = document.querySelector('.chat-window');
        const canvas = await html2canvas(chatEl, {scale: 1});
        const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
        const form = new FormData();
        form.append('message_id', msg.context.message_id);
        form.append('screenshot', blob, 'shot.png');
        await fetch('/upload_screenshot', { method: 'POST', body: form });
      } catch (e) {
        console.error('Screenshot failed', e);
      }
    }
  };

  ws.onclose = () => {
    appendBubble('Disconnected', 'system');
  };
}

function sendMessage() {
  const input = document.getElementById('message');
  const text = input.value;
  if (!text) return;
  ws.send(JSON.stringify({ to: peerUsername, message: text }));
  input.value = '';
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('connectBtn').addEventListener('click', connect);
  document.getElementById('sendBtn').addEventListener('click', sendMessage);
  document.getElementById('message').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
  document.getElementById('blockBtn').addEventListener('click', () => {
    if (!myUsername || !peerUsername) return;
    const form = new FormData();
    form.append('victim', myUsername);
    form.append('offender', peerUsername);
    fetch('/block', { method: 'POST', body: form }).then(() => appendBubble(`You blocked ${peerUsername}`, 'system'));
  });
  document.getElementById('unblockBtn').addEventListener('click', () => {
    if (!myUsername || !peerUsername) return;
    const form = new FormData();
    form.append('victim', myUsername);
    form.append('offender', peerUsername);
    fetch('/unblock', { method: 'POST', body: form }).then(() => appendBubble(`You unblocked ${peerUsername}`, 'system'));
  });
});

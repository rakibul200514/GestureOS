// GestureOS — Frontend Client Logic

document.addEventListener('DOMContentLoaded', () => {
  // UI Element References
  const fpsCounter = document.getElementById('fpsCounter');
  const safeModeBadge = document.getElementById('safeModeBadge');
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');
  const emergencyStopBtn = document.getElementById('emergencyStopBtn');
  const masterControlToggle = document.getElementById('masterControlToggle');
  const toggleLabel = document.getElementById('toggleLabel');
  const handDetectedTag = document.getElementById('handDetectedTag');
  const currentGestureTag = document.getElementById('currentGestureTag');
  const logsList = document.getElementById('logsList');
  const clearLogsBtn = document.getElementById('clearLogsBtn');

  // Sliders
  const smoothingSlider = document.getElementById('smoothingSlider');
  const smoothingVal = document.getElementById('smoothingVal');
  const cooldownSlider = document.getElementById('cooldownSlider');
  const cooldownVal = document.getElementById('cooldownVal');

  // Gesture Cards
  const gestureCards = {
    'Pointer': document.getElementById('cardPointer'),
    'Click': document.getElementById('cardClick'),
    'Scroll': document.getElementById('cardScroll'),
    'Pause': document.getElementById('cardPause'),
    'Stop': document.getElementById('cardStop')
  };

  // Helper to add log entries
  function appendLog(message, type = 'action') {
    const time = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${time}] ${message}`;
    logsList.appendChild(entry);
    logsList.scrollTop = logsList.scrollHeight;

    // Keep maximum 50 entries
    if (logsList.children.length > 50) {
      logsList.removeChild(logsList.firstChild);
    }
  }

  // Update Safe Mode & Control UI
  function updateControlUI(isActive) {
    masterControlToggle.checked = isActive;
    if (isActive) {
      statusDot.className = 'badge-dot green';
      statusText.textContent = 'MOUSE ACTIVE (LIVE)';
      toggleLabel.textContent = 'Mouse Control Active (Click to Lock)';
      toggleLabel.style.color = '#00ff88';
    } else {
      statusDot.className = 'badge-dot red';
      statusText.textContent = 'SAFE MODE (LOCKED)';
      toggleLabel.textContent = 'Safe Mode Active (Click to Enable)';
      toggleLabel.style.color = '#e2e8f0';
    }
  }

  // Highlight active gesture card
  function highlightGestureCard(gestureKey) {
    Object.values(gestureCards).forEach(card => card.classList.remove('active'));
    if (gestureCards[gestureKey]) {
      gestureCards[gestureKey].classList.add('active');
    }
  }

  // 1. Establish WebSocket Connection
  let ws = null;
  function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('[WS] Connected to GestureOS backend.');
      appendLog('WebSocket stream connected to AI vision engine.', 'system');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Update FPS
        if (data.fps !== undefined) {
          fpsCounter.textContent = Math.round(data.fps);
        }

        // Update Hand Presence
        if (data.hand_detected) {
          handDetectedTag.textContent = 'HAND DETECTED';
          handDetectedTag.style.color = '#00f0ff';
        } else {
          handDetectedTag.textContent = 'SEARCHING HAND...';
          handDetectedTag.style.color = '#8492a6';
        }

        // Update Gesture state
        if (data.gesture) {
          currentGestureTag.textContent = data.gesture.toUpperCase();
          highlightGestureCard(data.gesture_type);
        }

        // Update Safe Mode / Active State
        if (data.is_active !== undefined && masterControlToggle.checked !== data.is_active) {
          updateControlUI(data.is_active);
        }

        // Handle Log Events from backend
        if (data.new_log) {
          appendLog(data.new_log.text, data.new_log.level);
        }

      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onclose = () => {
      console.warn('[WS] Disconnected. Reconnecting in 2s...');
      setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
      console.error('[WS Error]', err);
    };
  }

  connectWebSocket();

  // 2. Master Toggle Switch Event
  masterControlToggle.addEventListener('change', async () => {
    try {
      const response = await fetch('/api/toggle_control', { method: 'POST' });
      const data = await response.json();
      updateControlUI(data.is_active);
      appendLog(data.is_active ? 'User ENABLED mouse control.' : 'User locked into SAFE MODE.', data.is_active ? 'action' : 'safe');
    } catch (err) {
      console.error('Failed to toggle control:', err);
    }
  });

  // 3. Emergency Stop Button Event
  emergencyStopBtn.addEventListener('click', async () => {
    try {
      const response = await fetch('/api/emergency_stop', { method: 'POST' });
      const data = await response.json();
      updateControlUI(false);
      appendLog('EMERGENCY STOP TRIGGERED! Control locked.', 'alert');
    } catch (err) {
      console.error('Emergency stop failed:', err);
    }
  });

  // 4. Sensitivity Sliders Events
  smoothingSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    smoothingVal.textContent = val;
    sendSettings({ smoothing: val });
  });

  cooldownSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    cooldownVal.textContent = `${val.toFixed(1)}s`;
    sendSettings({ click_cooldown: val });
  });

  async function sendSettings(settings) {
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
    } catch (err) {
      console.error('Failed to update settings:', err);
    }
  }

  // 5. Clear Logs
  clearLogsBtn.addEventListener('click', () => {
    logsList.innerHTML = '<div class="log-entry system">[SYSTEM] Logs cleared.</div>';
  });
});

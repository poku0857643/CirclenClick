/**
 * Popup Script
 * Manages extension popup UI and settings
 */

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const targetTab = tab.getAttribute('data-tab');

    // Update active tab
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    // Update active panel
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`${targetTab}-panel`)?.classList.add('active');
  });
});

// Status checking
async function checkBackendStatus() {
  const statusBadge = document.getElementById('backend-status');
  const cloudApisStatus = document.getElementById('cloud-apis-status');
  const cacheStatus = document.getElementById('cache-status');

  if (!statusBadge) return;

  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_STATUS' });

    if (response.success) {
      statusBadge.textContent = 'Online';
      statusBadge.className = 'status-badge online';

      const status = response.data;
      cloudApisStatus!.textContent = status.cloud_apis ? 'Enabled' : 'Disabled';
      cacheStatus!.textContent = `${status.cache?.items || 0} items`;
    } else {
      statusBadge.textContent = 'Offline';
      statusBadge.className = 'status-badge offline';
      cloudApisStatus!.textContent = 'Unknown';
      cacheStatus!.textContent = 'Unknown';
    }
  } catch (error) {
    statusBadge.textContent = 'Error';
    statusBadge.className = 'status-badge offline';
    cloudApisStatus!.textContent = 'Unknown';
    cacheStatus!.textContent = 'Unknown';
  }
}

// Activate Circle & Click
document.getElementById('activate-btn')?.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (tab.id) {
    await chrome.tabs.sendMessage(tab.id, { type: 'ACTIVATE_SELECTOR' });
    window.close();
  }
});

// Refresh status
document.getElementById('refresh-btn')?.addEventListener('click', () => {
  checkBackendStatus();
});

// Settings management
async function loadSettings() {
  const settings = await chrome.storage.local.get({
    strategy: 'hybrid',
    autoActivate: false
  });

  const strategySelect = document.getElementById('strategy-select') as HTMLSelectElement;
  const autoActivateCheckbox = document.getElementById('auto-activate') as HTMLInputElement;

  if (strategySelect) strategySelect.value = settings.strategy;
  if (autoActivateCheckbox) autoActivateCheckbox.checked = settings.autoActivate;
}

document.getElementById('save-settings-btn')?.addEventListener('click', async () => {
  const strategySelect = document.getElementById('strategy-select') as HTMLSelectElement;
  const autoActivateCheckbox = document.getElementById('auto-activate') as HTMLInputElement;

  await chrome.storage.local.set({
    strategy: strategySelect.value,
    autoActivate: autoActivateCheckbox.checked
  });

  // Show success feedback
  const btn = document.getElementById('save-settings-btn');
  if (btn) {
    const originalText = btn.textContent;
    btn.textContent = 'Saved!';
    setTimeout(() => {
      btn.textContent = originalText;
    }, 1500);
  }
});

// Clear cache
document.getElementById('clear-cache-btn')?.addEventListener('click', async () => {
  try {
    // Call backend to clear cache
    await chrome.runtime.sendMessage({ type: 'CLEAR_CACHE' });

    const btn = document.getElementById('clear-cache-btn');
    if (btn) {
      const originalText = btn.textContent;
      btn.textContent = 'Cleared!';
      setTimeout(() => {
        btn.textContent = originalText;
        checkBackendStatus(); // Refresh cache status
      }, 1500);
    }
  } catch (error) {
    console.error('Failed to clear cache:', error);
  }
});

// History management
async function loadHistory() {
  const { history = [] } = await chrome.storage.local.get('history');
  const historyList = document.getElementById('history-list');

  if (!historyList) return;

  if (history.length === 0) {
    historyList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📋</div>
        <div>No verification history yet</div>
        <div style="margin-top: 8px; font-size: 12px;">
          Start verifying content to see your history
        </div>
      </div>
    `;
    return;
  }

  historyList.innerHTML = history.map((item: any) => {
    const timestamp = new Date(item.timestamp);
    const timeStr = formatRelativeTime(timestamp);
    const text = item.request.text.substring(0, 80) + (item.request.text.length > 80 ? '...' : '');

    return `
      <div class="history-item">
        <div class="history-header">
          <span class="history-verdict verdict-${item.result.verdict}">${formatVerdict(item.result.verdict)}</span>
          <span class="history-time">${timeStr}</span>
        </div>
        <div class="history-text">${escapeHtml(text)}</div>
      </div>
    `;
  }).join('');
}

document.getElementById('clear-history-btn')?.addEventListener('click', async () => {
  if (confirm('Are you sure you want to clear all verification history?')) {
    await chrome.storage.local.set({ history: [] });
    loadHistory();
  }
});

// Utility functions
function formatVerdict(verdict: string): string {
  return verdict.charAt(0) + verdict.slice(1).toLowerCase();
}

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

  return date.toLocaleDateString();
}

function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  checkBackendStatus();
  loadSettings();
  loadHistory();
});

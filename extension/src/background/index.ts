/**
 * Background Service Worker
 * Handles native messaging with Python backend and manages extension state
 */

const NATIVE_HOST_NAME = 'com.anthropic.circlenclick';

interface VerificationRequest {
  text: string;
  url?: string;
  platform?: string;
  author?: string;
  strategy?: 'local' | 'cloud' | 'hybrid';
}

interface VerificationResult {
  verdict: 'TRUE' | 'FALSE' | 'MISLEADING' | 'UNVERIFIABLE' | 'UNCERTAIN';
  confidence: number;
  explanation: string;
  sources: string[];
  evidence: string[];
  processing_time: number;
  strategy_used: string;
  cached: boolean;
}

interface NativeMessage {
  type: 'VERIFY' | 'PING' | 'GET_STATUS';
  request_id: string;
  data?: any;
}

interface NativeResponse {
  type: 'RESPONSE' | 'ERROR';
  request_id: string;
  data?: any;
  error?: string;
}

class NativeMessagingClient {
  private port: chrome.runtime.Port | null = null;
  private requestCallbacks: Map<string, { resolve: Function; reject: Function; timeout: number }> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;

  constructor() {
    this.connect();
  }

  private connect() {
    try {
      console.log('[Background] Connecting to native host:', NATIVE_HOST_NAME);
      this.port = chrome.runtime.connectNative(NATIVE_HOST_NAME);

      this.port.onMessage.addListener((message: NativeResponse) => {
        this.handleMessage(message);
      });

      this.port.onDisconnect.addListener(() => {
        console.error('[Background] Native host disconnected:', chrome.runtime.lastError);
        this.handleDisconnect();
      });

      this.reconnectAttempts = 0;
      console.log('[Background] Connected to native host successfully');
    } catch (error) {
      console.error('[Background] Failed to connect to native host:', error);
      this.handleDisconnect();
    }
  }

  private handleMessage(response: NativeResponse) {
    console.log('[Background] Received from native host:', response);

    const callback = this.requestCallbacks.get(response.request_id);
    if (callback) {
      clearTimeout(callback.timeout);
      this.requestCallbacks.delete(response.request_id);

      if (response.type === 'ERROR') {
        callback.reject(new Error(response.error || 'Unknown error'));
      } else {
        callback.resolve(response.data);
      }
    }
  }

  private handleDisconnect() {
    this.port = null;

    // Reject all pending requests
    for (const [requestId, callback] of this.requestCallbacks.entries()) {
      clearTimeout(callback.timeout);
      callback.reject(new Error('Native host disconnected'));
    }
    this.requestCallbacks.clear();

    // Attempt reconnection
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`[Background] Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
    }
  }

  private generateRequestId(): string {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  public async sendRequest(type: string, data?: any, timeoutMs = 30000): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.port) {
        return reject(new Error('Native host not connected'));
      }

      const requestId = this.generateRequestId();
      const message: NativeMessage = { type: type as any, request_id: requestId, data };

      const timeout = setTimeout(() => {
        this.requestCallbacks.delete(requestId);
        reject(new Error('Request timeout'));
      }, timeoutMs);

      this.requestCallbacks.set(requestId, { resolve, reject, timeout });

      try {
        console.log('[Background] Sending to native host:', message);
        this.port.postMessage(message);
      } catch (error) {
        this.requestCallbacks.delete(requestId);
        clearTimeout(timeout);
        reject(error);
      }
    });
  }

  public async verify(request: VerificationRequest): Promise<VerificationResult> {
    return await this.sendRequest('VERIFY', request);
  }

  public async ping(): Promise<boolean> {
    try {
      await this.sendRequest('PING', {}, 5000);
      return true;
    } catch {
      return false;
    }
  }

  public async getStatus(): Promise<any> {
    return await this.sendRequest('GET_STATUS', {});
  }
}

// Initialize native messaging client
const nativeClient = new NativeMessagingClient();

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Background] Message from content script:', message);

  switch (message.type) {
    case 'VERIFY_CONTENT':
      handleVerifyContent(message.data)
        .then(result => sendResponse({ success: true, data: result }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true; // Keep channel open for async response

    case 'PING_BACKEND':
      nativeClient.ping()
        .then(isAlive => sendResponse({ success: true, data: { alive: isAlive } }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true;

    case 'GET_STATUS':
      nativeClient.getStatus()
        .then(status => sendResponse({ success: true, data: status }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true;

    default:
      sendResponse({ success: false, error: 'Unknown message type' });
  }
});

async function handleVerifyContent(request: VerificationRequest): Promise<VerificationResult> {
  console.log('[Background] Verifying content:', request);

  try {
    const result = await nativeClient.verify(request);

    // Store in history
    await storeInHistory(request, result);

    return result;
  } catch (error) {
    console.error('[Background] Verification failed:', error);
    throw error;
  }
}

async function storeInHistory(request: VerificationRequest, result: VerificationResult) {
  const historyItem = {
    timestamp: Date.now(),
    request,
    result
  };

  const { history = [] } = await chrome.storage.local.get('history');
  history.unshift(historyItem);

  // Keep only last 100 items
  if (history.length > 100) {
    history.splice(100);
  }

  await chrome.storage.local.set({ history });
}

// Handle keyboard shortcut
chrome.commands.onCommand.addListener((command) => {
  if (command === 'activate-selector') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'ACTIVATE_SELECTOR' });
      }
    });
  }
});

// Extension icon click
chrome.action.onClicked.addListener((tab) => {
  if (tab.id) {
    chrome.tabs.sendMessage(tab.id, { type: 'ACTIVATE_SELECTOR' });
  }
});

console.log('[Background] CircleNClick background service worker loaded');

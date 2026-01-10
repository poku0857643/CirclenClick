/**
 * Content Script
 * Implements "Circle & Click" selection UI and result display
 */

import { SelectionOverlay } from './selection-overlay';
import { ResultOverlay } from './result-overlay';
import { PlatformAdapter, createPlatformAdapter } from './platform-adapters';

class CircleNClickContent {
  private selectionOverlay: SelectionOverlay;
  private resultOverlay: ResultOverlay;
  private platformAdapter: PlatformAdapter;
  private isActive = false;

  constructor() {
    this.selectionOverlay = new SelectionOverlay();
    this.resultOverlay = new ResultOverlay();
    this.platformAdapter = createPlatformAdapter();

    this.setupMessageListeners();
    this.setupSelectionHandlers();

    console.log('[Content] CircleNClick initialized on:', window.location.hostname);
  }

  private setupMessageListeners() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      switch (message.type) {
        case 'ACTIVATE_SELECTOR':
          this.activateSelector();
          sendResponse({ success: true });
          break;

        case 'DEACTIVATE_SELECTOR':
          this.deactivateSelector();
          sendResponse({ success: true });
          break;
      }
    });
  }

  private setupSelectionHandlers() {
    this.selectionOverlay.on('selection-complete', async (selectedText: string, metadata: any) => {
      console.log('[Content] Selection complete:', selectedText);
      this.deactivateSelector();
      await this.verifyContent(selectedText, metadata);
    });

    this.selectionOverlay.on('selection-cancelled', () => {
      console.log('[Content] Selection cancelled');
      this.deactivateSelector();
    });
  }

  public activateSelector() {
    if (this.isActive) return;

    console.log('[Content] Activating selector');
    this.isActive = true;
    this.selectionOverlay.show();
    document.body.style.cursor = 'crosshair';
  }

  public deactivateSelector() {
    if (!this.isActive) return;

    console.log('[Content] Deactivating selector');
    this.isActive = false;
    this.selectionOverlay.hide();
    document.body.style.cursor = '';
  }

  private async verifyContent(text: string, metadata: any) {
    console.log('[Content] Verifying:', text);

    // Show loading state
    this.resultOverlay.showLoading(metadata.element);

    try {
      // Get platform-specific context
      const platformContext = this.platformAdapter.extractContext(metadata.element);

      // Send verification request to background
      const response = await chrome.runtime.sendMessage({
        type: 'VERIFY_CONTENT',
        data: {
          text: text,
          url: window.location.href,
          platform: this.platformAdapter.getPlatformName(),
          author: platformContext.author,
          strategy: 'hybrid' // Default strategy
        }
      });

      if (response.success) {
        console.log('[Content] Verification result:', response.data);
        this.resultOverlay.showResult(response.data, metadata.element);
      } else {
        console.error('[Content] Verification failed:', response.error);
        this.resultOverlay.showError(response.error, metadata.element);
      }
    } catch (error) {
      console.error('[Content] Error during verification:', error);
      this.resultOverlay.showError(error instanceof Error ? error.message : 'Unknown error', metadata.element);
    }
  }
}

// Initialize content script
const circleNClick = new CircleNClickContent();

// Export for debugging
(window as any).circleNClick = circleNClick;

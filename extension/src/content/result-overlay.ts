/**
 * Result Overlay
 * Displays verification results next to selected content
 */

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

export class ResultOverlay {
  private currentOverlay: HTMLDivElement | null = null;

  constructor() {
    this.injectStyles();
  }

  private injectStyles() {
    const styleId = 'circlenclick-result-styles';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .circlenclick-result-overlay {
        position: fixed;
        max-width: 400px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        z-index: 2147483646;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.5;
        animation: slideIn 0.3s ease-out;
      }

      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateY(-10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .circlenclick-result-header {
        padding: 16px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }

      .circlenclick-result-verdict {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        font-size: 16px;
      }

      .circlenclick-result-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #6b7280;
        padding: 0;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        transition: background 0.2s;
      }

      .circlenclick-result-close:hover {
        background: #f3f4f6;
      }

      .circlenclick-result-body {
        padding: 16px;
      }

      .circlenclick-result-confidence {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-size: 13px;
        color: #6b7280;
      }

      .circlenclick-result-confidence-bar {
        flex: 1;
        height: 6px;
        background: #e5e7eb;
        border-radius: 3px;
        overflow: hidden;
      }

      .circlenclick-result-confidence-fill {
        height: 100%;
        transition: width 0.5s ease-out;
        border-radius: 3px;
      }

      .circlenclick-result-explanation {
        margin-bottom: 12px;
        color: #374151;
        line-height: 1.6;
      }

      .circlenclick-result-section {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #e5e7eb;
      }

      .circlenclick-result-section-title {
        font-weight: 600;
        color: #111827;
        margin-bottom: 6px;
        font-size: 13px;
      }

      .circlenclick-result-list {
        list-style: none;
        padding: 0;
        margin: 0;
      }

      .circlenclick-result-list li {
        padding: 4px 0;
        color: #6b7280;
        font-size: 13px;
      }

      .circlenclick-result-source {
        color: #4A90E2;
        text-decoration: none;
        word-break: break-all;
      }

      .circlenclick-result-source:hover {
        text-decoration: underline;
      }

      .circlenclick-result-footer {
        padding: 12px 16px;
        background: #f9fafb;
        border-top: 1px solid #e5e7eb;
        font-size: 12px;
        color: #6b7280;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 0 0 12px 12px;
      }

      .circlenclick-result-footer-badge {
        padding: 2px 8px;
        background: #e5e7eb;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
      }

      .circlenclick-loading {
        padding: 24px;
        text-align: center;
      }

      .circlenclick-spinner {
        display: inline-block;
        width: 32px;
        height: 32px;
        border: 3px solid #e5e7eb;
        border-top-color: #4A90E2;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }

      .circlenclick-loading-text {
        margin-top: 12px;
        color: #6b7280;
      }

      .verdict-TRUE { color: #059669; }
      .verdict-FALSE { color: #dc2626; }
      .verdict-MISLEADING { color: #d97706; }
      .verdict-UNVERIFIABLE { color: #6b7280; }
      .verdict-UNCERTAIN { color: #8b5cf6; }

      .confidence-bar-TRUE { background: #059669; }
      .confidence-bar-FALSE { background: #dc2626; }
      .confidence-bar-MISLEADING { background: #d97706; }
      .confidence-bar-UNVERIFIABLE { background: #6b7280; }
      .confidence-bar-UNCERTAIN { background: #8b5cf6; }
    `;
    document.head.appendChild(style);
  }

  private createOverlay(anchor: Element | null): HTMLDivElement {
    const overlay = document.createElement('div');
    overlay.className = 'circlenclick-result-overlay';

    // Position near the anchor element
    if (anchor) {
      const rect = anchor.getBoundingClientRect();
      overlay.style.top = `${rect.bottom + window.scrollY + 10}px`;
      overlay.style.left = `${Math.min(rect.left + window.scrollX, window.innerWidth - 420)}px`;
    } else {
      overlay.style.top = '50%';
      overlay.style.left = '50%';
      overlay.style.transform = 'translate(-50%, -50%)';
    }

    return overlay;
  }

  public showLoading(anchor: Element | null) {
    this.removeCurrentOverlay();

    const overlay = this.createOverlay(anchor);
    overlay.innerHTML = `
      <div class="circlenclick-loading">
        <div class="circlenclick-spinner"></div>
        <div class="circlenclick-loading-text">Verifying content...</div>
      </div>
    `;

    document.body.appendChild(overlay);
    this.currentOverlay = overlay;
  }

  public showResult(result: VerificationResult, anchor: Element | null) {
    this.removeCurrentOverlay();

    const overlay = this.createOverlay(anchor);

    const verdictIcon = this.getVerdictIcon(result.verdict);
    const verdictColor = `verdict-${result.verdict}`;

    overlay.innerHTML = `
      <div class="circlenclick-result-header">
        <div class="circlenclick-result-verdict ${verdictColor}">
          <span>${verdictIcon}</span>
          <span>${this.formatVerdict(result.verdict)}</span>
        </div>
        <button class="circlenclick-result-close" title="Close">×</button>
      </div>
      <div class="circlenclick-result-body">
        <div class="circlenclick-result-confidence">
          <span>Confidence:</span>
          <div class="circlenclick-result-confidence-bar">
            <div class="circlenclick-result-confidence-fill confidence-bar-${result.verdict}"
                 style="width: ${result.confidence}%"></div>
          </div>
          <span>${result.confidence.toFixed(0)}%</span>
        </div>

        <div class="circlenclick-result-explanation">
          ${this.escapeHtml(result.explanation)}
        </div>

        ${result.evidence.length > 0 ? `
          <div class="circlenclick-result-section">
            <div class="circlenclick-result-section-title">Evidence</div>
            <ul class="circlenclick-result-list">
              ${result.evidence.slice(0, 3).map(e => `<li>• ${this.escapeHtml(e)}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        ${result.sources.length > 0 ? `
          <div class="circlenclick-result-section">
            <div class="circlenclick-result-section-title">Sources</div>
            <ul class="circlenclick-result-list">
              ${result.sources.slice(0, 3).map(s =>
                `<li><a href="${this.escapeHtml(s)}" class="circlenclick-result-source" target="_blank" rel="noopener">${this.shortenUrl(s)}</a></li>`
              ).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
      <div class="circlenclick-result-footer">
        <span>
          ${result.cached ? '⚡ Cached' : ''}
          ${result.processing_time ? `• ${result.processing_time.toFixed(2)}s` : ''}
        </span>
        <span class="circlenclick-result-footer-badge">${result.strategy_used.replace('_', ' ')}</span>
      </div>
    `;

    // Add close button handler
    const closeBtn = overlay.querySelector('.circlenclick-result-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.removeCurrentOverlay());
    }

    // Auto-close after 15 seconds
    setTimeout(() => {
      if (this.currentOverlay === overlay) {
        this.removeCurrentOverlay();
      }
    }, 15000);

    document.body.appendChild(overlay);
    this.currentOverlay = overlay;
  }

  public showError(error: string, anchor: Element | null) {
    this.removeCurrentOverlay();

    const overlay = this.createOverlay(anchor);
    overlay.innerHTML = `
      <div class="circlenclick-result-header">
        <div class="circlenclick-result-verdict" style="color: #dc2626;">
          <span>⚠️</span>
          <span>Verification Failed</span>
        </div>
        <button class="circlenclick-result-close" title="Close">×</button>
      </div>
      <div class="circlenclick-result-body">
        <div class="circlenclick-result-explanation">
          ${this.escapeHtml(error)}
        </div>
        <div style="margin-top: 12px; color: #6b7280; font-size: 13px;">
          Please make sure the CircleNClick backend is running.
        </div>
      </div>
    `;

    const closeBtn = overlay.querySelector('.circlenclick-result-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.removeCurrentOverlay());
    }

    document.body.appendChild(overlay);
    this.currentOverlay = overlay;
  }

  private removeCurrentOverlay() {
    if (this.currentOverlay) {
      this.currentOverlay.remove();
      this.currentOverlay = null;
    }
  }

  private getVerdictIcon(verdict: string): string {
    const icons: Record<string, string> = {
      TRUE: '✓',
      FALSE: '✗',
      MISLEADING: '⚠',
      UNVERIFIABLE: '?',
      UNCERTAIN: '~'
    };
    return icons[verdict] || '?';
  }

  private formatVerdict(verdict: string): string {
    return verdict.charAt(0) + verdict.slice(1).toLowerCase();
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  private shortenUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname + (urlObj.pathname.length > 20 ? urlObj.pathname.substring(0, 20) + '...' : urlObj.pathname);
    } catch {
      return url.length > 40 ? url.substring(0, 40) + '...' : url;
    }
  }
}

/**
 * Selection Overlay
 * Handles the "Circle & Click" text selection UI
 */

type EventCallback = (data: any, metadata?: any) => void;

export class SelectionOverlay {
  private overlay: HTMLDivElement | null = null;
  private isSelecting = false;
  private startX = 0;
  private startY = 0;
  private selectionBox: HTMLDivElement | null = null;
  private listeners: Map<string, EventCallback[]> = new Map();

  constructor() {
    this.createOverlay();
    this.setupEventListeners();
  }

  private createOverlay() {
    this.overlay = document.createElement('div');
    this.overlay.id = 'circlenclick-selection-overlay';
    this.overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 2147483647;
      pointer-events: none;
      display: none;
    `;
  }

  private createSelectionBox() {
    this.selectionBox = document.createElement('div');
    this.selectionBox.style.cssText = `
      position: fixed;
      border: 2px solid #4A90E2;
      background: rgba(74, 144, 226, 0.1);
      pointer-events: none;
      z-index: 2147483647;
      border-radius: 4px;
      box-shadow: 0 0 10px rgba(74, 144, 226, 0.5);
    `;
    return this.selectionBox;
  }

  private setupEventListeners() {
    document.addEventListener('mousedown', this.onMouseDown.bind(this), true);
    document.addEventListener('mousemove', this.onMouseMove.bind(this), true);
    document.addEventListener('mouseup', this.onMouseUp.bind(this), true);
    document.addEventListener('keydown', this.onKeyDown.bind(this), true);
  }

  private onMouseDown(e: MouseEvent) {
    if (!this.overlay || this.overlay.style.display === 'none') return;

    e.preventDefault();
    e.stopPropagation();

    this.isSelecting = true;
    this.startX = e.clientX;
    this.startY = e.clientY;

    this.selectionBox = this.createSelectionBox();
    document.body.appendChild(this.selectionBox);

    this.updateSelectionBox(e.clientX, e.clientY);
  }

  private onMouseMove(e: MouseEvent) {
    if (!this.isSelecting || !this.selectionBox) return;

    e.preventDefault();
    this.updateSelectionBox(e.clientX, e.clientY);
  }

  private onMouseUp(e: MouseEvent) {
    if (!this.isSelecting || !this.selectionBox) return;

    e.preventDefault();
    e.stopPropagation();

    this.isSelecting = false;

    // Calculate selection bounds
    const bounds = {
      left: Math.min(this.startX, e.clientX),
      top: Math.min(this.startY, e.clientY),
      right: Math.max(this.startX, e.clientX),
      bottom: Math.max(this.startY, e.clientY)
    };

    // Get selected text and element
    const result = this.getSelectedContent(bounds);

    // Remove selection box
    this.selectionBox.remove();
    this.selectionBox = null;

    if (result.text && result.text.trim().length > 0) {
      this.emit('selection-complete', result.text, result.metadata);
    } else {
      this.emit('selection-cancelled');
    }
  }

  private onKeyDown(e: KeyboardEvent) {
    if (e.key === 'Escape' && this.overlay && this.overlay.style.display !== 'none') {
      e.preventDefault();
      if (this.selectionBox) {
        this.selectionBox.remove();
        this.selectionBox = null;
      }
      this.isSelecting = false;
      this.emit('selection-cancelled');
    }
  }

  private updateSelectionBox(currentX: number, currentY: number) {
    if (!this.selectionBox) return;

    const left = Math.min(this.startX, currentX);
    const top = Math.min(this.startY, currentY);
    const width = Math.abs(currentX - this.startX);
    const height = Math.abs(currentY - this.startY);

    this.selectionBox.style.left = `${left}px`;
    this.selectionBox.style.top = `${top}px`;
    this.selectionBox.style.width = `${width}px`;
    this.selectionBox.style.height = `${height}px`;
  }

  private getSelectedContent(bounds: { left: number; top: number; right: number; bottom: number }) {
    // Find all text nodes within bounds
    const selectedElements: Element[] = [];
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_ELEMENT,
      {
        acceptNode: (node) => {
          if (node instanceof Element) {
            const rect = node.getBoundingClientRect();
            const intersects = !(
              rect.right < bounds.left ||
              rect.left > bounds.right ||
              rect.bottom < bounds.top ||
              rect.top > bounds.bottom
            );
            return intersects ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
          }
          return NodeFilter.FILTER_SKIP;
        }
      }
    );

    let node;
    while ((node = walker.nextNode())) {
      if (node instanceof Element) {
        selectedElements.push(node);
      }
    }

    // Extract text from selected elements
    let selectedText = '';
    let primaryElement: Element | null = null;

    for (const element of selectedElements) {
      const text = element.textContent?.trim();
      if (text && text.length > selectedText.length) {
        selectedText = text;
        primaryElement = element;
      }
    }

    return {
      text: selectedText,
      metadata: {
        element: primaryElement,
        bounds: bounds,
        elementCount: selectedElements.length
      }
    };
  }

  public show() {
    if (!this.overlay) return;

    if (!this.overlay.parentElement) {
      document.body.appendChild(this.overlay);
    }

    this.overlay.style.display = 'block';

    // Show instruction tooltip
    this.showInstructions();
  }

  public hide() {
    if (!this.overlay) return;

    this.overlay.style.display = 'none';

    if (this.selectionBox) {
      this.selectionBox.remove();
      this.selectionBox = null;
    }

    this.hideInstructions();
  }

  private showInstructions() {
    const instructions = document.createElement('div');
    instructions.id = 'circlenclick-instructions';
    instructions.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.85);
      color: white;
      padding: 12px 24px;
      border-radius: 8px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 14px;
      z-index: 2147483647;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      pointer-events: none;
    `;
    instructions.textContent = 'Click and drag to select content • Press ESC to cancel';
    document.body.appendChild(instructions);
  }

  private hideInstructions() {
    const instructions = document.getElementById('circlenclick-instructions');
    if (instructions) {
      instructions.remove();
    }
  }

  public on(event: string, callback: EventCallback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  private emit(event: string, data?: any, metadata?: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data, metadata));
    }
  }
}

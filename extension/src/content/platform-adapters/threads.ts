/**
 * Threads Platform Adapter
 */

import { PlatformAdapter, PlatformContext } from './index';

export class ThreadsAdapter implements PlatformAdapter {
  getPlatformName(): string {
    return 'threads';
  }

  extractContext(element: Element | null): PlatformContext {
    if (!element) return {};

    const threadContainer = this.findPostContainer(element);
    if (!threadContainer) return {};

    return {
      author: this.extractAuthor(threadContainer),
      postUrl: this.extractPostUrl(threadContainer),
      timestamp: this.extractTimestamp(threadContainer),
      postType: 'thread'
    };
  }

  findPostContainer(element: Element): Element | null {
    let current: Element | null = element;

    while (current && current !== document.body) {
      // Threads uses similar structure to Instagram
      const role = current.getAttribute('role');

      if (role === 'article') {
        return current;
      }

      // Check for common container patterns
      if (current.className && current.className.includes('thread')) {
        return current;
      }

      current = current.parentElement;
    }

    return null;
  }

  private extractAuthor(container: Element): string | undefined {
    // Threads author is typically in a link
    const authorSelectors = [
      'a[role="link"] span[dir="auto"]',
      'div[role="button"] span',
      'a span'
    ];

    for (const selector of authorSelectors) {
      const elements = container.querySelectorAll(selector);
      for (const element of Array.from(elements)) {
        const text = element.textContent?.trim();
        // Filter out timestamps and other text
        if (text && !this.looksLikeTimestamp(text) && !text.startsWith('@') && text.length > 2) {
          return text;
        }
      }
    }

    return undefined;
  }

  private extractPostUrl(container: Element): string | undefined {
    // Look for post link
    const postLinks = container.querySelectorAll('a[href*="/post/"]');

    for (const link of Array.from(postLinks)) {
      const href = link.getAttribute('href');
      if (href) {
        return href.startsWith('http') ? href : `https://www.threads.net${href}`;
      }
    }

    return undefined;
  }

  private extractTimestamp(container: Element): string | undefined {
    // Threads uses time elements similar to Instagram
    const timeElement = container.querySelector('time');
    if (timeElement) {
      return timeElement.getAttribute('datetime') || timeElement.textContent?.trim();
    }

    // Also check for timestamp text patterns
    const textElements = container.querySelectorAll('span, div');
    for (const element of Array.from(textElements)) {
      const text = element.textContent?.trim();
      if (text && this.looksLikeTimestamp(text)) {
        return text;
      }
    }

    return undefined;
  }

  private looksLikeTimestamp(text: string): boolean {
    const timestampPatterns = [
      /\d+[smhd]$/i,  // 5m, 2h, 3d
      /\d+\s*(min|hour|day|week)s?\s*ago/i,
      /just now/i,
      /yesterday/i
    ];

    return timestampPatterns.some(pattern => pattern.test(text));
  }
}

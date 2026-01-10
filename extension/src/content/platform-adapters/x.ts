/**
 * X (Twitter) Platform Adapter
 */

import { PlatformAdapter, PlatformContext } from './index';

export class XAdapter implements PlatformAdapter {
  getPlatformName(): string {
    return 'x';
  }

  extractContext(element: Element | null): PlatformContext {
    if (!element) return {};

    const tweetContainer = this.findPostContainer(element);
    if (!tweetContainer) return {};

    return {
      author: this.extractAuthor(tweetContainer),
      postUrl: this.extractPostUrl(tweetContainer),
      timestamp: this.extractTimestamp(tweetContainer),
      postType: 'tweet'
    };
  }

  findPostContainer(element: Element): Element | null {
    let current: Element | null = element;

    while (current && current !== document.body) {
      // X/Twitter posts are typically in article elements
      if (current.tagName === 'ARTICLE') {
        return current;
      }

      // Also check for data-testid
      const testId = current.getAttribute('data-testid');
      if (testId === 'tweet' || testId === 'tweetDetail') {
        return current;
      }

      current = current.parentElement;
    }

    return null;
  }

  private extractAuthor(container: Element): string | undefined {
    // Try multiple selectors for author name
    const authorSelectors = [
      '[data-testid="User-Name"] span',
      'a[role="link"] span[dir="ltr"]',
      '[data-testid="tweet"] a span'
    ];

    for (const selector of authorSelectors) {
      const elements = container.querySelectorAll(selector);
      for (const element of Array.from(elements)) {
        const text = element.textContent?.trim();
        // Filter out timestamps and other non-author text
        if (text && !this.looksLikeTimestamp(text) && !text.startsWith('@') && text.length > 2) {
          return text;
        }
      }
    }

    return undefined;
  }

  private extractPostUrl(container: Element): string | undefined {
    // Look for tweet status link
    const statusLinks = container.querySelectorAll('a[href*="/status/"]');

    for (const link of Array.from(statusLinks)) {
      const href = link.getAttribute('href');
      if (href) {
        return href.startsWith('http') ? href : `https://x.com${href}`;
      }
    }

    return undefined;
  }

  private extractTimestamp(container: Element): string | undefined {
    // X uses time elements
    const timeElement = container.querySelector('time');
    if (timeElement) {
      return timeElement.getAttribute('datetime') || timeElement.textContent?.trim();
    }

    return undefined;
  }

  private looksLikeTimestamp(text: string): boolean {
    const timestampPatterns = [
      /\d+[smhd]$/i,  // 5m, 2h, 3d
      /\w{3}\s+\d+/,  // Jan 15
      /just now/i,
      /yesterday/i
    ];

    return timestampPatterns.some(pattern => pattern.test(text));
  }
}

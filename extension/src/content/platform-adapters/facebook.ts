/**
 * Facebook Platform Adapter
 */

import { PlatformAdapter, PlatformContext } from './index';

export class FacebookAdapter implements PlatformAdapter {
  getPlatformName(): string {
    return 'facebook';
  }

  extractContext(element: Element | null): PlatformContext {
    if (!element) return {};

    const postContainer = this.findPostContainer(element);
    if (!postContainer) return {};

    return {
      author: this.extractAuthor(postContainer),
      postUrl: this.extractPostUrl(postContainer),
      timestamp: this.extractTimestamp(postContainer),
      postType: 'post'
    };
  }

  findPostContainer(element: Element): Element | null {
    // Facebook posts are typically wrapped in specific divs
    // This is a simplified version - Facebook's DOM structure changes frequently
    let current: Element | null = element;

    while (current && current !== document.body) {
      // Look for common post container attributes
      const role = current.getAttribute('role');
      const ariaLabel = current.getAttribute('aria-label');

      if (role === 'article' || ariaLabel?.includes('post')) {
        return current;
      }

      current = current.parentElement;
    }

    return null;
  }

  private extractAuthor(container: Element): string | undefined {
    // Try to find author name from various selectors
    const authorSelectors = [
      'h2 a[role="link"] span',
      'h3 a[role="link"] span',
      '[data-ad-comet-preview="message"] strong',
      'a[role="link"] strong'
    ];

    for (const selector of authorSelectors) {
      const authorElement = container.querySelector(selector);
      if (authorElement?.textContent) {
        return authorElement.textContent.trim();
      }
    }

    return undefined;
  }

  private extractPostUrl(container: Element): string | undefined {
    // Try to find permalink
    const linkElements = container.querySelectorAll('a[href*="/posts/"], a[href*="/permalink/"]');

    for (const link of Array.from(linkElements)) {
      const href = link.getAttribute('href');
      if (href) {
        return href.startsWith('http') ? href : `https://www.facebook.com${href}`;
      }
    }

    return undefined;
  }

  private extractTimestamp(container: Element): string | undefined {
    const timeElements = container.querySelectorAll('a[role="link"] span');

    for (const span of Array.from(timeElements)) {
      const text = span.textContent?.trim();
      if (text && this.looksLikeTimestamp(text)) {
        return text;
      }
    }

    return undefined;
  }

  private looksLikeTimestamp(text: string): boolean {
    const timestampPatterns = [
      /\d+\s*(min|hour|day|week|month|year)s?\s*ago/i,
      /just now/i,
      /yesterday/i,
      /\d{1,2}\/\d{1,2}\/\d{2,4}/
    ];

    return timestampPatterns.some(pattern => pattern.test(text));
  }
}

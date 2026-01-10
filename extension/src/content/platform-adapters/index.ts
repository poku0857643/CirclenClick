/**
 * Platform Adapters
 * Extracts platform-specific context from posts
 */

import { FacebookAdapter } from './facebook';
import { XAdapter } from './x';
import { ThreadsAdapter } from './threads';

export interface PlatformContext {
  author?: string;
  postUrl?: string;
  timestamp?: string;
  postType?: string;
}

export interface PlatformAdapter {
  getPlatformName(): string;
  extractContext(element: Element | null): PlatformContext;
  findPostContainer(element: Element): Element | null;
}

export function createPlatformAdapter(): PlatformAdapter {
  const hostname = window.location.hostname.toLowerCase();

  if (hostname.includes('facebook.com')) {
    return new FacebookAdapter();
  } else if (hostname.includes('twitter.com') || hostname.includes('x.com')) {
    return new XAdapter();
  } else if (hostname.includes('threads.net')) {
    return new ThreadsAdapter();
  }

  // Return generic adapter for unknown platforms
  return {
    getPlatformName: () => 'generic',
    extractContext: () => ({}),
    findPostContainer: (el) => el
  };
}

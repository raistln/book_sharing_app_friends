import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Polyfill SharedArrayBuffer ANTES de que webidl-conversions intente acceder
if (typeof globalThis.SharedArrayBuffer === 'undefined') {
  class SharedArrayBufferPolyfill {
    private _byteLength: number;

    constructor(length: number) {
      this._byteLength = Math.max(0, Math.floor(length));
    }

    get byteLength(): number {
      return this._byteLength;
    }

    get [Symbol.toStringTag](): string {
      return 'SharedArrayBuffer';
    }
  }

  (globalThis as any).SharedArrayBuffer = SharedArrayBufferPolyfill;
}

class MockURL {
  href: string;

  constructor(href: string) {
    this.href = href;
  }

  toString() {
    return this.href;
  }
}

class MockURLSearchParams {
  private store: Record<string, string[]> = {};

  constructor(init?: string | Record<string, string | string[]>) {
    if (typeof init === 'string') {
      init
        .replace(/^\?/, '')
        .split('&')
        .filter(Boolean)
        .forEach((pair) => {
          const [key, value = ''] = pair.split('=');
          this.append(decodeURIComponent(key), decodeURIComponent(value));
        });
    } else if (init && typeof init === 'object') {
      Object.entries(init).forEach(([key, value]) => {
        const values = Array.isArray(value) ? value : [value];
        this.store[key] = values.map((v) => String(v));
      });
    }
  }

  append(name: string, value: string) {
    const values = this.store[name] ?? [];
    values.push(String(value));
    this.store[name] = values;
  }

  delete(name: string) {
    delete this.store[name];
  }

  get(name: string) {
    const values = this.store[name];
    return values && values.length > 0 ? values[0] : null;
  }

  getAll(name: string) {
    return [...(this.store[name] ?? [])];
  }

  has(name: string) {
    return !!this.store[name]?.length;
  }

  set(name: string, value: string) {
    this.store[name] = [String(value)];
  }

  sort() {
    const ordered = Object.keys(this.store)
      .sort()
      .reduce<Record<string, string[]>>((acc, key) => {
        acc[key] = this.getAll(key);
        return acc;
      }, {});
    this.store = ordered;
  }

  forEach(callback: (value: string, key: string, parent: MockURLSearchParams) => void) {
    for (const [key, values] of Object.entries(this.store)) {
      for (const value of values) {
        callback(value, key, this);
      }
    }
  }

  entries(): IterableIterator<[string, string]> {
    const pairs: [string, string][] = [];
    for (const [key, values] of Object.entries(this.store)) {
      for (const value of values) {
        pairs.push([key, value]);
      }
    }
    return pairs[Symbol.iterator]();
  }

  keys(): IterableIterator<string> {
    return Object.keys(this.store)[Symbol.iterator]();
  }

  values(): IterableIterator<string> {
    const values: string[] = [];
    for (const valArray of Object.values(this.store)) {
      values.push(...valArray);
    }
    return values[Symbol.iterator]();
  }

  toString() {
    const segments: string[] = [];
    for (const [key, values] of Object.entries(this.store)) {
      for (const value of values) {
        segments.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
      }
    }
    return segments.join('&');
  }

  [Symbol.iterator]() {
    return this.entries();
  }
}

const mockModule = {
  URL: MockURL,
  URLSearchParams: MockURLSearchParams,
  default: {
    URL: MockURL,
    URLSearchParams: MockURLSearchParams,
  },
};

vi.mock('whatwg-url', () => mockModule);
(globalThis as any).__WHATWG_URL_MOCK__ = mockModule;

// Cleanup after each test
afterEach(() => {
  cleanup();
});

if (typeof globalThis.URL === 'undefined') {
  (globalThis as any).URL = MockURL as any;
} else {
  (globalThis as any).URL = MockURL as any;
}

if (typeof globalThis.URLSearchParams === 'undefined') {
  (globalThis as any).URLSearchParams = MockURLSearchParams as any;
} else {
  (globalThis as any).URLSearchParams = MockURLSearchParams as any;
}

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
  }),
  usePathname: () => '/',
  useSearchParams: () => ({
    get: vi.fn(),
    getAll: vi.fn().mockReturnValue([]),
    has: vi.fn().mockReturnValue(false),
    entries: vi.fn(() => [][Symbol.iterator]()),
    keys: vi.fn(() => [][Symbol.iterator]()),
    values: vi.fn(() => [][Symbol.iterator]()),
    forEach: vi.fn(),
    append: vi.fn(),
    delete: vi.fn(),
    set: vi.fn(),
    sort: vi.fn(),
    toString: vi.fn().mockReturnValue(''),
  }),
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
} as any;

// Algunos polyfills (jsdom no expone SharedArrayBuffer)
if (typeof globalThis.SharedArrayBuffer === 'undefined') {
  const SharedArrayBufferMock = function (this: any, length = 0) {
    this._byteLength = Number(length) || 0;
  };

  Object.defineProperty(SharedArrayBufferMock.prototype, 'byteLength', {
    configurable: true,
    get() {
      return this._byteLength ?? 0;
    },
  });

  Object.defineProperty(SharedArrayBufferMock.prototype, Symbol.toStringTag, {
    value: 'SharedArrayBuffer',
  });

  (globalThis as any).SharedArrayBuffer = SharedArrayBufferMock as any;
} else {
  const descriptor = Object.getOwnPropertyDescriptor(
    (globalThis as any).SharedArrayBuffer.prototype,
    'byteLength',
  );

  if (!descriptor || typeof descriptor.get !== 'function') {
    Object.defineProperty((globalThis as any).SharedArrayBuffer.prototype, 'byteLength', {
      configurable: true,
      get() {
        return this._byteLength ?? 0;
      },
    });
  }
}

export class URL {
  href: string;

  constructor(href: string) {
    this.href = href;
  }

  toString(): string {
    return this.href;
  }
}

export class URLSearchParams {
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

  append(name: string, value: string): void {
    const values = this.store[name] ?? [];
    values.push(String(value));
    this.store[name] = values;
  }

  delete(name: string): void {
    delete this.store[name];
  }

  get(name: string): string | null {
    const values = this.store[name];
    return values && values.length > 0 ? values[0] : null;
  }

  getAll(name: string): string[] {
    return [...(this.store[name] ?? [])];
  }

  has(name: string): boolean {
    return !!this.store[name]?.length;
  }

  set(name: string, value: string): void {
    this.store[name] = [String(value)];
  }

  sort(): void {
    const ordered = Object.keys(this.store)
      .sort()
      .reduce<Record<string, string[]>>((acc, key) => {
        acc[key] = this.getAll(key);
        return acc;
      }, {});
    this.store = ordered;
  }

  forEach(callback: (value: string, key: string, parent: URLSearchParams) => void): void {
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

  toString(): string {
    const segments: string[] = [];
    for (const [key, values] of Object.entries(this.store)) {
      for (const value of values) {
        segments.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
      }
    }
    return segments.join('&');
  }

  [Symbol.iterator](): IterableIterator<[string, string]> {
    return this.entries();
  }
}

export default {
  URL,
  URLSearchParams,
};

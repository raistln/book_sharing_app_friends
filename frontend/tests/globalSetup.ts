// Este archivo se ejecuta ANTES de cargar cualquier test o módulo
// Polyfill para SharedArrayBuffer que webidl-conversions necesita

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

export default function globalSetup() {
  // No necesita hacer nada más, el polyfill ya está instalado
}

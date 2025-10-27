// Este archivo se carga mediante NODE_OPTIONS antes de cualquier módulo
// Instala SharedArrayBuffer en el global antes de que webidl-conversions lo necesite

if (typeof globalThis.SharedArrayBuffer === 'undefined') {
  class SharedArrayBufferPolyfill {
    constructor(length) {
      this._byteLength = Math.max(0, Math.floor(length));
    }

    get byteLength() {
      return this._byteLength;
    }

    get [Symbol.toStringTag]() {
      return 'SharedArrayBuffer';
    }
  }

  globalThis.SharedArrayBuffer = SharedArrayBufferPolyfill;
}

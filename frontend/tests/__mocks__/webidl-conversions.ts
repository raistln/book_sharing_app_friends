// Stub mínimo de webidl-conversions para evitar acceso a SharedArrayBuffer en CI
// Este módulo se carga antes que whatwg-url y necesita un polyfill para jsdom

export const any = (value: unknown) => value;
export const undefined = () => void 0;
export const boolean = (value: unknown) => Boolean(value);

function createIntegerConversion(_bitLength: number, _options?: { unsigned?: boolean }) {
  return (value: unknown) => {
    const num = Number(value);
    return isNaN(num) ? 0 : Math.trunc(num);
  };
}

export const byte = createIntegerConversion(8, { unsigned: false });
export const octet = createIntegerConversion(8, { unsigned: true });
export const short = createIntegerConversion(16, { unsigned: false });
export const long = createIntegerConversion(32, { unsigned: false });
const unsignedShort = createIntegerConversion(16, { unsigned: true });
const unsignedLong = createIntegerConversion(32, { unsigned: true });
const longLong = createIntegerConversion(64, { unsigned: false });
const unsignedLongLong = createIntegerConversion(64, { unsigned: true });

export { unsignedShort as 'unsigned short' };
export { unsignedLong as 'unsigned long' };
export { longLong as 'long long' };
export { unsignedLongLong as 'unsigned long long' };

export const double = (value: unknown) => {
  const num = Number(value);
  if (!Number.isFinite(num)) {
    throw new TypeError('Value is not a finite floating-point value');
  }
  return num;
};

const unrestrictedDouble = (value: unknown) => Number(value);
export { unrestrictedDouble as 'unrestricted double' };

export const float = (value: unknown) => {
  const num = Number(value);
  if (!Number.isFinite(num)) {
    throw new TypeError('Value is not a finite floating-point value');
  }
  return Math.fround(num);
};

const unrestrictedFloat = (value: unknown) => {
  const num = Number(value);
  return isNaN(num) ? num : Math.fround(num);
};
export { unrestrictedFloat as 'unrestricted float' };

export const DOMString = (value: unknown) => {
  if (typeof value === 'symbol') {
    throw new TypeError('Cannot convert symbol to string');
  }
  return String(value);
};

export const ByteString = (value: unknown) => {
  const str = DOMString(value);
  for (let i = 0; i < str.length; i++) {
    if (str.charCodeAt(i) > 255) {
      throw new TypeError('Value is not a valid ByteString');
    }
  }
  return str;
};

export const USVString = (value: unknown) => {
  const str = String(value);
  const n = str.length;
  const result: string[] = [];
  
  for (let i = 0; i < n; i++) {
    const c = str.charCodeAt(i);
    if (c < 0xd800 || c > 0xdfff) {
      result.push(String.fromCodePoint(c));
    } else if (0xdc00 <= c && c <= 0xdfff) {
      result.push(String.fromCodePoint(0xfffd));
    } else if (i === n - 1) {
      result.push(String.fromCodePoint(0xfffd));
    } else {
      const d = str.charCodeAt(i + 1);
      if (0xdc00 <= d && d <= 0xdfff) {
        const a = c & 0x3ff;
        const b = d & 0x3ff;
        result.push(String.fromCodePoint((2 << 15) + ((2 << 9) * a) + b));
        i++;
      } else {
        result.push(String.fromCodePoint(0xfffd));
      }
    }
  }
  
  return result.join('');
};

export const object = (value: unknown) => {
  if (value === null || (typeof value !== 'object' && typeof value !== 'function')) {
    throw new TypeError('Value is not an object');
  }
  return value;
};

// Stub para ArrayBuffer sin depender de SharedArrayBuffer
export const ArrayBuffer = (value: unknown) => {
  if (!(value instanceof globalThis.ArrayBuffer)) {
    throw new TypeError('Value is not an ArrayBuffer');
  }
  return value;
};

export const DataView = (value: unknown) => {
  if (!(value instanceof globalThis.DataView)) {
    throw new TypeError('Value is not a DataView');
  }
  return value;
};

// Exportar por defecto para compatibilidad
export default {
  any,
  undefined,
  boolean,
  byte,
  octet,
  short,
  long,
  'unsigned short': createIntegerConversion(16, { unsigned: true }),
  'unsigned long': createIntegerConversion(32, { unsigned: true }),
  'long long': createIntegerConversion(64, { unsigned: false }),
  'unsigned long long': createIntegerConversion(64, { unsigned: true }),
  double,
  'unrestricted double': (value: unknown) => Number(value),
  float,
  'unrestricted float': (value: unknown) => {
    const num = Number(value);
    return isNaN(num) ? num : Math.fround(num);
  },
  DOMString,
  ByteString,
  USVString,
  object,
  ArrayBuffer,
  DataView,
};

// Network-free bridge for the plugin sandbox (no TextEncoder/crypto required).
// Append to the collector through --emit-transfer-js. Only plugin-local storage
// is changed; no document artwork or metadata is mutated.
const snapshot = storage.conformanceSnapshot;
if (!snapshot) throw Error('Collect a snapshot before preparing transfer');
// Tabular packing preserves every fact while avoiding repeated UUIDs/keys in
// tool output. Arrays and numbers remain typed; strings use explicit tags.
const strings = [], stringIds = new Map();
function pack(value) {
  if (typeof value === 'string') {
    if (!stringIds.has(value)) { stringIds.set(value, strings.length); strings.push(value); }
    return {s: stringIds.get(value)};
  }
  if (Array.isArray(value)) return value.map(pack);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, pack(v)]));
  return value;
}
const columns = [...new Set(snapshot.nodes.flatMap(n => Object.keys(n)))];
const rows = snapshot.nodes.map(n => columns.map(k => k in n ? pack(n[k]) : {missing: true}));
const metadata = pack({...snapshot, nodes: []});
const text = JSON.stringify({strings, columns, snapshot: {...metadata, nodes: rows}});
// Encode UTF-8 portably, preserving all Unicode text.
const bytes = [];
for (const char of text) {
  const cp = char.codePointAt(0);
  if (cp < 128) bytes.push(cp);
  else if (cp < 2048) bytes.push(192 | (cp >> 6), 128 | (cp & 63));
  else if (cp < 65536) bytes.push(224 | (cp >> 12), 128 | ((cp >> 6) & 63), 128 | (cp & 63));
  else bytes.push(240 | (cp >> 18), 128 | ((cp >> 12) & 63), 128 | ((cp >> 6) & 63), 128 | (cp & 63));
}
// LZW over bytes, bounded to 16-bit codes. Decoder independently checks size
// and Adler-32. This is corruption detection, not authentication of a snapshot.
const dictionary = new Map();
for (let i = 0; i < 256; i++) dictionary.set(String.fromCharCode(i), i);
let phrase = '', next = 256;
const codes = [];
for (const byte of bytes) {
  const char = String.fromCharCode(byte);
  if (dictionary.has(phrase + char)) phrase += char;
  else {
    codes.push(dictionary.get(phrase));
    if (next < 65536) dictionary.set(phrase + char, next++);
    phrase = char;
  }
}
if (phrase) codes.push(dictionary.get(phrase));
let a = 1, b = 0, binary = '';
for (const byte of bytes) { a = (a + byte) % 65521; b = (b + a) % 65521; }
for (const code of codes) binary += String.fromCharCode(code >> 8, code & 255);
const data = btoa(binary);
const size = 8000;
const transfer = {
  format: 'penpot-table-lzw16-v1', byteLength: bytes.length,
  checksum: ((b * 65536 + a) >>> 0).toString(16).padStart(8, '0'),
  chunkCount: Math.ceil(data.length / size),
  chunks: Array.from({length: Math.ceil(data.length / size)}, (_, i) => data.slice(i * size, (i + 1) * size))
};
storage.conformanceTransfer = transfer;
return {format: transfer.format, byteLength: transfer.byteLength, checksum: transfer.checksum,
        chunkCount: transfer.chunkCount, encodedLength: data.length};
"""Decode bounded plugin transfer envelopes; no network or third-party packages."""
import base64
import json
import zlib

MAX_BYTES = 32 * 1024 * 1024


def decode_transfer(envelope):
    if not isinstance(envelope, dict) or envelope.get('format') != 'penpot-table-lzw16-v1':
        raise ValueError('unsupported snapshot transfer format')
    length = envelope.get('byteLength')
    if type(length) is not int or not 0 < length <= MAX_BYTES:
        raise ValueError('invalid snapshot transfer size')
    chunks = envelope.get('chunks')
    if not isinstance(chunks, list) or not chunks or len(chunks) != envelope.get('chunkCount'):
        raise ValueError('missing snapshot chunks')
    if not all(isinstance(c, str) and 0 < len(c) <= 8000 for c in chunks) or sum(map(len, chunks)) > MAX_BYTES * 4:
        raise ValueError('invalid snapshot chunks')
    try:
        packed = base64.b64decode(''.join(chunks), validate=True)
    except ValueError as error:
        raise ValueError('invalid snapshot base64') from error
    if not packed or len(packed) % 2:
        raise ValueError('invalid LZW code stream')
    dictionary = [bytes([i]) for i in range(256)]
    previous = b''
    output = bytearray()
    for i in range(0, len(packed), 2):
        code = packed[i] * 256 + packed[i + 1]
        if code < len(dictionary):
            entry = dictionary[code]
        elif code == len(dictionary) and previous:
            entry = previous + previous[:1]
        else:
            raise ValueError('invalid LZW dictionary reference')
        if len(output) + len(entry) > length:
            raise ValueError('decoded snapshot exceeds declared size')
        output.extend(entry)
        if previous and len(dictionary) < 65536:
            dictionary.append(previous + entry[:1])
        previous = entry
    checksum = f'{zlib.adler32(output):08x}'
    if len(output) != length or checksum != envelope.get('checksum'):
        raise ValueError('snapshot transfer integrity mismatch')
    try:
        table = json.loads(output.decode('utf-8'))
    except (ValueError, UnicodeError) as error:
        raise ValueError('invalid transferred JSON') from error
    if not isinstance(table, dict) or not isinstance(table.get('strings'), list) or not isinstance(table.get('columns'), list) or not isinstance(table.get('snapshot'), dict):
        raise ValueError('invalid snapshot table')
    strings, columns = table['strings'], table['columns']
    if not all(isinstance(s, str) for s in strings + columns) or len(columns) != len(set(columns)):
        raise ValueError('invalid snapshot string table/columns')
    def unpack(value):
        if isinstance(value, dict):
            if set(value) == {'s'}:
                index = value['s']
                if type(index) is not int or not 0 <= index < len(strings):
                    raise ValueError('invalid snapshot string reference')
                return strings[index]
            return {k: unpack(v) for k, v in value.items()}
        if isinstance(value, list):
            return [unpack(v) for v in value]
        return value
    packed = table['snapshot']
    rows = packed.get('nodes')
    if not isinstance(rows, list) or any(not isinstance(row, list) or len(row) != len(columns) for row in rows):
        raise ValueError('invalid snapshot rows')
    snapshot = unpack({k: v for k, v in packed.items() if k != 'nodes'})
    snapshot['nodes'] = [{k: unpack(v) for k, v in zip(columns, row) if v != {'missing': True}} for row in rows]
    return snapshot
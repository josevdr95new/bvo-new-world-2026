"""MPQ archive parser for Warcraft III .w3x map files."""
from __future__ import annotations
import struct
import zlib
import os
from typing import List, Dict, Optional, Tuple


_crypt_table: List[int] = []


def _prepare_crypt_table() -> None:
    global _crypt_table
    if _crypt_table:
        return
    crypt_table = [0] * 0x500
    seed = 0x00100001
    for index in range(0x100):
        for i in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp1 = (seed & 0xFFFF) << 0x10
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp2 = seed & 0xFFFF
            idx = (i * 0x100) + index
            crypt_table[idx] = temp1 | temp2
    _crypt_table = crypt_table


def _hash_string(s: str, hash_type: int) -> int:
    if not _crypt_table:
        _prepare_crypt_table()
    seed1 = 0x7FED7FED
    seed2 = 0xEEEEEEEE
    s_upper = s.upper()
    for ch in s_upper:
        ch_val = ord(ch)
        if ch_val > 0x7F:
            ch_val = ord('?')
        seed1 = _crypt_table[hash_type * 0x100 + ch_val] ^ ((seed1 + seed2) & 0xFFFFFFFF)
        seed2 = (ch_val + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1 & 0xFFFFFFFF


def _decrypt(data: bytes, key: int) -> bytes:
    if not _crypt_table:
        _prepare_crypt_table()
    seed = 0xEEEEEEEE
    if len(data) % 4 != 0:
        padded = data + b'\x00' * (4 - (len(data) % 4))
    else:
        padded = data
    result = bytearray(len(padded))
    for i in range(0, len(padded), 4):
        seed = (seed + _crypt_table[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        block = struct.unpack('<I', padded[i:i+4])[0]
        decrypted = block ^ ((key + seed) & 0xFFFFFFFF)
        key = (((~key << 0x15) & 0xFFFFFFFF) + 0x11111122) | (key >> 0x0B)
        key = key & 0xFFFFFFFF
        struct.pack_into('<I', result, i, decrypted)
    return bytes(result[:len(data)])


class MPQFile:
    def __init__(self, name: str, offset: int, size: int, archived_size: int, flags: int):
        self.name = name
        self.offset = offset
        self.size = size
        self.archived_size = archived_size
        self.flags = flags
        self.encrypted = bool(flags & 0x02000000)
        self.imploded = bool(flags & 0x01000000)
        self.compressed = bool(flags & 0x00020000)
        self.exists = bool(flags & 0x80000000)
        self.single_unit = bool(flags & 0x40000000)

    def __repr__(self) -> str:
        return f"MPQFile({self.name!r}, size={self.size}, archived={self.archived_size})"


class MPQArchive:
    def __init__(self, file_path: str, mpq_offset: int = 0):
        self.file_path = file_path
        self.mpq_offset = mpq_offset
        self.hash_table: List[Tuple[int, int, int, int]] = []
        self.block_table: List[Tuple[int, int, int, int]] = []
        self.files: Dict[str, MPQFile] = {}
        self._parse()

    def _parse(self) -> None:
        with open(self.file_path, 'rb') as f:
            f.seek(self.mpq_offset)
            sig = f.read(4)
            if sig == b'MPQ\x1a':
                f.seek(self.mpq_offset)
                sig = f.read(4)
            elif sig != b'\x1aMPQ':
                raise ValueError(f"Invalid MPQ signature: {sig}")
            header_size = struct.unpack('<I', f.read(4))[0]
            archive_size = struct.unpack('<I', f.read(4))[0]
            f.read(4)
            hash_table_offset = struct.unpack('<I', f.read(4))[0]
            block_table_offset = struct.unpack('<I', f.read(4))[0]
            hash_table_size = struct.unpack('<I', f.read(4))[0]
            block_table_size = struct.unpack('<I', f.read(4))[0]

            print(f"MPQ header at offset {self.mpq_offset}:")
            print(f"  header_size: {header_size}, archive_size: {archive_size}")
            print(f"  hash_table: offset={hash_table_offset}, entries={hash_table_size}")
            print(f"  block_table: offset={block_table_offset}, entries={block_table_size}")

            f.seek(self.mpq_offset + hash_table_offset)
            hash_data = f.read(hash_table_size * 16)
            hash_key = _hash_string('(hash table)', 0)
            hash_data = _decrypt(hash_data, hash_key)
            for i in range(0, len(hash_data), 16):
                entry = hash_data[i:i+16]
                name1, name2, locale, block_index = struct.unpack('<IIII', entry)
                self.hash_table.append((name1, name2, locale, block_index))

            f.seek(self.mpq_offset + block_table_offset)
            block_data = f.read(block_table_size * 16)
            block_key = _hash_string('(block table)', 0)
            block_data = _decrypt(block_data, block_key)
            for i in range(0, len(block_data), 16):
                entry = block_data[i:i+16]
                offset, archived_size, size, flags = struct.unpack('<IIII', entry)
                self.block_table.append((offset, archived_size, size, flags))

            print(f"\n  Hash entries: {len(self.hash_table)} (empty: {sum(1 for h in self.hash_table if h[0] == 0xFFFFFFFF)})")
            print(f"  Block entries: {len(self.block_table)}")

    def find_file(self, name: str) -> Optional[MPQFile]:
        hash_a = _hash_string(name, 1)
        hash_b = _hash_string(name, 2)
        start_idx = _hash_string(name, 0) % len(self.hash_table)
        for i in range(len(self.hash_table)):
            idx = (start_idx + i) % len(self.hash_table)
            entry = self.hash_table[idx]
            if entry[0] == 0xFFFFFFFF:
                return None
            if entry[0] == 0xFFFFFFFE:
                continue  # Deleted entry
            if entry[0] == hash_a and entry[1] == hash_b:
                block_index = entry[3]
                if block_index >= len(self.block_table):
                    return None
                offset, archived_size, size, flags = self.block_table[block_index]
                return MPQFile(name, offset, size, archived_size, flags)
        return None

    def read_file(self, name: str) -> Optional[bytes]:
        f_info = self.find_file(name)
        if not f_info:
            return None
        with open(self.file_path, 'rb') as f:
            f.seek(self.mpq_offset + f_info.offset)
            raw = f.read(f_info.archived_size)
            return raw


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: mpq_parser.py <map.w3x>")
        sys.exit(1)
    map_path = sys.argv[1]
    with open(map_path, 'rb') as f:
        data = f.read(1024)
    mpq_offset = -1
    for sig in [b'\x1aMPQ', b'MPQ\x1a']:
        pos = data.find(sig)
        if pos != -1:
            mpq_offset = pos
            print(f"Found MPQ signature '{sig.decode('latin1')}' at offset {pos}")
            break
    if mpq_offset == -1:
        print("No MPQ signature found!")
        sys.exit(1)
    archive = MPQArchive(map_path, mpq_offset)
    test_files = [
        'war3map.j', 'war3map.w3i', 'war3map.w3u', 'war3map.w3t', 'war3map.w3a',
        'war3map.w3h', 'war3map.w3q', 'war3map.w3b', 'war3map.w3d', 'war3map.w3r',
        'war3map.doo', 'war3map.shd', 'war3map.w3e', 'war3map.wpm', 'war3map.mmp',
        'war3map.imp', 'war3mapMisc.txt', 'war3mapSkin.txt',
        '(listfile)', '(attributes)', '(signature)',
    ]
    print("\n=== Searching for known WC3 files ===")
    for fname in test_files:
        info = archive.find_file(fname)
        if info:
            print(f"  ✓ Found: {fname} (size={info.size}, archived={info.archived_size})")
        else:
            print(f"  ✗ Not found: {fname}")

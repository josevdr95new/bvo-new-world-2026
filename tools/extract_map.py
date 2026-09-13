"""WC3 Map file extractor.

Based on:
- mpyq by eagleflo (https://github.com/eagleflo/mpyq)
- wc3map by ChristophHaag (https://github.com/ChristophHaag/wc3map)
- StormLib by ladislav-zezula (https://github.com/ladislav-zezula/StormLib)

Parses a Warcraft III .w3x map file, finds the embedded MPQ archive,
extracts all files including war3map.j (the JASS script), war3map.w3u (units),
war3map.w3t (items), war3map.w3a (abilities), war3map.w3h (heroes),
war3map.w3q (upgrades), war3map.w3i (map info), etc.

Usage:
    python3 extract_map.py <map.w3x> <output_dir>
"""
from __future__ import annotations
import struct
import zlib
import bz2
import os
import sys
from typing import List, Dict, Optional, Tuple, Any
from io import BytesIO


# ============================================================
# MPQ CONSTANTS
# ============================================================
HASH_TABLE_ENTRY_SIZE = 16
BLOCK_TABLE_ENTRY_SIZE = 16

MPQ_FILE_IMPLODE = 0x00000100       # PKWARE Data compression
MPQ_FILE_COMPRESS = 0x00000200      # Multi-compression
MPQ_FILE_ENCRYPTED = 0x00010000     # File is encrypted
MPQ_FILE_FIX_KEY = 0x00020000       # Decryption key depends on file position
MPQ_FILE_PATCH_FILE = 0x00100000    # Patch file
MPQ_FILE_SINGLE_UNIT = 0x01000000   # Single unit (not sectorized)
MPQ_FILE_DELETE_MARKER = 0x02000000
MPQ_FILE_SECTOR_CRC = 0x04000000
MPQ_FILE_EXISTS = 0x80000000


# ============================================================
# MPQ CRYPTO TABLE (precomputed)
# ============================================================
def _prepare_crypt_table() -> List[int]:
    """Build the MPQ crypt table (1024 entries × 5 = 1280 actual values).

    Reference: StormLib's PrepareCryptTable function.
    """
    crypt_table = [0] * 0x500
    seed = 0x00100001
    for index in range(0x100):
        for i in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp1 = (seed & 0xFFFF) << 0x10
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp2 = seed & 0xFFFF
            crypt_table[(i * 0x100) + index] = (temp1 | temp2) & 0xFFFFFFFF
    return crypt_table


CRYPT_TABLE = _prepare_crypt_table()


def _hash_string(s: str, hash_type: int) -> int:
    """Hash a string using MPQ's algorithm.

    hash_type:
        0 = TABLE_OFFSET (used to find hash table entry)
        1 = NAME_A (used for filename match)
        2 = NAME_B (used for filename match)
        3 = TABLE (file key)
    """
    seed1 = 0x7FED7FED
    seed2 = 0xEEEEEEEE
    s_upper = s.upper()
    for ch in s_upper:
        ch_val = ord(ch)
        # MPQ treats chars > 0x7E specially. Common approach is to use '?'.
        if ch_val > 0x7E:
            ch_val = 0x3F  # '?'
        seed1 = (CRYPT_TABLE[(hash_type * 0x100) + ch_val] ^ ((seed1 + seed2) & 0xFFFFFFFF)) & 0xFFFFFFFF
        seed2 = (ch_val + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1 & 0xFFFFFFFF


def _decrypt_block(data: bytes, key: int) -> bytes:
    """Decrypt a block of data using MPQ algorithm.

    StormLib's Decrypt function.
    """
    if len(data) % 4 != 0:
        padded = data + b'\x00' * (4 - (len(data) % 4))
    else:
        padded = data
    result = bytearray(len(padded))
    seed = 0xEEEEEEEE
    cur_key = key
    for i in range(0, len(padded), 4):
        seed = (seed + CRYPT_TABLE[0x400 + (cur_key & 0xFF)]) & 0xFFFFFFFF
        block = struct.unpack('<I', padded[i:i+4])[0]
        decrypted = (block ^ ((cur_key + seed) & 0xFFFFFFFF)) & 0xFFFFFFFF
        # Key rotation: rotate right 11 bits then add 0x11111122
        # StormLib: key = ((~key << 0x15) + 0x11111122) | (key >> 0x0B)
        # But the ~key applies to the ORIGINAL key, not the rotated one
        cur_key = ((((~cur_key) & 0xFFFFFFFF) << 0x15) & 0xFFFFFFFF)
        cur_key = (cur_key + 0x11111122) & 0xFFFFFFFF
        cur_key = (cur_key | (key >> 0x0B)) & 0xFFFFFFFF  # Use original key for the OR
        # Actually: the OR uses the original key shifted right by 11
        # This is a bitwise rotation with NOT
        struct.pack_into('<I', result, i, decrypted)
    return bytes(result[:len(data)])


def _decompress(data: bytes) -> bytes:
    """Decompress MPQ file data.

    Compression type is the first byte:
        0 = uncompressed
        2 = zlib (deflate)
        8 = PKWARE DCL (not supported here)
        16 = bzip2
        Other = multi-compression, try several methods
    """
    if not data:
        return data
    compression_type = data[0]
    if compression_type == 0:
        return data
    elif compression_type == 2:
        try:
            return zlib.decompress(data[1:], 15)
        except Exception:
            try:
                return zlib.decompress(data[1:], -15)
            except Exception:
                return data
    elif compression_type == 16:
        try:
            return bz2.decompress(data[1:])
        except Exception:
            return data
    else:
        # Try multiple decompression methods
        for method in [zlib.decompress, lambda d: zlib.decompress(d, -15), bz2.decompress]:
            try:
                return method(data[1:])
            except Exception:
                continue
        return data


# ============================================================
# DATA CLASSES
# ============================================================
class HashEntry:
    """A hash table entry in MPQ archive."""
    __slots__ = ('name_a', 'name_b', 'locale', 'platform', 'block_index', 'status')

    EMPTY = 0xFFFFFFFF
    DELETED = 0xFFFFFFFE

    def __init__(self, name_a: int, name_b: int, locale: int, platform: int, block_index: int):
        self.name_a = name_a
        self.name_b = name_b
        self.locale = locale
        self.platform = platform
        self.block_index = block_index
        if name_a == 0xFFFFFFFF and name_b == 0xFFFFFFFF:
            self.status = 'empty'
        elif name_a == 0xFFFFFFFE and name_b == 0xFFFFFFFE:
            self.status = 'deleted'
        else:
            self.status = 'ok'

    def __repr__(self) -> str:
        return (f"HashEntry(name_a=0x{self.name_a:08x}, name_b=0x{self.name_b:08x}, "
                f"locale={self.locale}, block_idx={self.block_index}, status={self.status})")


class BlockEntry:
    """A block table entry in MPQ archive."""
    __slots__ = ('offset', 'archived_size', 'size', 'flags')

    def __init__(self, offset: int, archived_size: int, size: int, flags: int):
        self.offset = offset
        self.archived_size = archived_size
        self.size = size
        self.flags = flags

    @property
    def exists(self) -> bool:
        return bool(self.flags & MPQ_FILE_EXISTS)

    @property
    def encrypted(self) -> bool:
        return bool(self.flags & MPQ_FILE_ENCRYPTED)

    @property
    def fix_key(self) -> bool:
        return bool(self.flags & MPQ_FILE_FIX_KEY)

    @property
    def compressed(self) -> bool:
        return bool(self.flags & (MPQ_FILE_COMPRESS | MPQ_FILE_IMPLODE))

    @property
    def single_unit(self) -> bool:
        return bool(self.flags & MPQ_FILE_SINGLE_UNIT)

    def __repr__(self) -> str:
        return (f"BlockEntry(offset={self.offset}, archived={self.archived_size}, "
                f"size={self.size}, flags=0x{self.flags:08x})")


# ============================================================
# WC3 MAP PARSER
# ============================================================
class WC3Map:
    """Parses a Warcraft III .w3x or .w3m map file."""

    def __init__(self, map_path: str):
        self.map_path = map_path
        with open(map_path, 'rb') as f:
            self.data = f.read()
        self.mpq_offset = self._find_mpq_offset()
        self.hash_table: List[HashEntry] = []
        self.block_table: List[BlockEntry] = []
        self.sector_size = 0x200  # 512 bytes default; updated from header
        self._parse_mpq_header()
        self._parse_hash_table()
        self._parse_block_table()

    def _find_mpq_offset(self) -> int:
        """Find the offset of the MPQ header in the file.

        WC3 maps have:
        - HM3W header (4 bytes signature + map metadata)
        - Optional preview image
        - MPQ archive (starts with 'MPQ\\x1a' or '\\x1aMPQ')

        For WC3 maps, the MPQ offset is always 0x200 (512 bytes) when there's
        a minimap preview, or right after the HM3W header otherwise.
        """
        # Try offset 512 first (most common for WC3 maps)
        for offset in [512, 0]:
            if self.data[offset:offset+4] in (b'MPQ\x1a', b'\x1aMPQ'):
                return offset
        # Search for MPQ signature
        for sig in [b'\x1aMPQ', b'MPQ\x1a']:
            pos = self.data.find(sig)
            if pos != -1:
                return pos
        raise ValueError("MPQ signature not found in map file")

    def _parse_mpq_header(self) -> None:
        """Parse the MPQ header to get table offsets and sizes."""
        header = self.data[self.mpq_offset:self.mpq_offset + 32]
        if len(header) < 32:
            raise ValueError("MPQ header truncated")
        # Skip signature (4 bytes)
        self.header_size = struct.unpack('<I', header[4:8])[0]
        self.archive_size = struct.unpack('<I', header[8:12])[0]
        # Skip 4 bytes
        hash_table_offset = struct.unpack('<I', header[16:20])[0]
        block_table_offset = struct.unpack('<I', header[20:24])[0]
        self.hash_table_size = struct.unpack('<I', header[24:28])[0]
        self.block_table_size = struct.unpack('<I', header[28:32])[0]
        # Block size (sector size = 512 * 2^block_size)
        # In MPQ v1 header, block_size is at offset 12 (after archive_size)
        # Actually in v1 header (32 bytes), it's: sig(4), header_size(4), archive_size(4),
        # block_size(1), unknown(3), hash_table_offset(4), block_table_offset(4),
        # hash_table_size(4), block_table_size(4)
        # Wait, that's 36 bytes. Let me check StormLib.
        # Actually v1 header is:
        # uint32 dwID;            // MPQ header identifier
        # uint32 dwHeaderSize;    // Size of this header (32 bytes for v1)
        # uint32 dwArchiveSize;   // Size of the archive
        # uint16 wFormatVersion;  // 0 = original, 1 = burned
        # uint8  SectorSizeShift; // Sector size = 512 * 2^SectorSizeShift
        # uint16 wHashTablePos;   // ... no wait
        # Actually from StormLib source:
        # TMPQHeader v1 has 32 bytes:
        # 0x00: dwID
        # 0x04: dwHeaderSize
        # 0x08: dwArchiveSize
        # 0x0C: wFormatVersion (2 bytes)
        # 0x0E: SectorSizeShift (1 byte)  -- but with 1-byte padding?
        # Actually it's:
        # 0x0C: wBlockSize (2 bytes)  -- block size as power of 2
        # 0x0E: unused (2 bytes)
        # 0x10: dwHashTablePos (4 bytes)
        # 0x14: dwBlockTablePos (4 bytes)
        # 0x18: dwHashTableSize (4 bytes)
        # 0x1C: dwBlockTableSize (4 bytes)
        # Wait, header[12:14] is wFormatVersion
        # header[14:15] is SectorSizeShift
        # header[15:16] is padding
        # Actually let me just re-read StormLib:
        block_size_shift = header[14]  # Sector size = 512 << sector_size_shift
        self.sector_size = 512 << block_size_shift
        self.hash_table_pos = hash_table_offset
        self.block_table_pos = block_table_offset
        print(f"MPQ Header:")
        print(f"  Header size: {self.header_size}")
        print(f"  Archive size: {self.archive_size}")
        print(f"  Block size shift: {block_size_shift} → sector size: {self.sector_size}")
        print(f"  Hash table: offset={hash_table_offset}, entries={self.hash_table_size}")
        print(f"  Block table: offset={block_table_offset}, entries={self.block_table_size}")

    def _parse_hash_table(self) -> None:
        """Read and decrypt the hash table."""
        start = self.mpq_offset + self.hash_table_pos
        end = start + self.hash_table_size * HASH_TABLE_ENTRY_SIZE
        raw = self.data[start:end]
        # Decrypt hash table
        key = _hash_string('(hash table)', 0)
        decrypted = _decrypt_block(raw, key)
        for i in range(0, len(decrypted), HASH_TABLE_ENTRY_SIZE):
            entry = decrypted[i:i+HASH_TABLE_ENTRY_SIZE]
            if len(entry) < 16:
                break
            name_a, name_b, locale, platform, block_index = struct.unpack('<IIHHI', entry)
            self.hash_table.append(HashEntry(name_a, name_b, locale, platform, block_index))
        # Count valid entries
        valid = sum(1 for h in self.hash_table if h.status == 'ok')
        empty = sum(1 for h in self.hash_table if h.status == 'empty')
        deleted = sum(1 for h in self.hash_table if h.status == 'deleted')
        print(f"  Hash table parsed: {valid} valid, {empty} empty, {deleted} deleted")

    def _parse_block_table(self) -> None:
        """Read and decrypt the block table."""
        start = self.mpq_offset + self.block_table_pos
        end = start + self.block_table_size * BLOCK_TABLE_ENTRY_SIZE
        raw = self.data[start:end]
        # Decrypt block table
        key = _hash_string('(block table)', 0)
        decrypted = _decrypt_block(raw, key)
        for i in range(0, len(decrypted), BLOCK_TABLE_ENTRY_SIZE):
            entry = decrypted[i:i+BLOCK_TABLE_ENTRY_SIZE]
            if len(entry) < 16:
                break
            offset, archived_size, size, flags = struct.unpack('<IIII', entry)
            self.block_table.append(BlockEntry(offset, archived_size, size, flags))
        valid = sum(1 for b in self.block_table if b.exists)
        print(f"  Block table parsed: {len(self.block_table)} entries ({valid} exist)")

    def find_file(self, filename: str) -> Optional[Tuple[HashEntry, BlockEntry]]:
        """Find a file by name in the archive."""
        name_a = _hash_string(filename, 1)
        name_b = _hash_string(filename, 2)
        start_idx = _hash_string(filename, 0) % len(self.hash_table)
        for i in range(len(self.hash_table)):
            idx = (start_idx + i) % len(self.hash_table)
            entry = self.hash_table[idx]
            if entry.status == 'empty':
                return None  # File not found
            if entry.status == 'deleted':
                continue
            if entry.name_a == name_a and entry.name_b == name_b:
                if entry.block_index < len(self.block_table):
                    return entry, self.block_table[entry.block_index]
                return None
        return None

    def read_file(self, filename: str) -> Optional[bytes]:
        """Read a file from the archive, decrypting and decompressing as needed."""
        result = self.find_file(filename)
        if result is None:
            return None
        hash_entry, block_entry = result
        if not block_entry.exists:
            return None
        # Read raw file data
        start = self.mpq_offset + block_entry.offset
        raw = self.data[start:start + block_entry.archived_size]
        if len(raw) < block_entry.archived_size:
            return None  # Truncated file
        # Decrypt if needed
        if block_entry.encrypted:
            # Compute file key
            file_key = _hash_string(filename, 3)
            if block_entry.fix_key:
                # FIX_KEY: key is adjusted based on file position in archive
                file_key = (file_key + block_entry.offset) & 0xFFFFFFFF
            if block_entry.single_unit:
                raw = _decrypt_block(raw, file_key)
            else:
                # Decrypt sector by sector
                # First read the sector offsets table
                sector_count = (block_entry.size + self.sector_size - 1) // self.sector_size
                # Plus 1 for the end-of-file marker
                offsets_size = (sector_count + 1) * 4
                offsets_raw = raw[:offsets_size]
                offsets = list(struct.unpack(f'<{sector_count+1}I', offsets_raw))
                # Decrypt offsets table
                offsets_decrypted = _decrypt_block(offsets_raw, file_key - 1)
                offsets = list(struct.unpack(f'<{sector_count+1}I', offsets_decrypted))
                # Read and decrypt each sector
                file_data = b''
                for i in range(sector_count):
                    sec_start = offsets[i]
                    sec_end = offsets[i+1]
                    sec_data = raw[sec_start:sec_end]
                    sec_data = _decrypt_block(sec_data, file_key + i)
                    # Decompress if needed
                    if block_entry.compressed:
                        sec_data = _decompress(sec_data)
                    file_data += sec_data
                return file_data
        # Decompress if needed (single unit or no encryption)
        if block_entry.single_unit:
            if block_entry.compressed:
                raw = _decompress(raw)
            return raw
        # Multi-sector non-encrypted
        # Read sector offsets
        sector_count = (block_entry.size + self.sector_size - 1) // self.sector_size
        offsets_size = (sector_count + 1) * 4
        offsets = list(struct.unpack(f'<{sector_count+1}I', raw[:offsets_size]))
        file_data = b''
        for i in range(sector_count):
            sec_start = offsets[i]
            sec_end = offsets[i+1]
            sec_data = raw[sec_start:sec_end]
            if block_entry.compressed:
                sec_data = _decompress(sec_data)
            file_data += sec_data
        return file_data

    def list_files(self, listfile_path: Optional[str] = None) -> Dict[str, Tuple[HashEntry, BlockEntry]]:
        """List all files in the archive.

        If listfile_path is provided, try to match filenames from it.
        Otherwise, returns dict of index → (hash_entry, block_entry) with unknown names.
        """
        files: Dict[str, Tuple[HashEntry, BlockEntry]] = {}
        # Try listfile first
        if listfile_path and os.path.exists(listfile_path):
            with open(listfile_path, 'r', errors='replace') as f:
                for line in f:
                    fname = line.strip()
                    if not fname:
                        continue
                    result = self.find_file(fname)
                    if result:
                        files[fname] = result
        # Also try reading the (listfile) special file
        listfile_data = self.read_file('(listfile)')
        if listfile_data:
            try:
                listfile_text = listfile_data.decode('utf-8', errors='replace')
                for line in listfile_text.splitlines():
                    fname = line.strip()
                    if not fname:
                        continue
                    result = self.find_file(fname)
                    if result and fname not in files:
                        files[fname] = result
            except Exception:
                pass
        # Add any unlisted files by their block index
        listed_blocks = {h.block_index for h, b in files.values() if h.block_index != 0xFFFFFFFF}
        for i, block in enumerate(self.block_table):
            if block.exists and i not in listed_blocks:
                files[f'<unknown_block_{i}>'] = (HashEntry(0, 0, 0, 0, i), block)
        return files

    def extract_all(self, output_dir: str, listfile_path: Optional[str] = None) -> Dict[str, int]:
        """Extract all files to output_dir.

        Returns dict of filename → bytes extracted (or -1 on error).
        """
        os.makedirs(output_dir, exist_ok=True)
        files = self.list_files(listfile_path)
        results: Dict[str, int] = {}
        for fname, (hash_entry, block_entry) in files.items():
            try:
                data = self.read_file(fname) if not fname.startswith('<unknown') else None
                if data:
                    # Sanitize filename for filesystem
                    safe_name = fname.replace('\\', '/').replace('/', '_')
                    out_path = os.path.join(output_dir, safe_name)
                    with open(out_path, 'wb') as f:
                        f.write(data)
                    results[fname] = len(data)
                    print(f"  ✓ {fname} → {len(data)} bytes")
                else:
                    results[fname] = 0
            except Exception as e:
                results[fname] = -1
                print(f"  ✗ {fname}: {e}")
        return results


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_map.py <map.w3x> <output_dir> [listfile.txt]")
        sys.exit(1)
    map_path = sys.argv[1]
    output_dir = sys.argv[2]
    listfile_path = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"=== Parsing WC3 map: {map_path} ===")
    print(f"Output directory: {output_dir}")
    if listfile_path:
        print(f"Listfile: {listfile_path}")
    print()

    # Parse HM3W header
    with open(map_path, 'rb') as f:
        header_data = f.read(512)
    if header_data[:4] == b'HM3W':
        # Map name starts at offset 8
        name_end = header_data.index(b'\x00', 8)
        map_name = header_data[8:name_end].decode('utf-8', errors='replace')
        print(f"Map name: {map_name}")
        max_players = struct.unpack('<I', header_data[name_end+5:name_end+9])[0]
        print(f"Max players: {max_players}")
        print()

    # Parse MPQ archive
    mpq_map = WC3Map(map_path)
    print()
    print(f"=== Extracting files to: {output_dir} ===")
    results = mpq_map.extract_all(output_dir, listfile_path)
    print()
    print("=== Summary ===")
    extracted = sum(1 for v in results.values() if v > 0)
    failed = sum(1 for v in results.values() if v < 0)
    empty = sum(1 for v in results.values() if v == 0)
    total_bytes = sum(v for v in results.values() if v > 0)
    print(f"Extracted: {extracted} files ({total_bytes} bytes)")
    print(f"Failed: {failed}")
    print(f"Empty: {empty}")


if __name__ == '__main__':
    main()

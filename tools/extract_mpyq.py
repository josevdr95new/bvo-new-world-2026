"""Extract all files from a Warcraft III .w3x map using mpyq.

Handles:
- MPQ archives embedded in WC3 maps (skips HM3W header at offset 512)
- Encrypted files (MPQ_FILE_ENCRYPTED + MPQ_FILE_FIX_KEY)
- Compressed files (zlib, bzip2)
- Sector-based and single-unit files
- Special files: (listfile), (attributes), (signature)
"""
from __future__ import annotations
import os
import sys
import struct
import zlib
import bz2
from typing import Optional, List, Dict, Tuple
from io import BytesIO

import mpyq


# MPQ file flags
MPQ_FILE_IMPLODE = 0x00000100
MPQ_FILE_COMPRESS = 0x00000200
MPQ_FILE_ENCRYPTED = 0x00010000
MPQ_FILE_FIX_KEY = 0x00020000
MPQ_FILE_PATCH_FILE = 0x00100000
MPQ_FILE_SINGLE_UNIT = 0x01000000
MPQ_FILE_DELETE_MARKER = 0x02000000
MPQ_FILE_SECTOR_CRC = 0x04000000
MPQ_FILE_EXISTS = 0x80000000

# MPQ crypt table (built once)
_crypt_table: List[int] = None


def prepare_crypt_table() -> List[int]:
    """Build the 1280-entry MPQ crypt table."""
    global _crypt_table
    if _crypt_table is not None:
        return _crypt_table
    crypt_table = [0] * 0x500
    seed = 0x00100001
    for index in range(0x100):
        for i in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp1 = (seed & 0xFFFF) << 0x10
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp2 = seed & 0xFFFF
            crypt_table[(i * 0x100) + index] = (temp1 | temp2) & 0xFFFFFFFF
    _crypt_table = crypt_table
    return crypt_table


def hash_string(s: str, hash_type: int) -> int:
    """Hash a string using MPQ's algorithm.

    hash_type: 0=TABLE_OFFSET, 1=NAME_A, 2=NAME_B, 3=FILE_KEY
    """
    crypt_table = prepare_crypt_table()
    seed1 = 0x7FED7FED
    seed2 = 0xEEEEEEEE
    s_upper = s.upper()
    for ch in s_upper:
        ch_val = ord(ch)
        if ch_val > 0x7E:
            ch_val = 0x3F  # '?'
        seed1 = (crypt_table[(hash_type * 0x100) + ch_val] ^ ((seed1 + seed2) & 0xFFFFFFFF)) & 0xFFFFFFFF
        seed2 = (ch_val + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1 & 0xFFFFFFFF


def decrypt_block(data: bytes, key: int) -> bytes:
    """Decrypt a block of data using MPQ algorithm."""
    crypt_table = prepare_crypt_table()
    if len(data) % 4 != 0:
        padded = data + b'\x00' * (4 - (len(data) % 4))
    else:
        padded = data
    result = bytearray(len(padded))
    seed = 0xEEEEEEEE
    cur_key = key
    for i in range(0, len(padded), 4):
        seed = (seed + crypt_table[0x400 + (cur_key & 0xFF)]) & 0xFFFFFFFF
        block = struct.unpack('<I', padded[i:i+4])[0]
        decrypted = (block ^ ((cur_key + seed) & 0xFFFFFFFF)) & 0xFFFFFFFF
        # Key rotation: ~key << 21, +0x11111122, OR with key>>11
        cur_key = ((((~cur_key) & 0xFFFFFFFF) << 0x15) & 0xFFFFFFFF)
        cur_key = (cur_key + 0x11111122) & 0xFFFFFFFF
        cur_key = (cur_key | (key >> 0x0B)) & 0xFFFFFFFF
        struct.pack_into('<I', result, i, decrypted)
    return bytes(result[:len(data)])


def decompress_sector(data: bytes) -> bytes:
    """Decompress a single sector of MPQ data."""
    if not data:
        return data
    # First byte is compression type
    comp_type = data[0]
    if comp_type == 0:
        # Uncompressed
        return data
    elif comp_type == 2:
        # zlib (deflate)
        try:
            return zlib.decompress(data[1:], 15)
        except Exception:
            try:
                return zlib.decompress(data[1:], -15)
            except Exception:
                return data
    elif comp_type == 8:
        # PKWARE DCL (rare, not supported)
        # Try zlib as fallback
        try:
            return zlib.decompress(data[1:])
        except Exception:
            return data
    elif comp_type == 16:
        # bzip2
        try:
            return bz2.decompress(data[1:])
        except Exception:
            return data
    else:
        # Try all methods
        for method in [
            lambda d: zlib.decompress(d[1:], 15),
            lambda d: zlib.decompress(d[1:], -15),
            lambda d: bz2.decompress(d[1:]),
            lambda d: zlib.decompress(d[1:]),
        ]:
            try:
                return method(data)
            except Exception:
                continue
        # Return raw if nothing works
        return data


def extract_file(archive: mpyq.MPQArchive, filename: str, sector_size: int) -> Optional[bytes]:
    """Extract a single file from the MPQ archive, handling encryption + compression."""
    # Find hash entry
    hash_entry = archive.get_hash_table_entry(filename)
    if not hash_entry:
        return None
    block_idx = hash_entry.block_table_index
    if block_idx >= len(archive.block_table):
        return None
    block = archive.block_table[block_idx]
    # Check file exists
    if not (block.flags & MPQ_FILE_EXISTS):
        return None
    # Read raw data
    archive.file.seek(block.offset)
    raw = archive.file.read(block.archived_size)
    if len(raw) < block.archived_size:
        return None
    # Compute file key if encrypted
    file_key = 0
    if block.flags & MPQ_FILE_ENCRYPTED:
        file_key = hash_string(filename, 3)
        if block.flags & MPQ_FILE_FIX_KEY:
            # FIX_KEY: key adjusted based on file position
            file_key = (file_key + block.offset) & 0xFFFFFFFF
    # Single-unit file
    if block.flags & MPQ_FILE_SINGLE_UNIT:
        data = raw
        if block.flags & MPQ_FILE_ENCRYPTED:
            data = decrypt_block(data, file_key)
        if block.flags & (MPQ_FILE_COMPRESS | MPQ_FILE_IMPLODE):
            data = decompress_sector(data)
        return data[:block.size]
    # Sector-based file
    # Each file has a sector offsets table at the start (4 bytes per sector + 1 for end)
    sector_count = (block.size + sector_size - 1) // sector_size
    offsets_table_size = (sector_count + 1) * 4
    if len(raw) < offsets_table_size:
        return None
    offsets_raw = raw[:offsets_table_size]
    if block.flags & MPQ_FILE_ENCRYPTED:
        offsets_raw = decrypt_block(offsets_raw, file_key - 1)
    offsets = list(struct.unpack(f'<{sector_count+1}I', offsets_raw))
    # If file has sector CRCs, skip the CRC table (4 bytes after offsets)
    crc_offset = 0
    if block.flags & MPQ_FILE_SECTOR_CRC:
        crc_offset = 4  # CRC is 4 bytes
    # Read each sector
    result = b''
    for i in range(sector_count):
        sec_start = offsets[i]
        sec_end = offsets[i+1]
        # Adjust for CRC if present
        sec_data = raw[sec_start + crc_offset:sec_end + crc_offset]
        if not sec_data:
            continue
        if block.flags & MPQ_FILE_ENCRYPTED:
            sec_data = decrypt_block(sec_data, file_key + i)
        if block.flags & (MPQ_FILE_COMPRESS | MPQ_FILE_IMPLODE):
            sec_data = decompress_sector(sec_data)
        # Pad to sector size (except last sector)
        if i < sector_count - 1 and len(sec_data) < sector_size:
            sec_data = sec_data + b'\x00' * (sector_size - len(sec_data))
        result += sec_data
    return result[:block.size]


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_mpyq.py <map.w3x> <output_dir>")
        sys.exit(1)
    map_path = sys.argv[1]
    output_dir = sys.argv[2]
    print(f"=== Extracting {map_path} → {output_dir} ===")
    # Read map file
    with open(map_path, 'rb') as f:
        data = f.read()
    print(f"Map size: {len(data)} bytes")
    # Find HM3W header info
    if data[:4] == b'HM3W':
        # Map name starts at offset 8
        name_end = data.index(b'\x00', 8)
        map_name = data[8:name_end].decode('utf-8', errors='replace')
        print(f"Map name: {map_name}")
    # Write MPQ portion to temp file
    mpq_offset = 512  # Standard WC3 map header
    if data[mpq_offset:mpq_offset+4] not in (b'MPQ\x1a', b'\x1aMPQ'):
        # Search for MPQ signature
        for sig in [b'\x1aMPQ', b'MPQ\x1a']:
            pos = data.find(sig)
            if pos != -1:
                mpq_offset = pos
                break
    mpq_data = data[mpq_offset:]
    temp_path = '/tmp/wc3_extract_mpq_only.mpq'
    with open(temp_path, 'wb') as f:
        f.write(mpq_data)
    print(f"MPQ at offset {mpq_offset}, size: {len(mpq_data)} bytes")
    print()
    # Load with mpyq
    archive = mpyq.MPQArchive(temp_path, listfile=False)
    # Determine sector size from header
    # mpyq stores it in archive.header
    header = archive.header
    sector_size = 512 << header.block_size if hasattr(header, 'block_size') else 512
    print(f"Sector size: {sector_size}")
    print(f"Hash entries: {len(archive.hash_table)}")
    print(f"Block entries: {len(archive.block_table)}")
    print()
    # Common WC3 file names to try
    test_files = [
        '(listfile)', '(attributes)', '(signature)',
        'war3map.j', 'war3map.lua', 'war3map.w3i',
        'war3map.w3u', 'war3map.w3t', 'war3map.w3a', 'war3map.w3h',
        'war3map.w3q', 'war3map.w3b', 'war3map.w3d', 'war3map.w3r',
        'war3map.w3c', 'war3map.w3s',
        'war3map.doo', 'war3map.shd', 'war3map.w3e', 'war3map.wpm',
        'war3map.mmp', 'war3map.imp',
        'war3mapunits.doo',
        'war3mapMisc.txt', 'war3mapSkin.txt', 'war3mapExtra.txt',
        'war3mapMap.blp', 'war3mapMap.tga', 'war3mapPreview.tga', 'war3mapPreview.jpg',
        'scripts\\Blizzard.j', 'scripts\\common.j', 'scripts\\common.ai',
        'war3map.j.lua',
    ]
    # Try to extract (listfile) first to get more filenames
    listfile_data = extract_file(archive, '(listfile)', sector_size)
    extra_files = []
    if listfile_data:
        try:
            listfile_text = listfile_data.decode('utf-8', errors='replace')
            for line in listfile_text.splitlines():
                fname = line.strip().rstrip('\r\n')
                if fname and fname not in test_files:
                    extra_files.append(fname)
            print(f"✓ Extracted (listfile) with {len(extra_files)} additional filenames")
        except Exception as e:
            print(f"⚠ Failed to decode listfile: {e}")
    test_files = test_files + extra_files
    # Deduplicate
    test_files = list(dict.fromkeys(test_files))
    # Extract all
    print(f"\n=== Extracting {len(test_files)} potential files ===")
    os.makedirs(output_dir, exist_ok=True)
    extracted = 0
    failed = 0
    for fname in test_files:
        try:
            data = extract_file(archive, fname, sector_size)
            if data and len(data) > 0:
                # Save
                safe_name = fname.replace('\\', '/').replace('/', '_')
                out_path = os.path.join(output_dir, safe_name)
                # Create subdirs if needed
                os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else '.', exist_ok=True)
                with open(out_path, 'wb') as f:
                    f.write(data)
                size_str = f"{len(data)} bytes"
                # Detect file type
                if fname.endswith('.j') or fname.endswith('.lua'):
                    type_str = " (JASS script)"
                elif fname.endswith('.w3u'):
                    type_str = " (units)"
                elif fname.endswith('.w3t'):
                    type_str = " (items)"
                elif fname.endswith('.w3a'):
                    type_str = " (abilities)"
                elif fname.endswith('.w3h'):
                    type_str = " (heroes/heroes)"
                elif fname.endswith('.w3i'):
                    type_str = " (map info)"
                elif fname.endswith('.w3e'):
                    type_str = " (environment)"
                elif fname.endswith('.doo'):
                    type_str = " (doodads)"
                else:
                    type_str = ""
                print(f"  ✓ {fname:<35} → {size_str}{type_str}")
                extracted += 1
            else:
                pass  # File not found or empty - skip silently
        except Exception as e:
            print(f"  ✗ {fname}: {e}")
            failed += 1
    print(f"\n=== Summary ===")
    print(f"Extracted: {extracted} files")
    print(f"Failed: {failed}")
    print(f"Output: {output_dir}/")
    # Print total size
    total_size = sum(os.path.getsize(os.path.join(output_dir, f)) for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f)))
    print(f"Total extracted size: {total_size} bytes ({total_size/1024:.1f} KB)")


if __name__ == '__main__':
    main()

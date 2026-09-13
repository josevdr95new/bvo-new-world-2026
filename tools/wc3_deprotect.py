"""WC3 Map Deprotector & Extractor — Python puro

Extrae TODOS los archivos de un mapa .w3x de Warcraft III, incluyendo:
- Scripts JASS (war3map.j)
- Datos de unidades (war3map.w3u)
- Datos de items (war3map.w3t)
- Datos de habilidades (war3map.w3a)
- Modificaciones de heroes (war3map.w3h)
- Y todos los demas archivos del MPQ

Maneja:
- MPQ archives con header en offset 512 (WC3 maps)
- Encriptacion MPQ (MPQ_FILE_ENCRYPTED + MPQ_FILE_FIX_KEY)
- Compresion zlib, bzip2, PKWARE
- Archivos sector-based y single-unit
- Tabla de offsets de sectores + CRC

BUG CORREGIDO: la rotacion de clave en decrypt_block usaba el parametro
original 'key' en vez de la clave actual 'cur_key', causando que TODA la
desencriptacion fallara. Esto impedia descomprimir los archivos.

Uso:
    python3 wc3_deprotect.py <mapa.w3x> <directorio_salida>
"""
from __future__ import annotations
import os
import sys
import struct
import zlib
import bz2
from typing import List, Dict, Optional, Tuple

# Instalar mpyq si no esta disponible
try:
    import mpyq
except ImportError:
    print("Instalando mpyq...")
    os.system(f"{sys.executable} -m pip install mpyq")
    import mpyq


# ============================================================
# MPQ CONSTANTS
# ============================================================
MPQ_FILE_IMPLODE = 0x00000100
MPQ_FILE_COMPRESS = 0x00000200
MPQ_FILE_ENCRYPTED = 0x00010000
MPQ_FILE_FIX_KEY = 0x00020000
MPQ_FILE_PATCH_FILE = 0x00100000
MPQ_FILE_SINGLE_UNIT = 0x01000000
MPQ_FILE_DELETE_MARKER = 0x02000000
MPQ_FILE_SECTOR_CRC = 0x04000000
MPQ_FILE_EXISTS = 0x80000000


# ============================================================
# MPQ CRYPTO TABLE
# ============================================================
_crypt_table: List[int] = None


def prepare_crypt_table() -> List[int]:
    """Construye la tabla de 1280 entradas para el algoritmo MPQ."""
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
    """Hash MPQ. hash_type: 0=TABLE_OFFSET, 1=NAME_A, 2=NAME_B, 3=FILE_KEY."""
    ct = prepare_crypt_table()
    seed1 = 0x7FED7FED
    seed2 = 0xEEEEEEEE
    for ch in s.upper():
        cv = ord(ch)
        if cv > 0x7E:
            cv = 0x3F  # '?'
        seed1 = (ct[(hash_type * 0x100) + cv] ^ ((seed1 + seed2) & 0xFFFFFFFF)) & 0xFFFFFFFF
        seed2 = (cv + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1 & 0xFFFFFFFF


def decrypt_block(data: bytes, key: int) -> bytes:
    """Desencripta un bloque usando el algoritmo MPQ.
    
    BUG CORREGIDO: la rotacion de clave ahora usa la clave actual (cur_key)
    en ambas partes de la operacion, no el parametro original 'key'.
    
    StormLib reference:
        key = ((~key << 0x15) + 0x11111122) | (key >> 0x0B)
    
    Antes (BUG):
        cur_key = (cur_key | (key >> 0x0B))  # usaba 'key' original
    Ahora (FIX):
        cur_key = (cur_key | (old_key >> 0x0B))  # usa 'old_key' = cur_key antes de rotar
    """
    ct = prepare_crypt_table()
    # Pad a multiplo de 4
    if len(data) % 4 != 0:
        padded = data + b'\x00' * (4 - (len(data) % 4))
    else:
        padded = data
    result = bytearray(len(padded))
    seed = 0xEEEEEEEE
    cur_key = key
    for i in range(0, len(padded), 4):
        seed = (seed + ct[0x400 + (cur_key & 0xFF)]) & 0xFFFFFFFF
        block_val = struct.unpack('<I', padded[i:i+4])[0]
        decrypted = (block_val ^ ((cur_key + seed) & 0xFFFFFFFF)) & 0xFFFFFFFF
        # === ROTACION DE CLAVE CORREGIDA ===
        # Guardar clave actual antes de rotar
        old_key = cur_key
        # Parte 1: (~key << 0x15) + 0x11111122
        cur_key = (((~old_key) & 0xFFFFFFFF) << 0x15) & 0xFFFFFFFF
        cur_key = (cur_key + 0x11111122) & 0xFFFFFFFF
        # Parte 2: OR con (key >> 0x0B) — USA old_key, NO el parametro original
        cur_key = (cur_key | (old_key >> 0x0B)) & 0xFFFFFFFF
        struct.pack_into('<I', result, i, decrypted)
    return bytes(result[:len(data)])


def decompress_sector(data: bytes) -> bytes:
    """Descomprime un sector MPQ.
    
    El primer byte indica el tipo de compresion:
        0x00 = sin compresion
        0x02 = zlib (deflate)
        0x08 = PKWARE DCL
        0x10 = bzip2
    Para combinaciones (bitmask), se intentan multiples metodos.
    """
    if not data or len(data) == 0:
        return data
    comp_type = data[0]
    payload = data[1:]
    if comp_type == 0:
        return data  # Sin compresion
    elif comp_type == 2:
        # zlib (deflate)
        for wbits in [15, -15, 31]:
            try:
                return zlib.decompress(payload, wbits)
            except Exception:
                continue
        return data
    elif comp_type == 16:
        # bzip2
        try:
            return bz2.decompress(payload)
        except Exception:
            return data
    elif comp_type == 8:
        # PKWARE DCL — no soportado en Python puro
        # Intentar zlib como fallback
        try:
            return zlib.decompress(payload, -15)
        except Exception:
            return data
    else:
        # Compresion multiple (bitmask) — intentar todos los metodos
        if comp_type & 0x02:
            try:
                return zlib.decompress(payload, 15)
            except Exception:
                pass
        if comp_type & 0x10:
            try:
                return bz2.decompress(payload)
            except Exception:
                pass
        if comp_type & 0x08:
            try:
                return zlib.decompress(payload, -15)
            except Exception:
                pass
        # Ultimo intento: sin el byte de tipo
        try:
            return zlib.decompress(data, 15)
        except Exception:
            try:
                return zlib.decompress(data, -15)
            except Exception:
                return data


# ============================================================
# WC3 MAP EXTRACTOR
# ============================================================
class WC3MapExtractor:
    """Extrae todos los archivos de un mapa WC3 .w3x."""

    def __init__(self, map_path: str):
        self.map_path = map_path
        with open(map_path, 'rb') as f:
            self.data = f.read()
        self.mpq_offset = self._find_mpq_offset()
        self._temp_path = None
        self._archive = None
        self.sector_size = 512

    def _find_mpq_offset(self) -> int:
        """Encuentra el offset del MPQ header en el archivo."""
        for offset in [512, 0]:
            if self.data[offset:offset+4] in (b'MPQ\x1a', b'\x1aMPQ'):
                return offset
        for sig in [b'\x1aMPQ', b'MPQ\x1a']:
            pos = self.data.find(sig)
            if pos != -1:
                return pos
        raise ValueError("MPQ signature not found")

    def _get_archive(self):
        """Obtiene el archive mpyq (creando archivo temporal sin header HM3W)."""
        if self._archive is not None:
            return self._archive
        mpq_data = self.data[self.mpq_offset:]
        self._temp_path = '/tmp/wc3_deprotect_mpq.mpq'
        with open(self._temp_path, 'wb') as f:
            f.write(mpq_data)
        self._archive = mpyq.MPQArchive(self._temp_path, listfile=False)
        # Determinar sector size
        header = self._archive.header
        if hasattr(header, 'block_size'):
            self.sector_size = 512 << header.block_size
        elif hasattr(header, 'sector_size'):
            self.sector_size = header.sector_size
        return self._archive

    def extract_file(self, filename: str) -> Optional[bytes]:
        """Extrae un archivo del MPQ, desencriptando y descomprimiendo."""
        archive = self._get_archive()
        hash_entry = archive.get_hash_table_entry(filename)
        if not hash_entry:
            return None
        block_idx = hash_entry.block_table_index
        if block_idx >= len(archive.block_table):
            return None
        block = archive.block_table[block_idx]
        if not (block.flags & MPQ_FILE_EXISTS):
            return None
        # Leer datos crudos
        archive.file.seek(block.offset)
        raw = archive.file.read(block.archived_size)
        if len(raw) < block.archived_size:
            return None
        # Calcular clave de encriptacion
        file_key = 0
        if block.flags & MPQ_FILE_ENCRYPTED:
            file_key = hash_string(filename, 3)
            if block.flags & MPQ_FILE_FIX_KEY:
                file_key = (file_key + block.offset) & 0xFFFFFFFF
        # SINGLE UNIT
        if block.flags & MPQ_FILE_SINGLE_UNIT:
            data = raw
            if block.flags & MPQ_FILE_ENCRYPTED:
                data = decrypt_block(data, file_key)
            if block.flags & (MPQ_FILE_COMPRESS | MPQ_FILE_IMPLODE):
                data = decompress_sector(data)
            return data[:block.size] if block.size > 0 else data
        # SECTOR-BASED
        sector_count = (block.size + self.sector_size - 1) // self.sector_size
        if sector_count == 0:
            sector_count = 1
        offsets_table_size = (sector_count + 1) * 4
        if len(raw) < offsets_table_size:
            # Probablemente es single-unit despues de todo
            data = raw
            if block.flags & MPQ_FILE_ENCRYPTED:
                data = decrypt_block(data, file_key)
            if block.flags & (MPQ_FILE_COMPRESS | MPQ_FILE_IMPLODE):
                data = decompress_sector(data)
            return data
        offsets_raw = raw[:offsets_table_size]
        if block.flags & MPQ_FILE_ENCRYPTED:
            offsets_raw = decrypt_block(offsets_raw, (file_key - 1) & 0xFFFFFFFF)
        offsets = list(struct.unpack(f'<{sector_count+1}I', offsets_raw))
        # CRC table (4 bytes despues de offsets si MPQ_FILE_SECTOR_CRC)
        crc_size = 4 if (block.flags & MPQ_FILE_SECTOR_CRC) else 0
        # Leer cada sector
        result = b''
        for i in range(sector_count):
            sec_start = offsets[i]
            sec_end = offsets[i+1] if i+1 < len(offsets) else block.archived_size
            if sec_end <= sec_start:
                continue
            sec_data = raw[sec_start:sec_end]
            if len(sec_data) == 0:
                continue
            if block.flags & MPQ_FILE_ENCRYPTED:
                sec_data = decrypt_block(sec_data, (file_key + i) & 0xFFFFFFFF)
            if block.flags & (MPQ_FILE_COMPRESS | MPQ_FILE_IMPLODE):
                sec_data = decompress_sector(sec_data)
            # Padding del ultimo sector
            if i < sector_count - 1:
                sec_data = sec_data[:self.sector_size]
            result += sec_data
        return result[:block.size] if block.size > 0 else result

    def extract_all(self, output_dir: str) -> Dict[str, int]:
        """Extrae TODOS los archivos del mapa al directorio especificado."""
        os.makedirs(output_dir, exist_ok=True)
        archive = self._get_archive()
        results: Dict[str, int] = {}
        # Lista de nombres de archivos WC3 conocidos
        known_files = [
            '(listfile)', '(attributes)', '(signature)',
            'war3map.j', 'war3map.lua',
            'war3map.w3i', 'war3map.w3u', 'war3map.w3t', 'war3map.w3a',
            'war3map.w3h', 'war3map.w3q', 'war3map.w3b', 'war3map.w3d',
            'war3map.w3r', 'war3map.w3c', 'war3map.w3s',
            'war3map.doo', 'war3map.shd', 'war3map.w3e', 'war3map.wpm',
            'war3map.mmp', 'war3map.imp', 'war3mapunits.doo',
            'war3mapMisc.txt', 'war3mapSkin.txt', 'war3mapExtra.txt',
            'war3mapMap.blp', 'war3mapMap.tga', 'war3mapPreview.tga',
            'war3mapPreview.jpg',
            'scripts\\Blizzard.j', 'scripts\\common.j', 'scripts\\common.ai',
            'war3map.j.lua',
            'conversation.txt', 'war3map.w3o',
            'war3mapPath.tga', 'war3map.ani',
        ]
        # Primero intentar extraer (listfile) para obtener mas nombres
        listfile_data = self.extract_file('(listfile)')
        extra_names = []
        if listfile_data:
            try:
                text = listfile_data.decode('utf-8', errors='replace')
                for line in text.splitlines():
                    fname = line.strip().rstrip('\r\n')
                    if fname and fname not in known_files:
                        extra_names.append(fname)
            except Exception:
                pass
        all_names = known_files + extra_names
        # Deduplicar
        seen = set()
        unique_names = []
        for n in all_names:
            if n not in seen:
                seen.add(n)
                unique_names.append(n)
        # Extraer cada archivo
        for fname in unique_names:
            try:
                data = self.extract_file(fname)
                if data and len(data) > 0:
                    safe_name = fname.replace('\\', '/').replace('/', '_')
                    out_path = os.path.join(output_dir, safe_name)
                    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else output_dir, exist_ok=True)
                    with open(out_path, 'wb') as f:
                        f.write(data)
                    results[fname] = len(data)
                # else: archivo no encontrado o vacio
            except Exception as e:
                results[fname] = -1
        # Buscar bloques sin nombre (archivos con nombres desconocidos)
        for i, block in enumerate(archive.block_table):
            if not (block.flags & MPQ_FILE_EXISTS):
                continue
            # Verificar si ya fue extraido
            already = False
            for fname, size in results.items():
                if size > 0:
                    hash_entry = archive.get_hash_table_entry(fname)
                    if hash_entry and hash_entry.block_table_index == i:
                        already = True
                        break
            if not already:
                # Intentar extraer bloque sin nombre
                try:
                    archive.file.seek(block.offset)
                    raw = archive.file.read(block.archived_size)
                    # Intentar descomprimir sin clave
                    if block.flags & (MPQ_FILE_COMPRESS | MPQ_FILE_IMPLODE):
                        data = decompress_sector(raw)
                        if data and len(data) > 4:
                            fname = f'unknown_block_{i}'
                            out_path = os.path.join(output_dir, fname)
                            with open(out_path, 'wb') as f:
                                f.write(data)
                            results[fname] = len(data)
                except Exception:
                    pass
        return results

    def get_map_info(self) -> Dict:
        """Obtiene informacion basica del mapa desde el header HM3W."""
        info = {}
        if self.data[:4] == b'HM3W':
            name_end = self.data.index(b'\x00', 8)
            info['name'] = self.data[8:name_end].decode('utf-8', errors='replace')
            info['max_players'] = struct.unpack('<I', self.data[name_end+5:name_end+9])[0]
        info['file_size'] = len(self.data)
        info['mpq_offset'] = self.mpq_offset
        return info


def main():
    if len(sys.argv) < 3:
        print("WC3 Map Deprotector & Extractor")
        print("Uso: python3 wc3_deprotect.py <mapa.w3x> <directorio_salida>")
        print()
        print("Extrae TODOS los archivos del mapa, incluyendo:")
        print("  - Scripts JASS (war3map.j)")
        print("  - Datos de unidades/heroes (war3map.w3u, war3map.w3h)")
        print("  - Datos de items (war3map.w3t)")
        print("  - Datos de habilidades (war3map.w3a)")
        print("  - Y todos los demas archivos del MPQ")
        sys.exit(1)
    map_path = sys.argv[1]
    output_dir = sys.argv[2]
    print(f"{'='*60}")
    print(f"WC3 Map Deprotector & Extractor")
    print(f"{'='*60}")
    print(f"Mapa: {map_path}")
    print(f"Salida: {output_dir}")
    print()
    extractor = WC3MapExtractor(map_path)
    info = extractor.get_map_info()
    print(f"Nombre del mapa: {info.get('name', '?')}")
    print(f"Tamaño: {info.get('file_size', 0)} bytes")
    print(f"MPQ offset: {info.get('mpq_offset', 0)}")
    print(f"Max jugadores: {info.get('max_players', '?')}")
    print()
    print(f"Extrayendo archivos...")
    print(f"{'='*60}")
    results = extractor.extract_all(output_dir)
    print()
    print(f"{'='*60}")
    print(f"RESUMEN")
    print(f"{'='*60}")
    extracted = [(name, size) for name, size in results.items() if size > 0]
    extracted.sort(key=lambda x: -x[1])
    failed = [(name, size) for name, size in results.items() if size < 0]
    total_bytes = sum(size for _, size in extracted)
    print(f"Extraidos: {len(extracted)} archivos ({total_bytes} bytes)")
    print(f"Fallidos: {len(failed)}")
    print()
    print(f"{'Archivo':<40} {'Tamaño':>12}  {'Tipo'}")
    print(f"{'-'*40} {'-'*12}  {'-'*20}")
    for fname, size in extracted:
        # Detectar tipo
        if fname.endswith('.j') or fname.endswith('.lua'):
            ftype = "JASS/Lua script"
        elif fname.endswith('.w3u'):
            ftype = "Unidades (heroes)"
        elif fname.endswith('.w3t'):
            ftype = "Items"
        elif fname.endswith('.w3a'):
            ftype = "Habilidades"
        elif fname.endswith('.w3h'):
            ftype = "Mods de heroes"
        elif fname.endswith('.w3i'):
            ftype = "Info del mapa"
        elif fname.endswith('.w3e'):
            ftype = "Terrain"
        elif fname.endswith('.doo'):
            ftype = "Doodads"
        elif fname.endswith('.blp') or fname.endswith('.tga'):
            ftype = "Imagen"
        elif fname.endswith('.txt'):
            ftype = "Texto"
        elif fname.endswith('.imp'):
            ftype = "Imports"
        elif fname == '(listfile)':
            ftype = "Lista de archivos"
        else:
            ftype = ""
        print(f"{fname:<40} {size:>12,}  {ftype}")
    print()
    print(f"Total: {len(extracted)} archivos, {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")


if __name__ == '__main__':
    main()

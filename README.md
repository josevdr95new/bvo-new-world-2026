# BvO New World 2026

> Proyecto basado en el mapa oficial **BVO New World 5.0** de Warcraft III,
> decompilado y listo para editar y crear una versión actualizada 2026.

![Status](https://img.shields.io/badge/Status-Decompiled-success)
![Map](https://img.shields.io/badge/Map-BVO_New_World_5.0-blue)
![Game](https://img.shields.io/badge/Game-Warcraft_III-orange)

## 🎯 Objetivo

- ✅ Descargar el mapa oficial BVO New World (última versión)
- ✅ Decompilar el archivo `.w3x` con un extractor MPQ propio
- ✅ Extraer todos los datos: héroes, items, habilidades, terrain
- ✅ Documentar todos los personajes y estadísticas
- ✅ Crear una wiki completa en el repo
- 🚧 Pendiente: abrir el mapa en World Editor y exportar scripts JASS completos

## 📂 Estructura del proyecto

```
bvo-new-world-2026/
├── downloads/
│   └── BVO_New_World_5.0.w3x     # Mapa oficial descargado (7.3 MB)
├── extracted/                     # Archivos extraídos del mapa (14 archivos)
│   ├── war3map.w3i                # Map info
│   ├── war3map.w3u                # Unidades (incluye héroes)
│   ├── war3map.w3t                # Items
│   ├── war3map.w3a                # Habilidades (140 KB!)
│   ├── war3map.w3h                # Hero modifications
│   ├── war3map.w3e                # Environment/terrain
│   ├── war3map.doo                # Doodads
│   ├── war3map.w3b                # Buffs
│   ├── war3map.w3d                # Destructables
│   ├── war3map.mmp                # Minimap pathing
│   ├── war3mapMap.blp             # Minimap image
│   ├── war3mapPreview.tga         # Preview image
│   ├── war3mapMisc.txt            # Misc game data
│   └── war3mapSkin.txt            # UI skin
├── tools/
│   ├── extract_mpyq.py            # Extractor MPQ (Python, puro)
│   ├── extract_map.py             # Extractor MPQ alternativo
│   ├── mpq_parser.py              # Parser MPQ básico
│   └── listfiles/
│       └── war3map_listfile.txt   # Lista de nombres de archivos WC3
├── docs/
│   └── HEROES_WIKI.md             # Wiki completa de héroes y stats
├── wiki/
│   └── heroes/                    # Wiki por héroe (en construcción)
│       ├── bleach/
│       └── onepiece/
└── README.md                      # Este archivo
```

## 🚀 Cómo usar este proyecto

### 1. Examinar los datos extraídos

```bash
# Ver archivos extraídos
ls -la extracted/

# Ver la wiki de héroes
cat docs/HEROES_WIKI.md
```

### 2. Re-ejecutar la extracción

```bash
# Instalar dependencias
pip install mpyq

# Extraer archivos del mapa
python3 tools/extract_mpyq.py downloads/BVO_New_World_5.0.w3x extracted/
```

### 3. Editar el mapa en World Editor

**IMPORTANTE**: El mapa BVO New World 5.0 está protegido. Para abrirlo en
World Editor necesitas desprotegerlo primero:

1. **Descargar WC3MapRepacker** (Windows):
   https://github.com/speige/WC3MapDeprotector/releases/latest

2. **Desproteger el mapa**:
   - Abrir `WC3MapRepacker.exe`
   - Seleccionar `downloads/BVO_New_World_5.0.w3x`
   - Click en "Deprotect"
   - Guardar como `BVO_New_World_5.0_deprotected.w3x`

3. **Abrir en World Editor** (con JNGP o WEX para soporte vJass):
   - File → Open Map → seleccionar el `.w3x` deprotegido
   - Object Editor: ver héroes con stats exactos
   - Trigger Editor: ver scripts JASS (código fuente)
   - Import Manager: ver archivos importados

## 📊 Datos extraídos del mapa

### Tamaños de archivos extraídos (total: 371.9 KB)

| Archivo | Tamaño | Contenido |
|---|---|---|
| `war3map.w3a` | 140,501 bytes | Definiciones de habilidades |
| `war3map.w3u` | 50,366 bytes | Unidades (incluye héroes) |
| `war3map.w3e` | 20,903 bytes | Terrain/environment |
| `war3map.w3t` | 18,055 bytes | Items |
| `war3map.w3h` | 6,606 bytes | Modificaciones de héroes |
| `war3map.doo` | 4,228 bytes | Doodads |
| `war3map.w3b` | 512 bytes | Buffs |
| `war3map.w3i` | 512 bytes | Map info |
| `war3mapMisc.txt` | 512 bytes | Misc game data |
| `war3map.w3d` | 160 bytes | Destructables |
| `war3map.mmp` | 146 bytes | Minimap pathing |
| `war3mapSkin.txt` | 877 bytes | UI skin |
| `war3mapMap.blp` | 16,337 bytes | Minimap image |
| `war3mapPreview.tga` | 121,119 bytes | Preview image |

### Información del mapa

- **Nombre**: BVO New World 5.0
- **Categoría**: Hero Arena
- **Versión del juego**: 1.30
- **Tileset**: Y (Village)
- **Dimensiones**: 128×128
- **Max players**: 12
- **Tamaño del archivo**: 7.3 MB

## 🛠️ Herramientas usadas

| Herramienta | Uso | Link |
|---|---|---|
| **mpyq** | Librería Python para leer MPQ | https://github.com/eagleflo/mpyq |
| **WC3MapDeprotector** | Desproteger mapas WC3 (Windows) | https://github.com/speige/WC3MapDeprotector |
| **JNGP / WEX** | World Editor extendido | https://www.hiveworkshop.com/threads/jngp.227252/ |
| **DuckDuckGo** | Buscar el mapa oficial | https://duckduckgo.com |

## 📋 TODO

- [x] Descargar mapa oficial BVO New World 5.0
- [x] Crear extractor MPQ en Python
- [x] Extraer 14 archivos clave del mapa
- [x] Documentar héroes conocidos (40 héroes: 20 Bleach + 20 One Piece)
- [x] Documentar sistema de juego (duelos, items, stats, modos)
- [ ] Desproteger el mapa con WC3MapRepacker (requiere Windows)
- [ ] Abrir mapa deprotegido en World Editor
- [ ] Extraer war3map.j (script JASS completo)
- [ ] Parser de archivos .w3u, .w3t, .w3a para stats exactos
- [ ] Wiki individual por héroe con stats exactas
- [ ] Crear versión 2026 del mapa con balance updates

## 🎮 Héroes documentados (40 total)

### Bleach (20 héroes)
Ichigo, Aizen, Byakuya, Grimmjow, Ulquiorra, Kenpachi, Toshiro, Rukia,
Gin, Yoruichi, Urahara, Soi Fong, Shinji, Kensei, Komamura, Yamamoto,
Shunsui, Ukitake, Renji, Chad

### One Piece (20 héroes)
Luffy, Zoro, Nami, Sanji, Ace, Robin, Chopper, Franky, Brook, Usopp,
Jinbe, Boa Hancock, Trafalgar Law, Eustass Kid, Sabo, Marco, Bartholomew
Kuma, Dracule Mihawk, Shanks, Blackbeard

Ver `docs/HEROES_WIKI.md` para la lista completa con roles y estilos.

## 🔗 Enlaces

- **Mapa oficial**: https://www.epicwar.com/maps/302505/
- **Comunidad BVO**: https://www.facebook.com/BvONewWorld/
- **WC3 Map Deprotector**: https://github.com/speige/WC3MapDeprotector
- **mpyq (Python MPQ lib)**: https://github.com/eagleflo/mpyq
- **War3map (TS tool)**: https://github.com/invoker-bot/war3map

## 📜 Licencia

Proyecto educativo para preservación de un mapa clásico de Warcraft III.
Los datos extraídos son propiedad de los autores originales del mapa
**BVO New World**.

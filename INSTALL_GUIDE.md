# BVO New World 2026 — Guía de Instalación

## 🎮 Instalación Rápida (3 pasos)

### Paso 1: Descargar el mapa
Descarga el archivo `BVO_New_World_2026.w3x` desde:
- GitHub: https://github.com/josevdr95new/bvo-new-world-2026
- Tamaño: 7.3 MB

### Paso 2: Copiar a Warcraft III
Copia el archivo a tu carpeta de mapas de Warcraft III:
- **Windows**: `C:\Users\TU_USUARIO\Documents\Warcraft III\Maps\Download\`
- **Si no existe la carpeta**: créala

### Paso 3: ¡Jugar!
1. Abre Warcraft III (Frozen Throne)
2. Menú principal → **Custom Games**
3. Busca el mapa `BVO_New_World_2026` en la lista
4. ¡Selecciona y juega!

---

## 🗡️ Nuevo Héroe: Gin Ichimaru

Gin Ichimaru está integrado en el mapa con TODAS sus habilidades:

| Habilidad | Tecla | Efecto |
|---|---|---|
| **Shikai — Shinso** | Q | Espada se extiende 800-1200 range, daña + empuja |
| **Yari Perforante** | W | Estocada en línea 1200 range, reduce armor |
| **Shunpo** | E | Invisible + crítico garantizado + veneno |
| **Bankai — Kamishini no Yari** | R | Transformación 12s: ranged, Q atraviesa todos |
| **Sonrisa del Zorro** | D | Pasiva: crit chance, move speed, spell lifesteal |

### Stats base de Gin:
- HP: 850 (+75/nivel)
- Mana: 350 (+28/nivel)
- AGI: 30 (+3.5) ← atributo primario
- Move Speed: 310 (rápido)
- Attack: 52 (+4.2)

### Stats del mapa original (BVO New World 5.0):
- 51 héroes originales (19 Bleach + 18 One Piece + 14 Naruto)
- Sistema de duelo cada 5 minutos
- Max nivel 100
- Todos los items originales

---

## 📝 Para editar en World Editor (avanzado)

Si quieres modificar el mapa o añadir más héroes:

### Opción 1: Usar WC3MapRepacker (recomendado)
1. Descarga WC3MapRepacker: https://github.com/speige/WC3MapDeprotector/releases/latest
2. Desprotege `BVO_New_World_5.0.w3x` (el mapa base original)
3. Abre el resultado en World Editor
4. Importa `build/war3map.j` (nuestro script con Gin)
5. Configura el héroe en Object Editor

### Opción 2: Usar nuestro extractor
```bash
python3 tools/wc3_deprotect.py downloads/BVO_New_World_5.0.w3x extracted/
```

### Añadir más héroes custom:
```bash
# Crear nuevo héroe
mkdir -p custom_heroes/NOMBRE_HEROE/scripts
# Crear README.md con stats
# Crear scripts/NOMBRE_abilities.j con código JASS
# Añadir a build_map.py en AVAILABLE_HEROES
# Recompilar:
python3 build_map.py --hero gin --hero NOMBRE_HEROE
```

---

## 📦 Contenido del paquete

```
bvo-new-world-2026/
├── download/
│   └── BVO_New_World_2026.w3x     ← MAPA LISTO PARA JUGAR (7.3 MB)
├── build/
│   ├── BVO_New_World_2026.w3x     ← Mapa compilado
│   ├── war3map.j                   ← Script JASS con Gin (14.9 KB)
│   └── BUILD_INFO.txt              ← Info de la build
├── downloads/
│   ├── BVO_New_World_5.0.w3x       ← Mapa original (7.3 MB)
│   └── Bleach_Kidou_Wars_5.00.w3x  ← Mapa de referencia (4.3 MB)
├── custom_heroes/
│   └── gin_ichimaru/
│       ├── README.md                ← Diseño completo del héroe
│       ├── SPRITES.md               ← Guía de recursos visuales
│       └── scripts/
│           ├── gin_abilities.j      ← Código JASS de Gin (nuestro)
│           ├── shinso_original_kidou_wars.j ← Código original de Kidou Wars
│           └── Shinso_kidou_wars.j  ← Trigger Shinso original
├── tools/
│   ├── wc3_deprotect.py             ← Extractor MPQ (Python)
│   ├── extract_mpyq.py              ← Extractor alternativo
│   └── mpq_parser.py                ← Parser MPQ básico
├── extracted_v2/                    ← 62 héroes con stats reales
├── extracted_kidou/                 ← 274 archivos del Kidou Wars
├── docs/
│   └── HEROES_WIKI.md               ← Wiki de héroes
├── build_map.py                     ← Script de compilación
└── README.md                        ← Documentación completa
```

---

## ❓ Problemas frecuentes

**El mapa no aparece en la lista de custom games**
- Verifica que el archivo esté en `Documents\Warcraft III\Maps\Download\`
- Asegúrate de tener Warcraft III: The Frozen Throne (no solo Reign of Chaos)
- El mapa requiere versión 1.26+ de WC3

**Gin no aparece como héroe seleccionable**
- El script JASS con Gin está en `build/war3map.j`
- Para que Gin aparezca en el selector de héroes, necesitas:
  1. Desproteger el mapa con WC3MapRepacker
  2. Abrir en World Editor
  3. Object Editor → crear unidad de héroe para Gin
  4. Importar el war3map.j modificado
  5. Guardar y jugar

**¿Dónde están los sprites de Gin?**
- Ver `custom_heroes/gin_ichimaru/SPRITES.md` para la guía completa
- Modelo 3D: https://www.tapatalk.com/groups/hgft/gin-ichimaru-t761.html
- Iconos: crear con BLP Lab a partir de imágenes de Gin

---

## 🔗 Enlaces útiles

- **Repo**: https://github.com/josevdr95new/bvo-new-world-2026
- **Mapa original**: https://www.epicwar.com/maps/302505/
- **Bleach Kidou Wars**: https://www.hiveworkshop.com/threads/bleach-kidou-wars-5-00.142486/
- **WC3MapRepacker**: https://github.com/speige/WC3MapDeprotector/releases/latest
- **BLP Lab**: https://www.hiveworkshop.com/threads/blp-lab.167282/
- **Blender WC3 addon**: https://github.com/PavelBlend/Blender_WarCraft-3

¡Disfruta del mapa! 🎮

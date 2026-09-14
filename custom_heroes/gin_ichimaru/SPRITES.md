# Gin Ichimaru — Recursos Visuales (Sprites, Modelos, Efectos)

> Guía completa de recursos visuales compatibles con Warcraft III para el héroe
> Gin Ichimaru. Incluye modelos 3D, iconos, efectos y texturas.

## 🎨 Modelo 3D Principal

### Opción 1: Modelo existente de Gin Ichimaru para WC3 (RECOMENDADO)

Se confirmó que existe un modelo 3D de Gin Ichimaru convertido para WC3:

**Fuente**: Tapatalk (HGFT community)
- **URL**: https://www.tapatalk.com/groups/hgft/gin-ichimaru-t761.html
- **Creadores**: 
  - Model and Texture: Treasure Co. (rip original)
  - Ripped by: Shadowth117
  - Converting/Merging Textures: Robot-Dude
  - Bones and Animations: gabrueru
- **Formato**: MDX (Warcraft III nativo)
- **Estado**: ✅ Confirmado existente — requiere registro en Tapatalk para descargar

**Cómo obtenerlo**:
1. Registrarse en https://www.tapatalk.com/groups/hgft/ (gratis)
2. Visitar el thread: https://www.tapatalk.com/groups/hgft/gin-ichimaru-t761.html
3. Descargar el archivo adjunto (.mdx + .blp textures)
4. Importar en World Editor → Import Manager

---

### Opción 2: Modelo 3D de Sketchfab (convertir a MDX)

**Fuente**: Sketchfab
- **URL**: https://sketchfab.com/3d-models/gin-ichimaru-ec6e0d39ea6c4fce9e47c107b489c477
- **Autor**: leducgagnetommy
- **Formato**: GLTF/OBJ (descargable gratis)
- **Estado**: ✅ Descargable — requiere conversión a MDX

**Cómo convertirlo a MDX**:
1. Descargar el modelo desde Sketchfab (formato GLTF)
2. Importar en Blender con el addon **Blender WarCraft 3**:
   - https://github.com/PavelBlend/Blender_WarCraft-3
3. Exportar como .MDX
4. Crear texturas .BLP con BLP Lab o WC3 Image Converter

---

### Opción 3: Modelo base de WC3 + Reskin (FÁCIL)

Si no puedes obtener el modelo custom, usa un modelo base de WC3 con textura modificada:

| Modelo Base | ID | Por qué funciona |
|---|---|---|
| **Bandit Hero** | `Hvsh` | ⭐ Delgado, ágil, usa espada, build similar a Gin |
| **Blade Master** | `Obla` | Espadachín delgado, animaciones de corte rápidas |
| **Blood Elf Mage** | `Hbsm` | Delgado, elegante, para versión con kimono |
| **Demon Hunter** | `Edem` | Para el modo Bankai (forma más agresiva) |

**Pasos para reskin**:
1. Extraer la textura del modelo base con WC3 Image Viewer
2. Editar en Photoshop/GIMP:
   - Pelo: blanco plateado
   - Ojos: cerrados (sonrisa siniestra)
   - Ropa: kimono blanco con detalle azul (capitán 3er Escuadrón)
   - Piel: pálida
3. Guardar como .BLP (64x64 o 128x128)
4. Importar en World Editor → Import Manager

## 🖼️ Iconos (BLP)

### Icono de héroe (Command Button)

| Icono | Nombre | Tamaño | Uso |
|---|---|---|---|
| `BTN_Gin.blp` | Icono principal | 64×64 | Selector de héroe |
| `DISBTN_Gin.blp` | Versión gris | 64×64 | Estado deshabilitado |
| `ATC_Gin.blp` | Icono de ataque | 64×64 | Card de ataque |
| `PUR_Gin.blp` | Icono de retrato | 128×128 | Retrato del héroe |

**Cómo crearlos**:
1. Buscar imagen de Gin Ichimaru en Google Images (búsqueda: "Gin Ichimaru bleach face")
2. Recortar a cuadrado 64×64
3. Añadir borde dorado (estilo WC3)
4. Guardar como BLP usando:
   - **BLP Lab** (Windows): https://www.hiveworkshop.com/threads/blp-lab.167282/
   - **WC3 Image Converter** (Windows)
   - **Python**: `pip install pillow` + script de conversión BLP

### Iconos de habilidades

| Habilidad | Icono Sugerido | Fuente WC3 |
|---|---|---|
| **Q: Shinso** | `BTNHumanMissile.blp` | Abilities\Weapons\BloodElfMissile |
| **W: Yari** | `BTNMarkOfChaos.blp` | Abilities\Spells\Human\MarkOfChaos |
| **E: Shunpo** | `BTNInvisibility.blp` | Abilities\Spells\Human\Invisibility |
| **R: Bankai** | `BTNAvatar.blp` | Abilities\Spells\Human\Avatar |
| **D: Pasiva** | `BTNCriticalStrike.blp` | Abilities\Spells\Orc\CriticalStrike |

**Modificaciones para personalizar**:
- Q: Cambiar color del proyectil a blanco brillante
- R: Añadir aura roja pulsante al icono
- D: Añadir destello dorado (sonrisa del zorro)

## ✨ Efectos Visuales (Modelos MDX)

### Efectos por habilidad

| Habilidad | Efecto WC3 Existente | Path | Modificación |
|---|---|---|---|
| **Q: Shinso** | Huntress Missile | `Abilities\Weapons\HuntressMissile\HuntressMissile.mdl` | Cambiar color a blanco puro |
| **Q: Impacto** | Banish Target | `Abilities\Spells\Human\Banish\BanishTarget.mdl` | Sin cambios |
| **W: Yari** | Mark of Chaos | `Abilities\Spells\Human\MarkOfChaos\MarkOfChaosTarget.mdl` | Sin cambios |
| **W: Perforación** | Howl of Terror | `Abilities\Spells\Other\HowlOfTerror\HowlOfTerror.mdl` | Sin cambios |
| **E: Shunpo** | Invisibility | `Abilities\Spells\Human\Invisibility\Invisibility.mdl` | Sin cambios |
| **E: Humo** | Cloud of Fog | `Abilities\Spells\Human\CloudOfFog\CloudOfFog.mdl` | Cambiar a blanco |
| **E: Explosión** | Flame Strike | `Abilities\Spells\Human\FlameStrike\FlameStrike1.mdl` | Cambiar a blanco/azul |
| **R: Bankai Aura** | Avatar | `Abilities\Spells\Human\Avatar\Avatar.mdl` | Cambiar a rojo sangre |
| **R: Activación** | Howl of Terror | `Abilities\Spells\Other\HowlOfTerror\HowlOfTerror.mdl` | Sin cambios |
| **D: Crítico** | Howl of Terror | `Abilities\Spells\Other\HowlOfTerror\HowlOfTerror.mdl` | Sin cambios |

### Efectos de sonido

| Habilidad | Sonido WC3 | Path |
|---|---|---|
| **Q: Shinso** | Metal Hit + Shot | `Sound\Units\Combat\MetalHeavyChop1.wav` |
| **W: Yari** | Metal Heavy Slice | `Sound\Units\Combat\MetalHeavySlice1.wav` |
| **E: Shunpo (on)** | Invisibility On | `Sound\Abilities\Spells\Human\Invisibility\Invisibility1.wav` |
| **E: Shunpo (off)** | Invisibility Off | `Sound\Abilities\Spells\Human\Invisibility\InvisibilityOff1.wav` |
| **E: Explosión** | Flame Strike | `Sound\Abilities\Spells\Human\FlameStrike\FlameStrike1.wav` |
| **R: Bankai** | Avatar + Blade Master | `Sound\Abilities\Spells\Human\Avatar\Avatar1.wav` |
| **Crítico** | Metal Heavy Chop | `Sound\Units\Combat\MetalHeavyChop1.wav` |
| **Muerte** | Blade Master Death | `Sound\Units\Orc\HeroBladeMaster\HeroBladeMasterDeath1.wav` |

## 📐 Animaciones del Modelo

| Animación | WC3 Base | Uso para Gin |
|---|---|---|
| **Stand** | Bandit Hero Stand | Gin sonriendo con ojos cerrados, mano en espada |
| **Walk** | Bandit Hero Walk | Caminar relajado, casi burlón |
| **Attack 1** | Bandit Hero Attack | Estocada rápida (Shinso extendiéndose) |
| **Attack 2** | Blade Master Attack | Corte horizontal con retroceso |
| **Spell** | Bandit Hero Spell | Mano en empuñadura + sonrisa amplia |
| **Spell Slam** | Blade Master Slam | Para Bankai (movimiento poderoso) |
| **Death** | Bandit Hero Death | Caer de rodillas, espada clavada |
| **Decay** | Bandit Hero Decay | Desvanecerse |

## 🎨 Paleta de Colores para Reskin

| Elemento | Color | Hex |
|---|---|---|
| Pelo | Blanco plateado | `#E8E8E8` |
| Piel | Pálida | `#F0D8C0` |
| Kimono (base) | Blanco | `#F8F8F8` |
| Kimono (detalle) | Azul capitán | `#2C5F8A` |
| Obi (cinturón) | Azul oscuro | `#1A3A5A` |
| Espada (Shinso) | Blanco brillante | `#FFFFFF` |
| Espada (Bankai) | Rojo sangre | `#8B0000` |
| Ojos | Cerrados (línea) | `#000000` |
| Sonrisa | Blanca | `#FFFFFF` |

## 🔗 Enlaces de descarga de recursos

### Modelos 3D de Gin Ichimaru
1. **Tapatalk HGFT** (Modelo MDX ya convertido para WC3):
   https://www.tapatalk.com/groups/hgft/gin-ichimaru-t761.html
   - Requiere registro gratis
   - Incluye .MDX + .BLP textures + animaciones

2. **Sketchfab** (Modelo 3D genérico, convertir a MDX):
   https://sketchfab.com/3d-models/gin-ichimaru-ec6e0d39ea6c4fce9e47c107b489c477
   - Descarga gratis en formato GLTF/OBJ
   - Convertir con Blender + addon WarCraft 3

### Packs de modelos anime para WC3
3. **Hive Workshop - DBZ/Naruto/Anime Models** (incluye Bleach):
   https://www.hiveworkshop.com/threads/dbz-naruto-anime-models.53706/
   - Modelos de Ichigo, Kenpachi (mismo estilo que Gin)

4. **Hive Workshop - Anime Models site** (enlace a sitio chino con packs):
   https://www.hiveworkshop.com/threads/anime-models-not-request-but-if-you-are-looking-for-heres-teh-site.92545/
   - Packs completos de modelos anime

5. **Hive Workshop - Bleach Kidou Wars** (mapa con Ichimaru jugable):
   https://www.hiveworkshop.com/threads/bleach-kidou-wars.142714/
   - Descargar el mapa y extraer el modelo con nuestro extractor MPQ

6. **Hive Workshop - Bleach model pack**:
   https://www.hiveworkshop.com/threads/bleach-model-pack-for-anyone-who-can-make-icons.118808/
   - Pack con casi todos los personajes de Bleach

### Herramientas para editar modelos
7. **Blender WarCraft 3 addon** (importar/exportar MDX):
   https://github.com/PavelBlend/Blender_WarCraft-3

8. **BLP Lab** (convertir imágenes a BLP):
   https://www.hiveworkshop.com/threads/blp-lab.167282/

9. **WC3 Map Deprotector** (desproteger mapas para extraer modelos):
   https://github.com/speige/WC3MapDeprotector/releases/latest

### Inspiración visual
10. **Bleach Wiki - Gin Ichimaru** (referencia visual completa):
    https://bleach.fandom.com/wiki/Gin_Ichimaru

11. **Bleach Wiki - Shinso** (referencia del Zanpakuto):
    https://bleach.fandom.com/wiki/Shinso

12. **Bleach Wiki - Kamishini no Yari** (referencia del Bankai):
    https://bleach.fandom.com/wiki/Korose,_Kamishini_no_Yari

## 📋 Checklist de Importación en World Editor

```
□ 1. Obtener modelo MDX de Gin (Opción 1: Tapatalk, Opción 2: Sketchfab+Blender, Opción 3: Reskin)
□ 2. Crear iconos BLP (64×64): BTN_Gin, DISBTN_Gin, ATC_Gin, PUR_Gin
□ 3. Crear iconos de habilidades BLP: BTN_Shinso, BTN_Yari, BTN_Shunpo, BTN_Bankai, BTN_Sonrisa
□ 4. Importar modelo MDX en Import Manager:
    - Path: units\Heroes\Gin\Gin.mdl
□ 5. Importar texturas BLP:
    - units\Heroes\Gin\Gin.blp
    - units\Heroes\Gin\Gin_portrait.blp
□ 6. Importar iconos BLP:
    - ReplaceableTextures\CommandButtons\BTN_Gin.blp
    - ReplaceableTextures\CommandButtonsDisabled\DISBTN_Gin.blp
    - ReplaceableTextures\CommandButtons\BTN_Shinso.blp
    - ReplaceableTextures\CommandButtons\BTN_Yari.blp
    - ReplaceableTextures\CommandButtons\BTN_Shunpo.blp
    - ReplaceableTextures\CommandButtons\BTN_Bankai.blp
    - ReplaceableTextures\CommandButtons\BTN_Sonrisa.blp
□ 7. Configurar Object Editor:
    - Crear unidad basada en Bandit Hero (Hvsh)
    - Name: "Captain of 3rd Division"
    - Proper Name: "Gin Ichimaru"
    - Model: units\Heroes\Gin\Gin.mdl
    - Icon: ReplaceableTextures\CommandButtons\BTN_Gin.blp
    - Stats: según tabla en README.md
□ 8. Crear 5 habilidades en Object Editor
□ 9. Importar script JASS (gin_abilities.j) en Trigger Editor
□ 10. Testear el mapa
```

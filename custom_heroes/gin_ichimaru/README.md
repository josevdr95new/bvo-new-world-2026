# Gin Ichimaru — Nuevo Héroe (Bleach)

> Diseño completo de un nuevo héroe para BvO New World 2026.
> NO está presente en el mapa original (solo se le menciona en descripciones).
> Zanpakuto: Shinso (Shikai) / Kamishini no Yari (Bankai)

## 📋 Información

| Campo | Valor |
|---|---|
| **Nombre** | Gin Ichimaru |
| **Clase** | Captain of 3rd Division |
| **Anime** | Bleach |
| **Rol** | Assassin / Burst Caster |
| **Atributo** | AGI |
| **Move Speed** | 310 |

## 📊 Stats Base

| Stat | Base | /Nivel | Nv100 |
|---|---|---|---|
| HP | 850 | +75 | 8275 |
| Mana | 350 | +28 | 3072 |
| Atk Dmg | 52 | +4.2 | 465 |
| Atk Spd | 1.5 | +0.025 | 4.0 |
| Atk Range | 128 (melee) | - | - |
| Defense | 2 | +0.35 | 36.5 |
| STR | 18 | +2.0 | 218 |
| AGI | 30 | +3.5 | 378 |
| INT | 20 | +1.8 | 200 |

## 🗡️ Habilidades

### Q: Shikai — Shinso (Soga Blanca)
- **CD**: 5s | **Mana**: 60 | **Niveles**: 5 (1,3,5,7,9)
- Espada se extiende 800-1200 range en línea recta
- Daño al primer enemigo + knockback 100
- Reactivar en 3s para retraer y arrastrar enemigo hacia Gin
- `damage = (AGI * 2.0 + 70)` | `range = 700 + level * 100`

### W: Yari — Lanza Perforante
- **CD**: 10s | **Mana**: 90 | **Niveles**: 5 (1,3,5,7,9)
- Estocada en línea 1200 range, atraviesa enemigos
- Reduce armor 4-8 por 5s
- `damage = (AGI * 1.8 + 50) * level`

### E: Shunpo — Sonrisa Siniestra
- **CD**: 12s | **Mana**: 70 | **Niveles**: 5 (1,3,5,7,9)
- Invisible 2.5-4.5s
- Próximo ataque/habilidad: crit garantizado (2.3x-3.5x)
- Aplica veneno: AGI*0.5/s por 4s + slow 30%
- `invis = 2.0 + level * 0.5` | `crit = 2.0 + level * 0.3`

### R: Bankai — Kamishini no Yari (Lanza Mata-Dioses)
- **CD**: 100s | **Mana**: 250 | **Niveles**: 3 (6,12,18)
- **Duración**: 12s
- Rango de ataque → 600 (ranged)
- Q atraviesa TODOS los enemigos
- W reduce HP máximo 5% por stack (max 3)
- E cooldown → 4s
- +40% AGI temporal

### D: Sonrisa del Zorro (Pasiva)
- **Niveles**: 5 (1,3,5,7,9)
- Crit chance 8-20% | Crit dmg 1.6x-2.0x
- Move speed +15 a +35
- Spell lifesteal 7-15%

# Kisuke Urahara — Nuevo Héroe (Bleach)

> Diseño completo de un nuevo héroe para BvO New World 2026.
> Basado en el personaje de Bleach, NO presente en el mapa original.

## 📋 Información del Héroe

| Campo | Valor |
|---|---|
| **Nombre** | Kisuke Urahara |
| **Clase** | Former Captain of 12th Division |
| **Anime** | Bleach |
| **Equipo** | Bleach |
| **Rol** | Hybrid (Caster / Support) |
| **Estilo** | Intel-based caster con movilidad y control de área |
| **Modelo base** | Custom (recomendado:Units\Heroes\BloodElfMage\BloodElfMage.mdl) |
| **Icono** | BTN_Urahara.blp (custom) |

## 📊 Stats Base

| Stat | Valor Base | Por Nivel | Nivel 100 |
|---|---|---|---|
| **HP** | 900 | +85 | 9325 |
| **Mana** | 450 | +35 | 3850 |
| **HP Regen** | 2.5 | +0.15 | 17.5 |
| **Mana Regen** | 1.8 | +0.12 | 13.8 |
| **Attack Damage** | 48 | +3.8 | 422 |
| **Attack Speed** | 1.3 | +0.02 | 3.3 |
| **Attack Range** | 550 (ranged) | - | - |
| **Defense** | 3 | +0.4 | 43 |
| **Move Speed** | 295 | - | - |
| **STR** | 22 | +2.5 | 272 |
| **AGI** | 18 | +1.8 | 198 |
| **INT** | 28 | +3.2 | 348 |
| **Max Level** | 100 | - | - |

**Primary Attribute**: INT (Inteligencia)

## 🗡️ Habilidades (5)

### Q: Shikai — Benihimo (Sangre Carmesí)

| Campo | Valor |
|---|---|
| **Tipo** | Activa / Direccional |
| **Cooldown** | 8s |
| **Mana Cost** | 80 |
| **Niveles** | 5 (1, 3, 5, 7, 9) |
| **Missile Art** | Abilities\Weapons\BloodElfMissile\BloodElfMissile.mdl |

**Efecto**: Urahara libera su Shikai, disparando una onda de energía
carmesí en línea recta (800 range). Daña a todos los enemigos en el camino
y aplica un debuff de "Sangrado" ( Bleed) por 3 segundos.

**Fórmula de daño**:
```
damage = (INT * 1.5 + 80) * level
bleed_dot = INT * 0.3 per second for 3 seconds
```

| Nivel | Daño Base (INT 28) | Bleed/s |
|---|---|---|
| 1 | 122 | 8.4 |
| 2 | 164 | 8.4 |
| 3 | 206 | 8.4 |
| 4 | 248 | 8.4 |
| 5 | 290 | 8.4 |

---

### W: Nana no Senkū — Tela de Seda

| Campo | Valor |
|---|---|
| **Tipo** | Activa / Área |
| **Cooldown** | 14s |
| **Mana Cost** | 120 |
| **Niveles** | 5 (1, 3, 5, 7, 9) |
| **Art** | Abilities\Spells\Human\Blizzard\BlizzardTarget.mdl |

**Efecto**: Urahara despliega su tela de seda espiritual en un área (350 radius)
alrededor de sí mismo. Los enemigos atrapados son ralentizados un 40% y
silenciados por 2 segundos. Los aliados en el área reciben un escudo
que absorbe daño.

**Fórmulas**:
```
slow_amount = 0.40 (fixed)
silence_duration = 2.0s (fixed)
shield_amount = (INT * 2.0 + 100) * level
shield_duration = 5s
```

| Nivel | Escudo (INT 28) | Rango |
|---|---|---|
| 1 | 156 | 350 |
| 2 | 312 | 350 |
| 3 | 468 | 350 |
| 4 | 624 | 350 |
| 5 | 780 | 350 |

---

### E: Shunpo — Paso Instantáneo

| Campo | Valor |
|---|---|
| **Tipo** | Activa / Movilidad |
| **Cooldown** | 6s |
| **Mana Cost** | 50 |
| **Niveles** | 5 (1, 3, 5, 7, 9) |
| **Art** | Abilities\Spells\Human\StormBolt\StormBoltMissile.mdl |

**Efecto**: Urahara usa Shunpo para teletransportarse instantáneamente
a una posición objetivo (hasta 600 range). Al llegar, deja una ilusión
de sí mismo que dura 2 segundos y explota causando daño en área (250 radius).

**Fórmulas**:
```
teleport_range = 400 + (level * 50)  // 450-600
illusion_damage = (INT * 1.2 + 60) * level
explosion_radius = 250
```

| Nivel | Rango TP | Daño Explosión (INT 28) |
|---|---|---|
| 1 | 450 | 94 |
| 2 | 500 | 188 |
| 3 | 550 | 282 |
| 4 | 600 | 376 |
| 5 | 650 | 470 |

---

### R: Bankai — Kannonbiraki Benihime Aratame (Ultimate)

| Campo | Valor |
|---|---|
| **Tipo** | Activa / Transformación |
| **Cooldown** | 120s |
| **Mana Cost** | 300 |
| **Niveles** | 3 (6, 12, 18) |
| **Duration** | 15s |
| **Art** | Abilities\Spells\Human\Avatar\Avatar.mdl |

**Efecto**: Urahara entra en Bankai. Durante 15 segundos:
- Todas sus habilidades se mejoran
- Gana +50% INT temporal
- Sus ataques básicos causan splash damage (300 radius)
- Shikai (Q) ahora dispara 3 ondas en abanico
- Nana no Senkū (W) ahora afecta área doble (700 radius)
- Shunpo (E) cooldown reducido a 2s

**Stat boost**:
```
int_bonus = INT_base * 0.50
attack_splash_radius = 300
attack_splash_damage = 100% of attack damage
q_extra_projectiles = 2 (3 total in fan pattern)
w_radius_bonus = +350
e_cooldown_override = 2.0s
```

| Nivel | INT Bonus (INT 28) | Splash |
|---|---|---|
| 1 | +14 | 100% |
| 2 | +14 | 100% |
| 3 | +14 | 100% |

---

### D: Kisuke no Hatto — Sombrero y Zuecos (Pasiva)

| Campo | Valor |
|---|---|
| **Tipo** | Pasiva |
| **Niveles** | 5 (1, 3, 5, 7, 9) |

**Efecto**: El icónico sombrero de Urahara le da:
- Reducción de daño mágico
- Evasion chance
- Mana regen bonus

**Fórmulas**:
```
magic_resist = 0.05 + (level * 0.03)  // 8%-20%
evasion_chance = 0.05 + (level * 0.02) // 7%-15%
mana_regen_bonus = 0.5 + (level * 0.3)  // +0.8 to +2.0
```

| Nivel | Resist Mágica | Evasión | Mana Regen+ |
|---|---|---|---|
| 1 | 8% | 7% | +0.8 |
| 2 | 11% | 9% | +1.1 |
| 3 | 14% | 11% | +1.4 |
| 4 | 17% | 13% | +1.7 |
| 5 | 20% | 15% | +2.0 |

## 🎨 Sprites y Recursos

### Modelo 3D
- **Base recomendada**: `Units\Heroes\BloodElfMage\BloodElfMage.mdl`
  (cuerpo humanoide con túnica, similar a Urahara)
- **Modificaciones**: Cambiar textura a colores de Urahara (verde/blanco)
- **Sombrero**: Importar modelo MDX de sombrero de copa
- **Bastón**: Usar modelo de bastón de mago existente

### Icono
- **BTN_Urahara.blp**: Imagen 64×64 BLP de Urahara con sombrero
- **DISBTN_Urahara.blp**: Versión desaturada (disabled)
- **ATC_Urahara.blp**: Icono de ataque

### Efectos visuales
- **Q (Shikai)**: Onda carmesí (modificar BloodElfMissile a color rojo)
- **W (Nana)**: Tela blanca expandiéndose (usar Blizzard target art)
- **E (Shunpo)**: Residual de humo blanco + explosión al llegar
- **R (Bankai)**: Aura roja pulsante + partículas doradas
- **D (Pasiva)**: Brillo sutil en el sombrero

### Sonidos
- **Q**: "Cleave" sound (ya existe en WC3)
- **W**: "Shield" sound (ya existe)
- **E**: "Blink" sound + "Explosion" sound
- **R**: "Avatar" sound (ya existe)
- **Muerte**: "HeroBladeMasterDeath" sound

## 📐 Fórmulas de Crecimiento (JASS)

```jass
// Urahara stat growth per level
function Urahara_GetHP takes integer level returns real
    return 900.0 + (85.0 * (level - 1))
endfunction

function Urahara_GetMana takes integer level returns real
    return 450.0 + (35.0 * (level - 1))
endfunction

function Urahara_GetAttackDamage takes integer level returns real
    return 48.0 + (3.8 * (level - 1))
endfunction

function Urahara_GetSTR takes integer level returns real
    return 22.0 + (2.5 * (level - 1))
endfunction

function Urahara_GetAGI takes integer level returns real
    return 18.0 + (1.8 * (level - 1))
endfunction

function Urahara_GetINT takes integer level returns real
    return 28.0 + (3.2 * (level - 1))
endfunction

// Q: Shikai damage
function Urahara_ShikaiDamage takes unit caster, integer level returns real
    local real intel = GetHeroInt(caster, true)
    return (intel * 1.5 + 80.0) * level
endfunction

// W: Shield amount
function Urahara_ShieldAmount takes unit caster, integer level returns real
    local real intel = GetHeroInt(caster, true)
    return (intel * 2.0 + 100.0) * level
endfunction

// E: Explosion damage
function Urahara_ShunpoDamage takes unit caster, integer level returns real
    local real intel = GetHeroInt(caster, true)
    return (intel * 1.2 + 60.0) * level
endfunction

// R: Bankai INT bonus
function Urahara_BankaiIntBonus takes unit caster returns real
    return GetHeroInt(caster, false) * 0.50
endfunction

// D: Magic resistance
function Urahara_MagicResist takes integer level returns real
    return 0.05 + (level * 0.03)
endfunction
```

## 🎮 Estrategia y Rol

### Early Game (1-10)
- Urahara es un caster INT con buen rango (550)
- **Q (Shikai)** es tu principal fuente de daño: bajo cooldown, buen scaling
- **E (Shunpo)** te da movilidad para escapar ganks y posicionarte
- Farmea con Q + autoattacks

### Mid Game (10-25)
- **W (Nana)** se vuelve crucial en teamfights: silencia + escuda
- Combina E → Q para burst damage (teleport + onda carmesí)
- **D (Pasiva)** te da sustain con mana regen y magic resist

### Late Game (25-100)
- **R (Bankai)** es game-changing: 15s de poder absoluto
- En Bankai: Q dispara 3 ondas, W area doble, E cooldown 2s
- Eres un hyper-caster con movilidad extrema

### Combo Principal
1. **E (Shunpo)** hacia el carry enemigo → explosión + posicionamiento
2. **W (Nana)** → silencia al equipo enemigo + escuda aliados
3. **Q (Shikai)** → daño en línea + bleed
4. Autoattacks durante el silencio
5. **R (Bankai)** si necesitan all-in → Q ×3, E cada 2s

### Counters
- **Silencio**: Urahara depende de sus habilidades
- **Burst físico**: Su HP base es bajo (900 vs 1500 de tanks)
- **Gap closers**: Aunque tiene Shunpo, puede ser atrapado

### Sinergias
- **Con Soi Fon**: W silencia + Soi Fon burst
- **Con Yamamoto**: Ambos INT casters, cubren diferentes áreas
- **Con Ichigo**: Ichigo frontline + Urahara ranged support

## 📁 Archivos a crear en World Editor

### Object Editor
1. **Unidad**: Copiar "BloodElfMage" (Hvsm) → modificar:
   - Name: "Former Captain of 12th Division"
   - Proper Name: "Kisuke Urahara"
   - HP/Mana/STR/AGI/INT según tabla arriba
   - Model: custom Urahara model
   - Icon: BTN_Urahara.blp

2. **Habilidades** (5):
   - Q: Copiar "Breath of Fire" → modificar a skill de proyectil carmesí
   - W: Copiar "Thunder Clap" → modificar a área de silencio+escudo
   - E: Copiar "Blink" → añadir daño de explosión
   - R: Copiar "Avatar" → añadir buffs a Q/W/E
   - D: Pasiva con magic resist + evasion + mana regen

### Trigger Editor (JASS)
- Ver `scripts/urahara_abilities.j` para el código JASS completo

### Import Manager
- `ReplaceableTextures\CommandButtons\BTN_Urahara.blp`
- `ReplaceableTextures\CommandButtonsDisabled\DISBTN_Urahara.blp`
- `units\Urahara\Urahara.mdl` (modelo 3D custom)
- `Abilities\Spells\Urahara\Shikai.mdx` (efecto carmesí)
- `Abilities\Spells\Urahara\Bankai.mdx` (aura dorada)

//=============================================================================
// Gin Ichimaru — Custom Hero for BVO New World 2026
//
// MECÁNICAS: las mismas que usa BVO New World 5.0 (sistema del mapa original)
// EFECTOS/SONIDOS/SPRITES: extraídos del Bleach Kidou Wars 5.00
//
// Lo que se toma del Kidou Wars:
//   - Modelo 3D de Gin Ichimaru (MDX)
//   - Iconos de habilidades (TGA/BLP)
//   - Sonido del Shikai: Gin_Ichimarus_shikai___Shinsou
//   - Efectos visuales: FrostBoltMissile, feralspirit, NewGroundEX, NuclearExplosion
//   - Animaciones del modelo
//
// Lo que NO se toma del Kidou Wars:
//   - Sistema Zanpakuto (item pickup)
//   - KyoukaEffectGroup / FallGroup
//   - A02V/A02W (esas son habilidades del Kidou Wars, no de New World)
//   - Dummy h02F
//
// Las mecánicas son las de BVO New World:
//   - Habilidades Q/W/E/R/D directas (no item pickup)
//   - Stats basados en AGI (como los heroes del mapa original)
//   - Daño calculado con AGI (no con INT como en Kidou Wars)
//   - Sistema de niveles 1-100
//   - Habilidades se aprenden en niveles 1/3/5/7/9 (Q/W/E/D) y 6/12/18 (R)
//=============================================================================

globals
    // IDs de habilidades custom (NO chocan con BVO New World ni Kidou Wars)
    integer ABILITY_GIN_SHINSO    = 'A0GI'  // Q: Shikai Shinso
    integer ABILITY_GIN_YARI      = 'A0GJ'  // W: Yari Perforante
    integer ABILITY_GIN_SHUNPO    = 'A0GK'  // E: Shunpo
    integer ABILITY_GIN_BANKAI    = 'A0GL'  // R: Bankai Kamishini no Yari
    integer ABILITY_GIN_PASSIVE   = 'A0GM'  // D: Sonrisa del Zorro

    integer UNIT_GIN_DUMMY       = 'n0GI'
    integer BUFF_GIN_POISON      = 'B0GI'
    integer BUFF_GIN_INVIS       = 'B0GJ'
    integer BUFF_GIN_BANKAI      = 'B0GK'
    integer BUFF_GIN_ARMOR_RED   = 'B0GL'

    // === EFECTOS VISUALES (del Kidou Wars - solo sprites, no mecánicas) ===
    string EFFECT_SHINSO_PROJECTILE  = "Abilities\\Spells\\Other\\FrostBolt\\FrostBoltMissile.mdl"
    string EFFECT_SHINSO_IMPACT      = "Abilities\\Spells\\Orc\\FeralSpirit\\feralspirittarget.mdl"
    string EFFECT_GROUND             = "war3mapImported\\NewGroundEX.mdx"
    string EFFECT_EXPLOSION          = "war3mapImported\\NuclearExplosion.mdx"
    string EFFECT_DISSIPATE          = "Objects\\Spawnmodels\\Undead\\UndeadDissipate\\UndeadDissipate.mdl"
    string EFFECT_DEATH_COIL          = "Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl"

    // Efectos WC3 base para habilidades que no tienen equivalente en Kidou Wars
    string EFFECT_YARI               = "Abilities\\Spells\\Human\\MarkOfChaos\\MarkOfChaosTarget.mdl"
    string EFFECT_SHUNPO_SMOKE       = "Abilities\\Spells\\Human\\CloudOfFog\\CloudOfFog.mdl"
    string EFFECT_BANKAI_AURA        = "Abilities\\Spells\\Human\\Avatar\\Avatar.mdl"
    string EFFECT_CRIT               = "Abilities\\Spells\\Other\\HowlOfTerror\\HowlOfTerror.mdl"

    hashtable Gin_Hash = InitHashtable()
endglobals

//=============================================================================
// STATS (mecánicas BVO New World: AGI-based assassin)
//=============================================================================
function Gin_GetHP takes integer lvl returns real
    return 850.0 + 75.0 * I2R(lvl - 1)
endfunction
function Gin_GetMana takes integer lvl returns real
    return 350.0 + 28.0 * I2R(lvl - 1)
endfunction
function Gin_GetAGI takes integer lvl returns real
    return 30.0 + 3.5 * I2R(lvl - 1)
endfunction

// Q: Shinso damage (scales con AGI, mecánica de BVO New World)
function Gin_ShinsoDmg takes unit c returns real
    return GetHeroAgi(c, true) * 2.0 + 70.0
endfunction
function Gin_ShinsoRange takes integer lvl returns real
    return 700.0 + I2R(lvl) * 100.0  // 800-1200
endfunction

// W: Yari
function Gin_YariDmg takes unit c, integer lvl returns real
    return (GetHeroAgi(c, true) * 1.8 + 50.0) * I2R(lvl)
endfunction

// E: Shunpo
function Gin_ShunpoDur takes integer lvl returns real
    return 2.0 + I2R(lvl) * 0.5  // 2.5-4.5s
endfunction
function Gin_ShunpoCrit takes integer lvl returns real
    return 2.0 + I2R(lvl) * 0.3  // 2.3x-3.5x
endfunction
function Gin_ShunpoPoison takes unit c returns real
    return GetHeroAgi(c, true) * 0.5
endfunction

// R: Bankai
function Gin_BankaiAgiBonus takes unit c returns real
    return GetHeroAgi(c, false) * 0.40
endfunction

// D: Pasiva
function Gin_CritChance takes integer lvl returns real
    return 0.05 + I2R(lvl) * 0.03  // 8-20%
endfunction
function Gin_CritDmg takes integer lvl returns real
    return 1.5 + I2R(lvl) * 0.1  // 1.6x-2.0x
endfunction
function Gin_SpellVamp takes integer lvl returns real
    return 0.05 + I2R(lvl) * 0.02  // 7-15%
endfunction

//=============================================================================
// Q: SHIKAI — SHINSO
// Mecánica BVO New World: habilidad directa (no item pickup)
// Sprite del Kidou Wars: FrostBoltMissile + feralspirit + NewGroundEX
//=============================================================================
function Gin_Shinso_Cond takes nothing returns boolean
    return GetSpellAbilityId() == ABILITY_GIN_SHINSO
endfunction

function Gin_Shinso_Act takes nothing returns nothing
    local unit c = GetTriggerUnit()
    local integer lvl = GetUnitAbilityLevel(c, ABILITY_GIN_SHINSO)
    local real dmg = Gin_ShinsoDmg(c)
    local real r = Gin_ShinsoRange(lvl)
    local real cx = GetUnitX(c)
    local real cy = GetUnitY(c)
    local location t = GetSpellTargetLoc()
    local real tx = GetLocationX(t)
    local real ty = GetLocationY(t)
    local real ang = Atan2(ty - cy, tx - cx)
    local group g = CreateGroup()
    local unit u
    local real ux, uy, dist, uang, perp
    local boolean bankai = GetUnitAbilityLevel(c, BUFF_GIN_BANKAI) > 0

    // --- EFECTOS VISUALES (sprites del Kidou Wars) ---
    // Proyectil de Shinso (FrostBoltMissile del Kidou Wars)
    call DestroyEffect(AddSpecialEffect(EFFECT_SHINSO_PROJECTILE, cx, cy))
    // Efecto de suelo (NewGroundEX del Kidou Wars)
    call DestroyEffect(AddSpecialEffect(EFFECT_GROUND, cx, cy))

    // --- DAÑO EN LÍNEA (mecánica BVO New World) ---
    call GroupEnumUnitsInRange(g, cx, cy, r, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if IsUnitEnemy(u, GetOwningPlayer(c)) and not IsUnitType(u, UNIT_TYPE_DEAD) then
            set ux = GetUnitX(u)
            set uy = GetUnitY(u)
            set dist = SquareRoot((ux-cx)*(ux-cx) + (uy-cy)*(uy-cy))
            if dist <= r then
                set uang = Atan2(uy - cy, ux - cx)
                set perp = ang - uang
                if perp > 3.14159 then
                    set perp = perp - 6.28318
                elseif perp < -3.14159 then
                    set perp = perp + 6.28318
                endif
                if Abs(perp) < 0.2618 then  // ±15 grados
                    call UnitDamageTarget(c, u, dmg, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_NORMAL, WEAPON_TYPE_WHOKNOWS)
                    // Impacto (feralspirit del Kidou Wars)
                    call DestroyEffect(AddSpecialEffectTarget(EFFECT_SHINSO_IMPACT, u, "chest"))
                    // Knockback (mecánica BVO New World)
                    call SetUnitPosition(u, ux + 100 * Cos(uang), uy + 100 * Sin(uang))
                    // En Bankai: atraviesa a todos (mecánica BVO New World)
                    if not bankai then
                        call GroupClear(g)
                    endif
                endif
            endif
        endif
    endloop

    call RemoveLocation(t)
    call DestroyGroup(g)
    set c = null
    set t = null
    set g = null
endfunction

//=============================================================================
// W: YARI PERFORANTE
// Mecánica BVO New World: línea 1200, atraviesa, reduce armor
// Sprite: MarkOfChaos + NewGroundEX
//=============================================================================
function Gin_Yari_Cond takes nothing returns boolean
    return GetSpellAbilityId() == ABILITY_GIN_YARI
endfunction

function Gin_Yari_Act takes nothing returns nothing
    local unit c = GetTriggerUnit()
    local integer lvl = GetUnitAbilityLevel(c, ABILITY_GIN_YARI)
    local real dmg = Gin_YariDmg(c, lvl)
    local real cx = GetUnitX(c)
    local real cy = GetUnitY(c)
    local location t = GetSpellTargetLoc()
    local real tx = GetLocationX(t)
    local real ty = GetLocationY(t)
    local real ang = Atan2(ty - cy, tx - cx)
    local group g = CreateGroup()
    local unit u
    local real ux, uy, dist, uang, perp

    call DestroyEffect(AddSpecialEffect(EFFECT_YARI, cx, cy))
    call DestroyEffect(AddSpecialEffect(EFFECT_GROUND, cx, cy))

    call GroupEnumUnitsInRange(g, cx, cy, 1200.0, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if IsUnitEnemy(u, GetOwningPlayer(c)) and not IsUnitType(u, UNIT_TYPE_DEAD) then
            set ux = GetUnitX(u)
            set uy = GetUnitY(u)
            set dist = SquareRoot((ux-cx)*(ux-cx) + (uy-cy)*(uy-cy))
            set uang = Atan2(uy - cy, ux - cx)
            set perp = ang - uang
            if perp > 3.14159 then
                set perp = perp - 6.28318
            elseif perp < -3.14159 then
                set perp = perp + 6.28318
            endif
            if dist <= 1200.0 and Abs(perp) < 0.1309 then  // ±7.5 grados
                call UnitDamageTarget(c, u, dmg, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_NORMAL, WEAPON_TYPE_WHOKNOWS)
                call UnitApplyTimedLife(u, BUFF_GIN_ARMOR_RED, 5.0)
                call DestroyEffect(AddSpecialEffectTarget(EFFECT_CRIT, u, "chest"))
            endif
        endif
    endloop

    call RemoveLocation(t)
    call DestroyGroup(g)
    set c = null
    set t = null
    set g = null
endfunction

//=============================================================================
// E: SHUNPO — SONRISA SINIESTRA
// Mecánica BVO New World: invisibilidad + crit garantizado + veneno
// Sprite: CloudOfFog (humo)
//=============================================================================
function Gin_Shunpo_Cond takes nothing returns boolean
    return GetSpellAbilityId() == ABILITY_GIN_SHUNPO
endfunction

function Gin_Shunpo_Act takes nothing returns nothing
    local unit c = GetTriggerUnit()
    local integer lvl = GetUnitAbilityLevel(c, ABILITY_GIN_SHUNPO)
    local real dur = Gin_ShunpoDur(lvl)
    local real crit = Gin_ShunpoCrit(lvl)

    call UnitApplyTimedLife(c, BUFF_GIN_INVIS, dur)
    call SaveReal(Gin_Hash, GetHandleId(c), 10, crit)
    call SaveBoolean(Gin_Hash, GetHandleId(c), 11, true)

    // Humo (efecto WC3)
    call DestroyEffect(AddSpecialEffectTarget(EFFECT_SHUNPO_SMOKE, c, "origin"))

    call TimerStart(CreateTimer(), dur, false, function Gin_Shunpo_End)
    call SaveUnitHandle(Gin_Hash, GetHandleId(GetExpiredTimer()), 0, c)
    set c = null
endfunction

function Gin_Shunpo_End takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local unit c = LoadUnitHandle(Gin_Hash, GetHandleId(tm), 0)
    if c != null then
        call SaveBoolean(Gin_Hash, GetHandleId(c), 11, false)
        call FlushChildHashtable(Gin_Hash, GetHandleId(tm))
    endif
    call DestroyTimer(tm)
    set tm = null
    set c = null
endfunction

function Gin_PoisonApply takes unit c, unit t returns nothing
    call UnitApplyTimedLife(t, BUFF_GIN_POISON, 4.0)
    call SetUnitMoveSpeed(t, GetUnitMoveSpeed(t) * 0.70)
    call TimerStart(CreateTimer(), 4.0, false, function Gin_Poison_End)
    call SaveUnitHandle(Gin_Hash, GetHandleId(GetExpiredTimer()), 0, t)
endfunction

function Gin_Poison_End takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local unit u = LoadUnitHandle(Gin_Hash, GetHandleId(tm), 0)
    if u != null then
        call SetUnitMoveSpeed(u, GetUnitDefaultMoveSpeed(u))
    endif
    call FlushChildHashtable(Gin_Hash, GetHandleId(tm))
    call DestroyTimer(tm)
    set tm = null
    set u = null
endfunction

//=============================================================================
// R: BANKAI — KAMISHINI NO YARI
// Mecánica BVO New World: transformación 12s
// Sprite: Avatar (aura) + NuclearExplosion (activación)
//=============================================================================
function Gin_Bankai_Cond takes nothing returns boolean
    return GetSpellAbilityId() == ABILITY_GIN_BANKAI
endfunction

function Gin_Bankai_Act takes nothing returns nothing
    local unit c = GetTriggerUnit()
    local real bonus = Gin_BankaiAgiBonus(c)
    local effect aura

    call UnitApplyTimedLife(c, BUFF_GIN_BANKAI, 12.0)
    call SetHeroAgi(c, R2I(GetHeroAgi(c, false) + bonus), true)

    // Aura (Avatar del WC3)
    set aura = AddSpecialEffectTarget(EFFECT_BANKAI_AURA, c, "origin")
    // Explosión al activar (NuclearExplosion del Kidou Wars)
    call DestroyEffect(AddSpecialEffect(EFFECT_EXPLOSION, GetUnitX(c), GetUnitY(c)))

    call TimerStart(CreateTimer(), 12.0, false, function Gin_Bankai_End)
    call SaveUnitHandle(Gin_Hash, GetHandleId(GetExpiredTimer()), 0, c)
    call SaveEffectHandle(Gin_Hash, GetHandleId(GetExpiredTimer()), 1, aura)
    call SaveReal(Gin_Hash, GetHandleId(GetExpiredTimer()), 2, bonus)

    set c = null
    set aura = null
endfunction

function Gin_Bankai_End takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local integer id = GetHandleId(tm)
    local unit c = LoadUnitHandle(Gin_Hash, id, 0)
    local effect aura = LoadEffectHandle(Gin_Hash, id, 1)
    local real bonus = LoadReal(Gin_Hash, id, 2)

    if c != null then
        call SetHeroAgi(c, R2I(GetHeroAgi(c, false) - bonus), true)
        call UnitRemoveAbility(c, BUFF_GIN_BANKAI)
    endif
    if aura != null then
        call DestroyEffect(aura)
    endif
    call FlushChildHashtable(Gin_Hash, id)
    call DestroyTimer(tm)
    set tm = null
    set c = null
    set aura = null
endfunction

//=============================================================================
// D: SONRISA DEL ZORRO (Pasiva)
// Mecánica BVO New World: crit + speed + spell vamp
//=============================================================================
function Gin_Passive_Attack takes nothing returns nothing
    local unit attacker = GetEventDamageSource()
    local unit target = GetTriggerUnit()
    local integer lvl

    if GetUnitAbilityLevel(attacker, ABILITY_GIN_PASSIVE) > 0 then
        set lvl = GetUnitAbilityLevel(attacker, ABILITY_GIN_PASSIVE)
        // Crit chance (mecánica BVO New World)
        if GetRandomReal(0.0, 1.0) <= Gin_CritChance(lvl) then
            call UnitDamageTarget(attacker, target, GetEventDamage() * (Gin_CritDmg(lvl) - 1.0), false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_NORMAL, WEAPON_TYPE_WHOKNOWS)
            call DestroyEffect(AddSpecialEffectTarget(EFFECT_CRIT, target, "chest"))
        endif
        // Crit garantizado desde invisibilidad (mecánica BVO New World)
        if LoadBoolean(Gin_Hash, GetHandleId(attacker), 11) then
            call UnitDamageTarget(attacker, target, GetEventDamage() * (LoadReal(Gin_Hash, GetHandleId(attacker), 10) - 1.0), false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_NORMAL, WEAPON_TYPE_WHOKNOWS)
            call Gin_PoisonApply(attacker, target)
            call SaveBoolean(Gin_Hash, GetHandleId(attacker), 11, false)
        endif
    endif
    set attacker = null
    set target = null
endfunction

function Gin_Passive_SpellVamp takes nothing returns nothing
    local unit c = GetEventDamageSource()
    local integer lvl
    local real heal

    if GetUnitAbilityLevel(c, ABILITY_GIN_PASSIVE) > 0 then
        set lvl = GetUnitAbilityLevel(c, ABILITY_GIN_PASSIVE)
        set heal = GetEventDamage() * Gin_SpellVamp(lvl)
        call SetUnitState(c, UNIT_STATE_LIFE, GetUnitState(c, UNIT_STATE_LIFE) + heal)
    endif
    set c = null
endfunction

function Gin_Passive_Speed takes nothing returns nothing
    local unit c = GetEnumUnit()
    local integer lvl = GetUnitAbilityLevel(c, ABILITY_GIN_PASSIVE)
    if lvl > 0 then
        call SetUnitMoveSpeed(c, GetUnitDefaultMoveSpeed(c) + 10.0 + I2R(lvl) * 5.0)
    endif
    set c = null
endfunction

function Gin_Passive_Periodic takes nothing returns nothing
    local group g = CreateGroup()
    call GroupEnumUnitsOfType(g, "hero", null)
    call ForGroup(g, function Gin_Passive_Speed)
    call DestroyGroup(g)
    set g = null
endfunction

//=============================================================================
// INICIALIZACIÓN (mecánica BVO New World: triggers directos)
//=============================================================================
function InitGin takes nothing returns nothing
    local trigger t

    // Q: Shinso (habilidad directa, no item pickup)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Gin_Shinso_Cond))
    call TriggerAddAction(t, function Gin_Shinso_Act)

    // W: Yari
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Gin_Yari_Cond))
    call TriggerAddAction(t, function Gin_Yari_Act)

    // E: Shunpo
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Gin_Shunpo_Cond))
    call TriggerAddAction(t, function Gin_Shunpo_Act)

    // R: Bankai
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Gin_Bankai_Cond))
    call TriggerAddAction(t, function Gin_Bankai_Act)

    // D: Pasiva — crit + spell vamp
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DAMAGED)
    call TriggerAddAction(t, function Gin_Passive_Attack)

    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DAMAGED)
    call TriggerAddAction(t, function Gin_Passive_SpellVamp)

    // D: Pasiva — speed (periodic)
    set t = CreateTrigger()
    call TriggerRegisterTimerEventPeriodic(t, 1.0)
    call TriggerAddAction(t, function Gin_Passive_Periodic)
endfunction

// call InitGin()

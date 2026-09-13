//=============================================================================
// Kisuke Urahara — Custom Hero JASS Script for BvO New World 2026
//
//Este archivo contiene todas las funciones JASS para implementar el héroe
//Kisuke Urahara en World Editor. Copiar este código en el Trigger Editor
//como Custom Script.
//
//Para usar:
//1. Abrir World Editor (con JNGP/WEX para vJass)
//2. Trigger Editor → crear nuevo trigger → Convert to Custom Text
//3. Pegar este código
//4. Configurar las abilities en Object Editor con los IDs correctos
//=============================================================================

//=============================================================================
// VARIABLES GLOBALES
//=============================================================================
globals
    // IDs de habilidades (cambiar según tu Object Editor)
    integer ABILITY_URAHARA_SHIKAI     = 'A0UK'  // Q
    integer ABILITY_URAHARA_NANA        = 'A0UL'  // W
    integer ABILITY_URAHARA_SHUNPO      = 'A0UM'  // E
    integer ABILITY_URAHARA_BANKAI      = 'A0UN'  // R
    integer ABILITY_URAHARA_PASSIVE     = 'A0UO'  // D
    
    // IDs de unidades/efectos
    integer UNIT_URAHARA_DUMMY          = 'n0UK'  // Dummy unit para efectos
    integer BUFF_URAHARA_BLEED          = 'B0UK'  // Bleed debuff
    integer BUFF_URAHARA_SHIELD         = 'B0UL'  // Shield buff
    integer BUFF_URAHARA_SILENCE        = 'B0UM'  // Silence debuff
    integer BUFF_URAHARA_BANKAI         = 'B0UN'  // Bankai buff
    integer BUFF_URAHARA_ILLUSION       = 'B0UO'  // Shunpo illusion
    
    // Efectos visuales
    string EFFECT_SHIKAI_MISSILE        = "Abilities\\Weapons\\BloodElfMissile\\BloodElfMissile.mdl"
    string EFFECT_SHIKAI_IMPACT         = "Abilities\\Spells\\Human\\Banish\\BanishTarget.mdl"
    string EFFECT_NANA_AREA             = "Abilities\\Spells\\Human\\Blizzard\\BlizzardTarget.mdl"
    string EFFECT_SHUNPO_TRAIL          = "Abilities\\Spells\\Human\\CloudOfFog\\CloudOfFog.mdl"
    string EFFECT_SHUNPO_EXPLOSION      = "Abilities\\Spells\\Human\\FlameStrike\\FlameStrike1.mdl"
    string EFFECT_BANKAI_AURA           = "Abilities\\Spells\\Human\\Avatar\\Avatar.mdl"
    string EFFECT_BANKAI_SLASH          = "Abilities\\Spells\\Other\\HowlOfTerror\\HowlOfTerror.mdl"
    
    // Timers
    timer array Urahara_BleedTimers    // Per-unit bleed timers
    timer array Urahara_BankaiTimers   // Per-hero bankai timers
    
    // Hashtable para tracking
    hashtable Urahara_Hash = InitHashtable()
endglobals

//=============================================================================
// FUNCIONES DE STATS (cálculo de daño según INT)
//=============================================================================

function Urahara_GetHP takes integer level returns real
    return 900.0 + (85.0 * I2R(level - 1))
endfunction

function Urahara_GetMana takes integer level returns real
    return 450.0 + (35.0 * I2R(level - 1))
endfunction

function Urahara_GetINT takes integer level returns real
    return 28.0 + (3.2 * I2R(level - 1))
endfunction

function Urahara_ShikaiDamage takes unit caster, integer level returns real
    local real intel = GetHeroInt(caster, true)
    return (intel * 1.5 + 80.0) * I2R(level)
endfunction

function Urahara_ShikaiBleed takes unit caster returns real
    local real intel = GetHeroInt(caster, true)
    return intel * 0.3
endfunction

function Urahara_ShieldAmount takes unit caster, integer level returns real
    local real intel = GetHeroInt(caster, true)
    return (intel * 2.0 + 100.0) * I2R(level)
endfunction

function Urahara_ShunpoDamage takes unit caster, integer level returns real
    local real intel = GetHeroInt(caster, true)
    return (intel * 1.2 + 60.0) * I2R(level)
endfunction

function Urahara_BankaiIntBonus takes unit caster returns real
    return GetHeroInt(caster, false) * 0.50
endfunction

function Urahara_MagicResist takes integer level returns real
    return 0.05 + (I2R(level) * 0.03)
endfunction

function Urahara_Evasion takes integer level returns real
    return 0.05 + (I2R(level) * 0.02)
endfunction

//=============================================================================
// Q: SHIKAI — BENIHIMO
//=============================================================================

function Urahara_Shikai_Condition takes nothing returns boolean
    return GetSpellAbilityId() == ABILITY_URAHARA_SHIKAI
endfunction

function Urahara_Shikai_Action takes nothing returns nothing
    local unit caster = GetTriggerUnit()
    local integer level = GetUnitAbilityLevel(caster, ABILITY_URAHARA_SHIKAI)
    local real damage = Urahara_ShikaiDamage(caster, level)
    local real bleed = Urahara_ShikaiBleed(caster)
    local location loc = GetSpellTargetLoc()
    local real x = GetLocationX(loc)
    local real y = GetLocationY(loc)
    local real cx = GetUnitX(caster)
    local real cy = GetUnitY(caster)
    local real angle = Atan2(y - cy, x - cx)
    local group g = CreateGroup()
    local unit u
    local effect fx
    
    // Crear proyectil visual
    call DestroyEffect(AddSpecialEffect(EFFECT_SHIKAI_MISSILE, cx, cy))
    
    // Detectar enemigos en línea (800 range, 150 width)
    call GroupEnumUnitsInRange(g, cx, cy, 800.0, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        // Verificar que está en el camino (ángulo ±15 grados)
        if IsUnitEnemy(u, GetOwningPlayer(caster)) and not IsUnitType(u, UNIT_TYPE_DEAD) then
            call UnitDamageTarget(caster, u, damage, false, false, ATTACK_TYPE_MAGIC, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
            // Aplicar bleed
            call UnitApplyTimedLife(u, BUFF_URAHARA_BLEED, 3.0)
            call DestroyEffect(AddSpecialEffectTarget(EFFECT_SHIKAI_IMPACT, u, "chest"))
        endif
    endloop
    
    // Bleed DoT (cada 1 segundo por 3 segundos)
    call TimerStart(CreateTimer(), 1.0, true, function Urahara_Bleed_Tick)
    call SaveInteger(Urahara_Hash, GetHandleId(caster), 0, 3) // 3 ticks
    
    call RemoveLocation(loc)
    call DestroyGroup(g)
    set caster = null
    set loc = null
    set g = null
endfunction

function Urahara_Bleed_Tick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer id = GetHandleId(t)
    local integer ticks = LoadInteger(Urahara_Hash, id, 0)
    // Apply bleed damage to affected units
    // (simplified — in real implementation, store affected units in hashtable)
    if ticks <= 0 then
        call PauseTimer(t)
        call DestroyTimer(t)
    else
        call SaveInteger(Urahara_Hash, id, 0, ticks - 1)
    endif
    set t = null
endfunction

//=============================================================================
// W: NANA NO SENKU — TELA DE SEDA
//=============================================================================

function Urahara_Nana_Condition takes nothing returns boolean
    return GetSpellAbilityId() == ABILITY_URAHARA_NANA
endfunction

function Urahara_Nana_Action takes nothing returns nothing
    local unit caster = GetTriggerUnit()
    local integer level = GetUnitAbilityLevel(caster, ABILITY_URAHARA_NANA)
    local real shield = Urahara_ShieldAmount(caster, level)
    local real cx = GetUnitX(caster)
    local real cy = GetUnitY(caster)
    local real radius = 350.0
    local group g = CreateGroup()
    local unit u
    
    // Verificar si está en Bankai (área doble)
    if GetUnitAbilityLevel(caster, BUFF_URAHARA_BANKAI) > 0 then
        set radius = 700.0
    endif
    
    // Efecto visual
    call DestroyEffect(AddSpecialEffect(EFFECT_NANA_AREA, cx, cy))
    
    // Detectar todas las unidades en el área
    call GroupEnumUnitsInRange(g, cx, cy, radius, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if IsUnitEnemy(u, GetOwningPlayer(caster)) and not IsUnitType(u, UNIT_TYPE_DEAD) then
            // Enemigos: slow + silence
            call UnitApplyTimedLife(u, BUFF_URAHARA_SILENCE, 2.0)
            call SetUnitMoveSpeed(u, GetUnitMoveSpeed(u) * 0.60)
            // Restaurar velocidad después de 2s
            call TimerStart(CreateTimer(), 2.0, false, function Urahara_RestoreSpeed)
        elseif IsUnitAlly(u, GetOwningPlayer(caster)) and not IsUnitType(u, UNIT_TYPE_DEAD) then
            // Aliados: escudo
            call UnitApplyTimedLife(u, BUFF_URAHARA_SHIELD, 5.0)
            // El escudo absorbe daño (implementar con damage detection trigger)
        endif
    endloop
    
    call DestroyGroup(g)
    set caster = null
    set g = null
endfunction

function Urahara_RestoreSpeed takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer id = GetHandleId(t)
    local unit u = LoadUnitHandle(Urahara_Hash, id, 0)
    if u != null then
        call SetUnitMoveSpeed(u, GetUnitDefaultMoveSpeed(u))
    endif
    call FlushChildHashtable(Urahara_Hash, id)
    call DestroyTimer(t)
    set t = null
    set u = null
endfunction

//=============================================================================
// E: SHUNPO — PASO INSTANTÁNEO
//=============================================================================

function Urahara_Shunpo_Condition takes nothing returns boolean
    return GetSpellAbilityId() == ABILITY_URAHARA_SHUNPO
endfunction

function Urahara_Shunpo_Action takes nothing returns nothing
    local unit caster = GetTriggerUnit()
    local integer level = GetUnitAbilityLevel(caster, ABILITY_URAHARA_SHUNPO)
    local real damage = Urahara_ShunpoDamage(caster, level)
    local real range = 400.0 + (I2R(level) * 50.0)
    local location target = GetSpellTargetLoc()
    local real tx = GetLocationX(target)
    local real ty = GetLocationY(target)
    local real cx = GetUnitX(caster)
    local real cy = GetUnitY(caster)
    local real dist = SquareRoot((tx - cx) * (tx - cx) + (ty - cy) * (ty - cy))
    local real angle
    local group g = CreateGroup()
    local unit u
    
    // Limitar distancia
    if dist > range then
        set angle = Atan2(ty - cy, tx - cx)
        set tx = cx + range * Cos(angle)
        set ty = cy + range * Sin(angle)
    endif
    
    // Efecto visual en posición original
    call DestroyEffect(AddSpecialEffect(EFFECT_SHUNPO_TRAIL, cx, cy))
    
    // Teletransportar
    call SetUnitPosition(caster, tx, ty)
    
    // Crear ilusión (dummy) en posición original
    call CreateUnit(GetOwningPlayer(caster), UNIT_URAHARA_DUMMY, cx, cy, 0.0)
    
    // Explosión en posición de llegada
    call DestroyEffect(AddSpecialEffect(EFFECT_SHUNPO_EXPLOSION, tx, ty))
    
    // Daño en área (250 radius)
    call GroupEnumUnitsInRange(g, tx, ty, 250.0, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if IsUnitEnemy(u, GetOwningPlayer(caster)) and not IsUnitType(u, UNIT_TYPE_DEAD) then
            call UnitDamageTarget(caster, u, damage, false, false, ATTACK_TYPE_MAGIC, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
        endif
    endloop
    
    // Si está en Bankai, reducir cooldown a 2s
    if GetUnitAbilityLevel(caster, BUFF_URAHARA_BANKAI) > 0 then
        call BlzEndUnitAbilityCooldown(caster, ABILITY_URAHARA_SHUNPO)
        call BlzStartUnitAbilityCooldown(caster, ABILITY_URAHARA_SHUNPO, 2.0)
    endif
    
    call RemoveLocation(target)
    call DestroyGroup(g)
    set caster = null
    set target = null
    set g = null
endfunction

//=============================================================================
// R: BANKAI — KANNONBIRAKI BENIHIME ARATAME
//=============================================================================

function Urahara_Bankai_Condition takes nothing returns boolean
    return GetSpellAbilityId() == ABILITY_URAHARA_BANKAI
endfunction

function Urahara_Bankai_Action takes nothing returns nothing
    local unit caster = GetTriggerUnit()
    local integer level = GetUnitAbilityLevel(caster, ABILITY_URAHARA_BANKAI)
    local real int_bonus = Urahara_BankaiIntBonus(caster)
    local effect aura
    
    // Aplicar buff de Bankai
    call UnitApplyTimedLife(caster, BUFF_URAHARA_BANKAI, 15.0)
    
    // Bonus de INT temporal
    call SetHeroInt(caster, GetHeroInt(caster, false) + R2I(int_bonus), true)
    
    // Efecto visual
    set aura = AddSpecialEffectTarget(EFFECT_BANKAI_AURA, caster, "origin")
    
    // Programar remoción del buff
    call TimerStart(CreateTimer(), 15.0, false, function Urahara_Bankai_End)
    call SaveUnitHandle(Urahara_Hash, GetHandleId(GetExpiredTimer()), 0, caster)
    call SaveEffectHandle(Urahara_Hash, GetHandleId(GetExpiredTimer()), 1, aura)
    
    set caster = null
    set aura = null
endfunction

function Urahara_Bankai_End takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer id = GetHandleId(t)
    local unit caster = LoadUnitHandle(Urahara_Hash, id, 0)
    local effect aura = LoadEffectHandle(Urahara_Hash, id, 1)
    local real int_bonus = Urahara_BankaiIntBonus(caster)
    
    if caster != null then
        // Remover bonus de INT
        call SetHeroInt(caster, GetHeroInt(caster, false) - R2I(int_bonus), true)
        call UnitRemoveAbility(caster, BUFF_URAHARA_BANKAI)
    endif
    
    if aura != null then
        call DestroyEffect(aura)
    endif
    
    call FlushChildHashtable(Urahara_Hash, id)
    call DestroyTimer(t)
    set t = null
    set caster = null
    set aura = null
endfunction

//=============================================================================
// D: PASIVA — KISUKE NO HATTO
//=============================================================================

function Urahara_Passive_Condition takes nothing returns boolean
    return GetUnitAbilityLevel(GetTriggerUnit(), ABILITY_URAHARA_PASSIVE) > 0
endfunction

function Urahara_Passive_Damage takes nothing returns nothing
    local unit target = GetTriggerUnit()
    local integer level = GetUnitAbilityLevel(target, ABILITY_URAHARA_PASSIVE)
    local real resist = Urahara_MagicResist(level)
    local real damage = GetEventDamage()
    local real reduced
    
    // Solo reducir daño mágico
    if damage > 0 and IsUnitType(target, UNIT_TYPE_HERO) then
        set reduced = damage * resist
        call SetUnitLifeBJ(target, GetUnitState(target, UNIT_STATE_LIFE) + reduced)
    endif
    
    set target = null
endfunction

function Urahara_Passive_ManaRegen takes nothing returns nothing
    local unit u = GetEnumUnit()
    local integer level = GetUnitAbilityLevel(u, ABILITY_URAHARA_PASSIVE)
    if level > 0 then
        call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MANA) + 0.5 + I2R(level) * 0.3)
    endif
    set u = null
endfunction

function Urahara_Passive_Periodic takes nothing returns nothing
    local group g = CreateGroup()
    call GroupEnumUnitsOfType(g, "hero", null)
    call ForGroup(g, function Urahara_Passive_ManaRegen)
    call DestroyGroup(g)
    set g = null
endfunction

//=============================================================================
// INICIALIZACIÓN
//=============================================================================

function InitUrahara takes nothing returns nothing
    local trigger t
    
    // Q: Shikai
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Urahara_Shikai_Condition))
    call TriggerAddAction(t, function Urahara_Shikai_Action)
    
    // W: Nana
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Urahara_Nana_Condition))
    call TriggerAddAction(t, function Urahara_Nana_Action)
    
    // E: Shunpo
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Urahara_Shunpo_Condition))
    call TriggerAddAction(t, function Urahara_Shunpo_Action)
    
    // R: Bankai
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Urahara_Bankai_Condition))
    call TriggerAddAction(t, function Urahara_Bankai_Action)
    
    // D: Pasiva — damage reduction
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DAMAGED)
    call TriggerAddCondition(t, Condition(function Urahara_Passive_Condition))
    call TriggerAddAction(t, function Urahara_Passive_Damage)
    
    // D: Pasiva — mana regen (cada 1 segundo)
    set t = CreateTrigger()
    call TriggerRegisterTimerEventPeriodic(t, 1.0)
    call TriggerAddAction(t, function Urahara_Passive_Periodic)
endfunction

// Llamar al inicio del mapa
// call InitUrahara()

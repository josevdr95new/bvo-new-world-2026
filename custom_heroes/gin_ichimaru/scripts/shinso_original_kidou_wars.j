//=============================================================================
// Shinso Trigger — Extracted from Bleach Kidou Wars 5.00
// Original map: https://www.hiveworkshop.com/threads/bleach-kidou-wars-5-00.142486/
//
// This is the ORIGINAL code from the Bleach Kidou Wars map.
// It shows how Gin Ichimaru's Shinso ability was implemented.
//
// Key findings:
// - Item 'I013' activates the Shinso ability
// - Sound: gg_snd_Gin_Ichimarus_shikai___Shinsou
// - Abilities granted: 'A02V' and 'A02W'
// - Creates a dummy projectile unit
// - Adds the unit to KyoukaEffectGroup and FallGroup
// - Creates a text tag at the location (TRIGSTR_1582)
//=============================================================================

//===========================================================================
// Trigger: Shinso
//===========================================================================
function Trig_Shinso_Conditions takes nothing returns boolean
    if ( not ( GetItemTypeId(GetManipulatedItem()) == 'I013' ) ) then
        return false
    endif
    return true
endfunction

// The Actions function is referenced but appears to be in a shared
// trigger system. From the code found in war3map.j:
//
// When Shinso is activated:
// 1. A dummy projectile is created at TempLoc1
// 2. The dummy has a 3-second timed life (BTLF)
// 3. Sound "Gin_Ichimarus_shikai___Shinsou" plays at the location
// 4. Abilities A02V and A02W are added to the ZanCaster unit
// 5. The ZanCaster is added to KyoukaEffectGroup and FallGroup
// 6. A text tag (TRIGSTR_1582) is created at the location
//
// The actual damage/effect code is likely in the shared Zanpakuto
// system that handles all Shikai releases in the Bleach Kidou Wars map.

// Extracted action code (from war3map.j, shared trigger):
/*
    set udg_TempDummyProjectile = GetLastCreatedUnit()
    call UnitApplyTimedLifeBJ( 3.00, 'BTLF', udg_TempDummyProjectile )
    call PlaySoundAtPointBJ( gg_snd_Gin_Ichimarus_shikai___Shinsou, 100, udg_TempLoc1, 0 )
    call UnitAddAbilityBJ( 'A02V', udg_ZanCaster )
    call UnitAddAbilityBJ( 'A02W', udg_ZanCaster )
    call GroupAddUnitSimple( udg_ZanCaster, udg_KyoukaEffectGroup )
    call GroupAddUnitSimple( udg_ZanCaster, udg_FallGroup )
    call CreateTextTagLocBJ( "TRIGSTR_1582", udg_TempLoc1, 0, 10, 100, 100, 100, 0 )
    set udg_TempText = GetLastCreatedTextTag()
*/

// Also found: InitTrig_Gintei() is called in the init sequence
// "Gintei" appears to be a separate trigger for Gin's movement or teleport

//===========================================================================
// RESOURCE IDs FROM BLEACH KIDOU WARS:
//===========================================================================
// Item ID:  'I013' = Shinso activation item
// Ability:  'A02V' = Shinso ability 1 (likely the extension attack)
// Ability:  'A02W' = Shinso ability 2 (likely the retract/pull)
// Sound:    gg_snd_Gin_Ichimarus_shikai___Shinsou
// Trigger:  Shinso (conditions + shared actions)
// Trigger:  Gintei (separate Gin trigger, likely movement)
//
// The map uses a shared "Zanpakuto" system where each character's
// Shikai/Bankai is activated by picking up a specific item (I013 for Gin).
// The ZanCaster unit variable holds the hero who activated the ability.
//===========================================================================

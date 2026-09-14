// Trigger: Shinso
//===========================================================================
function Trig_Shinso_Conditions takes nothing returns boolean
    if ( not ( GetItemTypeId(GetManipulatedItem()) == 'I013' ) ) then
        return false
    endif
    return true
endfunction

function    call TriggerAddCondition( gg_trg_Kyouka_Suigetsu_Release, Condition( function Trig_Kyouka_Suigetsu_Release_Conditions ) )
    call TriggerAddAction( gg_trg_Kyouka_Suigetsu_Release, function Trig_Kyouka_Suigetsu_Release_Actions )
endfunction

//===========================================================================

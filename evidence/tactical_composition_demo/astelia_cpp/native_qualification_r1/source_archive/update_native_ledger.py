"""Explicit source responsibility to native caller/check map; rejects omissions."""
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
GROUPS={
 'api':('enemyOf drawOpponents setNet buildProfile monsters hunters summary run','api.cpp; api.h; config_codec.cpp','test_native_api.py'),
 'config':('resolveLookahead standoffOf applyRules isGame resolveF sk','config_codec.cpp; world.cpp; formation_tables.cpp; config.h','test_native_combat.py; test_native_formation.py; test_native_search.py; test_native_artillery.py'),
 'world':('finishingCounts finishing rng cloneRng makeUnit newPack create skirmishSpawn spawnHunter team teamMelee foes note damage moveToward fork done','world.cpp; world.h; rng.h; director.cpp; search.cpp','native_core_contract.cpp; native_combat_contract.cpp; native_search_contract.cpp; native_artillery_contract.cpp'),
 'geometry':('len clamp dist gap maxD','geometry.h','native_core_contract.cpp'),
 'spatial':('lineBlocker lgKey lgBuild lgPut lgRemove lgMoved buildGrid lineBlockerGrid separate','spatial.cpp; spatial.h; combat.cpp','native_core_contract.cpp'),
 'combat_rules':('couldStart gamePrep castPermit gameDash gameBlock gameUnit retime nearest laneClear vel interceptPoint windUp prepared released canDodge pHit pHitLine fc fireShot aimClear fireShell minR lobV blastR fireShellAt inReachOf','combat_rules.cpp; targeting.cpp; world.cpp; combat.cpp; artillery_prediction.cpp','native_combat_contract.cpp; native_formation_contract.cpp; native_artillery_contract.cpp'),
 'player':('gamePlayer playerShot playerBrain','player.cpp; world.cpp','native_combat_contract.cpp; test_native_combat.py'),
 'artillery':('shellEscape predictVolley threatWorth smartVolley fireGate artilleryVolley artyOutcome shellOf assignGuns launch','artillery.cpp; artillery_prediction.cpp','native_artillery_contract.cpp; test_native_artillery.py'),
 'formation':('rowOf ranks reachOf paceOf pinned composeF setPlan formationPlan positionAnchor assignSlots meleeOrders surroundOrders shooterFocusOrders','formation.cpp; formation_tables.cpp; targeting.cpp','native_formation_contract.cpp; test_native_formation.py'),
 'commander':('gamePackDecide threatRead readEnemy tacticsOf comboOf comboName planFrom planDwell planSwitchable commander','commander.cpp; formation_tables.cpp; formation_types.h; search.cpp','native_formation_contract.cpp; native_search_contract.cpp; test_native_formation.py'),
 'director':('cmdOf observe briefing directorStep','director.cpp; formation.h; formation_types.h','native_formation_contract.cpp; test_native_formation.py'),
 'decisions':('shotDodgeVector meleeAnswer goTo decMelee decDirect decArtillery decideAlone decideReleased kiterRetreat saveWounded decideOrder decideOwn decideFormation decide walk','decisions.cpp; combat.cpp; formation.cpp; targeting.cpp','native_formation_contract.cpp; test_native_formation.py; test_native_combat.py'),
 'targeting':('addPending shooterTarget artilleryTarget leaderFire','targeting.cpp; formation.cpp','native_formation_contract.cpp'),
 'dodge':('shellDodge dodgeVector castBlasts smartEscape','dodge.cpp; decisions.cpp','native_formation_contract.cpp; test_native_formation.py'),
 'abilities':('ready abStat spend busy useCharge useShield useAimed useDisengage useBarrage useSlow busyAct triggerAbility abilityReady triggerAbilityNow defaultAbilities coordOn coordAbilities','abilities.cpp; coord_abilities.cpp; world.cpp; combat.cpp','native_combat_contract.cpp; native_formation_contract.cpp; native_api_contract.cpp'),
 'combat':('act step','combat.cpp','native_combat_contract.cpp; native_formation_contract.cpp; native_search_contract.cpp; native_artillery_contract.cpp'),
 'search':('bcFeatures bcTop bcPredict lookahead reachRate distinctTactics','network.cpp; network_tables.cpp; search.cpp; formation_tables.cpp','native_search_contract.cpp; test_native_search.py'),
}
def main():
    path=ROOT/'native_feature_ledger.json';ledger=json.loads(path.read_text());mapping={}
    for group,(names,files,checks) in GROUPS.items():
        for name in names.split():
            if name in mapping:raise RuntimeError('duplicate function '+name)
            mapping[name]=dict(native_files=['src/native/'+s.strip() for s in files.split(';')],check=checks+'; verify_native.py exhaustive 623 requests and 20 traces',status='IMPLEMENTED_NATIVE',module=group)
    if set(mapping)!=set(ledger['functions']):raise RuntimeError('unmapped/extra source functions: '+str(set(mapping)^set(ledger['functions'])))
    for name,row in ledger['functions'].items():
        row.update(mapping[name]);row.pop('scope',None)
        for filename in row['native_files']:
            if not (ROOT/filename).is_file():raise RuntimeError('missing native implementation '+filename)
    ledger['table_and_combo_callbacks']=dict(status='IMPLEMENTED_NATIVE',implementations=['formation.cpp seven shapes','formation_tables.cpp 16 presets and 26 typed plans with ordered role patches','commander.cpp four rule commanders','director.cpp Tchain/Fixlob predicates, selection, binding, phases, completion and aborts'],catalog='src/native/catalog_data.h; callback paths are descriptors for typed implementations, never interpreted JavaScript',check='native_formation_contract.cpp; native_api_contract.cpp; test_native_api.py')
    ledger['clone_ledger']=dict(status='IMPLEMENTED_NATIVE',check='native_core_contract.cpp; native_combat_contract.cpp; native_formation_contract.cpp; native_search_contract.cpp; native_artillery_contract.cpp; native_matched_probe.cpp',policy=dict(shared='immutable Config/network and observational work counters only',copied='all hot/conditional/tactical/ability/player/pack/director/commands/artillery queues/cutoff/prediction/fields/dots/shots/hit sets/spawn/RNG/runtime authority',reset='Stats, events, bcData, local counters, recursive thinkTeams, derived rates/perception/spatial contexts',lease='stable allocations per nested lease; no mutable authority aliases parent',cost='equivalent complete authority copies for records and columns; both rebuild team/grid indexes'))
    inventory=json.loads((ROOT/'native_source_inventory.json').read_text());ledger['field_access_lifetime_map']={name:dict(source_functions=data['functions'],native_responsibilities=sorted({mapping[f]['module'] for f in data['functions'] if f in mapping}),policy='typed authority or world-local rebuilt context; exported constants compiled immutable; browser recording/presentation metadata is outside simulation decisions') for name,data in inventory['fields'].items()}
    ledger['browser_exclusions']=['DOM/global export assignment and browser-only JS adapter signatures; native typed controller API retained','bit-string trace formatting, free-form exact UI event prose, and optional browser AAR presentation objects; typed events, commands, observations and search records retained']
    ledger['checkpoint']='native_qualification_r1/qualification.json; final engineering evidence must be qualified separately from implementation inventory'
    path.write_text(json.dumps(ledger,indent=2)+'\n')
if __name__=='__main__':main()

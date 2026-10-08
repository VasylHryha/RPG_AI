// Read-only impact hook at the native shell loop, after walking/before damage.
#include "stage1_impacts.h"
namespace stage1_diag {
void impact(astelia::World& w,const astelia::Shell& shell) {
    auto* host=dynamic_cast<net_slice::Host*>(w.controllers[0].get());
    const auto* src=w.resolve(shell.source);
    if(!host||!src||shell.slow)return;
    js::Args hits,targets;
    for(auto i:w.active) {
        const auto& u=w.units[i];
        if(!u.alive)continue;
        if(u.team!=src->team)targets.push_back(js::obj({{"id",double(u.id)},{"x",u.pos.x},{"y",u.pos.y},{"radius",u.radius}}));
    }
    const auto& candidates=shell.lob?w.active:w.teams[1-src->team];
    for(auto i:candidates) {
        const auto& u=w.units[i];
        if(w.reference(i)==shell.source||!u.alive||astelia::distance(u.pos,shell.pos)>shell.splash+u.radius)continue;
        hits.push_back(js::obj({{"id",double(u.id)},{"team",double(u.team)},{"gun",u.role==astelia::Role::Artillery},
                               {"damage",std::min(shell.damage,u.hp)},{"killed",shell.damage>=u.hp}}));
    }
    host->collector.record(host->tick,src->id,"shell_impact",js::obj({{"source_team",double(src->team)},
        {"born",shell.born},{"landing_at",shell.at},{"aim",js::arr({shell.pos.x,shell.pos.y})},
        {"radius",shell.splash},{"hits",js::arr(std::move(hits))},{"living_targets",js::arr(std::move(targets))}}));
}
js::V totals(const astelia::World& w) {
    double damage=0,own=0,kills=0,shells=0;
    for(const auto& a:w.stats.attacks[0]){damage+=a.damage;own+=a.own;kills+=a.kills;shells+=a.shells;}
    return js::obj({{"enemy_damage",damage},{"friendly_damage",own},{"enemy_kills",kills},{"resolved_shells",shells}});
}
}

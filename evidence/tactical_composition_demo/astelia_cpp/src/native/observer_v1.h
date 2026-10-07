#pragma once
#include "world.h"
namespace astelia::observer_v1 {
struct Support {UnitId id;Vec2 pos;double range,minimum;};
struct Damage { UnitId source,target;uint8_t sourceTeam,targetTeam;Role sourceRole,targetRole;double amount,dealt,time,centreDistance;bool died;Vec2 sourcePos,targetPos;std::vector<UnitId> inReach,insideBand;std::vector<Support> support; };
struct DodgeEvent {UnitId id;uint8_t team;Vec2 from,goal;};
struct Launch {UnitId source,target;uint8_t team;Vec2 point;double born,at,splash;bool barrage,slow;};
struct Entry {UnitId unit,gun;Role role;double time,distance;Vec2 from,pos,gunPos;uint32_t cover;std::vector<UnitId> inReach,insideBand;std::vector<Vec2> otherGuns;};
struct Sink {const World* world=nullptr;std::vector<Damage> damage;std::vector<DodgeEvent> dodges;std::vector<Launch> launches;std::vector<Entry> entries;};
extern thread_local Sink* sink;
struct Scope {Sink* previous;Scope(Sink& s):previous(sink){sink=&s;}~Scope(){sink=previous;}Scope(const Scope&)=delete;};
void movement(const World&,uint32_t,Vec2);
void hit(const World&,const UnitHot&,const UnitHot&,double,double);
void dodge(const World&,uint32_t,bool,Vec2);
void launch(const World&,uint32_t,const Shell&);
}

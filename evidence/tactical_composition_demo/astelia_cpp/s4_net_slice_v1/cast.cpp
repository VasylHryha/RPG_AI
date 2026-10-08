#include "cast.h"
namespace net_slice {
CastOutput Cast::project(const CastInput& s,const Intent& c){last=c;if(!s.alive)return {"consumed-without-launch","dead",false,false,pending};bool winding=s.prep>0&&s.prep<s.windup-1e-9,ready=s.prep>0&&!winding;
 if(winding)return {"winding","native_progress",false,false,false};if(ready&&!readySince)readySince=s.tick;
 const bool legal=!s.body&&s.target&&s.targetReach&&s.aimReach;
 if(ready){if(!legal)return {"blocked",s.body?"body":!s.target?"target_absent":!s.targetReach?"target_range":"aim_range",false,false,s.tick-readySince>=6};bool release=c.release||s.tick-readySince>=6;return {release?"released":"prepared",release?(c.release?"permission":"hold_expired_auto_release"):"hold",false,release,false};}
 if(s.body||!s.target||!s.targetReach||!s.aimReach)return {"blocked",s.body?"body":!s.target?"target_absent":!s.targetReach?"target_range":"aim_range",false,false,false};
 if(s.cooldown>0||s.energy<s.cost)return {"idle/cooldown",s.cooldown>0?"cooldown":"energy",false,false,false};return {"start-ready",c.start?"request_start":"hold",c.start,false,false};}
void Cast::startedAck(uint64_t tick,const Intent& c,uint64_t decision){originDecision=decision?decision:tick;originVolley=c.volley;pending=true;aimLocked=c.release;lockedTarget=c.target;lockedAim=c.aim;started=tick;readySince=0;}
void Cast::consumedAck(){pending=false;aimLocked=false;lockedTarget=0;readySince=0;started=0;}
Intent intent(js::V v){Intent c;c.target=UnitId(js::num(js::get(v,"target")));auto g=js::get(v,"goal");c.goal={js::num(g.p->items[0]),js::num(g.p->items[1])};auto a=js::get(v,"aim");c.hasAim=a.tag!=js::V::Null;if(c.hasAim)c.aim={js::num(a.p->items[0]),js::num(a.p->items[1])};c.multiplier=js::num(js::get(v,"multiplier"));c.stop=js::num(js::get(v,"stop"));c.start=js::truth(js::get(v,"start"));c.release=js::truth(js::get(v,"release"));c.moveIndex=unsigned(js::num(js::get(v,"move_index")));auto ai=js::get(v,"aim_index");c.aimIndex=ai.tag==js::V::Null?0:unsigned(js::num(ai));c.targetIndex=unsigned(js::num(js::get(v,"target_index")));c.volley=uint64_t(js::num(js::get(v,"volley")));return c;}
js::V json(const Intent& c){return js::obj({{"multiplier",c.multiplier},{"stop",c.stop},{"goal",js::arr({c.goal.x,c.goal.y})},{"target",double(c.target)},{"start",c.start},{"release",c.release},{"aim",c.hasAim?js::arr({c.aim.x,c.aim.y}):js::V(nullptr)},{"move_index",double(c.moveIndex)},{"aim_index",c.hasAim?js::V(double(c.aimIndex)):js::V(nullptr)},{"target_index",double(c.targetIndex)},{"volley",double(c.volley)}});}
}

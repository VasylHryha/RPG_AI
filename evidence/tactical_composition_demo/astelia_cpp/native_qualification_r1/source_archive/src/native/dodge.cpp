#include "formation.h"

namespace astelia {
bool shellDodge(const World& w,uint8_t team){const auto& s=w.config->skills[team];return s.dodgeShells||s.smartShells||(s.planShells&&w.packs[team].enabled&&w.packs[team].formation.dodge);}
bool dodgeGoal(const World& w,uint32_t i,Vec2& goal){
  const auto& u=w.units[i];const auto& skills=w.config->skills[u.team];
  for(const auto& f:w.fields)if(f.team!=u.team&&f.from<=w.time&&f.until>=w.time+.5){const auto delta=u.pos-f.pos;const double d=length(delta);
    if(d<=f.radius+u.radius){goal=d<.5?u.pos+Vec2{30,0}:u.pos+delta*(40/d);return true;}}
  if(skills.smartShells){struct Blast{Vec2 pos;double at,radius;};std::vector<Blast> blasts;
    for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&src->team!=u.team&&sh.at>w.time&&!sh.slow)blasts.push_back({sh.pos,sh.at,sh.splash});}
    if(w.config->rules==Rules::Game&&skills.castDodge)for(auto j:w.active){const auto& gun=w.units[j];const auto& s=w.state[j];const auto* t=w.resolve(gun.target);
      if(!gun.alive||gun.team==u.team||gun.role!=Role::Artillery||!(s.prep>0)||!t||!t->alive||t->team!=u.team||gun.target==w.reference(i))continue;
      blasts.push_back({t->pos,w.time+std::max(0.0,windup(w,j)-s.prep)/s.timeRate+distance(t->pos,gun.pos)/((s.lobSpeed>0?s.lobSpeed:300)*s.launch),s.splash>0?s.splash:w.config->roles[2].splash});}
    double first=INFINITY;for(const auto& b:blasts)if(distance(u.pos,b.pos)<=b.radius+u.radius+4)first=std::min(first,b.at);if(!std::isfinite(first))return false;
    const auto cover=[&](Vec2 pos){uint32_t count=0;for(const auto& b:blasts)if(distance(pos,b.pos)<=b.radius+u.radius+4)++count;return count;};
    uint32_t best=cover(u.pos);double bd=0;bool found=false;const double extent=std::max(8.0,u.speed*(first-w.time+.1));
    for(double f:{1.0,.6})for(int j=0;j<16;++j){const double a=j*3.14159265358979323846/8;const auto point=u.pos+Vec2{std::cos(a),std::sin(a)}*(extent*f);
      const Vec2 candidate{clamp(point.x,u.radius,w.config->width-u.radius),clamp(point.y,u.radius,w.config->height-u.radius)};const auto k=cover(candidate);const double d=distance(candidate,u.pos);
      if(k<best||(k==best&&found&&d<bd)){goal=candidate;best=k;bd=d;found=true;}}
    return found;
  }
  const Shell* best=nullptr;double bt=INFINITY,bd=0;
  for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(!src||src->team==u.team)continue;
    const double d=distance(u.pos,sh.pos),need=sh.splash+u.radius+4-d,left=sh.at-w.time;
    if(need>0&&left>0&&u.speed>0&&need/u.speed<left+.1&&left<bt){best=&sh;bt=left;bd=d;}}
  if(!best)return false;goal=bd<.5?u.pos+Vec2{30,0}:u.pos+(u.pos-best->pos)*(40/bd);return true;
}
} // namespace astelia

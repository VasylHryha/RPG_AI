#include "search.h"

namespace astelia {
namespace {
struct Result {double our=0,their=0,flyOur=0,flyTheir=0,posOur=0,posTheir=0;double killsOur=0,killsTheir=0;};
double hp(const World& w,uint8_t team){double sum=0;for(auto i:w.teams[team])if(w.units[i].alive)sum+=std::max(0.0,w.units[i].hp);return sum;}
Tactics uniform(Plan plan){Tactics c;c.role.fill(plan);return c;}
bool finishing(const World& w,uint8_t me){if(w.config->rules!=Rules::Game)return false;const auto ours=w.teams[me].size(),theirs=w.foes(me).size();return theirs>0&&(theirs<=2||ours>=4*theirs);}
Result playout(World& w,uint8_t me,const Lookahead& la,const Tactics& plan,EnemyModel model){
  auto lease=w.branches().fork(w);auto& c=lease.world();++w.work->candidateModels;c.hasForced=true;c.forced=plan;c.forcedTeam=me;c.duration=w.time+la.horizon;c.dt=la.dt>0?la.dt:w.dt;
  if(!std::isfinite(c.duration)||!(c.dt>0)||c.duration/c.dt>1e7)throw std::invalid_argument("invalid lookahead branch horizon");
  ++w.work->branchSettings[{c.dt,c.duration-w.time}];
  auto& p=c.packs[me];p.plan=Plan::None;p.planSince=-99;p.lastThink=-1;
  const uint8_t them=1-me;auto& enemy=c.packs[them];
  if(enemy.enabled&&model==EnemyModel::Rules){enemy.search.hasChoice=false;enemy.lookPlan=Plan::None;enemy.lastThink=-1;}
  else if(enemy.enabled&&model!=EnemyModel::Oracle){c.brains[them]=Brain::Formation;if(model==EnemyModel::Rush){enemy.formation.release=7;enemy.formation.raidTarget=SoftTarget::Soft;}}
  const double our0=hp(c,me),their0=hp(c,them);const auto ours=c.survivors(me),theirs=c.survivors(them);
  while(!c.done())coreStep(c);Result r;r.our=our0-hp(c,me);r.their=their0-hp(c,them);r.killsOur=double(ours)-c.survivors(me);r.killsTheir=double(theirs)-c.survivors(them);
  for(const auto& sh:c.shells)if(!sh.slow){const auto* source=c.resolve(sh.source);if(!source)throw std::logic_error("branch shell source unavailable");const double x=sh.hasPrediction?sh.prediction:sh.damage*.76;
    if(source->team==me)r.flyTheir+=x;else r.flyOur+=x;}
  if(la.terminal){r.posOur=la.terminal*reachRate(c,me);r.posTheir=la.terminal*reachRate(c,them);}return r;
}
}
double reachRate(const World& w,uint8_t team){double rate=0;for(auto i:w.teams[team])if(w.units[i].alive){const auto& u=w.units[i];const auto& s=w.state[i];const double low=u.role==Role::Artillery?s.minRange:0;
  for(auto j:w.teams[1-team])if(w.units[j].alive){const double d=u.role==Role::Artillery?distance(u.pos,w.units[j].pos):gap(u,w.units[j]);if(d<=u.range&&d>=low){rate+=u.damage/(s.cooldownMax>0?s.cooldownMax:1);break;}}}return rate;}
void lookahead(World& w,uint8_t me){const auto& settings=w.config->lookahead[me];if(!settings.enabled||(w.branch&&!(w.thinkTeams&(1<<me))))return;auto& pack=w.packs[me];auto& search=pack.search;
  const double interval=search.stable&&settings.everyStable>0?settings.everyStable:settings.every;if(w.time-search.last<interval)return;search.last=w.time;++w.work->searchCalls;
  const bool prior=search.hasChoice;const auto old=search.choice;std::vector<Plan> candidates=settings.plans;
  if(finishing(w,me)){candidates={Plan::Advance,Plan::Hunt,Plan::Push,Plan::Surround,Plan::Engage,Plan::Rush,Plan::Flank};}
  else if(settings.network&&settings.netPrune){++w.work->inferenceCalls;const auto indices=bcTop(*settings.network,bcFeatures(w,me,settings.plans),settings.netPrune);candidates.clear();for(auto i:indices){if(i>=settings.plans.size())throw std::invalid_argument("network outputs do not match plans");candidates.push_back(settings.plans[i]);}
    for(auto plan:settings.extra)if(std::find(candidates.begin(),candidates.end(),plan)==candidates.end())candidates.push_back(plan);
    if(prior&&!settings.mind&&std::all_of(old.role.begin(),old.role.end(),[&](Plan p){return p==old.role[0];})&&std::find(candidates.begin(),candidates.end(),old.role[0])==candidates.end())candidates.push_back(old.role[0]);}
  if(settings.contact>0){double near=INFINITY;for(auto i:w.teams[me])if(w.units[i].alive)for(auto j:w.teams[1-me])if(w.units[j].alive)near=std::min(near,distance(w.units[i].pos,w.units[j].pos));
    if(near>settings.contact){search.hasChoice=false;pack.lookPlan=Plan::None;return;}}
  double k=settings.k;const double fraction=w.duration>0?w.time/w.duration:1;
  if(settings.urgency&&fraction>settings.urgencyFrom)k*=std::max(settings.urgencyMin,1-(1-settings.urgencyMin)*(fraction-settings.urgencyFrom)/(1-settings.urgencyFrom));
  bool stalled=false;if(settings.stall>0){for(const auto& hit:w.hitLog)if(hit.from==me&&hit.amount>0)search.progress=std::max(search.progress,hit.time);
    if(w.time-search.progress>settings.stall){k/=3;stalled=true;}}
  const auto value=[&](const Result& r){const double hw=settings.deaths?.3:1,dw=settings.deaths?100:0;return r.their+r.flyTheir+dw*r.killsTheir-k*(hw*(r.our+r.flyOur)+dw*r.killsOur);};
  const auto position=[&](const Result& r){return settings.terminal?r.posOur-k*r.posTheir:0;};
  Tactics best;bool hasBest=false;double bestScore=-INFINITY;
  if(!settings.mind){for(auto plan:candidates){const auto combo=uniform(plan);double score=INFINITY;
      for(auto model:settings.models){const auto r=playout(w,me,settings,combo,model);score=std::min(score,settings.hasObjective?value(r):(stalled?2:1)*r.their-k*r.our)+position(r);}
      if(prior&&combo.role==old.role)score+=settings.inertia;if(score>bestScore){bestScore=score;best=combo;hasBest=true;}}}
  else{struct Screen {Tactics combo;double value;};std::vector<Screen> screens;screens.reserve(settings.budget);uint32_t budget=settings.budget;
    const auto sticky=[&](const Tactics& c){return prior&&c.role==old.role?settings.inertia:0;};
    const auto evaluate=[&](const Tactics& combo){for(const auto& s:screens)if(s.combo.role==combo.role)return s.value+sticky(combo);
      if(!budget)return -std::numeric_limits<double>::infinity();--budget;const auto r=playout(w,me,settings,combo,settings.models[0]);const double score=value(r)+position(r);screens.push_back({combo,score});return score+sticky(combo);};
    std::vector<Tactics> seeds;if(prior)seeds.push_back(old);else if(pack.combo.role[0]!=Plan::None)seeds.push_back(pack.combo);for(auto p:candidates)seeds.push_back(uniform(p));
    for(const auto& c:seeds){const double score=evaluate(c);if(score>bestScore){bestScore=score;best=c;hasBest=true;}}
    search.turn=(search.turn+1)%4;constexpr std::array<uint8_t,4> roles{3,2,1,0};
    for(uint8_t i=0;i<4;++i){const auto role=roles[(search.turn+i)%4];for(auto tactic:distinctTactics(w.brains[me],role))if(hasBest&&tactic!=best.role[role]&&budget){auto combo=best;combo.role[role]=tactic;const double score=evaluate(combo);
        if(score>bestScore+settings.tweakMargin){bestScore=score;best=combo;}}}
    if(settings.models.size()>1){std::stable_sort(screens.begin(),screens.end(),[&](const Screen& a,const Screen& b){return a.value+sticky(a.combo)>b.value+sticky(b.combo);});bestScore=-INFINITY;
      for(size_t i=0;i<std::min(size_t(settings.robustTop),screens.size());++i){const auto& screened=screens[i];double worst=screened.value,sum=screened.value;
        for(size_t m=1;m<settings.models.size();++m){const auto r=playout(w,me,settings,screened.combo,settings.models[m]);const double v=value(r)+position(r);worst=std::min(worst,v);sum+=v;}
        const double v=settings.blend*worst+(1-settings.blend)*sum/settings.models.size()+sticky(screened.combo);if(v>bestScore){bestScore=v;best=screened.combo;hasBest=true;}}}
  }
  if(w.config->bcRecord&&!settings.mind){const auto found=hasBest?std::find(settings.plans.begin(),settings.plans.end(),best.role[0]):settings.plans.end();w.bcData.push_back({bcFeatures(w,me,settings.plans),found==settings.plans.end()?-1:int32_t(found-settings.plans.begin())});}
  search.stable=hasBest==prior&&(!hasBest||best.role==old.role);if(!search.stable)w.note("look-ahead picks "+std::string(hasBest?planName(best.role[0]):"none"),me);search.hasChoice=hasBest;search.choice=best;search.score=hasBest?bestScore:0;pack.lookPlan=hasBest?best.role[0]:Plan::None;
}
} // namespace astelia

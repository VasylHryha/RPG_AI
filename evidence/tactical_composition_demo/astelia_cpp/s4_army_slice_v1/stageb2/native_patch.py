"""Prospective native seams; fail on changed baseline text instead of guessing."""
from pathlib import Path

def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError('B2 native seam drift: '+a)
    return s.replace(a,b)

def apply(out):
    out=Path(out)
    p=out/'stagea.h';s=p.read_text();s=once(s,'std::string kind;Vec fireThresholds;','std::string kind;Vec fireThresholds;bool tools=false,learnedDodge=false;');s=once(s,'js::V input;', 'js::V input,candidatePicks;bool teacherDriving=false;double dartSigma=0,dartTarget=0;uint64_t daggerSeed=0;');p.write_text(s)
    p=out/'stagea.cpp';s='#include "candidates.h"\n'+p.read_text()
    s=once(s,'struct Packed {Matrix','struct Packed {js::V row;Matrix')
    s=once(s,'Packed p;auto units=','Packed p;p.row=row;auto units=')
    s=once(s,'Matrix infer(State& s,', '''stageb2::Frame toolFrame(js::V row){stageb2::Frame f;f.width=js::num(js::get(row,"width"));f.height=js::num(js::get(row,"height"));f.units=mat(js::get(row,"units"));f.own=mat(js::get(row,"own"));f.shells=mat(js::get(row,"shells"));f.shots=mat(js::get(row,"shots"));f.casts=mat(js::get(row,"casts"));f.fields=mat(js::get(row,"fields"));auto lv=js::get(row,"longVelocity");if(lv.tag!=js::V::Undefined)for(auto key:js::keys(lv)){auto v=nums(js::get(lv,key));if(v.size()!=2)throw std::invalid_argument("long velocity width");f.longVelocity[unsigned(std::stoul(js::str(key)))]={v[0],v[1]};}return f;}
Vec toolScores(const Weights& w,const Vec& h,const Matrix& encoded,const std::vector<stageb2::Candidate>& bank,const std::string& name,size_t cap){auto key=w.linear(name+"_choice",h),sourceKey=w.linear(name+"_source",h);Vec scores(cap,-1e6);for(size_t j=0;j<bank.size();++j){const auto& c=bank[j];Vec embedding(64);if(c.source>=0)embedding=encoded.at(size_t(c.source));auto joined=c.features;append(joined,h);append(joined,embedding);scores[j]=dot(key,c.features)/std::sqrt(double(stageb2::FEATURES))+dot(sourceKey,embedding)/8+w.linear(name+"_score",tan(w.linear(name+"_hidden",joined)))[0];}if(!bank.empty()){double maximum=*std::max_element(scores.begin(),scores.begin()+bank.size());for(size_t j=0;j<bank.size();++j){if(!std::isfinite(scores[j]))throw std::runtime_error("nonfinite candidate scores");scores[j]-=maximum;}}return scores;}
Matrix infer(State& s,''')
    s=once(s,'Matrix out;for(size_t i=0;i<n;++i)', 'js::Args picks;Matrix out;for(size_t i=0;i<n;++i)')
    s=once(s,'out.push_back(v);next[p.ids[i]]=mem[i];', '''if(w.tools){auto banks=stageb2::candidates(toolFrame(p.row),p.ids[i]);auto a=toolScores(w,h,s.cache,banks.aim,"aim",stageb2::MAX_AIM),m=toolScores(w,h,s.cache,banks.move,"move",stageb2::MAX_MOVE);auto ai=banks.aim.empty()?0:std::max_element(a.begin(),a.begin()+banks.aim.size())-a.begin(),mi=std::max_element(m.begin(),m.begin()+banks.move.size())-m.begin();auto ao=w.linear("aim_offset",h),mo=w.linear("move_offset",h);for(auto& x:ao)x=stageb2::AIM_OFFSET*std::tanh(x);for(auto& x:mo)x=stageb2::MOVE_OFFSET*std::tanh(x);auto ap=banks.aim.empty()?stageb2::Point{}:banks.aim.at(ai).point;auto mp=banks.move.at(mi).point;double W=js::num(js::get(p.row,"width")),H=js::num(js::get(p.row,"height"));v[0]=(mp.x+mo[0])/W;v[1]=(mp.y+mo[1])/H;v[6]=(ap.x+ao[0])/W;v[7]=(ap.y+ao[1])/H;append(v,a);append(v,m);append(v,ao);append(v,mo);for(auto uv:js::get(p.row,"units").p->items)if(js::num(uv.p->items[0])==p.ids[i]){std::string role=js::num(uv.p->items[2])==0?"melee":js::num(uv.p->items[2])==1?"ranged":"artillery";if(!banks.aim.empty())picks.push_back(js::obj({{"id",double(p.ids[i])},{"role",role},{"head","aim"},{"type",double(banks.aim[ai].type)}}));picks.push_back(js::obj({{"id",double(p.ids[i])},{"role",role},{"head","move"},{"type",double(banks.move[mi].type)}}));}}out.push_back(v);next[p.ids[i]]=mem[i];''')
    s=once(s,'s.memory=std::move(next);return out;', 's.candidatePicks=js::arr(std::move(picks));s.memory=std::move(next);return out;')
    s=once(s,'js::set(row,"networkKind",c.stage.weights->kind);', 'if(c.stage.weights->tools)js::set(row,"candidatePicks",c.stage.candidatePicks);js::set(row,"networkKind",c.stage.weights->kind);')
    s=once(s,'{"combat_steps",0}', '{"candidatePicks",s.candidatePicks},{"combat_steps",0}')
    s=once(s,'if(js::str(js::get(v,"version"))!="ARMYA1"||', 'tools=js::str(js::get(v,"version"))=="ARMYB2";learnedDodge=js::truth(js::get(v,"learnedDodge"));if(!tools&&learnedDodge)throw std::invalid_argument("dodge variant requires B2 weights");if((!tools&&js::str(js::get(v,"version"))!="ARMYA1")||')
    s=once(s,'if(js::keys(ps).size()!=shapes.size())', """if(tools)for(auto name:{"aim","move"})for(auto layer:std::vector<std::tuple<std::string,size_t,size_t>>{{"_choice",stageb2::FEATURES,64},{"_source",64,64},{"_hidden",16,stageb2::FEATURES+128},{"_score",1,16},{"_offset",2,64}}){auto key=std::string(name)+std::get<0>(layer);shapes[key+".weight"]={std::get<1>(layer),std::get<2>(layer)};shapes[key+".bias"]={std::get<1>(layer)};}
 if(js::keys(ps).size()!=shapes.size())""")
    s=once(s,'size_t target=std::max_element(y.begin()+10,y.end())-(y.begin()+10);','size_t target=std::max_element(y.begin()+10,c.stage.weights->tools?y.end()-(stageb2::MAX_AIM+stageb2::MAX_MOVE+4):y.end())-(y.begin()+10);')
    s=once(s,'if(refresh){s.cache.clear();','if(w.tools)refresh=true;if(refresh){s.cache.clear();')
    # New legal landing projection only for tools. Baseline arithmetic stays intact.
    start=s.index('if(u.role==astelia::ObservedRole::Artillery){')
    end=s.index('\n return cmd;}',start)
    original=s[start:end]
    s=s[:start]+'''if(u.role==astelia::ObservedRole::Artillery&&c.stage.weights->tools){auto p=stageb2::range_project({y[6]*o.width,y[7]*o.height},{u.x,u.y},u.minRange,u.range,{0,0,o.width,o.height});if(p){cmd.hasAim=true;cmd.aim={p->x,p->y};}}
 else '''+original+s[end:]
    s=once(s,'c.stage.shadow=js::truth(js::get(config,"shadow"));','c.stage.shadow=js::truth(js::get(config,"shadow"));auto mix=js::get(config,"dagger");if(mix.tag!=js::V::Undefined){if(!c.stage.shadow||!c.stage.weights||!c.stage.weights->tools)throw std::invalid_argument("DAgger requires B2 shadow");c.stage.teacherDriving=js::truth(js::get(mix,"teacher_driving"));c.stage.dartSigma=js::num(js::get(mix,"movement_sigma_px"));c.stage.dartTarget=js::num(js::get(mix,"target_replace_probability"));c.stage.daggerSeed=uint64_t(js::num(js::get(mix,"seed")));if(!std::isfinite(c.stage.dartSigma)||c.stage.dartSigma<0||!std::isfinite(c.stage.dartTarget)||c.stage.dartTarget<0||c.stage.dartTarget>1||(!c.stage.teacherDriving&&(c.stage.dartSigma||c.stage.dartTarget)))throw std::invalid_argument("DAgger noise bounds");}')
    p.write_text(s)
    p=out/'react.cpp';s='#include "dagger_driver.h"\n'+p.read_text();s=once(s,'reacting_[u.id]=reaction.active;', 'if(stage.teacherDriving){auto teacher=stageb2::teacherCommand(*this,u.id);r.executed=teacher.first;r.active=teacher.second;r.winner=r.active?"react":"teacher";if(s.guardUntil>o.t||s.busy)r.executed.fire=FireIntent::Hold;}reacting_[u.id]=r.active;');s=once(s,'const auto reaction=react(snapshot(),u.id);','const auto reaction=(stage.weights&&stage.weights->learnedDodge)?Reaction{}:react(snapshot(),u.id);');p.write_text(s)
    # Body dash remains shared: learned-dodge turns off only movement react.
    p=out/'react.h';s=p.read_text();s=once(s,'struct Snapshot {','struct Snapshot {std::map<UnitId,Vec2> stageLongVelocity;');p.write_text(s)
    p=out/'react.cpp';s=p.read_text();s=once(s,'const auto& s=w.state[i];const auto* t=w.resolve(u.target);','const auto& s=w.state[i];out.stageLongVelocity[u.id]=s.longVelocity;const auto* t=w.resolve(u.target);');p.write_text(s)
    p=out/'stagea.cpp';s=p.read_text();s=once(s,'return js::obj({{"stageA",true}', 'std::vector<std::pair<std::string,js::V>> velocity;for(auto& kv:s.stageLongVelocity)velocity.push_back({std::to_string(kv.first),js::arr({kv.second.x,kv.second.y})});auto lv=c.stage.layouts.object(velocity);return js::obj({{"longVelocity",lv},{"stageA",true}');p.write_text(s)
    # Tag actual damage call paths without changing the shared Damage/World ABI.
    p=out/'react_combat.cpp';s='#include "hazard_metrics.h"\n'+p.read_text()
    s=once(s,'void shots(World& w,double dt) {','void shots(World& w,double dt) {stageb2::DamageScope damageScope("shot");')
    s=once(s,'for (const auto& hit:w.meleeHits) {','for (const auto& hit:w.meleeHits) {stageb2::DamageScope damageScope("melee");')
    s=once(s,'for (auto& shell:w.shells) if (w.time>=shell.at) {','for (auto& shell:w.shells) if (w.time>=shell.at) {stageb2::DamageScope damageScope("shell");')
    s=once(s,'w.burnTick=true;for(auto& d:w.dots)', 'w.burnTick=true;{stageb2::DamageScope damageScope("burn");for(auto& d:w.dots)')
    s=once(s,'w.burnTick=false;', '}w.burnTick=false;');p.write_text(s)
    p=out/'lean_observer.cpp';s='#include "hazard_metrics.h"\n'+p.read_text();s=once(s,'sink->damage.push_back(std::move(event));','sink->damage.push_back(std::move(event));stageb2::damageKinds.push_back(stageb2::damageKind);');p.write_text(s)
    p=out/'lean_host.cpp';s='#include "hazard_metrics.h"\n'+p.read_text()
    s=once(s,'for(const auto& d:observer.damage)damage.push_back(js::obj({','size_t damageIndex=0;for(const auto& d:observer.damage)damage.push_back(js::obj({{"hazardType",stageb2::damageKinds.at(damageIndex++)},')
    s=once(s,'observer.damage.clear();','observer.damage.clear();stageb2::damageKinds.clear();');p.write_text(s)

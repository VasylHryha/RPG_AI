"""Prospective native seams; fail on changed baseline text instead of guessing."""
from pathlib import Path

def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError('B2 native seam drift: '+a)
    return s.replace(a,b)

def apply(out):
    out=Path(out)
    p=out/'stagea.h';s=p.read_text();s=once(s,'std::string kind;Vec fireThresholds;','std::string kind;Vec fireThresholds;bool tools=false,learnedDodge=false;');p.write_text(s)
    p=out/'stagea.cpp';s='#include "candidates.h"\n'+p.read_text()
    s=once(s,'struct Packed {Matrix','struct Packed {js::V row;Matrix')
    s=once(s,'Packed p;auto units=','Packed p;p.row=row;auto units=')
    s=once(s,'Matrix infer(State& s,', '''stageb2::Frame toolFrame(js::V row){stageb2::Frame f;f.width=js::num(js::get(row,"width"));f.height=js::num(js::get(row,"height"));f.units=mat(js::get(row,"units"));f.own=mat(js::get(row,"own"));f.shells=mat(js::get(row,"shells"));f.shots=mat(js::get(row,"shots"));f.casts=mat(js::get(row,"casts"));f.fields=mat(js::get(row,"fields"));return f;}
Vec toolScores(const Weights& w,const Vec& h,const std::vector<stageb2::Candidate>& bank,const std::string& name,size_t cap){auto key=w.linear(name+"_choice",h);Vec scores(cap,-1e6);for(size_t j=0;j<bank.size();++j)scores[j]=dot(key,bank[j].features)/4;if(!bank.empty()){double maximum=*std::max_element(scores.begin(),scores.begin()+bank.size());for(size_t j=0;j<bank.size();++j){if(!std::isfinite(scores[j]))throw std::runtime_error("nonfinite candidate scores");scores[j]-=maximum;}}return scores;}
Matrix infer(State& s,''')
    s=once(s,'out.push_back(v);next[p.ids[i]]=mem[i];', '''if(w.tools){auto banks=stageb2::candidates(toolFrame(p.row),p.ids[i]);auto a=toolScores(w,h,banks.aim,"aim",stageb2::MAX_AIM),m=toolScores(w,h,banks.move,"move",stageb2::MAX_MOVE);auto ai=banks.aim.empty()?0:std::max_element(a.begin(),a.begin()+banks.aim.size())-a.begin(),mi=std::max_element(m.begin(),m.begin()+banks.move.size())-m.begin();auto ao=w.linear("aim_offset",h),mo=w.linear("move_offset",h);for(auto& x:ao)x=stageb2::AIM_OFFSET*std::tanh(x);for(auto& x:mo)x=stageb2::MOVE_OFFSET*std::tanh(x);auto ap=banks.aim.empty()?stageb2::Point{}:banks.aim.at(ai).point;auto mp=banks.move.at(mi).point;double W=js::num(js::get(p.row,"width")),H=js::num(js::get(p.row,"height"));v[0]=(mp.x+mo[0])/W;v[1]=(mp.y+mo[1])/H;v[6]=(ap.x+ao[0])/W;v[7]=(ap.y+ao[1])/H;append(v,a);append(v,m);append(v,ao);append(v,mo);}out.push_back(v);next[p.ids[i]]=mem[i];''')
    s=once(s,'if(js::str(js::get(v,"version"))!="ARMYA1"||', 'tools=js::str(js::get(v,"version"))=="ARMYB2";learnedDodge=js::truth(js::get(v,"learnedDodge"));if(!tools&&learnedDodge)throw std::invalid_argument("dodge variant requires B2 weights");if((!tools&&js::str(js::get(v,"version"))!="ARMYA1")||')
    s=once(s,'if(js::keys(ps).size()!=shapes.size())', '''if(tools)for(auto name:{"aim_choice","move_choice","aim_offset","move_offset"}){size_t n=std::string(name).find("choice")!=std::string::npos?16:2;shapes[std::string(name)+".weight"]={n,64};shapes[std::string(name)+".bias"]={n};}
 if(js::keys(ps).size()!=shapes.size())''')
    s=once(s,'size_t target=std::max_element(y.begin()+10,y.end())-(y.begin()+10);','size_t target=std::max_element(y.begin()+10,c.stage.weights->tools?y.end()-1194:y.end())-(y.begin()+10);')
    # New legal landing projection only for tools. Baseline arithmetic stays intact.
    start=s.index('if(u.role==astelia::ObservedRole::Artillery){')
    end=s.index('\n return cmd;}',start)
    original=s[start:end]
    s=s[:start]+'''if(u.role==astelia::ObservedRole::Artillery&&c.stage.weights->tools){auto p=stageb2::range_project({y[6]*o.width,y[7]*o.height},{u.x,u.y},u.minRange,u.range,{0,0,o.width,o.height});if(p){cmd.hasAim=true;cmd.aim={p->x,p->y};}}
 else '''+original+s[end:]
    p.write_text(s)
    p=out/'react.cpp';s=p.read_text();s=once(s,'const auto reaction=react(snapshot(),u.id);','const auto reaction=(stage.weights&&stage.weights->learnedDodge)?Reaction{}:react(snapshot(),u.id);');p.write_text(s)
    p=out/'react_rules.cpp';s=p.read_text();s=once(s,'if(s.dodge!=Dodge::None && s.dashReady<=w.time)', '''auto* b2=dynamic_cast<react_v1::Controller*>(w.controllers[u.team].get());
  const bool learnedDodge=b2&&b2->stage.weights&&b2->stage.weights->learnedDodge;
  if(!learnedDodge && s.dodge!=Dodge::None && s.dashReady<=w.time)''');p.write_text(s)

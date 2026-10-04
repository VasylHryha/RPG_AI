#include "native/search.h"
#include <iostream>
#include <iomanip>
#include <sstream>
using namespace astelia;
namespace {
void require(bool b,const char* text){if(!b)throw std::runtime_error(text);}
std::string authority(const World& w){std::ostringstream s;s.precision(17);s<<w.time<<' '<<w.dt<<' '<<w.duration<<' '<<w.random.state<<' '<<w.spawnRandom.state<<' '<<w.nextId<<' '<<w.stats.ranged;
  for(const auto& u:w.units)if(u.occupied)s<<' '<<u.id<<' '<<u.pos.x<<' '<<u.pos.y<<' '<<u.hp<<' '<<u.cooldown<<' '<<u.target.slot<<' '<<u.generation;
  for(auto p:w.packs)s<<' '<<p.anchor.x<<' '<<p.anchor.y<<' '<<int(p.plan)<<' '<<p.formation.release;return s.str();}
void network(){Network net;net.inputs=2;net.hidden=2;net.outputs=3;net.w1={1,-1,-1,1};net.b1={0,0};net.w2={1,0,0,1,1,1};net.b2={0,0,0};net.validate();
  require(bcPredict(net,{2,1})==0,"network tie did not preserve first output");require(bcTop(net,{2,1},3)==std::vector<uint32_t>({0,2,1}),"stable network shortlist incorrect");
  require(bcPredict(net,{1,2})==1,"ReLU hidden sign wrong");bool rejected=false;try{bcPredict(net,{1});}catch(const std::invalid_argument&){rejected=true;}require(rejected,"bad network feature width accepted");
  require(frozenNetwork()->inputs==46&&frozenNetwork()->outputs==13,"frozen network dimensions changed");
  auto tactics=distinctTactics(Brain::Rules,3);require(tactics.size()>1&&tactics.size()<26,"artillery tactics were not deduplicated");}
Config fixture(){auto c=sandboxConfig();c.army={2,4,0};c.width=650;c.duration=3;c.brains[0]=Brain::Rules;c.lookahead[0].enabled=true;c.lookahead[0].contact=1000;c.lookahead[0].horizon=.2;c.lookahead[0].dt=.05;return c;}
void branches(){auto c=fixture();auto w=World::create(std::make_shared<const Config>(c));const auto before=authority(w);const auto rawFeatures=bcFeatures(w,0,c.lookahead[0].plans);
  require(rawFeatures.size()==46&&rawFeatures[0]==2/30.0&&rawFeatures[1]==1&&rawFeatures[2]==4/30.0&&rawFeatures[3]==1,"role/hp feature reduction incorrect");
  lookahead(w,0);require(authority(w)==before,"lookahead changed combat/config/RNG authority");require(w.packs[0].search.hasChoice&&w.work->forks==13&&w.work->candidateModels==13&&w.work->branchSteps>=52,"full lookahead skipped plan/model/horizon work");
  require(w.work->searchCalls==1&&w.work->inferenceCalls==0,"full search counters invalid");const auto counts=w.work->forks;lookahead(w,0);require(w.work->forks==counts,"lookahead cadence ignored");
  w.stats.ranged=7;auto lease=w.branches().fork(w);auto& branch=lease.world();require(branch.stats.ranged==0&&branch.dt==w.dt&&branch.duration==w.duration,"fork telemetry/runtime policy incorrect");
  branch.dt=.1;branch.duration=1;branch.brains[1]=Brain::Formation;branch.hasForced=true;branch.forced.role.fill(Plan::Rush);branch.forcedTeam=1;branch.thinkTeams=3;
  auto nested=branch.branches().fork(branch);nested.world().dt=.2;require(nested.world().thinkTeams==0&&branch.dt==.1&&w.dt==c.dt&&w.stats.ranged==7,"nested fork copied thinking or changed parent runtime");
  auto distant=fixture();distant.width=2400;distant.lookahead[0].network=frozenNetwork();distant.lookahead[0].netPrune=3;distant.lookahead[0].contact=1;
  auto out=World::create(std::make_shared<const Config>(distant));lookahead(out,0);require(out.work->inferenceCalls==1&&out.work->forks==0&&!out.packs[0].search.hasChoice,"precontact pruning/contact work order changed");}
void mind(){auto c=fixture();auto& la=c.lookahead[0];la.mind=true;la.budget=4;la.robustTop=2;la.models={EnemyModel::Continue,EnemyModel::Rush};la.blend=.7;la.network=frozenNetwork();la.netPrune=3;
  auto w=World::create(std::make_shared<const Config>(c));const auto initial=authority(w);lookahead(w,0);require(authority(w)==initial&&w.packs[0].search.hasChoice,"mind mutated parent or selected nothing");
  require(w.work->inferenceCalls==1&&w.work->forks==6&&w.work->candidateModels==6,"mind budget/robust models were not executed");
  auto repeat=World::create(std::make_shared<const Config>(c));lookahead(repeat,0);require(w.packs[0].search.choice.role==repeat.packs[0].search.choice.role&&w.packs[0].search.score==repeat.packs[0].search.score,"fresh mind decisions differ");
  auto branch=w.branches().fork(w);const auto forks=w.work->forks;branch.world().time=2;lookahead(branch.world(),0);require(w.work->forks==forks,"branch recursively searched without thinkTeams");
  w.time=1.1;lookahead(w,0);require(w.work->forks==13&&w.packs[0].search.turn==2,"reused branch/search budget state incorrect");
}
}
int main(int argc,char** argv){try{std::cout<<std::setprecision(17);
  if(argc>1&&std::string(argv[1])=="--network"){const auto net=frozenNetwork();while(true){std::vector<double> features(net->inputs);if(!(std::cin>>features[0]))break;for(uint32_t i=1;i<net->inputs;++i)if(!(std::cin>>features[i]))throw std::invalid_argument("truncated network fixture");std::vector<double> hidden,scores;networkScores(*net,features,hidden,scores);
      std::cout<<"[";for(size_t i=0;i<scores.size();++i){if(i)std::cout<<',';std::cout<<scores[i];}std::cout<<"]\n";}return 0;}
  network();branches();mind();std::cout<<"native search contracts passed\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

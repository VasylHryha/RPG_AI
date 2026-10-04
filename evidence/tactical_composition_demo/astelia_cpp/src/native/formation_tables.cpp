// Generated from frozen formation_sim.js SHA256 85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733
#include "formation.h"

namespace astelia {
Formation presetFormation(const std::string& name){Formation f;
if(name=="line"){return f;}
if(name=="wide line"){f.rangedRanks=1;f.frontSpacing=38;f.rankSpacing=22;f.screenGap=21;f.rearGap=59;f.standoff=0.89;f.turnRate=0.17;f.zoneDepth=45;f.coverFraction=0.84;f.maxStrikersPerTarget=2;f.laneLeash=22;f.kiteLeash=71;f.engagedWeight=1;f.closingSpeed=26;f.dive=false;f.zoneBehind=88;f.zoneSideMargin=57;return f;}
if(name=="wedge"){f.shape=Shape::Wedge;return f;}
if(name=="box"){f.shape=Shape::Box;return f;}
if(name=="column"){f.shape=Shape::Column;return f;}
if(name=="loose"){f.shape=Shape::Line;f.frontSpacing=55;f.rankSpacing=36;f.screenGap=45;return f;}
if(name=="screen"){f.shape=Shape::Screen;return f;}
if(name=="crescent"){f.shape=Shape::Crescent;return f;}
if(name=="ring"){f.shape=Shape::Ring;return f;}
if(name=="wedge hold"){f.shape=Shape::Wedge;f.meleeDoctrine=MeleeDoctrine::Screen;return f;}
if(name=="line anvil"){f.meleeDoctrine=MeleeDoctrine::Anvil;return f;}
if(name=="wedge flank"){f.shape=Shape::Wedge;f.meleeDoctrine=MeleeDoctrine::Flank;return f;}
if(name=="loose free"){f.shape=Shape::Line;f.frontSpacing=55;f.rankSpacing=36;f.screenGap=45;f.release=3;return f;}
if(name=="swarm"){f.shape=Shape::Line;f.frontSpacing=55;f.rankSpacing=36;f.screenGap=45;f.release=7;return f;}
if(name=="loose skirmish"){f.shape=Shape::Line;f.frontSpacing=55;f.rankSpacing=36;f.screenGap=45;f.release=2;f.dodge=true;f.holdWhileClosing=false;return f;}
if(name=="loose berserk"){f.shape=Shape::Line;f.frontSpacing=55;f.rankSpacing=36;f.screenGap=45;f.release=1;f.raidTarget=SoftTarget::Artillery;f.holdWhileClosing=false;return f;}
if(name.empty())return f;throw std::invalid_argument("unknown formation preset: "+name);}
Plan planByName(const std::string& name){
if(name=="hold")return Plan::Hold;
if(name=="siege")return Plan::Siege;
if(name=="counter")return Plan::Counter;
if(name=="advance")return Plan::Advance;
if(name=="skirmish")return Plan::Skirmish;
if(name=="spread")return Plan::Spread;
if(name=="widehold")return Plan::Widehold;
if(name=="meleehunt")return Plan::Meleehunt;
if(name=="bait")return Plan::Bait;
if(name=="intercept")return Plan::Intercept;
if(name=="hunt")return Plan::Hunt;
if(name=="push")return Plan::Push;
if(name=="flank")return Plan::Flank;
if(name=="surround")return Plan::Surround;
if(name=="raidart")return Plan::Raidart;
if(name=="oblique")return Plan::Oblique;
if(name=="engage")return Plan::Engage;
if(name=="focus")return Plan::Focus;
if(name=="pushfocus")return Plan::Pushfocus;
if(name=="rush")return Plan::Rush;
if(name=="raid")return Plan::Raid;
if(name=="pressure")return Plan::Pressure;
if(name=="loose")return Plan::Loose;
if(name=="dispersed")return Plan::Dispersed;
if(name=="defend")return Plan::Defend;
if(name=="withdraw")return Plan::Withdraw;
if(name.empty())return Plan::None;throw std::invalid_argument("unknown plan: "+name);}
const char* planName(Plan p){switch(p){
case Plan::Hold:return "hold";
case Plan::Siege:return "siege";
case Plan::Counter:return "counter";
case Plan::Advance:return "advance";
case Plan::Skirmish:return "skirmish";
case Plan::Spread:return "spread";
case Plan::Widehold:return "widehold";
case Plan::Meleehunt:return "meleehunt";
case Plan::Bait:return "bait";
case Plan::Intercept:return "intercept";
case Plan::Hunt:return "hunt";
case Plan::Push:return "push";
case Plan::Flank:return "flank";
case Plan::Surround:return "surround";
case Plan::Raidart:return "raidart";
case Plan::Oblique:return "oblique";
case Plan::Engage:return "engage";
case Plan::Focus:return "focus";
case Plan::Pushfocus:return "pushfocus";
case Plan::Rush:return "rush";
case Plan::Raid:return "raid";
case Plan::Pressure:return "pressure";
case Plan::Loose:return "loose";
case Plan::Dispersed:return "dispersed";
case Plan::Defend:return "defend";
case Plan::Withdraw:return "withdraw";
default:return "";}}
static void applyMain(Formation& f,Plan p,size_t role){switch(p){
case Plan::Hold:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;break;
case 2:break;
case 3:break;
}break;
case Plan::Siege:switch(role){
case 0:f.anchorMode=AnchorMode::Siege;f.rearGap=6;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;break;
case 2:break;
case 3:f.artilleryDoctrine=ArtilleryDoctrine::Soft;break;
}break;
case Plan::Counter:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.standoff=0.6;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;f.dive=false;break;
case 2:f.shooterFocus=ShooterFocus::Spread;break;
case 3:break;
}break;
case Plan::Advance:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.standoff=0.6;f.anchorSpeed=62;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;f.dive=false;break;
case 2:break;
case 3:break;
}break;
case Plan::Skirmish:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;break;
case 2:f.release|=2;f.shooterFocus=ShooterFocus::Spread;break;
case 3:break;
}break;
case Plan::Spread:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;f.frontSpacing=55;f.rankSpacing=36;f.screenGap=45;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;break;
case 2:break;
case 3:break;
}break;
case Plan::Widehold:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;f.rangedRanks=1;f.frontSpacing=38;f.screenGap=21;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;break;
case 2:break;
case 3:break;
}break;
case Plan::Meleehunt:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;f.release|=1;f.raidTarget=SoftTarget::Soft;break;
case 2:break;
case 3:break;
}break;
case Plan::Bait:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.standoff=1.05;f.screenGap=95;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;f.dive=false;break;
case 2:break;
case 3:break;
}break;
case Plan::Intercept:switch(role){
case 0:f.anchorMode=AnchorMode::Siege;f.rearGap=6;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;f.peelRadius=180;f.maxStrikersPerTarget=2;f.dive=false;break;
case 2:f.shooterFocus=ShooterFocus::Protect;break;
case 3:f.artilleryDoctrine=ArtilleryDoctrine::Pinned;f.engagedWeight=3;break;
}break;
case Plan::Hunt:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.standoff=0.7;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Zone;f.dive=true;f.diveMinTargets=1;f.diveRange=700;break;
case 2:break;
case 3:break;
}break;
case Plan::Push:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Anvil;break;
case 2:f.shooterFocus=ShooterFocus::Soft;break;
case 3:break;
}break;
case Plan::Flank:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Flank;break;
case 2:break;
case 3:break;
}break;
case Plan::Surround:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.surround=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Zone;f.dive=false;break;
case 2:f.shooterFocus=ShooterFocus::One;break;
case 3:break;
}break;
case Plan::Raidart:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Flank;f.flankForce=true;f.flankTarget=SoftTarget::Artillery;f.flankWidth=300;f.flankWait=4;break;
case 2:break;
case 3:break;
}break;
case Plan::Oblique:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.oblique=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;break;
case 2:break;
case 3:break;
}break;
case Plan::Engage:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;break;
case 1:f.release|=1;f.raidTarget=SoftTarget::Soft;break;
case 2:f.release|=2;f.shooterFocus=ShooterFocus::One;break;
case 3:f.release|=4;break;
}break;
case Plan::Focus:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;break;
case 2:f.shooterFocus=ShooterFocus::Squads;f.squadSize=4;break;
case 3:break;
}break;
case Plan::Pushfocus:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Anvil;break;
case 2:f.shooterFocus=ShooterFocus::Squads;f.squadSize=4;break;
case 3:break;
}break;
default:break;}}
static void applyStorm(Formation& f,Plan p,size_t role){switch(p){
case Plan::Advance:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.anchorSpeed=60;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Zone;f.dive=true;break;
case 2:break;
case 3:break;
}break;
case Plan::Rush:switch(role){
case 0:break;
case 1:f.release|=1;f.raidTarget=SoftTarget::Soft;break;
case 2:f.release|=2;break;
case 3:f.release|=4;break;
}break;
default:break;}}
static void applyWolfpack(Formation& f,Plan p,size_t role){switch(p){
case Plan::Raid:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.dodge=true;f.anchorSpeed=55;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Flank;f.flankForce=true;f.flankTarget=SoftTarget::Artillery;f.flankWidth=300;f.flankWait=4;break;
case 2:f.release|=2;f.shooterFocus=ShooterFocus::Soft;break;
case 3:f.artilleryDoctrine=ArtilleryDoctrine::Counter;break;
}break;
case Plan::Skirmish:switch(role){
case 0:f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.dodge=true;f.anchorSpeed=55;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Zone;break;
case 2:f.release|=2;break;
case 3:f.artilleryDoctrine=ArtilleryDoctrine::Counter;break;
}break;
default:break;}}
static void applyGamepack(Formation& f,Plan p,size_t role){switch(p){
case Plan::Pressure:switch(role){
case 0:f.shape=Shape::Line;f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.standoff=0.85;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Zone;f.dive=true;f.diveMinTargets=1;f.diveRange=400;break;
case 2:f.shooterFocus=ShooterFocus::One;break;
case 3:f.artilleryDoctrine=ArtilleryDoctrine::Cluster;break;
}break;
case Plan::Loose:switch(role){
case 0:f.shape=Shape::Line;f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.standoff=0.85;f.frontSpacing=55;f.rankSpacing=36;f.screenGap=45;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Zone;f.dive=true;f.diveMinTargets=1;f.diveRange=400;break;
case 2:f.shooterFocus=ShooterFocus::One;break;
case 3:f.artilleryDoctrine=ArtilleryDoctrine::Cluster;break;
}break;
case Plan::Dispersed:switch(role){
case 0:f.shape=Shape::Line;f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=false;f.syncGate=false;f.standoff=0.85;f.frontSpacing=70;f.rankSpacing=48;f.screenGap=55;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Zone;f.dive=true;f.diveMinTargets=1;f.diveRange=400;break;
case 2:f.shooterFocus=ShooterFocus::One;break;
case 3:f.artilleryDoctrine=ArtilleryDoctrine::Cluster;break;
}break;
case Plan::Defend:switch(role){
case 0:f.shape=Shape::Ring;f.anchorMode=AnchorMode::Standoff;f.holdWhileClosing=true;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;f.dive=false;break;
case 2:f.shooterFocus=ShooterFocus::Protect;break;
case 3:break;
}break;
case Plan::Withdraw:switch(role){
case 0:f.shape=Shape::Ring;f.anchorMode=AnchorMode::Siege;f.siegeMargin=60;break;
case 1:f.meleeDoctrine=MeleeDoctrine::Screen;f.dive=false;break;
case 2:f.shooterFocus=ShooterFocus::Protect;break;
case 3:break;
}break;
default:break;}}
static std::vector<Plan> distinctRules(uint8_t role){switch(role){
case 0:return {Plan::Hold,Plan::Siege,Plan::Counter,Plan::Advance,Plan::Spread,Plan::Widehold,Plan::Bait,Plan::Hunt,Plan::Push,Plan::Surround,Plan::Oblique,Plan::Engage};
case 1:return {Plan::Hold,Plan::Counter,Plan::Meleehunt,Plan::Intercept,Plan::Hunt,Plan::Push,Plan::Flank,Plan::Surround,Plan::Raidart,Plan::Engage};
case 2:return {Plan::Hold,Plan::Counter,Plan::Skirmish,Plan::Intercept,Plan::Push,Plan::Surround,Plan::Engage,Plan::Focus};
case 3:return {Plan::Hold,Plan::Siege,Plan::Intercept,Plan::Engage};
default:throw std::invalid_argument("invalid tactic role");}}
static std::vector<Plan> distinctStorm(uint8_t role){switch(role){
case 0:return {Plan::Advance,Plan::Rush};
case 1:return {Plan::Advance,Plan::Rush};
case 2:return {Plan::Advance,Plan::Rush};
case 3:return {Plan::Advance,Plan::Rush};
default:throw std::invalid_argument("invalid tactic role");}}
static std::vector<Plan> distinctWolfpack(uint8_t role){switch(role){
case 0:return {Plan::Raid};
case 1:return {Plan::Raid,Plan::Skirmish};
case 2:return {Plan::Raid,Plan::Skirmish};
case 3:return {Plan::Raid};
default:throw std::invalid_argument("invalid tactic role");}}
static std::vector<Plan> distinctGamepack(uint8_t role){switch(role){
case 0:return {Plan::Pressure,Plan::Loose,Plan::Dispersed,Plan::Defend,Plan::Withdraw};
case 1:return {Plan::Pressure,Plan::Defend};
case 2:return {Plan::Pressure,Plan::Defend};
case 3:return {Plan::Pressure,Plan::Defend};
default:throw std::invalid_argument("invalid tactic role");}}
std::vector<Plan> distinctTactics(Brain brain,uint8_t role){switch(brain){case Brain::Storm:return distinctStorm(role);case Brain::Wolfpack:return distinctWolfpack(role);case Brain::Gamepack:return distinctGamepack(role);default:return distinctRules(role);}}
Formation composeFormation(const Formation& base,Brain brain,const Tactics& combo){Formation f=base;f.release=0;for(size_t r=0;r<4;++r){
switch(brain){case Brain::Storm:applyStorm(f,combo.role[r],r);break;case Brain::Wolfpack:applyWolfpack(f,combo.role[r],r);break;case Brain::Gamepack:applyGamepack(f,combo.role[r],r);break;default:applyMain(f,combo.role[r],r);break;}}return f;}
}

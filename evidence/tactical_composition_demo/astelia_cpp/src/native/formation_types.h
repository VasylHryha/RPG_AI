#pragma once
#include "types.h"
#include <array>

namespace astelia {
enum class Brain : uint8_t { Alone, Formation, Rules, Storm, Wolfpack, Gamepack };
enum class Shape : uint8_t { Line, Wedge, Box, Column, Screen, Crescent, Ring };
enum class MeleeDoctrine : uint8_t { Zone, Screen, Flank, Anvil, Auto };
enum class ShooterFocus : uint8_t { Spread, One, Squads, Nearest, Protect, Soft };
enum class ArtilleryDoctrine : uint8_t { Cluster, Pinned, Counter, Soft };
enum class AnchorMode : uint8_t { Standoff, Siege };
enum class SoftTarget : uint8_t { Soft, Artillery };
enum class Plan : uint8_t { None, Hold, Siege, Counter, Intercept, Push, Hunt, Flank, Advance, Skirmish,
  Spread, Widehold, Meleehunt, Bait, Surround, Raidart, Oblique, Engage, Focus, Pushfocus,
  Rush, Raid, Pressure, Loose, Dispersed, Defend, Withdraw, Count };
enum class FlankPhase : uint8_t { None, Out, Along, Strike };
enum class PackPhase : uint8_t { Forming, Ordered, GivingGround, Creeping, Siege, Waiting, Advancing, Holding, Searching, Diving };
struct Formation {
  Shape shape=Shape::Line;
  MeleeDoctrine meleeDoctrine=MeleeDoctrine::Zone, autoAttack=MeleeDoctrine::Anvil;
  ShooterFocus shooterFocus=ShooterFocus::Spread;
  ArtilleryDoctrine artilleryDoctrine=ArtilleryDoctrine::Pinned;
  AnchorMode anchorMode=AnchorMode::Standoff;
  SoftTarget raidTarget=SoftTarget::Soft, flankTarget=SoftTarget::Soft;
  double frontSpacing=34, rankSpacing=22, rangedRanks=2, screenGap=32, rearGap=40;
  double standoff=.8, turnRate=.1, syncRadius=30, closingSpeed=15;
  double zoneDepth=200, zoneBehind=50, zoneSideMargin=40, coverFraction=.9, maxStrikersPerTarget=1;
  double diveMinTargets=4, diveRange=320, laneLeash=26, kiteLeash=60, engagedWeight=2, squadSize=5;
  double flankWidth=240, flankDepth=60, flankWait=8, siegeMargin=30, siegeArtMargin=10;
  double meleeKeepAway=160, siegeOwnArtMargin=60, siegeMinArt=1, peelRadius=120, fireDepth=0;
  double surroundRing=.65, surroundArc=200, surroundDist=.8, jink=0, anchorSpeed=0;
  uint8_t release=0;
  bool syncGate=true, holdWhileClosing=true, dive=true, dodge=false, fireControl=false;
  bool surroundLanes=true, oblique=false, surroundScreen=false, surroundCorner=false, flankForce=false;
  bool surround=false, coordAbilities=false;
};
struct Tactics {std::array<Plan,4> role{Plan::None,Plan::None,Plan::None,Plan::None};};
struct Wing {UnitRef unit;int8_t side=0;};
struct ShapeSlots {std::array<std::vector<Vec2>,3> role;}; // x depth, y lateral
struct GoalIds {std::vector<UnitId> ids;double until=0;};
struct GoalPlace {Vec2 point,face;double until=0;bool hasFace=false;};
struct GoalPlan {Tactics tactics;double until=0;};
struct PackGoals {GoalPlace place;GoalIds engage,release;GoalPlan plan;};
struct Observation {Vec2 oursCenter,theirsCenter,axis;std::array<uint32_t,3> oursByRole{},theirsByRole{};
  uint32_t ours=0,theirs=0;double hpOurs=0,hpTheirs=0,gapNear=std::numeric_limits<double>::infinity(),centers=0,spread=0,columnRatio=0,speedAlong=0,approach=0,chaseShare=0,wallDist=0;bool finishing=false;};
struct ComboRole {UnitRef unit;uint8_t role=0;};
struct DirectorEvent {double time;ComboKind combo;uint8_t phase,what;};
struct Director {PackGoals goals;Observation observation;std::vector<ComboRole> roles;std::vector<DirectorEvent> log;
  std::array<double,2> cool{};Vec2 away;double ratio0=0,last=-99,selected=-99,start=0,phaseStart=0;
  uint32_t startEnemies=0,starts=0,aborts=0,successes=0,switches=0;ComboKind combo=ComboKind::Tchain;uint8_t phase=0;bool active=false;};
struct Pack {
  PackGoals commands;Director director;
  Formation base, formation;
  Vec2 anchor, facing{1,0}, away;
  std::array<uint32_t,3> shapeCounts{};
  ShapeSlots shape;
  std::array<std::vector<uint32_t>,3> members;
  std::vector<Wing> wings;
  std::vector<double> pending;
  UnitRef focus, surroundTarget;
  Tactics combo;
  Plan plan=Plan::None, lookPlan=Plan::None, wantMode=Plan::None, response=Plan::None, responseSeen=Plan::None;
  FlankPhase flank=FlankPhase::None;
  PackPhase phase=PackPhase::Forming;
  double planSince=-99, lastThink=-1, fastSeen=-99, flankSince=0, retreatSince=-1, retreatDanger=0;
  double zoneFront=0, zoneBack=0, zoneMinL=0, zoneMaxL=0, coverRadius=0, hitRate=.3;
  Vec2 cover;
  uint64_t version=0, shapeVersion=UINT64_MAX;
  uint32_t flankStart=0, startCount=0, wantCount=0, responseCount=0;
  bool enabled=false, formed=false, waiting=false, diving=false, hasAway=false, caught=false, raidSpent=false, flankStarted=false;
};
struct TacticalState {
  UnitOrder order;
  UnitRef assigned, squadFocus, fireOrder;
  Vec2 flankGoal, surroundGoal;
  double aimOffset=0, jinkUntil=0, holdSince=-1, waitFrom=-1, reservedUntil=0;
  int8_t wing=0, jinkSide=1, holdTeam=-1;
  bool assignedSet=false, answering=false, hasFlankGoal=false, hasSurroundGoal=false, fireHold=false;
};
struct AbilityThresholds {
  double chargeSync=3,shieldAimedAt=2,shieldShellWindow=.6,aimedSafe=120,aimedWorth=1.5;
  double disengageNear=35,barrageMin=3,barrageHeld=2,slowMin=3,slowMoving=30;
};
} // namespace astelia

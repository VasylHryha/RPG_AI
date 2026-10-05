// Aggregate existing independent engineering contracts for one sanitizer run.
#include "native/api.h"
#include "native/artillery.h"
#include "native/formation.h"
#include "native/search.h"
#include "native/world.h"
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
namespace coreContract {
#define main contractMain
#include "native_core_contract.cpp"
#undef main
}
namespace combatContract {
#define main contractMain
#include "native_combat_contract.cpp"
#undef main
}
namespace formationContract {
#define main contractMain
#include "native_formation_contract.cpp"
#undef main
}
namespace searchContract {
#define main contractMain
#include "native_search_contract.cpp"
#undef main
}
namespace artilleryContract {
#define main contractMain
#include "native_artillery_contract.cpp"
#undef main
}
namespace apiContract {
#define main contractMain
#include "native_api_contract.cpp"
#undef main
}
int main(){
  char name[]="contract";char* argv[]={name,nullptr};
  if(coreContract::contractMain())return 1;
  if(combatContract::contractMain())return 1;
  if(formationContract::contractMain())return 1;
  if(searchContract::contractMain(1,argv))return 1;
  if(artilleryContract::contractMain(1,argv))return 1;
  if(apiContract::contractMain())return 1;
  return 0;
}

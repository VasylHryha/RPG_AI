#pragma once
#include <string>
#include <vector>
namespace stageb2 {
inline thread_local std::string damageKind="body";
inline thread_local std::vector<std::string> damageKinds;
struct DamageScope {std::string previous;DamageScope(const char* kind):previous(damageKind){damageKind=kind;}~DamageScope(){damageKind=previous;}};
}

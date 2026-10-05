#pragma once
#include "../medium/medium_c.h"
#include "../world/world.h"
// Bounded transfer ABI; no pointers in history records. Validated before use.
struct PerfRow { uint64_t id; double x,y,phase; int32_t count; uint64_t neighbors[64]; };
struct PerfFrame { int32_t index,count,sites; PerfRow rows[64]; gm_drive drives[8]; };
extern "C" {
const char* gp_batch(void* medium, GSWorld* world, const PerfFrame* frames, int count,
                    int index, const uint64_t* ids, const double* death, int n,
                    const double* novelty, const int32_t* assignment,
                    const double* sites, int steps, double coverage_start);
// One-step synthetic endpoint: supplied drives, optionally plasticity/timers.
const char* gp_contract(void* medium, const PerfFrame* frames, int count, int index,
                       const uint64_t* ids, const double* death, int n,
                       const double* novelty, const gm_drive* drives, int nd, int adapt);
}

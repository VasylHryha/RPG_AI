#ifndef GROWING_MEDIUM_C_H
#define GROWING_MEDIUM_C_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* ABI v1. All structs are plain C; functions return 0 on success, -1 on error.
   No global state. Handle-local error strings live until the next operation.
   A handle must be used by one thread at a time; distinct handles are independent. */
typedef struct {
    double A, B, J, K, eps, radius, geometry_rate;
    int32_t k, distance_weighted, window, min_samples;
} gm_params;
typedef struct { uint64_t id; double x, y, phase, rate, born; int32_t silent; } gm_element;
typedef struct { uint64_t id; double x, y, phase, rate, strength, width, reach; } gm_drive;
typedef struct {
    double L_on, L_off, S_split, T_nov, T_split, T_death;
    double growth_period, T_protect, split_offset, c_e, c_c, C_max;
    double E_need, T_need, epsilon_U;
    int32_t N_max, reward_arm, utility_checks;
} gm_growth;
typedef struct { double lock, strain, phase1, phase2; int32_t samples; } gm_measure;
typedef struct { uint64_t id; double x, y, phase, rate, error; } gm_need;
void* gm_create(uint64_t seed, const gm_params* params);
void gm_destroy(void* handle);
void* gm_clone(const void* handle);
const char* gm_error(const void* handle);
int gm_count(const void* handle);
double gm_time(const void* handle);
int gm_elements(void* handle, gm_element* output, int capacity);
int gm_add(void* handle, double x, double y, double phase, double rate, uint64_t* id);
int gm_set_element(void* handle, uint64_t id, double x, double y, double phase, double rate);
int gm_remove(void* handle, uint64_t id);
int gm_split(void* handle, uint64_t id, double phase1, double phase2, double offset, uint64_t* ids);
int gm_silence(void* handle, uint64_t id, int silent);
int gm_drives(void* handle, const gm_drive* drives, int count);
int gm_rhs(void* handle, double* output_xyz, int capacity);
/* Diagnostic includes masked padding: shape N x min(k,N-1), like numpy C4. */
int gm_neighbors(void* handle, int32_t* indices, double* masks, double* inverse_counts, int capacity);
int gm_step(void* handle, double dt);
int gm_observe(void* handle);
int gm_readout(void* handle, double x, double y, double width, double reach, double* amplitude_phase);
int gm_plv(void* handle, uint64_t i, uint64_t j, int drive_j, double* value);
int gm_measure_element(void* handle, uint64_t id, gm_measure* output);
int gm_groups(void* handle, double threshold, double link_factor, int32_t* labels, int capacity);
int gm_cost(void* handle, double c_e, double c_c, double* count_couplings_cost);
int gm_configure_growth(void* handle, const gm_growth* config);
int gm_utility(void* handle, uint64_t id, double value);
int gm_needs(void* handle, const gm_need* needs, int count);
int gm_apply_growth(void* handle);
/* Size query when output==NULL. Save contains parameters, elements, drives,
   history, rule timers, utility, need regions, RNG and complete event log. */
size_t gm_save(void* handle, void* output, size_t capacity);
void* gm_load(const void* bytes, size_t size);
size_t gm_events(void* handle, char* output, size_t capacity);
#ifdef __cplusplus
}
#endif
#endif

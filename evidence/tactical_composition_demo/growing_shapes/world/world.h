#ifndef GROWING_SHAPES_WORLD_H
#define GROWING_SHAPES_WORLD_H
#include <stdint.h>

/* ABI v1. All angles radians in [-pi, pi], distances arena units, time seconds.
 * Opaque handles own all mutable state; distinct handles may run concurrently.
 * Do not use a handle concurrently or after destruction. No external dependencies. */
#ifdef __cplusplus
extern "C" {
#endif
enum { GS_ABI_VERSION = 1, GS_MAX_ENEMIES = 8, GS_ALLOW_JUDGING = 1 };
enum GSTask { GS_PERCEIVE, GS_MOVE, GS_REMEMBER, GS_CHOOSE,
              GS_CHASE, GS_PURSUIT, GS_FOCUS_FIRE, GS_REMEMBER_STATIC, GS_TASK_COUNT };
enum GSNamespace { GS_DEV, GS_VALIDATION, GS_JUDGING };
enum GSPolicyKind { GS_REFERENCE, GS_RANDOM };
enum GSStatus { GS_OK, GS_BAD_ARGUMENT, GS_JUDGING_DENIED,
                GS_BAD_ACTION, GS_EPISODE_DONE };
typedef struct GSWorld GSWorld;
typedef struct GSPolicy GSPolicy;

typedef struct {
    int32_t id, visible;
    double dx, dy, angle, distance, vx, vy, hp;
} GSEnemy;

typedef struct {
    int32_t task, step, horizon, done, enemy_count, mode;
    double dt, half_size, agent_x, agent_y;
    /* Only MOVE supplies target_angle/target_distance. mode: 0 approach, 1 keep. */
    double target_angle, target_distance, desired_range;
    /* Only PURSUIT supplies the rectangle (vision only; movement is unobstructed). */
    double occluder_xmin, occluder_xmax, occluder_ymin, occluder_ymax;
    GSEnemy enemies[GS_MAX_ENEMIES];
} GSObservation;

typedef struct {
    double angle;
    /* PERCEIVE: estimated distance [0, sqrt(800)]; all others: speed [0,1].
     * REMEMBER/REMEMBER_STATIC/CHOOSE ignore speed and never move; PERCEIVE never moves. */
    double magnitude;
    /* CHOOSE/FOCUS_FIRE require an existing live id; every other task requires -1. */
    int32_t choice;
} GSAction;

typedef struct {
    int32_t steps, hidden_steps, invalid_actions, done;
    double angular_error, distance_error, goal_error, settle_seconds;
    double correct_choice_rate, damage_per_second, in_range_rate;
} GSScore;

typedef struct { int32_t episodes; GSScore mean; } GSEvaluation;

int32_t gs_abi_version(void);
/* sizeof checks defend ctypes layout. type: 0 observation, 1 action, 2 score,
 * 3 evaluation, 4 enemy. Returns 0 for unknown type. */
uint32_t gs_struct_size(int32_t type);
int32_t gs_create(int32_t task, int32_t seed_namespace, uint64_t seed,
                  uint32_t flags, GSWorld **out);
void gs_destroy(GSWorld *world);
int32_t gs_observe(const GSWorld *world, GSObservation *out);
/* Rejection increments invalid_actions once, returns BAD_ACTION and changes no
 * physics, RNG, score accumulators or clock. Fix and resubmit; no clipping.
 * Observation after a valid step describes the next decision. */
int32_t gs_step(GSWorld *world, const GSAction *action);
int32_t gs_score(const GSWorld *world, GSScore *out);
/* Evaluator metadata, deliberately absent from policy observations. */
int32_t gs_seed_tag(const GSWorld *world, uint64_t *out);
int32_t gs_policy_create(int32_t task, int32_t seed_namespace, uint64_t seed,
                         int32_t kind, uint32_t flags, GSPolicy **out);
void gs_policy_destroy(GSPolicy *policy);
/* Policies consume only a copied observation, never a world handle. One call
 * per decision in increasing step order; reuse requires a fresh policy. */
int32_t gs_policy_action(GSPolicy *policy, const GSObservation *observation,
                         GSAction *out);
/* Fast native rollout; no learning. Consecutive seed indices, namespace gated.
 * This convenience endpoint is never a recorded-experiment runner. */
int32_t gs_evaluate(int32_t task, int32_t seed_namespace, uint64_t first_seed,
                    int32_t episodes, int32_t kind, uint32_t flags,
                    GSEvaluation *out);
#ifdef __cplusplus
}
#endif
#endif

#include "world.h"
#include <cassert>
#include <cmath>
#include <cstring>
#include <iostream>
#include <limits>

int main() {
    static_assert(GS_MAX_ENEMIES==8, "ABI capacity");
    assert(gs_abi_version()==1);
    assert(gs_struct_size(0)==sizeof(GSObservation));
    assert(gs_struct_size(1)==sizeof(GSAction));
    assert(gs_struct_size(2)==sizeof(GSScore));
    assert(gs_struct_size(3)==sizeof(GSEvaluation));
    assert(gs_struct_size(4)==sizeof(GSEnemy));
    assert(gs_struct_size(5)==0);
    assert(gs_create(0,0,0,0,nullptr)==GS_BAD_ARGUMENT);
    assert(gs_observe(nullptr,nullptr)==GS_BAD_ARGUMENT);
    assert(gs_step(nullptr,nullptr)==GS_BAD_ARGUMENT);
    assert(gs_score(nullptr,nullptr)==GS_BAD_ARGUMENT);
    assert(gs_seed_tag(nullptr,nullptr)==GS_BAD_ARGUMENT);
    gs_destroy(nullptr); gs_policy_destroy(nullptr);
    GSWorld *w=nullptr;
    GSPolicy *p=nullptr;
    GSEvaluation evaluation{};
    assert(gs_create(GS_PERCEIVE,GS_JUDGING,0,0,&w)==GS_JUDGING_DENIED && !w);
    assert(gs_policy_create(GS_PERCEIVE,GS_JUDGING,0,GS_RANDOM,0,&p)==GS_JUDGING_DENIED && !p);
    assert(gs_evaluate(GS_PERCEIVE,GS_JUDGING,0,1,GS_RANDOM,0,&evaluation)==GS_JUDGING_DENIED);
    assert(gs_create(-1,GS_DEV,0,0,&w)==GS_BAD_ARGUMENT && !w);
    assert(gs_create(GS_TASK_COUNT,GS_DEV,0,0,&w)==GS_BAD_ARGUMENT && !w);
    assert(gs_create(0,3,0,0,&w)==GS_BAD_ARGUMENT && !w);
    assert(gs_create(0,0,0,2,&w)==GS_BAD_ARGUMENT && !w);
    assert(gs_policy_create(0,0,0,2,0,&p)==GS_BAD_ARGUMENT && !p);
    assert(gs_policy_action(nullptr,nullptr,nullptr)==GS_BAD_ARGUMENT);
    assert(gs_evaluate(0,0,0,0,0,0,&evaluation)==GS_BAD_ARGUMENT);
    assert(gs_evaluate(0,0,std::numeric_limits<uint64_t>::max(),2,0,0,&evaluation)==GS_BAD_ARGUMENT);

    // Namespace domain separation without accessing judging entropy.
    uint64_t dev=0,validation=0;
    assert(gs_create(0,GS_DEV,19,0,&w)==GS_OK);
    assert(gs_seed_tag(w,&dev)==GS_OK); gs_destroy(w);
    assert(gs_create(0,GS_VALIDATION,19,0,&w)==GS_OK);
    assert(gs_seed_tag(w,&validation)==GS_OK); gs_destroy(w);
    assert(dev!=validation);

    for (int task=0;task<GS_TASK_COUNT;++task) {
        assert(gs_create(task,GS_DEV,83,0,&w)==GS_OK);
        assert(gs_policy_create(task,GS_DEV,83,GS_REFERENCE,0,&p)==GS_OK);
        GSObservation before{},after{}; GSScore score{};
        assert(gs_observe(w,&before)==GS_OK);
        GSAction bad{std::numeric_limits<double>::quiet_NaN(),0,-1};
        assert(gs_step(w,&bad)==GS_BAD_ACTION);
        assert(gs_observe(w,&after)==GS_OK);
        assert(std::memcmp(&before,&after,sizeof(before))==0);
        assert(gs_score(w,&score)==GS_OK && score.invalid_actions==1 && score.steps==0);
        assert(gs_step(w,nullptr)==GS_BAD_ARGUMENT);
        for (int step=0;step<before.horizon;++step) {
            GSObservation o{}; GSAction a{};
            assert(gs_observe(w,&o)==GS_OK && o.step==step);
            assert(gs_policy_action(p,&o,&a)==GS_OK);
            assert(gs_step(w,&a)==GS_OK);
            if ((task==GS_REMEMBER || task==GS_REMEMBER_STATIC) && step>=40) {
                const auto &e=o.enemies[0];
                assert(!e.visible && e.dx==0 && e.dy==0 && e.angle==0 && e.distance==0);
                assert(e.vx==0 && e.vy==0 && e.hp==0);
            }
        }
        assert(gs_observe(w,&after)==GS_OK && after.done && after.step==160);
        assert(gs_score(w,&score)==GS_OK && score.done && score.steps==160);
        GSAction a{0,0,-1}; assert(gs_step(w,&a)==GS_EPISODE_DONE);
        if (task==GS_REMEMBER || task==GS_REMEMBER_STATIC) assert(score.hidden_steps==120 && score.angular_error<1e-10);
        if (task==GS_CHOOSE) assert(score.correct_choice_rate==1);
        gs_destroy(w); gs_policy_destroy(p);
    }
    // Hand-computed public policy cases: exact ties use the lowest id,
    // weakest in range wins, all outside falls back to nearest.
    assert(gs_policy_create(GS_CHOOSE,GS_DEV,0,GS_REFERENCE,0,&p)==GS_OK);
    GSObservation o{}; o.task=GS_CHOOSE; o.dt=0.1; o.enemy_count=3; o.desired_range=2.5;
    o.enemies[0]={0,1,1,0,0,1,0,0,90};
    o.enemies[1]={1,1,2,0,0,2,0,0,10};
    o.enemies[2]={2,1,3,0,0,3,0,0,1};
    GSAction a{}; assert(gs_policy_action(p,&o,&a)==GS_OK && a.choice==1);
    ++o.step; o.desired_range=0.5;
    assert(gs_policy_action(p,&o,&a)==GS_OK && a.choice==0);
    ++o.step; o.enemies[1].distance=1;
    assert(gs_policy_action(p,&o,&a)==GS_OK && a.choice==0);
    ++o.step; o.desired_range=2.5; o.enemies[0].hp=10;
    assert(gs_policy_action(p,&o,&a)==GS_OK && a.choice==0);
    // Duplicate step calls fail explicitly instead of advancing memory twice.
    assert(gs_policy_action(p,&o,&a)==GS_BAD_ARGUMENT);
    gs_policy_destroy(p);
    std::cout << "native world contract: PASS (8 tasks; no judging access)\n";
}

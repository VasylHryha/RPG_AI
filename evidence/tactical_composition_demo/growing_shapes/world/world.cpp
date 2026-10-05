#include "world.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <new>

namespace {
constexpr double pi = 3.14159265358979323846;
constexpr double half_size = 10.0, dt = 0.1, max_speed = 3.0;
constexpr double diagonal = 28.284271247461902;
constexpr int horizon = 160, visible_period = 40, settle_window = 10;
constexpr double tolerance = 0.25, attack_range = 2.5, damage_rate = 1.0;
constexpr std::array<uint64_t, 3> namespace_salt = {
    0x4d824731a9c26b05ULL, 0xf769308b125cd4eaULL, 0x821ce5a067d9b34fULL};

uint64_t mix(uint64_t x) {
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}
uint64_t tag(int task, int ns, uint64_t seed) {
    return mix(seed ^ namespace_salt[ns] ^ mix(uint64_t(task) + 0x37bf90a1ULL));
}
struct RNG {
    uint64_t state;
    uint64_t next() { return mix(state += 0x9e3779b97f4a7c15ULL); }
    double unit() { return double(next() >> 11) * 0x1.0p-53; }
    double uniform(double lo, double hi) { return lo + (hi-lo)*unit(); }
    int integer(int n) { return int(next() % uint64_t(n)); }
};
double angle(double x, double y) { return std::atan2(y, x); }
double wrap(double x) { return std::remainder(x, 2*pi); }
double angular_error(double a, double b) { return std::abs(wrap(a-b)); }
int arguments(int task, int ns, uint32_t flags) {
    if (task < 0 || task >= GS_TASK_COUNT || ns < GS_DEV || ns > GS_JUDGING ||
        (flags & ~uint32_t(GS_ALLOW_JUDGING))) return GS_BAD_ARGUMENT;
    if (ns == GS_JUDGING && !(flags & GS_ALLOW_JUDGING)) return GS_JUDGING_DENIED;
    return GS_OK;
}
void reflect(double &position, double &velocity) {
    if (position > half_size) { position = 2*half_size-position; velocity = -std::abs(velocity); }
    if (position < -half_size) { position = -2*half_size-position; velocity = std::abs(velocity); }
}
bool occluded(double ax, double ay, double bx, double by) {
    // Closed segment vs rectangle [-1.5,1.5] x [-2,2], including endpoints.
    double lo = 0, hi = 1;
    const double a[2] = {ax,ay}, d[2] = {bx-ax,by-ay};
    const double mn[2] = {-1.5,-2}, mx[2] = {1.5,2};
    for (int k = 0; k < 2; ++k) {
        if (std::abs(d[k]) < 1e-12) {
            if (a[k] < mn[k] || a[k] > mx[k]) return false;
        } else {
            double t0 = (mn[k]-a[k])/d[k], t1 = (mx[k]-a[k])/d[k];
            if (t0 > t1) std::swap(t0,t1);
            lo = std::max(lo,t0); hi = std::min(hi,t1);
            if (lo > hi) return false;
        }
    }
    return true;
}
struct Entity { double x=0, y=0, vx=0, vy=0, hp=0; };
}

struct GSWorld {
    int task, step=0, count=0, mode=0, invalid=0, hidden=0, streak=0;
    uint64_t seed_tag;
    double x=0, y=0, tx=0, ty=0, desired=0;
    std::array<Entity, GS_MAX_ENEMIES> enemies{};
    double sum_angle=0, sum_distance=0, sum_goal=0, correct=0, damage=0, in_range=0;
    double settle=horizon*dt;

    GSWorld(int t, int ns, uint64_t seed): task(t), seed_tag(tag(t,ns,seed)) {
        RNG rng{seed_tag};
        x = rng.uniform(-1,1); y = rng.uniform(-1,1);
        auto place = [&](Entity &e, double rlo, double rhi, bool moving) {
            double a=rng.uniform(-pi,pi), r=rng.uniform(rlo,rhi);
            e.x=x+r*std::cos(a); e.y=y+r*std::sin(a);
            e.hp=rng.uniform(10,100);
            if (moving) {
                double va=rng.uniform(-pi,pi), speed=rng.uniform(0.25,0.65);
                e.vx=speed*std::cos(va); e.vy=speed*std::sin(va);
            }
        };
        if (task == GS_MOVE) {
            mode=rng.integer(2); desired=mode ? rng.uniform(1.5,3.5) : 0;
            double a=rng.uniform(-pi,pi);
            double r=(mode && rng.integer(2)) ? rng.uniform(0.2,1.0) : rng.uniform(4,8);
            tx=x+r*std::cos(a); ty=y+r*std::sin(a);
        } else if (task == GS_PURSUIT) {
            count=1; desired=2;
            x=-8; y=rng.uniform(0.8,1.4);
            enemies[0]={rng.uniform(-5,-4),rng.uniform(-0.6,0.6),rng.uniform(0.55,0.85),0,100};
        } else {
            count=(task == GS_REMEMBER || task == GS_REMEMBER_STATIC) ? 1 : 3+rng.integer(6);
            desired=(task == GS_CHASE) ? 2 :
                    ((task == GS_CHOOSE || task == GS_FOCUS_FIRE) ? attack_range : 0);
            bool inside=rng.integer(2) == 0;
            for (int i=0; i<count; ++i) {
                bool moving=task == GS_PERCEIVE || task == GS_REMEMBER || task == GS_CHASE;
                double rlo=(task == GS_REMEMBER || task == GS_REMEMBER_STATIC) ? 3 : 1.5;
                double rhi=(task == GS_REMEMBER || task == GS_REMEMBER_STATIC) ? 6 : 8;
                if (task == GS_CHOOSE) {
                    rlo=inside && i < 2 ? 0.5 : 3.5;
                    rhi=inside && i < 2 ? 2.0 : 8;
                }
                if (task == GS_FOCUS_FIRE) { rlo=3; rhi=8; }
                place(enemies[i],rlo,rhi,moving);
                // Focus has no deaths (min HP 30 > max episode damage 16).
                if (task == GS_FOCUS_FIRE) enemies[i].hp=rng.uniform(30,80);
            }
        }
    }
    double distance(int i) const { return std::hypot(enemies[i].x-x,enemies[i].y-y); }
    int nearest() const {
        int best=0;
        for (int i=1;i<count;++i) if (distance(i) < distance(best)) best=i;
        return best; // Exact ties resolved by lowest id.
    }
    bool visible(int i) const {
        if (task == GS_REMEMBER || task == GS_REMEMBER_STATIC) return step < visible_period;
        if (task == GS_PURSUIT) return !occluded(x,y,enemies[i].x,enemies[i].y);
        return true;
    }
    int correct_target() const {
        int best=-1;
        for (int i=0;i<count;++i) if (enemies[i].hp > 0 && distance(i) <= desired) {
            if (best < 0 || enemies[i].hp < enemies[best].hp) best=i;
        }
        return best < 0 ? nearest() : best;
    }
    void observe(GSObservation &o) const {
        o={}; o.task=task; o.step=step; o.horizon=horizon; o.done=step==horizon;
        o.enemy_count=count; o.mode=mode; o.dt=dt; o.half_size=half_size;
        o.agent_x=x; o.agent_y=y; o.desired_range=desired;
        if (task == GS_MOVE) {
            o.target_angle=angle(tx-x,ty-y); o.target_distance=std::hypot(tx-x,ty-y);
        }
        if (task == GS_PURSUIT) {
            o.occluder_xmin=-1.5; o.occluder_xmax=1.5;
            o.occluder_ymin=-2; o.occluder_ymax=2;
        }
        for (int i=0;i<count;++i) {
            auto &e=o.enemies[i]; e.id=i; e.visible=visible(i);
            // Redaction is applied at source, also for native scripted policies.
            if (e.visible) {
                e.dx=enemies[i].x-x; e.dy=enemies[i].y-y;
                e.distance=distance(i); e.angle=angle(e.dx,e.dy);
                e.vx=enemies[i].vx; e.vy=enemies[i].vy; e.hp=enemies[i].hp;
            }
        }
    }
    bool valid(const GSAction &a) const {
        double limit=task == GS_PERCEIVE ? diagonal : 1;
        if (!std::isfinite(a.angle) || std::abs(a.angle)>pi ||
            !std::isfinite(a.magnitude) || a.magnitude<0 || a.magnitude>limit) return false;
        if (task == GS_CHOOSE || task == GS_FOCUS_FIRE)
            return a.choice>=0 && a.choice<count && enemies[a.choice].hp>0;
        return a.choice == -1;
    }
    int advance(const GSAction &a) {
        if (step==horizon) return GS_EPISODE_DONE;
        if (!valid(a)) { ++invalid; return GS_BAD_ACTION; }
        if (task == GS_PERCEIVE) {
            int i=nearest();
            sum_angle+=angular_error(a.angle,angle(enemies[i].x-x,enemies[i].y-y));
            sum_distance+=std::abs(a.magnitude-distance(i));
        }
        if ((task == GS_REMEMBER || task == GS_REMEMBER_STATIC) && !visible(0)) {
            ++hidden; sum_angle+=angular_error(a.angle,angle(enemies[0].x-x,enemies[0].y-y));
        }
        if (task == GS_CHOOSE) correct+=a.choice == correct_target();
        if (task == GS_PURSUIT && !visible(0)) ++hidden;
        if (task == GS_MOVE || task == GS_CHASE || task == GS_PURSUIT || task == GS_FOCUS_FIRE) {
            x=std::clamp(x+max_speed*dt*a.magnitude*std::cos(a.angle),-half_size,half_size);
            y=std::clamp(y+max_speed*dt*a.magnitude*std::sin(a.angle),-half_size,half_size);
        }
        for (int i=0;i<count;++i) {
            auto &e=enemies[i]; e.x+=e.vx*dt; e.y+=e.vy*dt;
            reflect(e.x,e.vx); reflect(e.y,e.vy);
        }
        double error=0;
        if (task == GS_MOVE) error=std::abs(std::hypot(tx-x,ty-y)-desired);
        if (task == GS_CHASE || task == GS_PURSUIT)
            error=std::abs(distance(task == GS_CHASE ? nearest() : 0)-desired);
        if (task == GS_MOVE || task == GS_CHASE || task == GS_PURSUIT) {
            sum_goal+=error; in_range+=error<=tolerance;
            streak=error<=tolerance ? streak+1 : 0;
            if (streak==settle_window && settle==horizon*dt)
                settle=(step+2-settle_window)*dt; // Time of first sample in verified 1s window.
        }
        if (task == GS_FOCUS_FIRE && distance(a.choice)<=desired) {
            double hit=std::min(enemies[a.choice].hp,damage_rate*dt);
            enemies[a.choice].hp-=hit; damage+=hit; in_range+=1;
        }
        ++step; return GS_OK;
    }
    GSScore score() const {
        GSScore s{}; s.steps=step; s.hidden_steps=hidden; s.invalid_actions=invalid;
        s.done=step==horizon;
        if (step>0) {
            s.angular_error=sum_angle/((task == GS_REMEMBER || task == GS_REMEMBER_STATIC) ? std::max(1,hidden) : step);
            s.distance_error=sum_distance/step; s.goal_error=sum_goal/step;
            s.correct_choice_rate=correct/step; s.damage_per_second=damage/(step*dt);
            s.in_range_rate=in_range/step;
        }
        s.settle_seconds=settle; return s;
    }
};

struct GSPolicy {
    int task, kind, last_step=-1, tracked_id=-1;
    RNG rng;
    bool tracking=false;
    double px=0, py=0, vx=0, vy=0;
    GSPolicy(int t,int ns,uint64_t seed,int k):task(t),kind(k),
        rng{mix(tag(t,ns,seed)^0xc69f7e20a83db451ULL)} {}

    GSAction action(const GSObservation &o) {
        GSAction a{0,0,-1};
        if (kind==GS_RANDOM) {
            a.angle=rng.uniform(-pi,pi);
            a.magnitude=rng.uniform(0,task==GS_PERCEIVE ? diagonal : 1);
            if (task==GS_CHOOSE || task==GS_FOCUS_FIRE) a.choice=rng.integer(o.enemy_count);
            return a;
        }
        if (task==GS_MOVE) {
            motion(o.target_angle,o.target_distance,o.desired_range,o,a);
            return a;
        }
        int best=-1;
        for (int i=0;i<o.enemy_count;++i) if (o.enemies[i].visible && o.enemies[i].hp>0) {
            if (best<0 || o.enemies[i].distance<o.enemies[best].distance) best=i;
        }
        if (task==GS_CHOOSE) {
            int weak=-1;
            for (int i=0;i<o.enemy_count;++i) if (o.enemies[i].visible &&
                o.enemies[i].hp>0 && o.enemies[i].distance<=o.desired_range) {
                if (weak<0 || o.enemies[i].hp<o.enemies[weak].hp) weak=i;
            }
            a.choice=o.enemies[weak<0 ? best : weak].id; return a;
        }
        if (task==GS_FOCUS_FIRE) {
            // Sticky nearest target: travel once and maintain damage rather than
            // switching to a distant weak target. Choice rule applies to CHOOSE only.
            for (int i=0;i<o.enemy_count;++i)
                if (o.enemies[i].visible && o.enemies[i].id==tracked_id && o.enemies[i].hp>0) best=i;
        }
        if (best>=0) {
            const auto &e=o.enemies[best];
            px=o.agent_x+e.dx; py=o.agent_y+e.dy; vx=e.vx; vy=e.vy;
            tracking=true; tracked_id=e.id;
        } else if (tracking && task != GS_REMEMBER_STATIC) {
            px+=vx*o.dt; py+=vy*o.dt; reflect(px,vx); reflect(py,vy);
        }
        double dx=px-o.agent_x, dy=py-o.agent_y;
        a.angle=tracking ? angle(dx,dy) : 0;
        if (task==GS_PERCEIVE) a.magnitude=std::hypot(dx,dy);
        if (task==GS_CHASE || task==GS_PURSUIT || task==GS_FOCUS_FIRE) {
            // One-step velocity prediction is permissible from visible observations
            // or policy memory. Fixed .3 step length follows the observed dt.
            double nx=px+vx*o.dt, ny=py+vy*o.dt, nvx=vx, nvy=vy;
            reflect(nx,nvx); reflect(ny,nvy);
            double target=task==GS_FOCUS_FIRE ? o.desired_range-0.1 : o.desired_range;
            motion(angle(nx-o.agent_x,ny-o.agent_y),
                   std::hypot(nx-o.agent_x,ny-o.agent_y),target,o,a);
            if (task==GS_FOCUS_FIRE) a.choice=tracked_id;
        }
        return a;
    }
    static void motion(double heading,double distance,double desired,
                       const GSObservation &o,GSAction &a) {
        double error=distance-desired;
        a.angle=wrap(heading+(error<0 ? pi : 0));
        a.magnitude=std::min(1.0,std::abs(error)/(max_speed*o.dt));
    }
};

extern "C" {
int32_t gs_abi_version(void) { return GS_ABI_VERSION; }
uint32_t gs_struct_size(int32_t type) {
    switch(type) {
        case 0:return sizeof(GSObservation); case 1:return sizeof(GSAction);
        case 2:return sizeof(GSScore); case 3:return sizeof(GSEvaluation);
        case 4:return sizeof(GSEnemy); default:return 0;
    }
}
int32_t gs_create(int32_t task,int32_t ns,uint64_t seed,uint32_t flags,GSWorld **out) {
    if (!out) return GS_BAD_ARGUMENT;
    *out=nullptr; int status=arguments(task,ns,flags); if (status) return status;
    *out=new(std::nothrow) GSWorld(task,ns,seed); return *out ? GS_OK : GS_BAD_ARGUMENT;
}
void gs_destroy(GSWorld *w) { delete w; }
int32_t gs_observe(const GSWorld *w,GSObservation *out) {
    if (!w || !out) return GS_BAD_ARGUMENT;
    w->observe(*out); return GS_OK;
}
int32_t gs_step(GSWorld *w,const GSAction *a) {
    if (!w || !a) return GS_BAD_ARGUMENT;
    return w->advance(*a);
}
int32_t gs_score(const GSWorld *w,GSScore *out) {
    if (!w || !out) return GS_BAD_ARGUMENT;
    *out=w->score(); return GS_OK;
}
int32_t gs_seed_tag(const GSWorld *w,uint64_t *out) {
    if (!w || !out) return GS_BAD_ARGUMENT;
    *out=w->seed_tag; return GS_OK;
}
int32_t gs_policy_create(int32_t task,int32_t ns,uint64_t seed,int32_t kind,
                         uint32_t flags,GSPolicy **out) {
    if (!out) return GS_BAD_ARGUMENT;
    *out=nullptr; int status=arguments(task,ns,flags); if (status) return status;
    if (kind<GS_REFERENCE || kind>GS_RANDOM) return GS_BAD_ARGUMENT;
    *out=new(std::nothrow) GSPolicy(task,ns,seed,kind); return *out ? GS_OK : GS_BAD_ARGUMENT;
}
void gs_policy_destroy(GSPolicy *p) { delete p; }
int32_t gs_policy_action(GSPolicy *p,const GSObservation *o,GSAction *out) {
    if (!p || !o || !out || o->task!=p->task || o->done || o->step!=p->last_step+1 ||
        o->enemy_count<0 || o->enemy_count>GS_MAX_ENEMIES || !std::isfinite(o->dt) || o->dt<=0)
        return GS_BAD_ARGUMENT;
    // Observations are supplied by gs_observe. Check the minimal semantic shape
    // before policy indexing; fabricated observations are not a simulation API.
    if (p->task!=GS_MOVE) {
        bool seen=false;
        for (int i=0;i<o->enemy_count;++i) seen |= o->enemies[i].visible && o->enemies[i].hp>0;
        if (!seen && p->task!=GS_REMEMBER && p->task!=GS_REMEMBER_STATIC && p->task!=GS_PURSUIT) return GS_BAD_ARGUMENT;
        if (o->enemy_count==0) return GS_BAD_ARGUMENT;
    }
    *out=p->action(*o); p->last_step=o->step; return GS_OK;
}
int32_t gs_evaluate(int32_t task,int32_t ns,uint64_t seed,int32_t episodes,
                    int32_t kind,uint32_t flags,GSEvaluation *out) {
    if (!out || episodes<=0 || episodes>1000000 ||
        uint64_t(episodes-1)>std::numeric_limits<uint64_t>::max()-seed) return GS_BAD_ARGUMENT;
    *out={}; int status=arguments(task,ns,flags); if (status) return status;
    if (kind<GS_REFERENCE || kind>GS_RANDOM) return GS_BAD_ARGUMENT;
    double sa=0,sd=0,sg=0,ss=0,sc=0,sp=0,sr=0;
    int64_t hidden=0;
    for (int i=0;i<episodes;++i) {
        GSWorld w(task,ns,seed+uint64_t(i)); GSPolicy p(task,ns,seed+uint64_t(i),kind);
        for (int j=0;j<horizon;++j) {
            GSObservation o; w.observe(o); GSAction a=p.action(o);
            if (w.advance(a)!=GS_OK) return GS_BAD_ACTION;
        }
        GSScore s=w.score(); sa+=s.angular_error; sd+=s.distance_error; sg+=s.goal_error;
        ss+=s.settle_seconds; sc+=s.correct_choice_rate; sp+=s.damage_per_second;
        sr+=s.in_range_rate; hidden+=s.hidden_steps;
    }
    out->episodes=episodes; auto &s=out->mean; s.steps=horizon; s.done=1;
    s.hidden_steps=int32_t(hidden/episodes); // Integer mean, truncated; errors are episode means.
    s.angular_error=sa/episodes; s.distance_error=sd/episodes; s.goal_error=sg/episodes;
    s.settle_seconds=ss/episodes; s.correct_choice_rate=sc/episodes;
    s.damage_per_second=sp/episodes; s.in_range_rate=sr/episodes; return GS_OK;
}
}

// CPU float64 synchronous local Euler dynamics. No direct solver or gradient training.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

extern "C" {
struct Cost {
    uint64_t phases, sweeps, bound_edges, force_edges, force_nodes, node_updates;
    uint64_t learning_edges, committed, refused, saturated;
    double max_force, update_norm;
};

// All forces are computed from the same old activity vector before ANY node moves.
int c2_relax(int n, int m, const int *a, const int *b, const double *g,
             int p, int q, int out, const double *x, double target, double beta,
             double lambda, double tolerance, int limit, double *u, Cost *cost) {
    std::vector<double> degree(n, 0.0), force(n);
    for (int e=0; e<m; ++e) { degree[a[e]]+=g[e]; degree[b[e]]+=g[e]; }
    cost->phases++; cost->bound_edges+=m;
    const double dt=0.25/(2.0 * *std::max_element(degree.begin(),degree.end())+lambda+beta);
    u[p]=x[0]; u[q]=x[1];
    for (int step=0; step<=limit; ++step) {
        for (int i=0; i<n; ++i) force[i]=lambda*u[i];
        for (int e=0; e<m; ++e) {
            const double current=g[e]*(u[a[e]]-u[b[e]]);
            force[a[e]]+=current; force[b[e]]-=current;
        }
        force[out]+=beta*(u[out]-target); force[p]=force[q]=0.0;
        cost->force_edges+=m; cost->force_nodes+=n;
        double maximum=0.0;
        for (int i=0; i<n; ++i) {
            if (!std::isfinite(force[i]) || !std::isfinite(u[i])) return 2;
            maximum=std::max(maximum,std::abs(force[i]));
        }
        cost->max_force=maximum;
        if (maximum<tolerance) return 0;
        if (step==limit) return 1;
        for (int i=0; i<n; ++i) if (i!=p && i!=q) u[i]-=dt*force[i];
        cost->node_updates+=n-2; cost->sweeps++;
    }
    return 1;
}

// Per-example transaction: both phases use g_old; only then write proposed g.
int c2_learn(int n, int m, const int *a, const int *b, double *g,
             int p, int q, int out, const double *x, double y, double beta,
             double lambda, double tolerance, int limit, double eta,
             int feedback, double *free_state, double *nudged_state, Cost *cost) {
    std::fill(free_state,free_state+n,0.0);
    int status=c2_relax(n,m,a,b,g,p,q,out,x,0.0,0.0,lambda,tolerance,limit,free_state,cost);
    if (status) { cost->refused++; return status; }
    std::copy(free_state,free_state+n,nudged_state);
    // Removing feedback means the nudge requests the already attained output.
    const double training_target=feedback ? y : free_state[out];
    status=c2_relax(n,m,a,b,g,p,q,out,x,training_target,beta,lambda,tolerance,limit,nudged_state,cost);
    if (status) { cost->refused++; return status; }
    std::vector<double> proposal(m);
    double square_norm=0.0;
    for (int e=0; e<m; ++e) {
        cost->learning_edges++;
        const double df=free_state[a[e]]-free_state[b[e]];
        const double dn=nudged_state[a[e]]-nudged_state[b[e]];
        const double value=g[e]+eta/(2.0*beta)*(df*df-dn*dn);
        if (!std::isfinite(value)) { cost->refused++; return 2; }
        proposal[e]=std::min(5.0,std::max(0.05,value));
        cost->saturated+=(proposal[e]==0.05 || proposal[e]==5.0);
        square_norm+=(proposal[e]-g[e])*(proposal[e]-g[e]);
    }
    cost->committed++;
    cost->update_norm+=std::sqrt(square_norm);
    std::copy(proposal.begin(),proposal.end(),g);
    return 0;
}
}

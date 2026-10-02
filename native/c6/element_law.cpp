// C4's element law, float64 only. Build with the pin in tools/build_c6.py.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <numeric>
#include <vector>

static_assert(sizeof(double) == 8 && std::numeric_limits<double>::is_iec559,
              "C6 requires IEEE float64");

extern "C" {
struct C6Params {
    double A, B, J, K, eps;
    int distance_weighted, frozen_phase_topology;
};
}

namespace {
struct Topology {
    std::vector<int64_t> idx;
    std::vector<double> mask, inv;
    Topology(int64_t elements, int64_t k)
        : idx(elements * k), mask(elements * k), inv(elements) {}
};

// NumPy's contiguous float64 reduction uses eight lanes and pairwise blocks.
double sum(const double* a, int64_t n) {
    if (n < 8) {
        double s = -0.0;
        for (int64_t i = 0; i < n; ++i) s += a[i];
        return s;
    }
    if (n <= 128) {
        double r[8];
        for (int i = 0; i < 8; ++i) r[i] = a[i];
        int64_t i = 8;
        for (; i <= n - 8; i += 8)
            for (int j = 0; j < 8; ++j) r[j] += a[i + j];
        double s = ((r[0] + r[1]) + (r[2] + r[3]))
                 + ((r[4] + r[5]) + (r[6] + r[7]));
        for (; i < n; ++i) s += a[i];
        return s;
    }
    int64_t half = n / 2;
    half -= half % 8;
    return sum(a, half) + sum(a + half, n - half);
}

void neighbors(const double* x, int64_t worlds, int64_t n, int64_t k,
               double radius, Topology& t) {
    std::vector<double> distances(n);
    std::vector<int64_t> order(n);
    for (int64_t b = 0; b < worlds; ++b) {
        for (int64_t i = 0; i < n; ++i) {
            const int64_t e = b * n + i;
            for (int64_t j = 0; j < n; ++j) {
                const int64_t other = b * n + j;
                distances[j] = i == j ? std::numeric_limits<double>::infinity()
                    : std::hypot(x[2 * other] - x[2 * e], x[2 * other + 1] - x[2 * e + 1]);
            }
            std::iota(order.begin(), order.end(), 0);
            const auto less = [&](int64_t a, int64_t b) {
                // Stable NumPy order: finite values, infinities, then NaNs.
                if (std::isnan(distances[a]))
                    return std::isnan(distances[b]) && a < b;
                if (std::isnan(distances[b])) return true;
                return distances[a] < distances[b]
                    || (distances[a] == distances[b] && a < b);
            };
            std::partial_sort(order.begin(), order.begin() + k, order.end(), less);
            double count = 0.0;
            for (int64_t q = 0; q < k; ++q) {
                t.idx[e * k + q] = order[q];
                const double mask = distances[order[q]] < radius ? 1.0 : 0.0;
                t.mask[e * k + q] = mask;
                count += mask;
            }
            t.inv[e] = 1.0 / std::max(count, 1.0);
        }
    }
}

void rhs(const double* x, const double* th, const double* omega,
         const C6Params* params, int64_t worlds, int64_t n, int64_t k,
         const Topology& t, const int64_t* phase_idx, const double* phase_mask,
         const double* phase_inv, double* out_x, double* out_th) {
    std::vector<double> fx(k), fy(k), ft(k);
    for (int64_t b = 0; b < worlds; ++b) {
        const auto& p = params[b];
        for (int64_t i = 0; i < n; ++i) {
            const int64_t e = b * n + i;
            for (int64_t q = 0; q < k; ++q) {
                const int64_t link = e * k + q;
                const int64_t j = b * n + t.idx[link];
                const double dx = x[2 * j] - x[2 * e];
                const double dy = x[2 * j + 1] - x[2 * e + 1];
                double r = std::hypot(dx, dy);
                const double rr = (std::isnan(r) || std::isnan(p.eps))
                    ? std::numeric_limits<double>::quiet_NaN() : std::max(r, p.eps);
                double dth = th[j] - th[e];
                const double radial = (p.A * (1.0 + p.J * std::cos(dth)) - p.B / rr)
                                    * t.mask[link] / rr;
                fx[q] = dx * radial;
                fy[q] = dy * radial;
                double mask = t.mask[link];
                if (p.frozen_phase_topology) {
                    const int64_t pj = b * n + phase_idx[link];
                    r = std::hypot(x[2 * pj] - x[2 * e], x[2 * pj + 1] - x[2 * e + 1]);
                    dth = th[pj] - th[e];
                    mask = phase_mask[link];
                }
                const double w = p.distance_weighted ? std::exp(-r * r) : 1.0;
                ft[q] = p.K * w * std::sin(dth) * mask;
            }
            out_x[2 * e] = sum(fx.data(), k) * t.inv[e];
            out_x[2 * e + 1] = sum(fy.data(), k) * t.inv[e];
            const double inv = p.frozen_phase_topology ? phase_inv[e] : t.inv[e];
            out_th[e] = omega[e] + sum(ft.data(), k) * inv;
        }
    }
}
}  // namespace

extern "C" int c6_neighbors(const double* x, int64_t worlds, int64_t n,
                            int64_t k, double radius, int64_t* idx,
                            double* mask, double* inv) {
    try {
        Topology t(worlds * n, k);
        neighbors(x, worlds, n, k, radius, t);
        std::copy(t.idx.begin(), t.idx.end(), idx);
        std::copy(t.mask.begin(), t.mask.end(), mask);
        std::copy(t.inv.begin(), t.inv.end(), inv);
        return 0;
    } catch (...) { return -1; }
}

// Positive return: first non-finite step. -1: native allocation/other failure.
extern "C" int64_t c6_simulate(
    double* x, double* th, const double* omega, const C6Params* params,
    int64_t worlds, int64_t n, int64_t k, double radius, double dt,
    int64_t steps, int hold_neighbors, const int64_t* phase_idx,
    const double* phase_mask, const double* phase_inv,
    const int64_t* sample_steps, int64_t sample_count,
    double* sample_x, double* sample_th) {
    try {
        const int64_t elements = worlds * n, coords = 2 * elements;
        Topology t(elements, k);
        std::vector<double> stage_x(coords), stage_th(elements);
        std::vector<double> kx[4], kt[4];
        for (int s = 0; s < 4; ++s) {
            kx[s].resize(coords);
            kt[s].resize(elements);
        }
        if (hold_neighbors) neighbors(x, worlds, n, k, radius, t);
        int64_t sample = 0;
        for (int64_t step = 1; step <= steps; ++step) {
            if (!hold_neighbors) neighbors(x, worlds, n, k, radius, t);
            rhs(x, th, omega, params, worlds, n, k, t, phase_idx,
                phase_mask, phase_inv, kx[0].data(), kt[0].data());
            for (int s = 1; s < 4; ++s) {
                const double scale = s == 3 ? dt : 0.5 * dt;
                for (int64_t e = 0; e < coords; ++e)
                    stage_x[e] = x[e] + scale * kx[s - 1][e];
                for (int64_t e = 0; e < elements; ++e)
                    stage_th[e] = th[e] + scale * kt[s - 1][e];
                rhs(stage_x.data(), stage_th.data(), omega, params, worlds, n, k,
                    t, phase_idx, phase_mask, phase_inv, kx[s].data(), kt[s].data());
            }
            for (int64_t e = 0; e < coords; ++e) {
                x[e] += dt / 6.0 * (kx[0][e] + 2 * kx[1][e] + 2 * kx[2][e] + kx[3][e]);
                if (!std::isfinite(x[e])) return step;
            }
            for (int64_t e = 0; e < elements; ++e) {
                th[e] += dt / 6.0 * (kt[0][e] + 2 * kt[1][e] + 2 * kt[2][e] + kt[3][e]);
                if (!std::isfinite(th[e])) return step;
            }
            if (sample < sample_count && step == sample_steps[sample]) {
                std::copy(x, x + coords, sample_x + sample * coords);
                std::copy(th, th + elements, sample_th + sample * elements);
                ++sample;
            }
        }
        return 0;
    } catch (...) { return -1; }
}

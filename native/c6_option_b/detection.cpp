// C4 connected-component semantics for the Option B path. No detector thresholds.
#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>
#include <climits>

extern "C" int option_b_components(int n, const double* x, double link,
                                  const unsigned char* locked, long long* labels) {
    if (n < 0 || n > INT_MAX/2 || !std::isfinite(link) || (n && (!x || !locked || !labels))) return 1;
    try {
        std::vector<double> distances(size_t(n)*n), nearest(n);
        for (int i=0;i<n;i++) {
            nearest[i]=std::numeric_limits<double>::infinity();
            for (int j=0;j<n;j++) {
                double dx=x[2*i]-x[2*j], dy=x[2*i+1]-x[2*j+1];
                double d=i==j?std::numeric_limits<double>::infinity():std::sqrt(dx*dx+dy*dy);
                distances[size_t(i)*n+j]=d;nearest[i]=std::min(nearest[i],d);
            }
            labels[i]=-1;
        }
        if (!n) return 0;
        std::sort(nearest.begin(),nearest.end());
        double median=n%2?nearest[n/2]:(nearest[n/2-1]+nearest[n/2])/2.;
        double threshold=link*median;
        std::vector<int> stack;
        int current=0;
        for (int start=0;start<n;start++) {
            if (labels[start]>=0) continue;
            labels[start]=current;stack.push_back(start);
            while (!stack.empty()) {
                int u=stack.back();stack.pop_back();
                for (int v=0;v<n;v++) {
                    if (labels[v]<0 && locked[size_t(u)*n+v] && distances[size_t(u)*n+v]<threshold) {
                        labels[v]=current;stack.push_back(v);
                    }
                }
            }
            current++;
        }
        return 0;
    } catch (...) { return -1; }
}

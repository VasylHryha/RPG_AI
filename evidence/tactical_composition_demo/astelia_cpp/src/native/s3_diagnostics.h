#pragma once
#include "s3_controller.h"
#include <deque>
namespace astelia::control {
struct DiagnosticFrame {double t=0;std::vector<DiagnosticUnit> units;};
struct GroupDiagnostics {
  bool phases=false,coherenceValid=false,windowReady=false;
  double coherence=0,concentration=0;
  size_t distinct=0;
  std::vector<std::vector<UnitId>> candidates;
};
class DiagnosticHistory {
  std::deque<DiagnosticFrame> frames_;
public:
  void append(double t,const std::vector<DiagnosticUnit>&);
  GroupDiagnostics summarize(bool phases) const;
};
} // namespace astelia::control

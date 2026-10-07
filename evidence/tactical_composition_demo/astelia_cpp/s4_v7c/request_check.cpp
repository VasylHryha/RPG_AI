// Parse-only test executable. No World construction, prepare, decide or coreStep.
// Uses the combat binary's unchanged configuration codec and controller registry.
#include "config_codec.h"
#include "js_value.h"
#include <iostream>
#include <cmath>

int main() {
  std::string line;
  while (std::getline(std::cin, line)) {
    try {
      auto request = js::parse(line);
      const auto c = astelia::configuration(request);
      // World::create's scalar guard, evaluated without creating a world.
      if (!std::isfinite(c.dt) || c.dt <= 0 || !std::isfinite(c.duration) || c.duration < 0 ||
          !std::isfinite(c.width) || !std::isfinite(c.height) || c.width <= 0 || c.height <= 0 ||
          !std::isfinite(c.seed) || c.width > 1e9 || c.height > 1e9 || c.duration / c.dt > 1e7)
        throw std::invalid_argument("invalid world configuration");
      std::cout << js::stringify(js::obj({{"status", "VALID"},
        {"executed_fights", 0}, {"executed_steps", 0}, {"worlds_created", 0},
        {"duration", c.duration}, {"dt", c.dt}, {"width", c.width}, {"height", c.height}})) << '\n';
    } catch (const std::exception& e) {
      std::cout << js::stringify(js::obj({{"error", e.what()},
        {"executed_fights", 0}, {"executed_steps", 0}, {"worlds_created", 0}})) << '\n';
    }
    js::collect({}, 0);
  }
}

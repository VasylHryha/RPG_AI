#include "collector.h"
namespace net_slice {
void Collector::record(uint64_t tick,UnitId unit,const std::string& stage,js::V value,uint64_t volley,uint64_t decision,uint64_t cast){events.push_back(js::obj({{"fight",fight},{"tick",double(tick)},{"unit",double(unit)},{"stage",stage},{"value",value},{"volley",double(volley)},{"decision_tick",double(decision?decision:tick)},{"cast_tick",double(cast)}}));}
js::V Collector::drain(){js::Args rows;rows.swap(events);return js::arr(std::move(rows));}
}

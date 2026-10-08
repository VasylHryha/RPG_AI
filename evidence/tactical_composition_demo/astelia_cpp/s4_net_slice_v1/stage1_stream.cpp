// Bounded offline sequence RPC. Host state persists across chunks; no World,
// physical advancement or collector fight is instantiated by these operations.
namespace {
std::unique_ptr<net_slice::Host> stage1StreamHost;
}
js::V stage1Stream(js::V req) {
    using namespace net_slice;
    const auto operation=js::str(js::get(req,"operation"));
    if(operation=="stage1_stream_init") {
        auto weights=std::make_shared<const Weights>(js::get(req,"weights"));
        stage1StreamHost=std::make_unique<Host>(0,weights);
        stage1StreamHost->ablation=js::str(js::get(req,"ablation"));
        return js::obj({{"status","READY"}});
    }
    if(!stage1StreamHost||operation!="stage1_stream_frames")throw std::invalid_argument("sequence stream not initialized");
    auto& h=*stage1StreamHost;js::Args rows;
    const auto frames=js::get(req,"frames");
    if(frames.p->items.size()>12)throw std::invalid_argument("parity chunk bound");
    for(auto frame:frames.p->items) {
        ++h.tick;h.views.clear();
        auto joint=js::get(frame,"joint");
        for(auto id:js::get(frame,"ids").p->items) {
            js::V snapshot=js::obj({});
            for(auto key:js::keys(joint))js::set(snapshot,js::str(key),js::get(joint,js::str(key)));
            js::set(snapshot,"self",id);h.views.push_back(snapshot);
        }
        h.prepare({});
        js::Args states,actions,memories,drifts;
        for(auto p:h.phases)states.push_back(js::arr({double(p.first),p.second}));
        for(auto p:h.cache)actions.push_back(js::obj({{"id",double(p.first)},{"action",net_slice::json(p.second)}}));
        for(auto p:h.memory)memories.push_back(js::arr({double(p.first),arr(p.second)}));
        for(auto p:h.lastDrift)drifts.push_back(js::arr({p.x,p.y}));
        rows.push_back(js::obj({{"phases",js::arr(std::move(states))},{"actions",js::arr(std::move(actions))},
                               {"memory",js::arr(std::move(memories))},{"drift",js::arr(std::move(drifts))}}));
        if(h.ablation!="no_reset"&&h.ablation!="frozen_phase")
            for(auto id:js::get(frame,"launches").p->items)
                if(h.phases.count(astelia::UnitId(js::num(id))))h.phases[astelia::UnitId(js::num(id))]=0;
        h.collector.events.clear();h.shadowLabels.clear();
    }
    return js::arr(std::move(rows));
}
void stage1StreamCollect() {
    if(stage1StreamHost) {
        // Host recurrence, weights, assignments and cached Intents are native
        // values, not JS nodes. No prior public snapshot is needed next chunk.
        stage1StreamHost->views.clear();stage1StreamHost->collector.events.clear();
        stage1StreamHost->shadowLabels.clear();
    }
    js::collect({},0);
}

// Supplemental fixture sequence: no World or physical time advancement.
// The build tool includes this after the admitted, generated RPC translation unit.
js::V stage1Sequence(js::V req) {
    using namespace net_slice;
    Weights weights(js::get(req,"weights"));
    Host h(0,std::make_shared<const Weights>(weights));
    h.ablation=js::str(js::get(req,"ablation"));
    js::Args rows;
    auto launchFrames=js::get(req,"launches");
    size_t index=0;
    for(auto frame:js::get(req,"frames").p->items) {
        ++h.tick;h.views=frame.p->items;h.prepare({});
        js::Args states,actions,memories,drifts;
        for(auto p:h.phases)states.push_back(js::arr({double(p.first),p.second}));
        for(auto p:h.cache)actions.push_back(js::obj({{"id",double(p.first)},{"action",net_slice::json(p.second)}}));
        for(auto p:h.memory)memories.push_back(js::arr({double(p.first),arr(p.second)}));
        for(auto p:h.lastDrift)drifts.push_back(js::arr({p.x,p.y}));
        rows.push_back(js::obj({{"phases",js::arr(std::move(states))},{"actions",js::arr(std::move(actions))},
                               {"memory",js::arr(std::move(memories))},{"drift",js::arr(std::move(drifts))}}));
        if(h.ablation!="no_reset"&&h.ablation!="frozen_phase")
            for(auto id:launchFrames.p->items.at(index).p->items)
                if(h.phases.count(astelia::UnitId(js::num(id))))h.phases[astelia::UnitId(js::num(id))]=0;
        ++index;
    }
    return js::arr(std::move(rows));
}

int main(int argc,char** argv) {
    try {
        bool collection=argc==2&&std::string(argv[1])=="--collect";
        if(argc>1&&!collection)throw std::invalid_argument("unknown flag");
        std::string line;
        while(std::getline(std::cin,line)) {
            auto req=js::parse(line);
            if(collection)collect(req);
            else std::cout<<js::stringify(js::str(js::get(req,"operation"))=="stage1_sequence"?stage1Sequence(req):rpc(req))<<'\n';
        }
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}

"""Compile the pinned frozen network to contiguous typed coefficients."""
import hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parent
source=root.parent/'astelia_snapshot/bc_net.json'
identity=hashlib.sha256(source.read_bytes()).hexdigest()
if identity!='d11e9a2da43cb0eb5b8b9539be4ab5834e750b4148121d56e632c75d7fb2e3e5':
    raise RuntimeError('frozen network mismatch')
net=json.loads(source.read_text())
flat=lambda rows:[value for row in rows for value in row]
number=lambda value:repr(value) if isinstance(value,float) else str(value)+'.0'
lines=['// Generated frozen network SHA256 '+identity,'#include "search_types.h"','namespace astelia {','std::shared_ptr<const Network> frozenNetwork(){static const auto net=[](){auto n=std::make_shared<Network>();',f'n->inputs={len(net["W1"][0])};n->hidden={len(net["W1"])};n->outputs={len(net["W2"])};']
for dest,values in [('w1',flat(net['W1'])),('b1',net['b1']),('w2',flat(net['W2'])),('b2',net['b2'])]:
    lines.append('n->'+dest+'={'+','.join(map(number,values))+'};')
lines+=['n->validate();return std::shared_ptr<const Network>(n);}();return net;}','} // namespace astelia']
(root/'src/native/network_tables.cpp').write_text('\n'.join(lines)+'\n')
print('generated network',len(net['W1'][0]),len(net['W1']),len(net['W2']))

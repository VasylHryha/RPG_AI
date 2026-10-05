import fs from 'node:fs';
const tabs=await(await fetch('http://127.0.0.1:9235/json')).json();
const ws=new WebSocket(tabs[0].webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let id=0,pending=new Map(),errors=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}))});
await call('Runtime.enable');await call('Page.enable');
const dir='/Users/new/RiderProjects/ai_RPG_test/evidence/tactical_composition_demo/astelia_cpp/s4_anomaly/replays';
let receipt=[];
for(const file of fs.readdirSync(dir).filter(x=>x.endsWith('.html'))){
 await call('Page.navigate',{url:'file://'+dir+'/'+file});
 let ready=false;for(let i=0;i<100;i++){await new Promise(r=>setTimeout(r,100));const o=await call('Runtime.evaluate',{expression:'typeof data === "object" && data?.frames?.length > 0',returnByValue:true});if(o.result.value){ready=true;break}}
 if(!ready)throw Error('Replay failed to load: '+file);
 const state=await call('Runtime.evaluate',{expression:`(()=>{index=data.frames.findIndex(f=>f.state.t>=60);if(index<0)index=data.frames.length-1;draw();return {frames:data.frames.length,spec:data.spec,time:data.frames[index].state.t,initial:data.frames[0].state.units.filter(u=>u.alive).length,alive:[0,1].map(team=>data.frames[index].state.units.filter(u=>u.team===team&&u.alive).length),stateUnits:data.frames[index].state.units.filter(u=>u.alive&&u.controllerState!=null).length,summary:data.summary}})()`,returnByValue:true});
 const png=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(dir+'/../../s4_checks/'+file+'.png',Buffer.from(png.data,'base64'));
 await call('Runtime.evaluate',{expression:`$('play').click()`});await new Promise(r=>setTimeout(r,300));
 const controls=await call('Runtime.evaluate',{expression:`(()=>{const moved=data.frames[index].state.t;$('play').click();$('seek').value=data.frames.length-1;$('seek').dispatchEvent(new Event('input'));$('targets').click();return {moved,terminal:data.frames[index].state.t,playing,targets:$('targets').checked}})()`,returnByValue:true});
 receipt.push({file,loaded:true,...state.result.value,controls:controls.result.value});
}
if(errors.length)throw Error(JSON.stringify(errors));fs.writeFileSync(dir+'/../../s4_checks/browser_receipt.json',JSON.stringify({errors,checks:receipt},null,2));console.log(JSON.stringify(receipt.map(x=>({file:x.file,time:x.time,alive:x.alive,controls:x.controls}))));ws.close();

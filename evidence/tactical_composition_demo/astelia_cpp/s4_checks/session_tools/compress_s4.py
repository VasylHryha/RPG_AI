from pathlib import Path
p=Path('evidence/tactical_composition_demo/astelia_cpp/s4_development.py');s=p.read_text().replace('import argparse\n','import argparse\nimport base64\n')
start=s.index("    write(output/(name+'.replay.json'),payload)");end=s.index("    return dict(file=name+'.html'",start)
s=s[:start]+"    package_replay(output,name,payload)\n"+s[end:]
pos=s.index('\ndef anomaly(bench):')
s=s[:pos]+'''\ndef package_replay(output,name,payload):
    for frame in payload['frames']:
        for unit in frame['state']['units']:
            for key in list(unit):
                if key not in ('id','team','role','x','y','hp','alive','target','controllerState','commitment','debug'):
                    del unit[key]
            if 'debug' in unit:
                unit['debug']={k:unit['debug'][k] for k in ('r','maxhp')}
        frame['state'].pop('debug',None)
    packed=gzip.compress(json.dumps(payload,separators=(',',':')).encode(),mtime=0)
    (output/(name+'.replay.json.gz')).write_bytes(packed)
    template=(ROOT/'s4_replay.html').read_text()
    (output/(name+'.html')).write_text(template.replace('/*REPLAY_DATA*/null',json.dumps(base64.b64encode(packed).decode())))

''' + s[pos:]
p.write_text(s)
p=Path('evidence/tactical_composition_demo/astelia_cpp/s4_replay.html');s=p.read_text().replace('accept=".json"','accept=".json,.gz"').replace('a .replay.json file','a .replay.json.gz file')
s=s.replace("$('load').onchange=async()=>{try{install(JSON.parse(await $('load').files[0].text()))}","async function unpack(bytes){const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));return JSON.parse(await new Response(stream).text())}\n$('load').onchange=async()=>{try{const file=$('load').files[0];install(file.name.endsWith('.gz')?await unpack(await file.arrayBuffer()):JSON.parse(await file.text()))}")
s=s.replace("if(data)install(data);requestAnimationFrame(tick);", "if(typeof data==='string'){unpack(Uint8Array.from(atob(data),c=>c.charCodeAt(0))).then(install).catch(e=>{$('info').textContent=e.message})}else if(data)install(data);requestAnimationFrame(tick);")
p.write_text(s)

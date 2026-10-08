"""Isolated offline copy or exact online install. Never alters the source environment."""
import argparse
import hashlib
import importlib.metadata as md
import json
import pathlib
import shutil
import subprocess

HERE=pathlib.Path(__file__).resolve().parent

def offline(sources):
    target=HERE/'_local/mlenv/lib/python3.11/site-packages'
    target.mkdir(parents=True,exist_ok=True)
    wanted={line.split('==')[0].lower().replace('-','_'):line.split('==')[1] for line in (HERE/'requirements.lock').read_text().splitlines() if line and not line.startswith('#')}
    found={}
    expanded=[]
    for source in sources:
        expanded.extend([source,*[x for x in source.iterdir() if x.is_dir()]])
    for source in expanded:
        for dist in md.distributions(path=[str(source)]):
            name=dist.metadata['Name'].lower().replace('-','_')
            if name in wanted and dist.version==wanted[name] and name not in found:found[name]=dist
    if set(found)!=set(wanted):raise RuntimeError('missing offline distributions: '+str(set(wanted)-set(found)))
    records={}
    for name,dist in found.items():
        digest=hashlib.sha256();count=0;size=0
        for f in sorted(dist.files or [],key=str):
            if '..' in pathlib.Path(f).parts or str(f).endswith(('.pyc','.pth')):continue
            src=pathlib.Path(dist.locate_file(f));dst=target/f
            if not src.is_file():raise RuntimeError('missing source package file '+str(src))
            dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
            h=hashlib.sha256(dst.read_bytes()).hexdigest();digest.update((str(f)+'\0'+h+'\n').encode());count+=1;size+=dst.stat().st_size
        records[name]={'version':dist.version,'files':count,'bytes':size,'tree_sha256':digest.hexdigest()}
    (HERE/'ENVIRONMENT.json').write_text(json.dumps({'method':'isolated offline distribution copies','python':'3.11.15','device':'cpu','torch_threads':4,'interop_threads':1,'sources':list(map(str,sources)),'packages':records},indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--offline-source',action='append',type=pathlib.Path);a=p.parse_args()
    if a.offline_source:offline(a.offline_source)
    else:subprocess.run(['uv','pip','sync','--python',str(HERE/'_local/mlenv/bin/python'),str(HERE/'requirements.lock')],check=True)

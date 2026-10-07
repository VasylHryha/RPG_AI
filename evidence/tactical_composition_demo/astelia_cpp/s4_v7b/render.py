"""Self-contained stored report; no engine invocation."""
import html
from common import *

def render():
 pins();r=read(HERE/'ANALYSIS.json')
 if r['validation_sha256']!=sha(HERE/'VALIDATION.json') or r['tuning_sha256']!=sha(HERE/'TUNING.json'):raise RuntimeError('analysis identity drift')
 rows=['<tr><th>Arm</th><th>Head</th><th>Wins /40</th><th>Mean S</th><th>Own losses</th></tr>']
 for c in r['cells']:rows.append(f"<tr><td>{html.escape(c['arm'])}</td><td>{c['head']}</td><td>{c['wins']}</td><td>{c['mean_S']:.3f}</td><td>{c['own_losses']:.3f}</td></tr>")
 text='<!doctype html><meta charset="utf-8"><title>v7 development</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto}td,th{padding:8px;border-bottom:1px solid #bbb}pre{white-space:pre-wrap}</style><h1>v7 development observations</h1><p>Descriptive development; no scientific acceptance, population inference or S5 authorization.</p><table>'+''.join(rows)+'</table><p>'+html.escape(r['readings']['relative'])+'</p><p>Observed owner criterion: '+str(r['readings']['observed_owner_criterion'])+'</p><pre>'+html.escape(json.dumps({k:r[k] for k in ('positive_clusters','negative_clusters','tied_clusters','orientation_discordance','paired_cluster_bootstrap','omega0_duplicate','omega0_interpretation')},indent=2))+'</pre><details><summary>Paired cluster table and per-fight mechanism diagnostics</summary><pre>'+html.escape(json.dumps({k:r[k] for k in ('paired_clusters','per_fight')},indent=2))+'</pre></details>'
 (HERE/'REPORT.html').write_text(text)
 write(HERE/'RENDER.json',dict(analysis_sha256=sha(HERE/'ANALYSIS.json'),report_sha256=sha(HERE/'REPORT.html'),stored_only=True))
def render_tuning():
 pins();r=read(HERE/'TUNING_ANALYSIS.json')
 if r['tuning_sha256']!=sha(HERE/'TUNING.json'):raise RuntimeError('tuning analysis drift')
 text='<!doctype html><meta charset="utf-8"><title>v7 tuning</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto}pre{white-space:pre-wrap}</style><h1>v7 sealed tuning</h1><p>Development only. No validation outcomes used in selection.</p><pre>'+html.escape(json.dumps(r,indent=2))+'</pre>'
 (HERE/'TUNING_REPORT.html').write_text(text)
 write(HERE/'TUNING_RENDER.json',dict(analysis_sha256=sha(HERE/'TUNING_ANALYSIS.json'),report_sha256=sha(HERE/'TUNING_REPORT.html'),stored_only=True))

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('stage',nargs='?',default='validate',choices=('tune','validate'));args=parser.parse_args()
 with attempt('render_'+args.stage,dict(status='not_run',reason='stored rendering; no fights')) as (deadline,_,__):
  render_tuning() if args.stage=='tune' else render();deadline.remaining()

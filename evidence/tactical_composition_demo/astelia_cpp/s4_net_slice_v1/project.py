"""Teacher-data resource projection only. No draws, engine execution or collection."""
import argparse
import json
import math
from pathlib import Path
from schema import WIDTH

HERE=Path(__file__).resolve().parent

def projection(duration=40,mean_record_bytes=None,maximum_record_bytes=None):
    measured=mean_record_bytes is not None and maximum_record_bytes is not None
    if (mean_record_bytes is None)!=(maximum_record_bytes is None):raise ValueError('both measured sizes required')
    if measured and (not all(math.isfinite(x) for x in (mean_record_bytes,maximum_record_bytes)) or not 0<mean_record_bytes<=maximum_record_bytes<=1048576):raise ValueError('measured record sizes')
    fights=200 # both orientations included, NOT 200 per orientation
    guns=10;units=24;threats=64
    rows=fights*duration*5*guns
    ticks=fights*duration*30
    decision_bytes=rows*(WIDTH*4+160)
    # Joint geometry once/tick: IDs, pos, velocity, health, cast/lifecycle metadata.
    joint_bytes=ticks*(128+units*96+threats*128)
    # Two rounds, 10 trajectories per arm per round, same 40s estimate /150s cap.
    dagger_fights=2*3*10
    factor=1+dagger_fights/fights
    converted=(decision_bytes+joint_bytes)*factor
    raw=ticks*mean_record_bytes*factor if measured else None
    reserve=ticks*maximum_record_bytes*factor if measured else None
    return {'status':'MEASURED_SIZE_PROJECTION' if measured else 'SIZES_REQUIRED','fights':fights,'orientations':'included equally within 200','guns_cap':guns,'public_units_cap':units,'public_threats_cap':threats,'duration_seconds':duration,'feature_width':WIDTH,'decision_rows':rows,'joint_ticks':ticks,'decision_bytes':decision_bytes,'joint_bytes':joint_bytes,'with_DAgger_bytes':int(converted),'raw_JSON_record_cap_bytes':1048576,'measured_mean_record_bytes':mean_record_bytes,'measured_maximum_record_bytes':maximum_record_bytes,'raw_JSON_with_DAgger_bytes':math.ceil(raw) if measured else None,'raw_JSON_reserve_bytes':math.ceil(reserve) if measured else None,'disk_allowance_bytes':math.ceil(reserve+converted*2+3*1024**3) if measured else None,'peak_memory_bytes':512*1024**2,'batch_joint_windows':4,'window_ticks':90,'burnin':'reconstruct full prefix no-grad; do not zero random windows','epochs_per_fit':10,'fits_per_arm':3,'data_loader_workers':0,'torch_threads':4,'interop_threads':1,'collector_threads':1,'ES_physical_fights':{'candidates_per_arm':3200,'incumbents_per_arm':200,'reporting_all_arms_and_teacher':800,'total_max':11000},'CPU_projection':{'collection':'200 * measured collection CPU s/fight','DAgger':'60 * measured student+shadow CPU s/fight','fits':'9 * 10 * ceil(training_windows / 4) * measured CPU s/step','export':'3 * measured export CPU s','ES':'10200 * measured CPU s/fight','reporting':'800 * measured CPU s/fight'},'timing_required':'Separate authorized <=20-fight / <=20-step sample on actual paths before collection/training; no measurements invented','approval_threshold':'Collection time authority: s4_shape_lab_v1/raw/LAB_CAP.json; training remains separate'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'TEACHER_DATA_PROJECTION.json');p.add_argument('--mean-record-bytes',type=float);p.add_argument('--maximum-record-bytes',type=int);a=p.parse_args()
    payload={'expected_40s':projection(40,a.mean_record_bytes,a.maximum_record_bytes),'hard_150s':projection(150,a.mean_record_bytes,a.maximum_record_bytes),'collection_authorized':False,'training_authorized':False,'fights_executed':0}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps(payload,indent=2))

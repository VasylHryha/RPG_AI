"""Strict v6 summary extension; historical schemas remain unchanged."""
import math
from result_schema import S3_FIELDS,finite,timing_options,validate_rows as historical_validate_rows

FIELDS={'side','samples','lowAmplitudeSamples','fractionBelow02','argRateSamples','argRateAbsSum',
        'argRateAbsMean','argRateNullReason','argValidityThreshold','retryCount','numericalFailureTicks',
        'mu','omega_ranged','omega_melee'}

def validate_complex(request,summary):
    profiles=request.get('options',{}).get('ai',[])
    sides=[i for i,p in enumerate(profiles) if p.get('controller')=='resonator' and p.get('skeleton')=='v6']
    if 'complexDiagnostics' not in summary:
        if sides:raise ValueError('v6 resonator summary missing complex diagnostics')
        return
    if not S3_FIELDS<=set(summary):raise ValueError('v6 summary missing native failure accounting')
    d=summary['complexDiagnostics']
    if len(sides)!=1 or not isinstance(d,dict) or set(d)!=FIELDS or d['side']!=sides[0]:raise ValueError('invalid v6 diagnostic schema/side')
    for key in ('side','samples','lowAmplitudeSamples','argRateSamples','retryCount','numericalFailureTicks'):
        if not finite(d[key]) or d[key]<0 or int(d[key])!=d[key]:raise ValueError('invalid v6 counter: '+key)
    if not 0<=d['lowAmplitudeSamples']<=d['samples'] or not 0<=d['argRateSamples']<=d['samples']-d['lowAmplitudeSamples']:raise ValueError('invalid v6 denominators')
    if d['argValidityThreshold']!=.2 or not finite(d['argValidityThreshold']):raise ValueError('invalid v6 amplitude threshold')
    for key in ('mu','omega_ranged'):
        if not finite(d[key]) or not -2<=d[key]<=2:raise ValueError('invalid v6 rate: '+key)
        expected=profiles[sides[0]].get('params',{}).get(key,0)
        if not finite(expected) or d[key]!=expected:raise ValueError('request/diagnostic v6 rate mismatch: '+key)
    if not finite(d['omega_melee']) or d['omega_melee']!=0:raise ValueError('v6 melee omega is fixed zero')
    if not finite(d['argRateAbsSum']) or d['argRateAbsSum']<0:raise ValueError('invalid v6 arg-rate sum')
    if d['samples']:
        if not finite(d['fractionBelow02']) or abs(d['fractionBelow02']-d['lowAmplitudeSamples']/d['samples'])>1e-12:raise ValueError('invalid v6 low-amplitude fraction')
    elif d['fractionBelow02'] is not None:raise ValueError('empty v6 amplitude denominator must be null')
    if d['argRateSamples']:
        if not finite(d['argRateAbsMean']) or abs(d['argRateAbsMean']-d['argRateAbsSum']/d['argRateSamples'])>1e-12 or d['argRateNullReason'] is not None:raise ValueError('invalid v6 arg-rate mean')
    elif d['argRateAbsMean'] is not None or d['argRateAbsSum']!=0 or d['argRateNullReason']!='no_consecutive_valid_endpoints':raise ValueError('invalid v6 arg-rate null reason')
    if summary.get('controllerStatus')=='completed' and d['numericalFailureTicks']!=0:raise ValueError('completed v6 fight has numerical failures')
    _,dt,_=timing_options(request)
    if not finite(summary.get('t')):raise ValueError('invalid v6 final time')
    ticks=round(summary['t']/dt)
    if d['retryCount']>ticks or d['numericalFailureTicks']>ticks:raise ValueError('v6 retry/failure ticks exceed physical ticks')

def validate_rows(request,rows):
    if not isinstance(rows,list) or not rows:return historical_validate_rows(request,rows)
    last=rows[-1]
    if not isinstance(last,dict) or set(last)=={'error'}:return historical_validate_rows(request,rows)
    validate_complex(request,last)
    core=dict(last);core.pop('complexDiagnostics',None)
    return historical_validate_rows(request,rows[:-1]+[core])

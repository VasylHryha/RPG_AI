"""Operation-specific result validation shared by cache and benchmark admission."""
import math
import re

SUMMARY_FIELDS = {'mode','melee','ranged','artillery','total','wasted','monsterDeaths',
                  'hunterKills','aliveSeconds','enemyDamage','survivors','enemySurvivors','t'}
S3_FIELDS = {'controllerFailures','controllerStatus','crossTeamDealt','crossTeamTaken','friendlyDealt','friendlyTaken'}
COUNTS = {'monsterDeaths','hunterKills','survivors','enemySurvivors'}


def finite(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def validate_summary(row, allow_error=True):
    if isinstance(row, dict) and set(row) == {'error'} and isinstance(row['error'], str):
        if allow_error:
            return 'error'
        raise ValueError('fight did not complete: ' + row['error'])
    if not isinstance(row, dict) or set(row) not in (SUMMARY_FIELDS, SUMMARY_FIELDS | S3_FIELDS) or not isinstance(row['mode'], str):
        raise ValueError('invalid combat summary schema')
    for key in SUMMARY_FIELDS - {'mode'}:
        if not finite(row[key]) or row[key] < 0:
            raise ValueError('invalid summary quantity: ' + key)
    for key in COUNTS:
        if row[key] != int(row[key]):
            raise ValueError('invalid integer summary quantity: ' + key)
    if abs(row['total']-(row['melee']+row['ranged']+row['artillery'])) > 1e-9 * max(1, row['total']):
        raise ValueError('summary damage total inconsistent')
    if S3_FIELDS <= set(row):
        for field in S3_FIELDS - {'controllerStatus'}:
            values=row[field]
            if not isinstance(values,list) or len(values)!=2 or any(not finite(x) or x<0 for x in values):
                raise ValueError('invalid extended summary: '+field)
        failures=row['controllerFailures']
        if any(x!=int(x) for x in failures):raise ValueError('invalid controller failure count')
        expected='controller_failure' if any(failures) else 'completed'
        if row['controllerStatus']!=expected:raise ValueError('inconsistent controller status')
        if expected=='controller_failure':return expected
    return 'completed'


def timing_options(request):
    options = request.get('options') or {}
    dt, duration = options.get('dt', 1/30), options.get('duration', 90)
    if not finite(dt) or dt <= 0 or not finite(duration) or duration < 0:
        raise ValueError('invalid combat time configuration')
    if not finite(duration/dt) or duration/dt > 10_000_000:
        raise ValueError('combat exceeds supported step budget')
    return options, dt, duration


def validate_completion(request, row):
    """Necessary observable termination conditions; full mechanics need traces."""
    options, dt, duration = timing_options(request)
    tolerance = 1e-12 * max(1, duration, dt)
    if row['t'] > duration + dt + tolerance:
        raise ValueError('fight exceeded configured duration')
    if row['t'] < duration and row['survivors'] > 0:
        if options.get('scenario', 'hunters') not in ('mirror', 'skirmish') or row['enemySurvivors'] > 0:
            raise ValueError('fight did not reach a valid termination condition')
    steps = row['t']/dt
    if not finite(steps) or steps > 10_000_001:
        raise ValueError('invalid final combat step count')
    return int(round(steps))


def validate_rows(request, rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError('missing result rows')
    operation = request.get('operation')
    if operation:
        if len(rows) != 1:
            raise ValueError('operation returned multiple rows')
        value = rows[0]
        if isinstance(value, dict) and set(value) == {'error'} and isinstance(value['error'], str):
            return 'error'
        if operation == 'echo' and value == request.get('value'):
            return 'operation'
        if operation == 'fixed' and isinstance(value, str):
            return 'operation'
        if operation in ('keys','rng') and isinstance(value, list) and all(isinstance(s, str) for s in value):
            return 'operation'
        if operation == 'string' and (isinstance(value, (str,list,bool)) or finite(value)):
            return 'operation'
        if operation == 'math' and isinstance(value, dict) and set(value)=={'value','bits'} and re.fullmatch('[0-9a-f]{16}',value.get('bits','')):
            if value['value'] is None or finite(value['value']):
                return 'operation'
        raise ValueError('invalid operation result schema')
    status = validate_summary(rows[-1])
    if status == 'completed' and rows[-1]['mode'] != (request.get('mode') or 'alone'):
        raise ValueError('request/summary mode mismatch')
    if status == 'completed':
        validate_completion(request, rows[-1])
    if not request.get('trace'):
        if len(rows) != 1:
            raise ValueError('unexpected trace rows')
        return status
    # A creation failure may legitimately precede the initial trace.
    if status == 'error' and len(rows) == 1:
        return status
    if len(rows) < 2:
        raise ValueError('trace missing initial frame')
    last_time = -1
    for index, frame in enumerate(rows[:-1]):
        if not isinstance(frame, dict) or type(frame.get('step')) is not int or frame['step'] != index:
            raise ValueError('trace frame order/gap invalid')
        state = frame.get('state')
        if not isinstance(state, dict) or not finite(state.get('t')) or (index>0 and state['t']<=last_time) or state['t'] < 0:
            raise ValueError('invalid trace time')
        last_time = state['t']
        units = state.get('units')
        if not isinstance(units, list):
            raise ValueError('trace missing units')
        seen = set()
        for unit in units:
            if not isinstance(unit, dict) or type(unit.get('id')) is not int or unit['id'] <= 0 or unit['id'] in seen:
                raise ValueError('invalid or duplicate trace identity')
            seen.add(unit['id'])
            if unit.get('team') not in (0,1) or not isinstance(unit.get('role'), str) or type(unit.get('alive')) is not bool:
                raise ValueError('invalid trace unit fields')
            if not all(finite(unit.get(k)) for k in ('x','y','hp','cd')):
                raise ValueError('non-finite trace unit')
            target = unit.get('target')
            if target is not None and (type(target) is not int or target <= 0):
                raise ValueError('invalid trace target identity')
    if status == 'completed' and rows[-1]['t'] != last_time:
        raise ValueError('trace/summary final time mismatch')
    return status

"""Versioned, value-only drills. Variation uses sealed per-draw seed, not fight ID.

D1 leaves native static-target behavior intact; D2 retains native enemy guns.
The original requests.drill and collection remain historical evidence.
"""
import hashlib
import math
import random
from requests import drill as legacy_drill

VERSION = 'NS1-drill-2'
RANGES = dict(jitter_px=[-8.,8.], separation_px=[225.,275.],
              line_spacing_px=[26.,34.], rotation_rad=[-.15,.15],
              static_target_x_px=[875.,925.], static_target_y_offset_px=[-15.,15.])


def drill(cell,guns,seed,orientation=0,arm='teacher',weights=None,fight='unsealed'):
    request=legacy_drill(cell,guns,seed,orientation,arm,weights,fight)
    digest=hashlib.sha256(f'{VERSION}:{seed}'.encode()).hexdigest()
    rng=random.Random(int(digest,16))
    separation=rng.uniform(*RANGES['separation_px'])
    spacing=rng.uniform(*RANGES['line_spacing_px'])
    angle=rng.uniform(*RANGES['rotation_rad'])
    samples=[]
    for unit in request['roster']:
        dx=rng.uniform(*RANGES['jitter_px']); dy=rng.uniform(*RANGES['jitter_px'])
        x,y=unit['position']
        if unit['role']==2:
            x=525+(-1 if unit['team']==0 else 1)*separation/2
            y=400+(y-400)/30*spacing
        elif unit['team']==1:
            x=rng.uniform(*RANGES['static_target_x_px'])
            y+=rng.uniform(*RANGES['static_target_y_offset_px'])
        # Shared formation rotation plus independent unit jitter. Native reflects
        # the complete roster later for orientation 1; never count it as a draw.
        xx,yy=x-525,y-400
        unit['position']=[525+xx*math.cos(angle)-yy*math.sin(angle)+dx,
                          400+xx*math.sin(angle)+yy*math.cos(angle)+dy]
        samples.append(dict(jitter=[dx,dy],position=unit['position'][:]))
    request['variation']=dict(version=VERSION,entropy_sha256=digest,ranges=RANGES,
        separation_px=separation,line_spacing_px=spacing,rotation_rad=angle,units=samples)
    return request

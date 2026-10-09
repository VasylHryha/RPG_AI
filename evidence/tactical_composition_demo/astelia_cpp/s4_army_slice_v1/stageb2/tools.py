"""Pure public-state geometry, mirrored by tools.h. Pixel/second units throughout."""
import math

EPS=1e-8

def finite(*values):
    for value in values:
        if isinstance(value,(tuple,list)) or hasattr(value,'__iter__'):
            finite(*value)
        elif not math.isfinite(value):raise ValueError('nonfinite tool input')

def add(a,b):
    p=(a[0]+b[0],a[1]+b[1]);finite(p);return p
def sub(a,b):
    p=(a[0]-b[0],a[1]-b[1]);finite(p);return p
def mul(a,s):
    p=(a[0]*s,a[1]*s);finite(p);return p
def norm(a):
    r=math.hypot(*a);finite(r);return r
def direction(a):
    r=norm(a)
    return (1.,0.) if r<1e-12 else mul(a,1/r)
def lead(position,velocity,flight_time):
    finite(position,velocity,flight_time)
    if flight_time<0 or not math.isfinite(flight_time):raise ValueError('flight seconds')
    return add(position,mul(velocity,flight_time))
def flight_time(own,target,lob_speed,windup=0.):
    """Engine lob law: distance / own effective lobSpeed + remaining windup."""
    finite(own,target,lob_speed,windup)
    if lob_speed<=0 or windup<0:raise ValueError('flight parameters')
    t=windup+norm(sub(target,own))/lob_speed;finite(t);return t
def circle_intersections(a,ra,b,rb):
    finite(a,ra,b,rb)
    if ra<0 or rb<0:raise ValueError('circle radii')
    d=norm(sub(b,a))
    if d<1e-12 or d>ra+rb+EPS or d<abs(ra-rb)-EPS:return []
    x=(ra*ra-rb*rb+d*d)/(2*d);h=math.sqrt(max(0.,ra*ra-x*x));v=direction(sub(b,a));c=add(a,mul(v,x));n=(-v[1],v[0])
    return [add(c,mul(n,h)),sub(c,mul(n,h))]
def circle_edges(o,r,box):
    finite(o,r,box)
    if r<0:raise ValueError('circle radius')
    x0,y0,x1,y1=box;out=[]
    for x in (x0,x1):
        h=r*r-(x-o[0])**2
        if h>=-EPS:
            for y in (o[1]+math.sqrt(max(0.,h)),o[1]-math.sqrt(max(0.,h))):
                if y0-EPS<=y<=y1+EPS:out.append((x,y))
    for y in (y0,y1):
        h=r*r-(y-o[1])**2
        if h>=-EPS:
            for x in (o[0]+math.sqrt(max(0.,h)),o[0]-math.sqrt(max(0.,h))):
                if x0-EPS<=x<=x1+EPS:out.append((x,y))
    return out
def legal(p,o,lo,hi,box):
    finite(p,o,lo,hi,box)
    x0,y0,x1,y1=box;d=norm(sub(p,o))
    return x0-EPS<=p[0]<=x1+EPS and y0-EPS<=p[1]<=y1+EPS and lo-EPS<=d<=hi+EPS

def range_project(p,o,lo,hi,box):
    """Euclidean nearest point in annulus intersect rectangle; None iff empty."""
    finite(p,o,lo,hi,box)
    x0,y0,x1,y1=box
    if not 0<=lo<=hi or x0>x1 or y0>y1:raise ValueError('range/box')
    clamp=lambda q:(min(x1,max(x0,q[0])),min(y1,max(y0,q[1])))
    pts=[clamp(p)]
    v=direction(sub(p,o))
    for r in (lo,hi):pts += [add(o,mul(v,r)),*circle_edges(o,r,box)]
    pts += [(x,min(y1,max(y0,p[1]))) for x in (x0,x1)]
    pts += [(min(x1,max(x0,p[0])),y) for y in (y0,y1)]
    pts += [(x,y) for x in (x0,x1) for y in (y0,y1)]
    pts=[q for q in pts if legal(q,o,lo,hi,box)]
    return min(pts,key=lambda q:(norm(sub(q,p)),q[0],q[1])) if pts else None

def splash_coverage(point,enemies,radius):
    finite(point,enemies,radius)
    if radius<0:raise ValueError('splash radius')
    return sum(norm(sub(point,p))<=radius+EPS for p in enemies)
def best_splash(enemies,radius,origin,lo,hi,box):
    """Exact maximum centre count in equal-radius disks with legal landing region.
    Arrangement vertices, point projections and boundary intersections suffice.
    Ties among enumerated count-maximizing witnesses: nearest origin, then x/y.
    This is not a global nearest-origin optimum within every maximum-count region.
    No target/fire decision is returned.
    """
    finite(enemies,radius,origin,lo,hi,box)
    if radius<0:raise ValueError('splash radius')
    pts=[]
    for i,a in enumerate(enemies):
        q=range_project(a,origin,lo,hi,box)
        if q is not None:pts.append(q)
        pts += circle_edges(a,radius,box)
        for r in (lo,hi):pts += circle_intersections(a,radius,origin,r)
        for b in enemies[i+1:]:pts += circle_intersections(a,radius,b,radius)
    pts=[p for p in pts if legal(p,origin,lo,hi,box)]
    if not pts:return range_project(origin,origin,lo,hi,box)
    # Batched arrangement coverage avoids Python's cubic inner loop; same count math.
    import numpy as np
    p=np.asarray(pts);e=np.asarray(enemies);d=p[:,None,:]-e[None,:,:]
    counts=(np.hypot(d[:,:,0],d[:,:,1])<=radius+EPS).sum(1)
    i=min(range(len(pts)),key=lambda i:(-int(counts[i]),norm(sub(pts[i],origin)),pts[i][0],pts[i][1]))
    return pts[i]

def cluster_centres(points,link_radius):
    """Connected components of distance<=link_radius; arithmetic centres, input order."""
    finite(points,link_radius)
    if link_radius<0:raise ValueError('cluster radius')
    seen=set();out=[]
    for i in range(len(points)):
        if i in seen:continue
        component=[i];seen.add(i);at=0
        while at<len(component):
            for j in range(len(points)):
                if j not in seen and norm(sub(points[component[at]],points[j]))<=link_radius+EPS:seen.add(j);component.append(j)
            at+=1
        centre=(sum(points[j][0] for j in component)/len(component),sum(points[j][1] for j in component)/len(component));finite(centre);out.append(centre)
    return out

def dodge_spot(own,enemy_position,enemy_velocity,horizon,clearance,side):
    """Two perpendicular offsets from predicted public motion, side supplied by caller."""
    finite(own,enemy_position,enemy_velocity,horizon,clearance,side)
    if side not in (-1,1) or clearance<0:raise ValueError('dodge parameters')
    predicted=lead(enemy_position,enemy_velocity,horizon);v=direction(sub(predicted,own));normal=(-v[1],v[0])
    return add(own,mul(normal,clearance*side))
def behind_friend(friend,threat,clearance,target,lo,hi,box):
    finite(friend,threat,clearance,target,lo,hi,box)
    if clearance<0:raise ValueError('friend clearance')
    return range_project(add(friend,mul(direction(sub(friend,threat)),clearance)),target,lo,hi,box)
def threat_estimate(point,enemies,horizon):
    """Sum damage/cycle * 1/(1+(distance/max(1,reach))^2), damage/s.
    Enemy records (position, velocity, damage, cycle seconds, range pixels).
    Public extrapolation; not a calibrated hit probability or safety decision.
    """
    finite(point,enemies,horizon)
    if horizon<0:raise ValueError('threat horizon')
    value=0.
    for pos,vel,damage,cycle,reach in enemies:
        if damage<0 or cycle<=0 or reach<0:raise ValueError('threat parameters')
        d=norm(sub(point,lead(pos,vel,horizon)))/max(1.,reach)
        value+=damage/cycle/(1+d*d)
    finite(value)
    return value

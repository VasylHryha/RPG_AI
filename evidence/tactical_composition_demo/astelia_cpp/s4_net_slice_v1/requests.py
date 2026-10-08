"""Value-only slice cells. No seed allocation or engine execution."""

def drill(cell,guns,seed,orientation=0,arm='teacher',weights=None,fight='unsealed'):
    if cell not in ('D1-static','D2-shellfire') or guns not in (1,2,10) or orientation not in (0,1):raise ValueError('slice cell')
    roster=[]
    for team,x in ((0,400),(1,650)):
        for i in range(guns):roster.append({'team':team,'role':2,'position':[x,400+30*(i-(guns-1)/2)]})
    for y in (360,440):roster.append({'team':0,'role':0,'position':[440,y]})
    if cell=='D1-static':
        for y in (360,440):roster.append({'team':1,'role':0,'position':[630,y]})
    return {'arm':arm,'seed':seed,'orientation':orientation,'fight':fight,'roster':roster,'weights':str(weights) if weights else None,'shadow':False}

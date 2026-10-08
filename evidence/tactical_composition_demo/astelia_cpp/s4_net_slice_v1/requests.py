"""Value-only slice cells. No seed allocation or engine execution."""

def drill(cell,guns,seed,orientation=0,arm='teacher',weights=None,fight='unsealed'):
    if cell not in ('D1-static','D2-shellfire') or guns not in (1,2,10) or orientation not in (0,1):raise ValueError('slice cell')
    roster=[]
    for team,x in ((0,400),(1,650)):
        for i in range(guns):roster.append({'team':team,'role':2,'position':[x,400+30*(i-(guns-1)/2)]})
    for y in (360,440):roster.append({'team':0,'role':0,'position':[240,y]})
    if cell=='D1-static':
        for y in (360,440):roster.append({'team':1,'role':0,'position':[900,y]})
    return {'cell':cell,'threat_source':'none' if cell=='D1-static' else 'native_enemy_guns','threat_timing':'none' if cell=='D1-static' else 'native_cooldown_windup_lob','arm':arm,'seed':seed,'orientation':orientation,'fight':fight,'roster':roster,'weights':str(weights) if weights else None,'shadow':False}


if __name__=='__main__':
    import argparse,json
    parser=argparse.ArgumentParser(description='Emit one explicit sealed teacher request; does not execute')
    parser.add_argument('--cell',required=True,choices=('D1-static','D2-shellfire'))
    parser.add_argument('--guns',required=True,type=int,choices=(1,2,10))
    parser.add_argument('--seed',required=True,type=int)
    parser.add_argument('--fight',required=True)
    parser.add_argument('--orientation',required=True,type=int,choices=(0,1))
    args=parser.parse_args()
    print(json.dumps(drill(args.cell,args.guns,args.seed,args.orientation,fight=args.fight),allow_nan=False))

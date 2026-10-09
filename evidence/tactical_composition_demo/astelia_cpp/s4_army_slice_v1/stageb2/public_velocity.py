"""O's one-second velocity smoother reconstructed from full public prefixes.
At snapshot t, velocity is the displacement completed on the prior tick. The
engine has already smoothed it with min(1, dt); initial velocity/state are zero.
"""
def attach(rows):
    state={}
    for row in rows:
        k=min(1.,row['dt'])
        if 'longVelocity' in row:state={key:list(v) for key,v in row['longVelocity'].items()}
        else:
            for u in row['units']:
                old=state.get(str(u[0]),[0.,0.])
                state[str(u[0])]=[old[j]+(u[5+j]-old[j])*k for j in range(2)]
        yield dict(row,longVelocity={str(u[0]):state.get(str(u[0]),[0.,0.])[:] for u in row['units']})

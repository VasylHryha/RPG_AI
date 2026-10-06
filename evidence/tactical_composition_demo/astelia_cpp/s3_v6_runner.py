"""Versioned request dispatch; historical requests pass through unchanged."""
from s3_runner import request as historical_request

def request(spec):
    if spec.get('skeleton')!='v6':return historical_request(spec)
    previous=dict(spec,skeleton='v5');req=historical_request(previous)
    side=spec.get('controlledSide',0);req['options']['ai'][side]['skeleton']='v6'
    return req

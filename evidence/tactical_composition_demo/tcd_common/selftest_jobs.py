"""Synthetic jobs for the harness self-tests (module level, so spawned workers can import them)."""
import time


def echo_job(args):
    cfg, entropy, seed = args
    return {'seed': seed, 'value': seed*2+entropy % 7}


def failing_job(args):
    cfg, entropy, seed = args
    if seed == 1:
        raise ValueError('boom')
    return {'seed': seed, 'value': 1}


def slow_job(args):
    cfg, entropy, seed = args
    time.sleep(cfg.get('sleep', 30))
    return {'seed': seed, 'value': 1}

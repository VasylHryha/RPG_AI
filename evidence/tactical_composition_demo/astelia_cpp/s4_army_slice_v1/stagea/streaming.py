"""Bounded pipe-to-gzip recorder; failed compressed attempts remain evidence."""
import gzip
import json
import os
import selectors
import signal
import subprocess
import time

CHUNK_BYTES = 64 * 1024
MAX_RAW_BYTES = 1024**3

def stream_host(binary, request, raw, err, deadline, monitor, receipt, profile=False):
    child = None
    receipt.update(uncompressed_bytes=0, peak_rss_bytes=0)
    try:
        with raw.open('xb') as target, gzip.GzipFile(fileobj=target, mode='wb', compresslevel=1, mtime=0) as out, err.open('xb') as errors, selectors.DefaultSelector() as selector:
            env = dict(os.environ)
            env.pop('STAGEA_MEMORY_PROFILE', None)
            if profile: env['STAGEA_MEMORY_PROFILE'] = '1'
            child = subprocess.Popen(['nice', '-n', '15', str(binary)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=errors, start_new_session=True, env=env)
            child.stdin.write((json.dumps(request, separators=(',', ':'), allow_nan=False)+'\n').encode())
            child.stdin.close()
            os.set_blocking(child.stdout.fileno(), False)
            selector.register(child.stdout, selectors.EVENT_READ)
            next_monitor = 0
            while selector.get_map() or child.poll() is None:
                now = time.monotonic()
                if now >= deadline: raise TimeoutError('fight cap reached')
                if now >= next_monitor and child.poll() is None:
                    try: receipt['peak_rss_bytes'] = max(receipt['peak_rss_bytes'], monitor.live_memory(child.pid))
                    except RuntimeError:
                        if child.poll() is None: raise
                    next_monitor = now + .2
                for key, _ in selector.select(.1):
                    chunk = os.read(key.fd, CHUNK_BYTES)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    receipt['uncompressed_bytes'] += len(chunk)
                    if receipt['uncompressed_bytes'] > MAX_RAW_BYTES:
                        raise RuntimeError('raw fight exceeds 1 GiB local bound')
                    out.write(chunk)
            child.wait()
            if child.returncode or err.stat().st_size:
                raise RuntimeError('host failed; inspect stderr')
            target.flush()
    finally:
        if child is not None:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            if child.stdout is not None: child.stdout.close()
        if raw.exists(): receipt['compressed_bytes'] = raw.stat().st_size

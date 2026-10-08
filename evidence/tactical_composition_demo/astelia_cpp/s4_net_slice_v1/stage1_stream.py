"""Bounded persistent native fixture sessions, exact child CPU/peak RSS via wait4."""
import json
import os
import select
import signal
import subprocess
import sys
import time
from stage1_native_v2 import BINARY

CHUNK=12


class Session:
    def __init__(self,weights,ablation,deadline=None,binary=BINARY):
        self.deadline=deadline or time.monotonic()+3600
        self.start=time.monotonic(); self.resources=None
        self.p=subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,bufsize=0)
        try:
            if self.call(dict(operation='stage1_stream_init',weights=weights,ablation=ablation))!={'status':'READY'}:
                raise RuntimeError('native stream initialization failed')
        except Exception:
            self.close(kill=True)
            raise

    def call(self,value):
        import selectors
        # Nonblocking bounded IO enforces the deadline on both directions.
        payload=(json.dumps(value,allow_nan=False,separators=(',',':'))+'\n').encode()
        if len(payload)>13*1048576:
            raise ValueError('native stream request bound')
        sent=0; result=bytearray(); local_deadline=min(self.deadline,time.monotonic()+180)
        os.set_blocking(self.p.stdin.fileno(),False); os.set_blocking(self.p.stdout.fileno(),False)
        with selectors.DefaultSelector() as selector:
            selector.register(self.p.stdin,selectors.EVENT_WRITE)
            selector.register(self.p.stdout,selectors.EVENT_READ)
            while True:
                remaining=local_deadline-time.monotonic()
                if remaining<=0:
                    raise TimeoutError('native stream IO deadline')
                events=selector.select(min(remaining,1))
                for key,_ in events:
                    if key.fileobj is self.p.stdin:
                        try:
                            sent+=os.write(self.p.stdin.fileno(),payload[sent:sent+65536])
                        except BlockingIOError:
                            continue
                        if sent==len(payload):
                            selector.unregister(self.p.stdin)
                    else:
                        try:
                            part=os.read(self.p.stdout.fileno(),65536)
                        except BlockingIOError:
                            continue
                        if not part:
                            raise RuntimeError('native parity stream exited without a complete response')
                        result.extend(part)
                        if len(result)>4*1048576:
                            raise ValueError('native stream response bound')
                        if result.endswith(b'\n'):
                            if sent!=len(payload):
                                raise RuntimeError('response before full request')
                            return json.loads(result)

    def close(self,kill=False):
        if self.resources is not None:
            return self.resources
        if kill:
            try:os.kill(self.p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        self.p.stdin.close()
        while True:
            pid,status,usage=os.wait4(self.p.pid,os.WNOHANG)
            if pid:
                break
            if time.monotonic()>=self.deadline:
                try:os.kill(self.p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            time.sleep(.01)
        self.p.returncode=os.waitstatus_to_exitcode(status); self.p.stdout.close()
        self.resources=dict(cpu_seconds=usage.ru_utime+usage.ru_stime,wall_seconds=time.monotonic()-self.start,
            peak_rss_bytes=int(usage.ru_maxrss*(1 if sys.platform=='darwin' else 1024)),exit_code=self.p.returncode)
        if not kill and self.p.returncode:
            raise RuntimeError('native parity child failed')
        if self.resources['peak_rss_bytes']>512*1024**2:
            raise MemoryError('native parity child exceeds 512 MiB cap')
        return self.resources

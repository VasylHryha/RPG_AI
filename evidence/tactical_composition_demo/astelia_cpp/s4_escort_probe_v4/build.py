"""Admit exact sealed v3 binary; no compilation, replacement or combat."""
from common import *
@stage('build')
def main():
 d=pins();identity=admit(BINARY)
 assert identity==d['exact_v3']['binary_identity']
 write(HERE/'BUILD.json',dict(status='PASS',identity=identity,reused_exact_v3=True,source_commit='c27f5b9',utc=utc()))
 print('PASS: exact sealed v3 executable and source identities reused')
if __name__=='__main__':main()

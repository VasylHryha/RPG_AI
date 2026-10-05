from pathlib import Path
p=Path('evidence/tactical_composition_demo/astelia_cpp/s4_development.py');s=p.read_text()
s=s.replace("ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,default=OUT)","ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,default=OUT);ap.add_argument('--anomaly-only',action='store_true')")
s=s.replace("        anomaly(bench)\n        for stage", "        if args.anomaly_only:\n            anomaly(bench)\n            write(output/'summary.json',dict(status='ANOMALY_REVIEW_REQUIRED_BEFORE_TUNING',executed_fights=bench.executed,elapsed_seconds=time.monotonic()-begin))\n            return\n        anomaly_path=ROOT/'s4_anomaly/anomaly.json'\n        if not anomaly_path.exists():raise RuntimeError('inspect preliminary anomaly before tuning')\n        write(output/'anomaly_reference.json',dict(path=str(anomaly_path.relative_to(ROOT)),sha256=sha(anomaly_path)))\n        for stage")
p.write_text(s)

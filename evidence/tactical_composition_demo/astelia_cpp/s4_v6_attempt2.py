"""Authorized attempt 2: unchanged repaired A/B runner with separate receipts/entropy."""
import pathlib
import s4_v6_cache_repair as V
V.CHECKS = V.ROOT / 's4_v6_attempt2_checks'
V.LEDGER = V.ROOT / 'S4_V6_ATTEMPT2_SEEDS.json'
if __name__ == '__main__':
    V.main()

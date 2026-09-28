#!/usr/bin/env python3
"""Verify a Qelevium licence offline: signature (Ed25519), validity window, grace period.
   python verify_license.py license.json --vendor-key <hex public key>
Exit 0 if the licence is authentic and ACTIVE/GRACE, 1 otherwise. Requires `cryptography`."""
import argparse, json, sys, time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
def canon(x): return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("license"); ap.add_argument("--vendor-key", required=True); ap.add_argument("--now", type=float, default=time.time()); a = ap.parse_args()
    try:
        with open(a.license, encoding="utf-8") as f:
            lic = json.load(f)
        body = {k: v for k, v in lic.items() if k != "sig"}
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(a.vendor_key)).verify(bytes.fromhex(lic["sig"]), canon(body).encode())
        for k in ("valid_from", "valid_until", "plan", "licensee"):
            if k not in body: raise ValueError(f"missing field {k}")
        if not isinstance(body["valid_from"], int) or not isinstance(body["valid_until"], int) or not isinstance(body.get("grace_s", 0), int): raise ValueError("dates must be integers")
    except Exception as e: print(f"INVALID — signature does not match the vendor key, or malformed licence ({type(e).__name__})"); return 1
    if a.now < body["valid_from"]: print("NOT YET VALID"); return 1
    if a.now <= body["valid_until"]: print(f"VALID — ACTIVE · plan {body['plan']} · licensee {body['licensee']} · until {time.strftime('%Y-%m-%d', time.gmtime(body['valid_until']))}"); return 0
    if a.now <= body["valid_until"] + body.get("grace_s", 0): print("VALID — GRACE period"); return 0
    print("EXPIRED"); return 1
if __name__ == "__main__": sys.exit(main())

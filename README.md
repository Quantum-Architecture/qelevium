# Qelevium — public verification & proofs

[![verify](https://github.com/Quantum-Architecture/qelevium/actions/workflows/verify.yml/badge.svg)](https://github.com/Quantum-Architecture/qelevium/actions/workflows/verify.yml)

**Your AI agents, your key, your machine.** Qelevium is a personal-agent application (subscription). This public repository does not contain the product; it contains what lets anyone **check our claims**.

## What we claim, and how you verify it
| Claim | How to verify |
|---|---|
| Your API key never leaves your computer | it is stored AES-256-GCM encrypted under your own passphrase; the application makes no call to Quantum Excellium servers — check the outgoing connections of the process (only your chosen provider) |
| Nothing irreversible happens without your approval | every send/write goes through an approval queue; refused items are never executed (covered by automated tests) |
| Your licence is verifiable offline | `tools/verify_license.py` checks the Ed25519 signature and validity window — try `examples/license_example.json` (VALID) and `examples/license_tampered.json` (INVALID) with the demo key in `examples/vendor_public_key_DEMO.txt` |
| Everything is journaled | the application keeps a chained journal; exports verify with [ledger-verify](https://github.com/Quantum-Architecture/ledger-verify) |

```
pip install cryptography
python tools/verify_license.py examples/license_example.json --vendor-key $(cat examples/vendor_public_key_DEMO.txt)
```

## Quality evidence
12 automated tests in the product (vault round-trip, wrong passphrase, daily and monthly caps, approval before dispatch, idempotent dispatch, refused never sent, licence lifecycle, tampered licence, clock rollback, user-controlled memory, signed webhook).

## Limits, stated
Offline mode uses a local model and is weaker than large hosted models. Provider prices are indicative and must be kept up to date. This repository is public documentation and tooling; the product is licensed per subscription at [qelevium.com](https://qelevium.com).

"""Adversarial tests for the Qelevium licence verifier (clock pinned: the example licence is valid around 1790500000)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "examples", "vendor_public_key_DEMO.txt"), encoding="utf-8") as _f:
    KEY = _f.read().strip()
NOW = "1790500000"


def run(path, now=NOW, key=KEY):
    return subprocess.run([sys.executable, os.path.join(HERE, "tools", "verify_license.py"), path, "--vendor-key", key, "--now", now], capture_output=True, text=True)


def variant(mutate):
    with open(os.path.join(HERE, "examples", "license_example.json"), encoding="utf-8") as f:
        lic = json.load(f)
    mutate(lic)
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(lic, f)
    f.close()
    return f.name


class TestLicence(unittest.TestCase):
    def test_example_valid_now(self):
        p = run(os.path.join(HERE, "examples", "license_example.json"))
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("ACTIVE", p.stdout)

    def test_tampered_example_refused(self):
        self.assertEqual(run(os.path.join(HERE, "examples", "license_tampered.json")).returncode, 1)

    def test_plan_upgrade_without_resign_refused(self):
        self.assertEqual(run(variant(lambda l: l.update(plan="enterprise"))).returncode, 1)

    def test_extended_validity_without_resign_refused(self):
        self.assertEqual(run(variant(lambda l: l.update(valid_until=l["valid_until"] + 10**8))).returncode, 1)

    def test_expired_and_not_yet_valid(self):
        self.assertEqual(run(os.path.join(HERE, "examples", "license_example.json"), now="1900000000").returncode, 1)
        self.assertEqual(run(os.path.join(HERE, "examples", "license_example.json"), now="1700000000").returncode, 1)

    def test_grace_period(self):
        with open(os.path.join(HERE, "examples", "license_example.json"), encoding="utf-8") as f:
            lic = json.load(f)
        inside = str(lic["valid_until"] + lic["grace_s"] - 1)
        after = str(lic["valid_until"] + lic["grace_s"] + 1)
        self.assertEqual(run(os.path.join(HERE, "examples", "license_example.json"), now=inside).returncode, 0)
        self.assertEqual(run(os.path.join(HERE, "examples", "license_example.json"), now=after).returncode, 1)

    def test_wrong_vendor_key_refused(self):
        self.assertEqual(run(os.path.join(HERE, "examples", "license_example.json"), key="ab" * 32).returncode, 1)

    def test_malformed_inputs_do_not_crash(self):
        for m in (lambda l: l.pop("sig"), lambda l: l.update(sig="zz"), lambda l: l.pop("valid_until"), lambda l: l.update(valid_from="soon")):
            p = run(variant(m))
            self.assertEqual(p.returncode, 1)
            self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)

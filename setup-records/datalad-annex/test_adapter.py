"""Behavioral checks for the narrowly supported parser compatibility layer."""

import importlib
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "compat_replay", ROOT / ".agents/skills/datalad-annex/scripts/replay.py"
)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
NATIVE = ('[DATALAD RUNCMD] example\n\n=== Do not change lines below ===\n'
          '{"cmd": "python compute.py", "exit": 0}\n'
          '^^^ Do not change lines above ^^^\n')


class AdapterContract(unittest.TestCase):
    def test_native_and_supported_conventional_records(self):
        conventional = "feat: record DataLad run\n\n" + NATIVE
        with adapter.compatibility_parser() as (native, compatible):
            self.assertIsNone(native(None, conventional)[1])
            self.assertEqual(compatible(None, conventional), native(None, NATIVE))
            self.assertEqual(compatible(None, NATIVE), native(None, NATIVE))

    def test_rejects_unsupported_prefix_without_changing_native_parser(self):
        module = importlib.import_module("datalad.local.rerun")
        original = module.get_run_info
        with self.assertRaises(ValueError):
            with adapter.compatibility_parser() as (_, compatible):
                compatible(None, "feat: " + NATIVE)
        self.assertIs(module.get_run_info, original)

    def test_rejects_unsupported_version(self):
        with patch.object(adapter.datalad, "__version__", "99.0.0"):
            with self.assertRaisesRegex(RuntimeError, "supports DataLad"):
                with adapter.compatibility_parser():
                    self.fail("unsupported version accepted")

    def test_does_not_invent_record_for_ordinary_commit(self):
        with adapter.compatibility_parser() as (_, compatible):
            self.assertEqual(compatible(None, "docs: update README\n"), (None, None))


if __name__ == "__main__":
    unittest.main()

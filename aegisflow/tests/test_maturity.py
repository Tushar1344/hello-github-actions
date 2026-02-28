"""Tests for the maturity scoring module."""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.maturity_score import (
    check_basic_structure,
    check_ci_enforcement,
    check_observability,
    check_full_governance,
    compute_maturity,
    format_maturity_report,
)


class MaturityTestBase(unittest.TestCase):
    """Base class that creates a test aegisflow directory."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.root = self.tmpdir

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _create_file(self, path, content=""):
        full_path = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)


class TestBasicStructure(MaturityTestBase):
    def test_empty_dir(self):
        checks = check_basic_structure(self.root)
        self.assertFalse(any(checks.values()))

    def test_all_present(self):
        self._create_file("skills/skills.md", "# Skills")
        self._create_file("skills/skill_schema.yaml", "---")
        self._create_file("plugins/registry.json", "[]")
        self._create_file("plugins/plugin_schema.json", "{}")
        checks = check_basic_structure(self.root)
        self.assertTrue(all(checks.values()))


class TestCIEnforcement(MaturityTestBase):
    def test_no_ci(self):
        checks = check_ci_enforcement(self.root)
        self.assertFalse(all(checks.values()))

    def test_all_ci(self):
        self._create_file("ci/validate_skills.yml", "name: test")
        self._create_file("ci/validate_plugins.yml", "name: test")
        self._create_file("ci/security_scan.yml", "name: test")
        checks = check_ci_enforcement(self.root)
        self.assertTrue(all(checks.values()))


class TestObservability(MaturityTestBase):
    def test_no_observability(self):
        checks = check_observability(self.root)
        self.assertFalse(all(checks.values()))

    def test_with_telemetry_and_slo(self):
        self._create_file(
            "plugins/telemetry/test.yaml", "plugin: test\nenabled: true"
        )
        self._create_file(
            "plugins/healthchecks/healthcheck.py", "# healthcheck"
        )
        registry = [
            {
                "name": "test",
                "version": "1.0.0",
                "status": "active",
                "api_version": "v1",
                "owner": "team",
                "permissions": [],
                "healthcheck_url": "/health",
                "slo": {"latency_p95_ms": 500, "error_rate_percent": 1},
            }
        ]
        self._create_file(
            "plugins/registry.json", json.dumps(registry)
        )
        checks = check_observability(self.root)
        self.assertTrue(all(checks.values()))


class TestFullGovernance(MaturityTestBase):
    def test_no_governance(self):
        checks = check_full_governance(self.root)
        self.assertFalse(all(checks.values()))

    def test_all_governance(self):
        self._create_file("governance/lifecycle_policy.md", "# Policy")
        self._create_file(
            "governance/deprecation_policy.md",
            "# Policy\nAutomated retirement is enabled.",
        )
        self._create_file("governance/security_policy.md", "# Policy")
        self._create_file("governance/maturity_model.md", "# Model")
        self._create_file("scripts/detect_orphans.py", "# orphans")
        self._create_file("scripts/enforce_versioning.py", "# version")
        checks = check_full_governance(self.root)
        self.assertTrue(all(checks.values()))


class TestComputeMaturity(MaturityTestBase):
    def test_level_0(self):
        result = compute_maturity(self.root)
        self.assertEqual(result["level"], 0)

    def test_level_1(self):
        self._create_file("skills/skills.md", "# Skills")
        self._create_file("skills/skill_schema.yaml", "---")
        self._create_file("plugins/registry.json", "[]")
        self._create_file("plugins/plugin_schema.json", "{}")
        result = compute_maturity(self.root)
        self.assertEqual(result["level"], 1)


class TestFormatReport(MaturityTestBase):
    def test_format_report(self):
        result = compute_maturity(self.root)
        report = format_maturity_report(result)
        self.assertIn("AegisFlow Maturity", report)
        self.assertIn("Level", report)
        self.assertIn("Score", report)


if __name__ == "__main__":
    unittest.main()

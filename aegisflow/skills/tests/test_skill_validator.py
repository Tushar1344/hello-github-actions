"""Tests for the skill validator module."""

import os
import sys
import tempfile
import unittest

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.validators.skill_validator import (
    parse_skills_md,
    validate_semver,
    validate_status,
    validate_risk_level,
    validate_date,
    validate_coverage,
    validate_skill,
    validate_skills_file,
    check_stale_review,
    check_coverage_threshold,
    compare_versions,
    parse_semver,
)


VALID_SKILLS_MD = """# Skills Registry

## Skill: Data Processing
- Owner: platform-team
- Version: 1.2.0
- Status: Active
- Dependencies: pandas>=2.0
- Last Reviewed: 2026-02-01
- Test Coverage: 93%
- Risk Level: Medium
- Deprecation Date: N/A

## Skill: Text Normalization
- Owner: nlp-team
- Version: 0.3.0
- Status: Draft
- Dependencies: regex>=2023.0
- Last Reviewed: 2026-02-15
- Test Coverage: 85%
- Risk Level: Low
- Deprecation Date: N/A
"""

INVALID_SKILLS_MD = """# Skills Registry

## Skill: Bad Skill
- Owner: platform-team
- Version: not-a-version
- Status: Invalid
- Dependencies: none
- Last Reviewed: not-a-date
- Test Coverage: abc%
- Risk Level: Extreme
- Deprecation Date: N/A
"""

MISSING_FIELDS_MD = """# Skills Registry

## Skill: Incomplete Skill
- Owner: test-team
- Version: 1.0.0
"""


class TestSemver(unittest.TestCase):
    def test_valid_semver(self):
        self.assertTrue(validate_semver("1.0.0"))
        self.assertTrue(validate_semver("0.1.0"))
        self.assertTrue(validate_semver("10.20.30"))

    def test_invalid_semver(self):
        self.assertFalse(validate_semver("1.0"))
        self.assertFalse(validate_semver("v1.0.0"))
        self.assertFalse(validate_semver("1.0.0-beta"))
        self.assertFalse(validate_semver("abc"))
        self.assertFalse(validate_semver(""))

    def test_parse_semver(self):
        self.assertEqual(parse_semver("1.2.3"), (1, 2, 3))
        self.assertEqual(parse_semver("0.0.0"), (0, 0, 0))

    def test_compare_versions(self):
        self.assertEqual(compare_versions("1.0.0", "1.0.1"), 1)
        self.assertEqual(compare_versions("1.0.0", "1.1.0"), 1)
        self.assertEqual(compare_versions("1.0.0", "2.0.0"), 1)
        self.assertEqual(compare_versions("1.0.0", "1.0.0"), 0)
        self.assertEqual(compare_versions("2.0.0", "1.0.0"), -1)


class TestStatus(unittest.TestCase):
    def test_valid_statuses(self):
        for status in ["Draft", "Active", "Deprecated", "Retired"]:
            self.assertTrue(validate_status(status))

    def test_invalid_statuses(self):
        self.assertFalse(validate_status("draft"))
        self.assertFalse(validate_status("active"))
        self.assertFalse(validate_status("Invalid"))
        self.assertFalse(validate_status(""))


class TestRiskLevel(unittest.TestCase):
    def test_valid_risk_levels(self):
        for risk in ["Low", "Medium", "High"]:
            self.assertTrue(validate_risk_level(risk))

    def test_invalid_risk_levels(self):
        self.assertFalse(validate_risk_level("Extreme"))
        self.assertFalse(validate_risk_level("low"))
        self.assertFalse(validate_risk_level(""))


class TestDate(unittest.TestCase):
    def test_valid_dates(self):
        self.assertTrue(validate_date("2026-02-01"))
        self.assertTrue(validate_date("2025-12-31"))

    def test_invalid_dates(self):
        self.assertFalse(validate_date("02-01-2026"))
        self.assertFalse(validate_date("2026/02/01"))
        self.assertFalse(validate_date("not-a-date"))
        self.assertFalse(validate_date("2026-13-01"))


class TestCoverage(unittest.TestCase):
    def test_valid_coverage(self):
        self.assertEqual(validate_coverage("93%"), 93)
        self.assertEqual(validate_coverage("0%"), 0)
        self.assertEqual(validate_coverage("100%"), 100)

    def test_invalid_coverage(self):
        self.assertIsNone(validate_coverage("abc%"))
        self.assertIsNone(validate_coverage("93"))
        self.assertIsNone(validate_coverage(""))
        self.assertIsNone(validate_coverage("101%"))


class TestStaleReview(unittest.TestCase):
    def test_recent_review(self):
        from datetime import datetime, timedelta
        recent = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertFalse(check_stale_review(recent))

    def test_stale_review(self):
        self.assertTrue(check_stale_review("2020-01-01"))

    def test_invalid_date(self):
        self.assertTrue(check_stale_review("not-a-date"))


class TestCoverageThreshold(unittest.TestCase):
    def test_above_threshold(self):
        self.assertTrue(check_coverage_threshold("93%", 80))
        self.assertTrue(check_coverage_threshold("80%", 80))

    def test_below_threshold(self):
        self.assertFalse(check_coverage_threshold("50%", 80))
        self.assertFalse(check_coverage_threshold("0%", 80))


class TestParseSkillsMd(unittest.TestCase):
    def test_parse_valid(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(VALID_SKILLS_MD)
            path = f.name

        try:
            skills = parse_skills_md(path)
            self.assertEqual(len(skills), 2)
            self.assertEqual(skills[0]["name"], "Data Processing")
            self.assertEqual(skills[0]["Version"], "1.2.0")
            self.assertEqual(skills[0]["Status"], "Active")
            self.assertEqual(skills[0]["Owner"], "platform-team")
            self.assertEqual(skills[1]["name"], "Text Normalization")
        finally:
            os.unlink(path)

    def test_parse_empty(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write("# Empty registry\n")
            path = f.name

        try:
            skills = parse_skills_md(path)
            self.assertEqual(len(skills), 0)
        finally:
            os.unlink(path)


class TestValidateSkill(unittest.TestCase):
    def test_valid_skill(self):
        skill = {
            "name": "Test Skill",
            "Owner": "test-team",
            "Version": "1.0.0",
            "Status": "Active",
            "Dependencies": "none",
            "Last Reviewed": "2026-02-01",
            "Test Coverage": "90%",
            "Risk Level": "Low",
            "Deprecation Date": "N/A",
        }
        errors = validate_skill(skill)
        self.assertEqual(errors, [])

    def test_missing_fields(self):
        skill = {"name": "Incomplete"}
        errors = validate_skill(skill)
        self.assertTrue(len(errors) > 0)
        # Should have errors for each missing required field
        missing = [e for e in errors if "Missing" in e]
        self.assertTrue(len(missing) >= 5)

    def test_invalid_version(self):
        skill = {
            "name": "Bad Version",
            "Owner": "team",
            "Version": "abc",
            "Status": "Active",
            "Dependencies": "none",
            "Last Reviewed": "2026-02-01",
            "Test Coverage": "90%",
            "Risk Level": "Low",
            "Deprecation Date": "N/A",
        }
        errors = validate_skill(skill)
        self.assertTrue(any("version" in e.lower() for e in errors))

    def test_deprecated_without_date(self):
        skill = {
            "name": "Deprecated Skill",
            "Owner": "team",
            "Version": "1.0.0",
            "Status": "Deprecated",
            "Dependencies": "none",
            "Last Reviewed": "2026-02-01",
            "Test Coverage": "90%",
            "Risk Level": "Low",
            "Deprecation Date": "N/A",
        }
        errors = validate_skill(skill)
        self.assertTrue(
            any("Deprecated" in e and "Deprecation Date" in e for e in errors)
        )


class TestValidateSkillsFile(unittest.TestCase):
    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(VALID_SKILLS_MD)
            path = f.name

        try:
            result = validate_skills_file(path)
            self.assertTrue(result["valid"])
            self.assertEqual(len(result["skills"]), 2)
            self.assertEqual(len(result["errors"]), 0)
        finally:
            os.unlink(path)

    def test_invalid_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(INVALID_SKILLS_MD)
            path = f.name

        try:
            result = validate_skills_file(path)
            self.assertFalse(result["valid"])
            self.assertTrue(len(result["errors"]) > 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()

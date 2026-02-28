"""Tests for the SkillForge CLI."""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.forge_cli import (
    _bump_version,
    build_parser,
    cmd_add_skill,
    cmd_validate,
    cmd_list,
    cmd_bump,
    cmd_promote,
    cmd_deprecate,
    cmd_retire,
    cmd_review,
)
from skills.validators.skill_validator import parse_skills_md


class TestBumpVersion(unittest.TestCase):
    def test_bump_patch(self):
        self.assertEqual(_bump_version("1.0.0", "patch"), "1.0.1")

    def test_bump_minor(self):
        self.assertEqual(_bump_version("1.0.0", "minor"), "1.1.0")

    def test_bump_major(self):
        self.assertEqual(_bump_version("1.0.0", "major"), "2.0.0")

    def test_bump_minor_resets_patch(self):
        self.assertEqual(_bump_version("1.2.3", "minor"), "1.3.0")

    def test_bump_major_resets_minor_and_patch(self):
        self.assertEqual(_bump_version("1.2.3", "major"), "2.0.0")


class TestParser(unittest.TestCase):
    def test_parse_validate(self):
        parser = build_parser()
        args = parser.parse_args(["validate"])
        self.assertEqual(args.command, "validate")

    def test_parse_add_skill(self):
        parser = build_parser()
        args = parser.parse_args(
            ["add-skill", "My Skill", "--owner", "test-team", "--risk", "High"]
        )
        self.assertEqual(args.command, "add-skill")
        self.assertEqual(args.name, "My Skill")
        self.assertEqual(args.owner, "test-team")
        self.assertEqual(args.risk, "High")

    def test_parse_bump(self):
        parser = build_parser()
        args = parser.parse_args(
            ["bump", "skill", "My Skill", "--type", "minor"]
        )
        self.assertEqual(args.command, "bump")
        self.assertEqual(args.type, "skill")
        self.assertEqual(args.name, "My Skill")
        self.assertEqual(args.bump_type, "minor")

    def test_parse_list(self):
        parser = build_parser()
        args = parser.parse_args(["list", "skills"])
        self.assertEqual(args.command, "list")
        self.assertEqual(args.type, "skills")

    def test_parse_promote(self):
        parser = build_parser()
        args = parser.parse_args(["promote", "skill", "My Skill"])
        self.assertEqual(args.command, "promote")
        self.assertEqual(args.type, "skill")
        self.assertEqual(args.name, "My Skill")

    def test_parse_deprecate_with_replacement(self):
        parser = build_parser()
        args = parser.parse_args(
            ["deprecate", "plugin", "old_plugin", "--replacement", "new_plugin"]
        )
        self.assertEqual(args.command, "deprecate")
        self.assertEqual(args.replacement, "new_plugin")


class CLITestBase(unittest.TestCase):
    """Base class that sets up a temporary skillforge directory."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.skillforge_dir = os.path.join(self.tmpdir, "skillforge")
        os.makedirs(os.path.join(self.skillforge_dir, "skills", "validators"), exist_ok=True)
        os.makedirs(os.path.join(self.skillforge_dir, "skills", "tests"), exist_ok=True)
        os.makedirs(os.path.join(self.skillforge_dir, "plugins", "validators"), exist_ok=True)
        os.makedirs(os.path.join(self.skillforge_dir, "plugins", "telemetry"), exist_ok=True)
        os.makedirs(os.path.join(self.skillforge_dir, "plugins", "healthchecks"), exist_ok=True)
        os.makedirs(os.path.join(self.skillforge_dir, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(self.skillforge_dir, "ci"), exist_ok=True)
        os.makedirs(os.path.join(self.skillforge_dir, "governance"), exist_ok=True)

        # Copy schema files
        src_root = os.path.join(os.path.dirname(__file__), "..")
        shutil.copy2(
            os.path.join(src_root, "skills", "skill_schema.yaml"),
            os.path.join(self.skillforge_dir, "skills", "skill_schema.yaml"),
        )
        shutil.copy2(
            os.path.join(src_root, "plugins", "plugin_schema.json"),
            os.path.join(self.skillforge_dir, "plugins", "plugin_schema.json"),
        )

        # Create skills.md
        self.skills_md = os.path.join(self.skillforge_dir, "skills", "skills.md")
        with open(self.skills_md, "w") as f:
            f.write("""# Skills Registry

## Skill: Test Skill
- Owner: test-team
- Version: 1.0.0
- Status: Draft
- Dependencies: N/A
- Last Reviewed: 2026-02-01
- Test Coverage: 90%
- Risk Level: Low
- Deprecation Date: N/A
""")

        # Create registry.json
        self.registry_json = os.path.join(
            self.skillforge_dir, "plugins", "registry.json"
        )
        with open(self.registry_json, "w") as f:
            json.dump(
                [
                    {
                        "name": "test_plugin",
                        "version": "1.0.0",
                        "status": "draft",
                        "api_version": "v1",
                        "owner": "test-team",
                        "permissions": ["external_api"],
                        "healthcheck_url": "/health",
                        "slo": {
                            "latency_p95_ms": 500,
                            "error_rate_percent": 1,
                        },
                    }
                ],
                f,
                indent=2,
            )

        # Monkey-patch find_skillforge_root
        import scripts.forge_cli as cli_module
        self._original_find = cli_module.find_skillforge_root
        cli_module.find_skillforge_root = lambda: self.skillforge_dir

    def tearDown(self):
        import scripts.forge_cli as cli_module
        cli_module.find_skillforge_root = self._original_find
        shutil.rmtree(self.tmpdir)


class TestCLIAddSkill(CLITestBase):
    def test_add_skill(self):
        parser = build_parser()
        args = parser.parse_args(
            ["add-skill", "New Skill", "--owner", "dev-team", "--risk", "Medium"]
        )
        result = cmd_add_skill(args)
        self.assertEqual(result, 0)

        skills = parse_skills_md(self.skills_md)
        self.assertEqual(len(skills), 2)
        new_skill = skills[1]
        self.assertEqual(new_skill["name"], "New Skill")
        self.assertEqual(new_skill["Owner"], "dev-team")
        self.assertEqual(new_skill["Version"], "0.1.0")
        self.assertEqual(new_skill["Status"], "Draft")

    def test_add_duplicate_skill(self):
        parser = build_parser()
        args = parser.parse_args(["add-skill", "Test Skill", "--owner", "team"])
        result = cmd_add_skill(args)
        self.assertEqual(result, 1)


class TestCLIBump(CLITestBase):
    def test_bump_skill_patch(self):
        parser = build_parser()
        args = parser.parse_args(["bump", "skill", "Test Skill", "--type", "patch"])
        result = cmd_bump(args)
        self.assertEqual(result, 0)

        skills = parse_skills_md(self.skills_md)
        self.assertEqual(skills[0]["Version"], "1.0.1")

    def test_bump_skill_minor(self):
        parser = build_parser()
        args = parser.parse_args(["bump", "skill", "Test Skill", "--type", "minor"])
        result = cmd_bump(args)
        self.assertEqual(result, 0)

        skills = parse_skills_md(self.skills_md)
        self.assertEqual(skills[0]["Version"], "1.1.0")

    def test_bump_plugin(self):
        parser = build_parser()
        args = parser.parse_args(["bump", "plugin", "test_plugin", "--type", "major"])
        result = cmd_bump(args)
        self.assertEqual(result, 0)

        with open(self.registry_json) as f:
            plugins = json.load(f)
        self.assertEqual(plugins[0]["version"], "2.0.0")


class TestCLIPromote(CLITestBase):
    def test_promote_skill(self):
        parser = build_parser()
        args = parser.parse_args(["promote", "skill", "Test Skill"])
        result = cmd_promote(args)
        self.assertEqual(result, 0)

        skills = parse_skills_md(self.skills_md)
        self.assertEqual(skills[0]["Status"], "Active")

    def test_promote_plugin(self):
        parser = build_parser()
        args = parser.parse_args(["promote", "plugin", "test_plugin"])
        result = cmd_promote(args)
        self.assertEqual(result, 0)

        with open(self.registry_json) as f:
            plugins = json.load(f)
        self.assertEqual(plugins[0]["status"], "active")

    def test_promote_nonexistent(self):
        parser = build_parser()
        args = parser.parse_args(["promote", "skill", "Nonexistent"])
        result = cmd_promote(args)
        self.assertEqual(result, 1)


class TestCLIDeprecate(CLITestBase):
    def test_deprecate_skill(self):
        # First promote to Active
        parser = build_parser()
        args = parser.parse_args(["promote", "skill", "Test Skill"])
        cmd_promote(args)

        # Then deprecate
        args = parser.parse_args(
            ["deprecate", "skill", "Test Skill", "--replacement", "Better Skill"]
        )
        result = cmd_deprecate(args)
        self.assertEqual(result, 0)

        skills = parse_skills_md(self.skills_md)
        self.assertEqual(skills[0]["Status"], "Deprecated")


class TestCLIRetire(CLITestBase):
    def test_retire_skill(self):
        parser = build_parser()
        args = parser.parse_args(["retire", "skill", "Test Skill"])
        result = cmd_retire(args)
        self.assertEqual(result, 0)

        skills = parse_skills_md(self.skills_md)
        self.assertEqual(skills[0]["Status"], "Retired")

    def test_retire_plugin(self):
        parser = build_parser()
        args = parser.parse_args(["retire", "plugin", "test_plugin"])
        result = cmd_retire(args)
        self.assertEqual(result, 0)

        with open(self.registry_json) as f:
            plugins = json.load(f)
        self.assertEqual(plugins[0]["status"], "retired")


class TestCLIReview(CLITestBase):
    def test_review_skill(self):
        parser = build_parser()
        args = parser.parse_args(["review", "skill", "Test Skill"])
        result = cmd_review(args)
        self.assertEqual(result, 0)

        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        skills = parse_skills_md(self.skills_md)
        self.assertEqual(skills[0]["Last Reviewed"], today)


if __name__ == "__main__":
    unittest.main()

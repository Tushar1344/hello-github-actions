#!/usr/bin/env python3
"""AegisFlow CLI - Unified Lifecycle Governance Tool

The main command-line interface for managing skills and plugins
through the AegisFlow governance framework.

Usage:
    aegis init
    aegis add-skill "Skill Name" --owner team-name --risk Medium
    aegis validate
    aegis promote skill "Skill Name"
    aegis deprecate plugin plugin_name --replacement new_plugin
    aegis retire skill "Skill Name"
    aegis review skill "Skill Name"
    aegis bump skill "Skill Name" --type minor
    aegis list skills
    aegis list plugins
    aegis score
    aegis audit
    aegis telemetry plugin_name
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yaml

from skills.validators.skill_validator import (
    parse_skills_md,
    validate_skills_file,
    validate_semver,
    check_stale_review,
)
from plugins.validators.plugin_validator import validate_registry


def find_aegisflow_root():
    """Find the aegisflow root directory by searching upward from CWD."""
    # First check if we're inside aegisflow/
    current = os.path.abspath(os.getcwd())
    while current != "/":
        if os.path.basename(current) == "aegisflow":
            return current
        if os.path.isdir(os.path.join(current, "aegisflow")):
            return os.path.join(current, "aegisflow")
        current = os.path.dirname(current)

    # Fallback: relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


# ──────────────────────────────────────────────
# Command: init
# ──────────────────────────────────────────────

INIT_SCAFFOLD = {
    "skills": ["skills.md", "skill_schema.yaml"],
    "skills/validators": ["__init__.py"],
    "skills/tests": ["__init__.py"],
    "plugins": ["registry.json", "plugin_schema.json"],
    "plugins/validators": ["__init__.py"],
    "plugins/telemetry": [],
    "plugins/healthchecks": [],
    "ci": [],
    "governance": [],
    "scripts": ["__init__.py"],
    "tests": ["__init__.py"],
}

SKILLS_MD_TEMPLATE = """# AegisFlow Skills Registry

This file is the authoritative registry of all managed skills.
Each skill entry must conform to the skill schema defined in `skill_schema.yaml`.

---
"""

REGISTRY_JSON_TEMPLATE = "[]"


def cmd_init(args):
    """Initialize AegisFlow in the current repository."""
    target = os.path.join(os.getcwd(), "aegisflow")

    if os.path.exists(target):
        print(f"AegisFlow already initialized at {target}")
        return 1

    print(f"Initializing AegisFlow at {target}")
    os.makedirs(target, exist_ok=True)

    for directory, files in INIT_SCAFFOLD.items():
        dir_path = os.path.join(target, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"  Created {directory}/")

        for filename in files:
            filepath = os.path.join(dir_path, filename)
            if filename == "skills.md":
                with open(filepath, "w") as f:
                    f.write(SKILLS_MD_TEMPLATE)
            elif filename == "registry.json":
                with open(filepath, "w") as f:
                    f.write(REGISTRY_JSON_TEMPLATE)
            elif filename == "__init__.py":
                with open(filepath, "w") as f:
                    f.write("")
            else:
                # Copy schema files from our installation
                src = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), ".."
                )
                src_file = os.path.join(src, directory, filename)
                if os.path.exists(src_file):
                    shutil.copy2(src_file, filepath)
                else:
                    with open(filepath, "w") as f:
                        f.write("")

    print()
    print("AegisFlow initialized successfully.")
    print("Next steps:")
    print("  1. Add skills: aegis add-skill 'My Skill' --owner my-team")
    print("  2. Add plugins to plugins/registry.json")
    print("  3. Run: aegis validate")
    return 0


# ──────────────────────────────────────────────
# Command: add-skill
# ──────────────────────────────────────────────


def cmd_add_skill(args):
    """Add a new skill entry to skills.md."""
    root = find_aegisflow_root()
    skills_path = os.path.join(root, "skills", "skills.md")

    if not os.path.exists(skills_path):
        print(f"Error: Skills file not found: {skills_path}")
        return 1

    name = args.name
    owner = args.owner or "unassigned"
    risk = args.risk or "Low"
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if skill already exists
    existing = parse_skills_md(skills_path)
    for skill in existing:
        if skill["name"].lower() == name.lower():
            print(f"Error: Skill '{name}' already exists")
            return 1

    entry = f"""
## Skill: {name}
- Owner: {owner}
- Version: 0.1.0
- Status: Draft
- Dependencies: N/A
- Last Reviewed: {today}
- Test Coverage: 0%
- Risk Level: {risk}
- Deprecation Date: N/A
"""

    with open(skills_path, "a") as f:
        f.write(entry)

    print(f"Added skill '{name}' (Draft, v0.1.0)")
    print(f"  Owner: {owner}")
    print(f"  Risk: {risk}")
    return 0


# ──────────────────────────────────────────────
# Command: validate
# ──────────────────────────────────────────────


def cmd_validate(args):
    """Run all validations."""
    root = find_aegisflow_root()
    has_errors = False

    # Validate skills
    skills_path = os.path.join(root, "skills", "skills.md")
    if os.path.exists(skills_path):
        print("Validating skills...")
        result = validate_skills_file(skills_path)
        print(f"  {result['summary']}")
        if result["errors"]:
            has_errors = True
            for skill_name, errors in result["errors"].items():
                for error in errors:
                    print(f"    [X] {skill_name}: {error}")
    else:
        print("  No skills.md found, skipping skill validation")

    print()

    # Validate plugins
    registry_path = os.path.join(root, "plugins", "registry.json")
    if os.path.exists(registry_path):
        print("Validating plugins...")
        result = validate_registry(registry_path)
        print(f"  {result['summary']}")
        if result["errors"]:
            has_errors = True
            for plugin_name, errors in result["errors"].items():
                for error in errors:
                    print(f"    [X] {plugin_name}: {error}")
    else:
        print("  No registry.json found, skipping plugin validation")

    print()
    if has_errors:
        print("Validation FAILED. Fix the errors above.")
        return 1
    else:
        print("All validations passed.")
        return 0


# ──────────────────────────────────────────────
# Command: promote
# ──────────────────────────────────────────────


def cmd_promote(args):
    """Promote an artifact (Draft -> Active)."""
    root = find_aegisflow_root()
    artifact_type = args.type
    name = args.name

    if artifact_type == "skill":
        return _promote_skill(root, name)
    elif artifact_type == "plugin":
        return _promote_plugin(root, name)
    else:
        print(f"Error: Unknown type '{artifact_type}'. Use 'skill' or 'plugin'.")
        return 1


def _promote_skill(root, name):
    """Promote a skill from Draft to Active."""
    skills_path = os.path.join(root, "skills", "skills.md")
    with open(skills_path, "r") as f:
        content = f.read()

    # Find the skill section and update status
    pattern = re.compile(
        r"(## Skill: " + re.escape(name) + r"\n(?:.*\n)*?- Status: )(\w+)",
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        print(f"Error: Skill '{name}' not found")
        return 1

    current_status = match.group(2)
    if current_status != "Draft":
        print(
            f"Error: Can only promote Draft skills. "
            f"'{name}' is currently {current_status}."
        )
        return 1

    content = pattern.sub(r"\g<1>Active", content)

    with open(skills_path, "w") as f:
        f.write(content)

    print(f"Promoted skill '{name}': Draft -> Active")
    return 0


def _promote_plugin(root, name):
    """Promote a plugin from draft to active."""
    registry_path = os.path.join(root, "plugins", "registry.json")
    with open(registry_path, "r") as f:
        plugins = json.load(f)

    found = False
    for plugin in plugins:
        if plugin.get("name") == name:
            found = True
            if plugin["status"] != "draft":
                print(
                    f"Error: Can only promote draft plugins. "
                    f"'{name}' is currently {plugin['status']}."
                )
                return 1
            plugin["status"] = "active"
            break

    if not found:
        print(f"Error: Plugin '{name}' not found")
        return 1

    with open(registry_path, "w") as f:
        json.dump(plugins, f, indent=2)
        f.write("\n")

    print(f"Promoted plugin '{name}': draft -> active")
    return 0


# ──────────────────────────────────────────────
# Command: deprecate
# ──────────────────────────────────────────────


def cmd_deprecate(args):
    """Deprecate an artifact."""
    root = find_aegisflow_root()
    artifact_type = args.type
    name = args.name
    replacement = args.replacement

    if artifact_type == "skill":
        return _deprecate_skill(root, name, replacement)
    elif artifact_type == "plugin":
        return _deprecate_plugin(root, name, replacement)
    else:
        print(f"Error: Unknown type '{artifact_type}'. Use 'skill' or 'plugin'.")
        return 1


def _deprecate_skill(root, name, replacement=None):
    """Deprecate a skill."""
    skills_path = os.path.join(root, "skills", "skills.md")
    with open(skills_path, "r") as f:
        content = f.read()

    today = datetime.now().strftime("%Y-%m-%d")

    # Update status
    status_pattern = re.compile(
        r"(## Skill: " + re.escape(name) + r"\n(?:.*\n)*?- Status: )(\w+)",
        re.MULTILINE,
    )
    match = status_pattern.search(content)
    if not match:
        print(f"Error: Skill '{name}' not found")
        return 1

    current_status = match.group(2)
    if current_status not in ("Active", "Draft"):
        print(f"Error: Cannot deprecate a {current_status} skill.")
        return 1

    content = status_pattern.sub(r"\g<1>Deprecated", content)

    # Update deprecation date
    dep_pattern = re.compile(
        r"(## Skill: "
        + re.escape(name)
        + r"\n(?:.*\n)*?- Deprecation Date: )([^\n]+)",
        re.MULTILINE,
    )
    content = dep_pattern.sub(r"\g<1>" + today, content)

    with open(skills_path, "w") as f:
        f.write(content)

    msg = f"Deprecated skill '{name}' (effective {today})"
    if replacement:
        msg += f" -> replacement: '{replacement}'"
    print(msg)
    return 0


def _deprecate_plugin(root, name, replacement=None):
    """Deprecate a plugin."""
    registry_path = os.path.join(root, "plugins", "registry.json")
    with open(registry_path, "r") as f:
        plugins = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")

    found = False
    for plugin in plugins:
        if plugin.get("name") == name:
            found = True
            if plugin["status"] not in ("active", "draft"):
                print(f"Error: Cannot deprecate a {plugin['status']} plugin.")
                return 1
            plugin["status"] = "deprecated"
            plugin["deprecation_date"] = today
            if replacement:
                plugin["replacement"] = replacement
            break

    if not found:
        print(f"Error: Plugin '{name}' not found")
        return 1

    with open(registry_path, "w") as f:
        json.dump(plugins, f, indent=2)
        f.write("\n")

    msg = f"Deprecated plugin '{name}' (effective {today})"
    if replacement:
        msg += f" -> replacement: '{replacement}'"
    print(msg)
    return 0


# ──────────────────────────────────────────────
# Command: retire
# ──────────────────────────────────────────────


def cmd_retire(args):
    """Retire an artifact."""
    root = find_aegisflow_root()
    artifact_type = args.type
    name = args.name

    if artifact_type == "skill":
        return _retire_skill(root, name)
    elif artifact_type == "plugin":
        return _retire_plugin(root, name)
    else:
        print(f"Error: Unknown type '{artifact_type}'. Use 'skill' or 'plugin'.")
        return 1


def _retire_skill(root, name):
    """Retire a skill."""
    skills_path = os.path.join(root, "skills", "skills.md")
    with open(skills_path, "r") as f:
        content = f.read()

    status_pattern = re.compile(
        r"(## Skill: " + re.escape(name) + r"\n(?:.*\n)*?- Status: )(\w+)",
        re.MULTILINE,
    )
    match = status_pattern.search(content)
    if not match:
        print(f"Error: Skill '{name}' not found")
        return 1

    content = status_pattern.sub(r"\g<1>Retired", content)

    with open(skills_path, "w") as f:
        f.write(content)

    print(f"Retired skill '{name}'")
    return 0


def _retire_plugin(root, name):
    """Retire a plugin."""
    registry_path = os.path.join(root, "plugins", "registry.json")
    with open(registry_path, "r") as f:
        plugins = json.load(f)

    found = False
    for plugin in plugins:
        if plugin.get("name") == name:
            found = True
            plugin["status"] = "retired"
            break

    if not found:
        print(f"Error: Plugin '{name}' not found")
        return 1

    with open(registry_path, "w") as f:
        json.dump(plugins, f, indent=2)
        f.write("\n")

    print(f"Retired plugin '{name}'")
    return 0


# ──────────────────────────────────────────────
# Command: review
# ──────────────────────────────────────────────


def cmd_review(args):
    """Update the review date for an artifact."""
    root = find_aegisflow_root()
    artifact_type = args.type
    name = args.name

    if artifact_type == "skill":
        return _review_skill(root, name)
    elif artifact_type == "plugin":
        print("Plugin review tracking is managed via the registry.")
        print("Update the plugin entry directly in registry.json.")
        return 0
    else:
        print(f"Error: Unknown type '{artifact_type}'. Use 'skill' or 'plugin'.")
        return 1


def _review_skill(root, name):
    """Update the Last Reviewed date for a skill."""
    skills_path = os.path.join(root, "skills", "skills.md")
    with open(skills_path, "r") as f:
        content = f.read()

    today = datetime.now().strftime("%Y-%m-%d")

    pattern = re.compile(
        r"(## Skill: "
        + re.escape(name)
        + r"\n(?:.*\n)*?- Last Reviewed: )([^\n]+)",
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        print(f"Error: Skill '{name}' not found")
        return 1

    content = pattern.sub(r"\g<1>" + today, content)

    with open(skills_path, "w") as f:
        f.write(content)

    print(f"Updated review date for skill '{name}': {today}")
    return 0


# ──────────────────────────────────────────────
# Command: bump
# ──────────────────────────────────────────────


def _bump_version(version, bump_type):
    """Increment a semver version string."""
    parts = version.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1

    return f"{major}.{minor}.{patch}"


def cmd_bump(args):
    """Bump the version of an artifact."""
    root = find_aegisflow_root()
    artifact_type = args.type
    name = args.name
    bump_type = args.bump_type or "patch"

    if bump_type not in ("major", "minor", "patch"):
        print(f"Error: Invalid bump type '{bump_type}'. Use major, minor, or patch.")
        return 1

    if artifact_type == "skill":
        return _bump_skill(root, name, bump_type)
    elif artifact_type == "plugin":
        return _bump_plugin(root, name, bump_type)
    else:
        print(f"Error: Unknown type '{artifact_type}'. Use 'skill' or 'plugin'.")
        return 1


def _bump_skill(root, name, bump_type):
    """Bump a skill's version."""
    skills_path = os.path.join(root, "skills", "skills.md")
    with open(skills_path, "r") as f:
        content = f.read()

    pattern = re.compile(
        r"(## Skill: "
        + re.escape(name)
        + r"\n(?:.*\n)*?- Version: )(\d+\.\d+\.\d+)",
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        print(f"Error: Skill '{name}' not found or has invalid version")
        return 1

    old_version = match.group(2)
    new_version = _bump_version(old_version, bump_type)

    content = pattern.sub(r"\g<1>" + new_version, content)

    with open(skills_path, "w") as f:
        f.write(content)

    print(f"Bumped skill '{name}': {old_version} -> {new_version} ({bump_type})")
    return 0


def _bump_plugin(root, name, bump_type):
    """Bump a plugin's version."""
    registry_path = os.path.join(root, "plugins", "registry.json")
    with open(registry_path, "r") as f:
        plugins = json.load(f)

    found = False
    for plugin in plugins:
        if plugin.get("name") == name:
            found = True
            old_version = plugin["version"]
            new_version = _bump_version(old_version, bump_type)
            plugin["version"] = new_version
            print(
                f"Bumped plugin '{name}': {old_version} -> {new_version} ({bump_type})"
            )
            break

    if not found:
        print(f"Error: Plugin '{name}' not found")
        return 1

    with open(registry_path, "w") as f:
        json.dump(plugins, f, indent=2)
        f.write("\n")

    return 0


# ──────────────────────────────────────────────
# Command: list
# ──────────────────────────────────────────────


def cmd_list(args):
    """List skills or plugins."""
    root = find_aegisflow_root()
    list_type = args.type

    if list_type == "skills":
        return _list_skills(root)
    elif list_type == "plugins":
        return _list_plugins(root)
    else:
        print(f"Error: Unknown type '{list_type}'. Use 'skills' or 'plugins'.")
        return 1


def _list_skills(root):
    """List all skills."""
    skills_path = os.path.join(root, "skills", "skills.md")
    if not os.path.exists(skills_path):
        print("No skills.md found.")
        return 1

    skills = parse_skills_md(skills_path)
    if not skills:
        print("No skills found.")
        return 0

    print(f"{'Name':<30} {'Version':<10} {'Status':<12} {'Owner':<20} {'Risk':<8}")
    print("-" * 80)
    for skill in skills:
        print(
            f"{skill.get('name', '?'):<30} "
            f"{skill.get('Version', '?'):<10} "
            f"{skill.get('Status', '?'):<12} "
            f"{skill.get('Owner', '?'):<20} "
            f"{skill.get('Risk Level', '?'):<8}"
        )

    print()
    print(f"Total: {len(skills)} skill(s)")
    return 0


def _list_plugins(root):
    """List all plugins."""
    registry_path = os.path.join(root, "plugins", "registry.json")
    if not os.path.exists(registry_path):
        print("No registry.json found.")
        return 1

    with open(registry_path) as f:
        data = json.load(f)

    plugins = data if isinstance(data, list) else data.get("plugins", [])
    if not plugins:
        print("No plugins found.")
        return 0

    print(
        f"{'Name':<25} {'Version':<10} {'Status':<12} "
        f"{'API':<6} {'Owner':<20}"
    )
    print("-" * 73)
    for plugin in plugins:
        print(
            f"{plugin.get('name', '?'):<25} "
            f"{plugin.get('version', '?'):<10} "
            f"{plugin.get('status', '?'):<12} "
            f"{plugin.get('api_version', '?'):<6} "
            f"{plugin.get('owner', '?'):<20}"
        )

    print()
    print(f"Total: {len(plugins)} plugin(s)")
    return 0


# ──────────────────────────────────────────────
# Command: score
# ──────────────────────────────────────────────


def cmd_score(args):
    """Show maturity score."""
    # Import and run maturity scoring
    from scripts.maturity_score import compute_maturity, format_maturity_report

    root = find_aegisflow_root()
    result = compute_maturity(root)
    print(format_maturity_report(result))
    return 0


# ──────────────────────────────────────────────
# Command: audit
# ──────────────────────────────────────────────


def cmd_audit(args):
    """Run a comprehensive governance audit."""
    root = find_aegisflow_root()
    issues = []

    print("AegisFlow Governance Audit")
    print("=" * 50)
    print()

    # 1. Run validations
    print("1. Schema Validation")
    print("-" * 30)

    skills_path = os.path.join(root, "skills", "skills.md")
    if os.path.exists(skills_path):
        result = validate_skills_file(skills_path)
        if result["valid"]:
            print(f"  [+] Skills: {result['summary']}")
        else:
            print(f"  [X] Skills: {result['summary']}")
            for name, errors in result["errors"].items():
                for error in errors:
                    issues.append(f"Skill '{name}': {error}")

    registry_path = os.path.join(root, "plugins", "registry.json")
    if os.path.exists(registry_path):
        result = validate_registry(registry_path)
        if result["valid"]:
            print(f"  [+] Plugins: {result['summary']}")
        else:
            print(f"  [X] Plugins: {result['summary']}")
            for name, errors in result["errors"].items():
                for error in errors:
                    issues.append(f"Plugin '{name}': {error}")

    print()

    # 2. Orphan detection
    print("2. Orphan Detection")
    print("-" * 30)

    from scripts.detect_orphans import find_orphan_skills, find_orphan_plugins

    skill_orphans = find_orphan_skills(root)
    plugin_orphans = find_orphan_plugins(root)

    if skill_orphans or plugin_orphans:
        for orphan in skill_orphans + plugin_orphans:
            msg = f"Orphan {orphan['type']}: '{orphan['name']}'"
            print(f"  [!] {msg}")
            issues.append(msg)
    else:
        print("  [+] No orphans detected")

    print()

    # 3. Stale review check
    print("3. Stale Review Check")
    print("-" * 30)

    if os.path.exists(skills_path):
        skills = parse_skills_md(skills_path)
        for skill in skills:
            last_reviewed = skill.get("Last Reviewed", "")
            if last_reviewed and check_stale_review(last_reviewed):
                msg = f"Skill '{skill['name']}' review is stale (last: {last_reviewed})"
                print(f"  [!] {msg}")
                issues.append(msg)
            elif last_reviewed:
                print(f"  [+] Skill '{skill['name']}': reviewed {last_reviewed}")

    print()

    # 4. Maturity assessment
    print("4. Maturity Assessment")
    print("-" * 30)

    from scripts.maturity_score import compute_maturity

    maturity = compute_maturity(root)
    print(f"  Level: {maturity['level']}")
    print(f"  Score: {maturity['score']}%")

    print()

    # Summary
    print("=" * 50)
    if issues:
        print(f"Audit completed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("Audit passed. No issues found.")
        return 0


# ──────────────────────────────────────────────
# Command: telemetry
# ──────────────────────────────────────────────


def cmd_telemetry(args):
    """Show telemetry configuration for a plugin."""
    root = find_aegisflow_root()
    name = args.name

    telemetry_dir = os.path.join(root, "plugins", "telemetry")
    config_path = os.path.join(telemetry_dir, f"{name}.yaml")

    if not os.path.exists(config_path):
        config_path = os.path.join(telemetry_dir, f"{name}.yml")

    if not os.path.exists(config_path):
        print(f"No telemetry configuration found for '{name}'")
        print(f"Expected at: {os.path.join(telemetry_dir, f'{name}.yaml')}")
        return 1

    with open(config_path) as f:
        config = yaml.safe_load(f)

    print(f"Telemetry Configuration: {name}")
    print("=" * 40)
    print(f"  Enabled: {config.get('enabled', False)}")
    print()

    metrics = config.get("metrics", {})
    if metrics:
        print("  Metrics:")
        for metric, status in metrics.items():
            icon = "+" if status == "enabled" else "X"
            print(f"    [{icon}] {metric}: {status}")

    print()

    slo = config.get("slo", {})
    if slo:
        print("  SLO Targets:")
        for key, value in slo.items():
            print(f"    {key}: {value}")

    print()

    alerts = config.get("alerts", {})
    if alerts:
        print("  Alerts:")
        for alert_name, alert_config in alerts.items():
            print(
                f"    {alert_name}: {alert_config.get('condition', '?')} "
                f"[{alert_config.get('severity', '?')}]"
            )

    return 0


# ──────────────────────────────────────────────
# Main CLI Parser
# ──────────────────────────────────────────────


def build_parser():
    """Build the argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="aegis",
        description="AegisFlow - Unified Lifecycle Governance CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    subparsers.add_parser("init", help="Initialize AegisFlow in current repo")

    # add-skill
    add_skill_parser = subparsers.add_parser(
        "add-skill", help="Add a new skill entry"
    )
    add_skill_parser.add_argument("name", help="Name of the skill")
    add_skill_parser.add_argument("--owner", help="Owner team/individual")
    add_skill_parser.add_argument(
        "--risk",
        choices=["Low", "Medium", "High"],
        default="Low",
        help="Risk level",
    )

    # validate
    subparsers.add_parser("validate", help="Run all validations")

    # promote
    promote_parser = subparsers.add_parser(
        "promote", help="Promote artifact (Draft -> Active)"
    )
    promote_parser.add_argument(
        "type", choices=["skill", "plugin"], help="Artifact type"
    )
    promote_parser.add_argument("name", help="Artifact name")

    # deprecate
    deprecate_parser = subparsers.add_parser(
        "deprecate", help="Deprecate an artifact"
    )
    deprecate_parser.add_argument(
        "type", choices=["skill", "plugin"], help="Artifact type"
    )
    deprecate_parser.add_argument("name", help="Artifact name")
    deprecate_parser.add_argument(
        "--replacement", help="Name of replacement artifact"
    )

    # retire
    retire_parser = subparsers.add_parser("retire", help="Retire an artifact")
    retire_parser.add_argument(
        "type", choices=["skill", "plugin"], help="Artifact type"
    )
    retire_parser.add_argument("name", help="Artifact name")

    # review
    review_parser = subparsers.add_parser(
        "review", help="Update review date"
    )
    review_parser.add_argument(
        "type", choices=["skill", "plugin"], help="Artifact type"
    )
    review_parser.add_argument("name", help="Artifact name")

    # bump
    bump_parser = subparsers.add_parser("bump", help="Bump artifact version")
    bump_parser.add_argument(
        "type", choices=["skill", "plugin"], help="Artifact type"
    )
    bump_parser.add_argument("name", help="Artifact name")
    bump_parser.add_argument(
        "--type",
        dest="bump_type",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Version bump type (default: patch)",
    )

    # list
    list_parser = subparsers.add_parser("list", help="List artifacts")
    list_parser.add_argument(
        "type", choices=["skills", "plugins"], help="What to list"
    )

    # score
    subparsers.add_parser("score", help="Show maturity score")

    # audit
    subparsers.add_parser("audit", help="Run governance audit")

    # telemetry
    telemetry_parser = subparsers.add_parser(
        "telemetry", help="Show telemetry config"
    )
    telemetry_parser.add_argument("name", help="Plugin name")

    return parser


COMMAND_MAP = {
    "init": cmd_init,
    "add-skill": cmd_add_skill,
    "validate": cmd_validate,
    "promote": cmd_promote,
    "deprecate": cmd_deprecate,
    "retire": cmd_retire,
    "review": cmd_review,
    "bump": cmd_bump,
    "list": cmd_list,
    "score": cmd_score,
    "audit": cmd_audit,
    "telemetry": cmd_telemetry,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    handler = COMMAND_MAP.get(args.command)
    if handler:
        exit_code = handler(args)
        sys.exit(exit_code or 0)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

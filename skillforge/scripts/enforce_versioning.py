#!/usr/bin/env python3
"""Version enforcement utility.

Compares current skill/plugin versions against a previous state
(from git) and ensures versions have been properly incremented
when changes are detected.

Usage:
    python enforce_versioning.py [--base-ref REF]
"""

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.validators.skill_validator import (
    parse_skills_md,
    validate_semver,
    compare_versions,
)


def find_skillforge_root():
    """Find the skillforge root directory."""
    current = os.path.dirname(os.path.abspath(__file__))
    while current != "/":
        if os.path.basename(current) == "skillforge":
            return current
        if os.path.isdir(os.path.join(current, "skillforge")):
            return os.path.join(current, "skillforge")
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_file_at_ref(filepath, ref):
    """Get file contents at a specific git ref."""
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{filepath}"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception:
        return None


def get_changed_files(base_ref):
    """Get list of files changed since base_ref."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")
        return []
    except Exception:
        return []


def check_skill_versions(root, base_ref):
    """Check that skill versions have been incremented when content changes."""
    skills_path = os.path.join(root, "skills", "skills.md")
    rel_path = os.path.relpath(skills_path)
    errors = []

    changed_files = get_changed_files(base_ref)
    if rel_path not in changed_files:
        return []

    # Parse current skills
    current_skills = parse_skills_md(skills_path)
    current_map = {s["name"]: s for s in current_skills}

    # Parse old skills from git ref
    old_content = get_file_at_ref(rel_path, base_ref)
    if old_content is None:
        return []  # New file, no version comparison needed

    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(old_content)
        tmp_path = f.name

    try:
        old_skills = parse_skills_md(tmp_path)
    finally:
        os.unlink(tmp_path)

    old_map = {s["name"]: s for s in old_skills}

    # Compare versions
    for name, current in current_map.items():
        if name not in old_map:
            continue  # New skill, no comparison needed

        old = old_map[name]
        old_ver = old.get("Version", "0.0.0")
        new_ver = current.get("Version", "0.0.0")

        if not validate_semver(old_ver) or not validate_semver(new_ver):
            continue  # Handled by regular validation

        if compare_versions(old_ver, new_ver) <= 0:
            errors.append(
                f"Skill '{name}': version not incremented "
                f"(was {old_ver}, now {new_ver})"
            )

    return errors


def check_plugin_versions(root, base_ref):
    """Check that plugin versions have been incremented when content changes."""
    registry_path = os.path.join(root, "plugins", "registry.json")
    rel_path = os.path.relpath(registry_path)
    errors = []

    changed_files = get_changed_files(base_ref)
    if rel_path not in changed_files:
        return []

    # Load current registry
    with open(registry_path) as f:
        current_plugins = json.load(f)
    if isinstance(current_plugins, dict):
        current_plugins = current_plugins.get("plugins", [])
    current_map = {p["name"]: p for p in current_plugins}

    # Load old registry from git ref
    old_content = get_file_at_ref(rel_path, base_ref)
    if old_content is None:
        return []

    try:
        old_plugins = json.loads(old_content)
    except json.JSONDecodeError:
        return []

    if isinstance(old_plugins, dict):
        old_plugins = old_plugins.get("plugins", [])
    old_map = {p["name"]: p for p in old_plugins}

    # Compare versions
    for name, current in current_map.items():
        if name not in old_map:
            continue

        old = old_map[name]
        old_ver = old.get("version", "0.0.0")
        new_ver = current.get("version", "0.0.0")

        if compare_versions(old_ver, new_ver) <= 0:
            errors.append(
                f"Plugin '{name}': version not incremented "
                f"(was {old_ver}, now {new_ver})"
            )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Enforce version increments on changes"
    )
    parser.add_argument(
        "--base-ref",
        default="HEAD~1",
        help="Git ref to compare against (default: HEAD~1)",
    )
    args = parser.parse_args()

    root = find_skillforge_root()

    print(f"Checking version enforcement against {args.base_ref}")
    print()

    skill_errors = check_skill_versions(root, args.base_ref)
    plugin_errors = check_plugin_versions(root, args.base_ref)

    all_errors = skill_errors + plugin_errors

    if all_errors:
        print("Version enforcement errors:")
        for error in all_errors:
            print(f"  [X] {error}")
        print()
        print("Versions must be incremented when content changes.")
        sys.exit(1)
    else:
        print("[+] All version checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()

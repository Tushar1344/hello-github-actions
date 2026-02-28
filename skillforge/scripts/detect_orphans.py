#!/usr/bin/env python3
"""Orphan detection utility.

Finds skills and plugins that have missing or empty owners,
indicating they may need to be reassigned or retired.

Usage:
    python detect_orphans.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.validators.skill_validator import parse_skills_md


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


def find_orphan_skills(root):
    """Find skills with missing or empty owners."""
    skills_path = os.path.join(root, "skills", "skills.md")
    if not os.path.exists(skills_path):
        return []

    skills = parse_skills_md(skills_path)
    orphans = []

    for skill in skills:
        owner = skill.get("Owner", "").strip()
        if not owner:
            orphans.append({
                "type": "skill",
                "name": skill.get("name", "Unknown"),
                "version": skill.get("Version", "?"),
                "status": skill.get("Status", "?"),
                "reason": "Missing or empty owner",
            })

    return orphans


def find_orphan_plugins(root):
    """Find plugins with missing or empty owners."""
    registry_path = os.path.join(root, "plugins", "registry.json")
    if not os.path.exists(registry_path):
        return []

    with open(registry_path) as f:
        data = json.load(f)

    plugins = data if isinstance(data, list) else data.get("plugins", [])
    orphans = []

    for plugin in plugins:
        owner = plugin.get("owner", "").strip()
        if not owner:
            orphans.append({
                "type": "plugin",
                "name": plugin.get("name", "unknown"),
                "version": plugin.get("version", "?"),
                "status": plugin.get("status", "?"),
                "reason": "Missing or empty owner",
            })

    return orphans


def main():
    root = find_skillforge_root()

    print("SkillForge Orphan Detection")
    print("=" * 40)
    print()

    skill_orphans = find_orphan_skills(root)
    plugin_orphans = find_orphan_plugins(root)
    all_orphans = skill_orphans + plugin_orphans

    if all_orphans:
        for orphan in all_orphans:
            print(
                f"  [!] {orphan['type'].title()} '{orphan['name']}' "
                f"(v{orphan['version']}, {orphan['status']}): "
                f"{orphan['reason']}"
            )
        print()
        print(f"Found {len(all_orphans)} orphan(s). Please assign owners.")
        sys.exit(1)
    else:
        print("  [+] No orphans detected. All artifacts have owners.")
        sys.exit(0)


if __name__ == "__main__":
    main()

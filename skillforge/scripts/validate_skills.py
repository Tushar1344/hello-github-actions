#!/usr/bin/env python3
"""Standalone skill validation script.

Validates all skills in skills.md against the skill schema.
Exits with code 0 on success, 1 on validation errors.

Usage:
    python validate_skills.py [--skills-path PATH] [--schema-path PATH]
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.validators.skill_validator import validate_skills_file


def find_skillforge_root():
    """Find the skillforge root directory by searching upward."""
    current = os.path.dirname(os.path.abspath(__file__))
    while current != "/":
        if os.path.basename(current) == "skillforge":
            return current
        if os.path.isdir(os.path.join(current, "skillforge")):
            return os.path.join(current, "skillforge")
        current = os.path.dirname(current)
    # Default: assume scripts/ is inside skillforge/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description="Validate SkillForge skills")
    parser.add_argument(
        "--skills-path",
        default=None,
        help="Path to skills.md file",
    )
    parser.add_argument(
        "--schema-path",
        default=None,
        help="Path to skill_schema.yaml file",
    )
    args = parser.parse_args()

    root = find_skillforge_root()
    skills_path = args.skills_path or os.path.join(root, "skills", "skills.md")
    schema_path = args.schema_path or os.path.join(
        root, "skills", "skill_schema.yaml"
    )

    if not os.path.exists(skills_path):
        print(f"Error: Skills file not found: {skills_path}")
        sys.exit(1)

    print(f"Validating skills: {skills_path}")
    print(f"Using schema: {schema_path}")
    print()

    result = validate_skills_file(skills_path, schema_path)

    print(result["summary"])
    print()

    if result["errors"]:
        for skill_name, errors in result["errors"].items():
            print(f"  Skill '{skill_name}':")
            for error in errors:
                print(f"    [X] {error}")
            print()
        sys.exit(1)
    else:
        for skill in result["skills"]:
            print(f"  [+] {skill['name']}: OK (v{skill.get('Version', '?')})")
        print()
        print("All skills validated successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()

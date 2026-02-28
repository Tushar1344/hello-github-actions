#!/usr/bin/env python3
"""SkillForge Maturity Scoring Engine.

Evaluates the governance maturity of the SkillForge deployment
across multiple dimensions and provides a scored assessment.

Maturity Levels:
  Level 0: No governance
  Level 1: Basic structure (schema + skills.md exist)
  Level 2: Validation enabled (validators present and passing)
  Level 3: CI enforcement (CI workflows configured)
  Level 4: Observability (telemetry + SLO monitoring active)
  Level 5: Full governance (automated retirement, complete policies)

Usage:
    python maturity_score.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


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


def check_basic_structure(root):
    """Check Level 1: Basic structure exists."""
    checks = {
        "Skills registry exists": os.path.exists(
            os.path.join(root, "skills", "skills.md")
        ),
        "Skill schema exists": os.path.exists(
            os.path.join(root, "skills", "skill_schema.yaml")
        ),
        "Plugin registry exists": os.path.exists(
            os.path.join(root, "plugins", "registry.json")
        ),
        "Plugin schema exists": os.path.exists(
            os.path.join(root, "plugins", "plugin_schema.json")
        ),
    }
    return checks


def check_validation(root):
    """Check Level 2: Validation is enabled."""
    checks = {
        "Skill validator exists": os.path.exists(
            os.path.join(root, "skills", "validators", "skill_validator.py")
        ),
        "Plugin validator exists": os.path.exists(
            os.path.join(root, "plugins", "validators", "plugin_validator.py")
        ),
        "Validation scripts exist": (
            os.path.exists(os.path.join(root, "scripts", "validate_skills.py"))
            and os.path.exists(
                os.path.join(root, "scripts", "validate_plugins.py")
            )
        ),
    }

    # Try running validators
    try:
        from skills.validators.skill_validator import validate_skills_file

        skills_path = os.path.join(root, "skills", "skills.md")
        if os.path.exists(skills_path):
            result = validate_skills_file(skills_path)
            checks["Skills validation passes"] = result["valid"]
        else:
            checks["Skills validation passes"] = False
    except Exception:
        checks["Skills validation passes"] = False

    try:
        from plugins.validators.plugin_validator import validate_registry

        registry_path = os.path.join(root, "plugins", "registry.json")
        if os.path.exists(registry_path):
            result = validate_registry(registry_path)
            checks["Plugin validation passes"] = result["valid"]
        else:
            checks["Plugin validation passes"] = False
    except Exception:
        checks["Plugin validation passes"] = False

    return checks


def check_ci_enforcement(root):
    """Check Level 3: CI enforcement is configured."""
    checks = {
        "CI enforcement enabled": (
            os.path.exists(os.path.join(root, "ci", "validate_skills.yml"))
            or os.path.exists(
                os.path.join(root, "..", ".github", "workflows", "skillforge.yml")
            )
        ),
        "Skill validation CI exists": os.path.exists(
            os.path.join(root, "ci", "validate_skills.yml")
        ),
        "Plugin validation CI exists": os.path.exists(
            os.path.join(root, "ci", "validate_plugins.yml")
        ),
        "Security scan CI exists": os.path.exists(
            os.path.join(root, "ci", "security_scan.yml")
        ),
    }
    return checks


def check_observability(root):
    """Check Level 4: Observability is active."""
    telemetry_dir = os.path.join(root, "plugins", "telemetry")

    checks = {
        "Telemetry active": (
            os.path.isdir(telemetry_dir)
            and len(os.listdir(telemetry_dir)) > 0
        ),
        "Healthcheck utility exists": os.path.exists(
            os.path.join(root, "plugins", "healthchecks", "healthcheck.py")
        ),
    }

    # Check if plugins have SLOs defined
    registry_path = os.path.join(root, "plugins", "registry.json")
    if os.path.exists(registry_path):
        try:
            with open(registry_path) as f:
                data = json.load(f)
            plugins = data if isinstance(data, list) else data.get("plugins", [])
            active_plugins = [p for p in plugins if p.get("status") != "retired"]
            slo_count = sum(1 for p in active_plugins if "slo" in p)
            checks["SLO monitoring enabled"] = slo_count == len(active_plugins) and len(active_plugins) > 0
        except Exception:
            checks["SLO monitoring enabled"] = False
    else:
        checks["SLO monitoring enabled"] = False

    return checks


def check_full_governance(root):
    """Check Level 5: Full governance controls."""
    checks = {
        "Lifecycle policy exists": os.path.exists(
            os.path.join(root, "governance", "lifecycle_policy.md")
        ),
        "Deprecation policy exists": os.path.exists(
            os.path.join(root, "governance", "deprecation_policy.md")
        ),
        "Security policy exists": os.path.exists(
            os.path.join(root, "governance", "security_policy.md")
        ),
        "Maturity model documented": os.path.exists(
            os.path.join(root, "governance", "maturity_model.md")
        ),
        "Orphan detection available": os.path.exists(
            os.path.join(root, "scripts", "detect_orphans.py")
        ),
        "Version enforcement available": os.path.exists(
            os.path.join(root, "scripts", "enforce_versioning.py")
        ),
    }

    # Check for automated retirement policy
    dep_policy = os.path.join(root, "governance", "deprecation_policy.md")
    if os.path.exists(dep_policy):
        with open(dep_policy) as f:
            content = f.read().lower()
        checks["Automated retirement enabled"] = "retirement" in content and "automat" in content
    else:
        checks["Automated retirement enabled"] = False

    return checks


def compute_maturity(root):
    """Compute the overall maturity level and score.

    Returns:
        dict: {
            'level': int (0-5),
            'score': float (0-100),
            'checks': dict of all checks by level,
            'summary': str
        }
    """
    levels = {
        1: ("Basic Structure", check_basic_structure(root)),
        2: ("Validation", check_validation(root)),
        3: ("CI Enforcement", check_ci_enforcement(root)),
        4: ("Observability", check_observability(root)),
        5: ("Full Governance", check_full_governance(root)),
    }

    all_checks = {}
    achieved_level = 0
    total_checks = 0
    passed_checks = 0

    for level_num, (level_name, checks) in levels.items():
        all_checks[level_num] = {"name": level_name, "checks": checks}
        level_passed = all(checks.values())
        total_checks += len(checks)
        passed_checks += sum(1 for v in checks.values() if v)

        if level_passed and level_num == achieved_level + 1:
            achieved_level = level_num

    score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    return {
        "level": achieved_level,
        "score": round(score, 1),
        "checks": all_checks,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
    }


def format_maturity_report(result):
    """Format maturity score as a human-readable report."""
    lines = [
        f"SkillForge Maturity: Level {result['level']}",
        f"Score: {result['score']}% ({result['passed_checks']}/{result['total_checks']} checks passed)",
        "=" * 50,
    ]

    for level_num, level_data in result["checks"].items():
        lines.append(f"")
        lines.append(f"Level {level_num}: {level_data['name']}")
        lines.append(f"-" * 30)
        for check_name, passed in level_data["checks"].items():
            icon = "+" if passed else "X"
            lines.append(f"  [{icon}] {check_name}")

    lines.append("")
    if result["level"] < 5:
        lines.append(
            f"Next: Achieve Level {result['level'] + 1} by completing "
            f"the remaining checks above."
        )
    else:
        lines.append("Congratulations! Full governance maturity achieved.")

    return "\n".join(lines)


def main():
    root = find_skillforge_root()
    result = compute_maturity(root)
    print(format_maturity_report(result))
    sys.exit(0)


if __name__ == "__main__":
    main()

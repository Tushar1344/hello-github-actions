"""SkillForge Skill Validator

Parses skills.md markdown files and validates each skill entry against
the skill schema. Supports semver validation, lifecycle state checks,
stale review detection, and coverage threshold enforcement.
"""

import re
import os
from datetime import datetime, timedelta
from pathlib import Path

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COVERAGE_PATTERN = re.compile(r"^(\d{1,3})%$")
VALID_STATUSES = {"Draft", "Active", "Deprecated", "Retired"}
VALID_RISK_LEVELS = {"Low", "Medium", "High"}

SKILL_HEADER_PATTERN = re.compile(r"^##\s+Skill:\s+(.+)$", re.MULTILINE)
FIELD_PATTERN = re.compile(r"^-\s+(.+?):\s+(.+)$", re.MULTILINE)


def load_schema(schema_path=None):
    """Load the skill schema YAML file."""
    if schema_path is None:
        schema_path = Path(__file__).parent.parent / "skill_schema.yaml"
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)


def parse_skills_md(path):
    """Parse a skills.md file into a list of skill dictionaries.

    Each skill is identified by a '## Skill: <name>' header followed by
    '- Key: Value' metadata lines.

    Returns:
        list[dict]: List of parsed skill entries, each with a 'name' key
        and additional metadata fields.
    """
    with open(path, "r") as f:
        content = f.read()

    skills = []
    sections = re.split(r"(?=^##\s+Skill:)", content, flags=re.MULTILINE)

    for section in sections:
        header_match = SKILL_HEADER_PATTERN.search(section)
        if not header_match:
            continue

        skill = {"name": header_match.group(1).strip()}

        for field_match in FIELD_PATTERN.finditer(section):
            key = field_match.group(1).strip()
            value = field_match.group(2).strip()
            skill[key] = value

        skills.append(skill)

    return skills


def validate_semver(version):
    """Check if a version string is valid semantic versioning."""
    return bool(SEMVER_PATTERN.match(version))


def parse_semver(version):
    """Parse a semver string into (major, minor, patch) tuple."""
    parts = version.split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])


def compare_versions(old_version, new_version):
    """Compare two semver strings. Returns 1 if new > old, 0 if equal, -1 if new < old."""
    old = parse_semver(old_version)
    new = parse_semver(new_version)
    if new > old:
        return 1
    elif new == old:
        return 0
    else:
        return -1


def validate_status(status):
    """Check if a status value is valid."""
    return status in VALID_STATUSES


def validate_risk_level(risk):
    """Check if a risk level value is valid."""
    return risk in VALID_RISK_LEVELS


def validate_date(date_str):
    """Check if a date string is valid ISO 8601 format."""
    if not DATE_PATTERN.match(date_str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_coverage(coverage_str):
    """Validate a coverage percentage string like '93%'. Returns the numeric value or None."""
    match = COVERAGE_PATTERN.match(coverage_str)
    if not match:
        return None
    value = int(match.group(1))
    if 0 <= value <= 100:
        return value
    return None


def check_stale_review(last_reviewed, max_days=90):
    """Check if a review date is stale (older than max_days).

    Returns:
        bool: True if the review is stale, False otherwise.
    """
    try:
        review_date = datetime.strptime(last_reviewed, "%Y-%m-%d")
        threshold = datetime.now() - timedelta(days=max_days)
        return review_date < threshold
    except (ValueError, TypeError):
        return True


def check_coverage_threshold(coverage_str, min_pct=80):
    """Check if coverage meets the minimum threshold.

    Returns:
        bool: True if coverage meets threshold, False otherwise.
    """
    value = validate_coverage(coverage_str)
    if value is None:
        return False
    return value >= min_pct


def validate_skill(skill, schema=None):
    """Validate a single skill entry against the schema.

    Args:
        skill: Dictionary of skill metadata.
        schema: Optional schema dict. If None, uses defaults.

    Returns:
        list[str]: List of validation error messages. Empty list means valid.
    """
    errors = []

    required_fields = {
        "Owner": "owner",
        "Version": "semver",
        "Status": "enum",
        "Dependencies": "string",
        "Last Reviewed": "date",
        "Test Coverage": "percentage",
        "Risk Level": "enum",
        "Deprecation Date": "date_or_na",
    }

    # Check required fields
    for field, field_type in required_fields.items():
        if field not in skill:
            errors.append(f"Missing required field: {field}")
            continue

        value = skill[field]

        if field_type == "semver" and not validate_semver(value):
            errors.append(
                f"Invalid semantic version for {field}: '{value}' "
                f"(expected MAJOR.MINOR.PATCH)"
            )

        elif field_type == "date" and not validate_date(value):
            errors.append(
                f"Invalid date format for {field}: '{value}' "
                f"(expected YYYY-MM-DD)"
            )

        elif field_type == "date_or_na":
            if value != "N/A" and not validate_date(value):
                errors.append(
                    f"Invalid date format for {field}: '{value}' "
                    f"(expected YYYY-MM-DD or N/A)"
                )

        elif field == "Status" and not validate_status(value):
            errors.append(
                f"Invalid status: '{value}' "
                f"(expected one of: {', '.join(sorted(VALID_STATUSES))})"
            )

        elif field == "Risk Level" and not validate_risk_level(value):
            errors.append(
                f"Invalid risk level: '{value}' "
                f"(expected one of: {', '.join(sorted(VALID_RISK_LEVELS))})"
            )

        elif field_type == "percentage":
            if validate_coverage(value) is None:
                errors.append(
                    f"Invalid coverage format for {field}: '{value}' "
                    f"(expected 0-100%)"
                )

    # Check for empty owner
    if "Owner" in skill and not skill["Owner"].strip():
        errors.append("Owner field is empty")

    # Check name
    if "name" not in skill or not skill["name"].strip():
        errors.append("Skill name is missing or empty")

    # Load schema validation rules
    if schema:
        rules = schema.get("validation_rules", {})
        min_coverage = rules.get("min_test_coverage", 80)
        max_review_age = rules.get("max_review_age_days", 90)
    else:
        min_coverage = 80
        max_review_age = 90

    # Check coverage threshold (warning, not error)
    if "Test Coverage" in skill:
        if not check_coverage_threshold(skill["Test Coverage"], min_coverage):
            errors.append(
                f"Test coverage {skill['Test Coverage']} is below "
                f"minimum threshold of {min_coverage}%"
            )

    # Check stale review (warning)
    if "Last Reviewed" in skill and validate_date(skill["Last Reviewed"]):
        if check_stale_review(skill["Last Reviewed"], max_review_age):
            errors.append(
                f"Review is stale: last reviewed {skill['Last Reviewed']} "
                f"(exceeds {max_review_age} day threshold)"
            )

    # Deprecation date required if status is Deprecated
    if skill.get("Status") == "Deprecated":
        dep_date = skill.get("Deprecation Date", "N/A")
        if dep_date == "N/A":
            errors.append(
                "Deprecated skills must have a Deprecation Date set"
            )

    return errors


def validate_skills_file(path, schema_path=None):
    """Validate an entire skills.md file.

    Returns:
        dict: {
            'valid': bool,
            'skills': list of skill dicts,
            'errors': dict mapping skill names to error lists,
            'summary': str
        }
    """
    schema = load_schema(schema_path) if schema_path else load_schema()
    skills = parse_skills_md(path)

    if not skills:
        return {
            "valid": False,
            "skills": [],
            "errors": {"_global": ["No skills found in file"]},
            "summary": "No skills found",
        }

    all_errors = {}
    for skill in skills:
        name = skill.get("name", "Unknown")
        errors = validate_skill(skill, schema)
        if errors:
            all_errors[name] = errors

    is_valid = len(all_errors) == 0
    total_errors = sum(len(e) for e in all_errors.values())

    summary = (
        f"Validated {len(skills)} skill(s): "
        f"{len(skills) - len(all_errors)} passed, "
        f"{len(all_errors)} failed ({total_errors} error(s))"
    )

    return {
        "valid": is_valid,
        "skills": skills,
        "errors": all_errors,
        "summary": summary,
    }

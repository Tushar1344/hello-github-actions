"""AegisFlow Plugin Validator

Validates plugin entries in registry.json against the plugin schema.
Performs structural checks, semver validation, SLO validation,
permission checks, and healthcheck URL verification.
"""

import json
import re
from pathlib import Path


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
API_VERSION_PATTERN = re.compile(r"^v\d+$")
HEALTHCHECK_PATTERN = re.compile(r"^/")
PLUGIN_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

VALID_STATUSES = {"draft", "active", "deprecated", "retired"}
VALID_PERMISSIONS = {
    "external_api",
    "database",
    "filesystem",
    "network",
    "secrets",
    "compute",
}


def load_schema(schema_path=None):
    """Load the plugin JSON schema file."""
    if schema_path is None:
        schema_path = Path(__file__).parent.parent / "plugin_schema.json"
    with open(schema_path, "r") as f:
        return json.load(f)


def load_registry(path):
    """Load the plugin registry JSON file.

    Supports both a JSON array of plugins and an object with a 'plugins' key.

    Returns:
        list[dict]: List of plugin entry dictionaries.
    """
    with open(path, "r") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "plugins" in data:
        return data["plugins"]
    else:
        raise ValueError(
            "Invalid registry format: expected array or object with 'plugins' key"
        )


def validate_plugin(plugin):
    """Validate a single plugin entry.

    Args:
        plugin: Dictionary of plugin metadata.

    Returns:
        list[str]: List of validation error messages. Empty list means valid.
    """
    errors = []

    required_fields = [
        "name",
        "version",
        "status",
        "api_version",
        "owner",
        "permissions",
        "healthcheck_url",
        "slo",
    ]

    # Check required fields
    for field in required_fields:
        if field not in plugin:
            errors.append(f"Missing required field: {field}")

    # Validate name format
    if "name" in plugin:
        if not isinstance(plugin["name"], str):
            errors.append("Field 'name' must be a string")
        elif not PLUGIN_NAME_PATTERN.match(plugin["name"]):
            errors.append(
                f"Invalid plugin name: '{plugin['name']}' "
                f"(must be lowercase snake_case, starting with a letter)"
            )

    # Validate version (semver)
    if "version" in plugin:
        if not isinstance(plugin["version"], str):
            errors.append("Field 'version' must be a string")
        elif not SEMVER_PATTERN.match(plugin["version"]):
            errors.append(
                f"Invalid semantic version: '{plugin['version']}' "
                f"(expected MAJOR.MINOR.PATCH)"
            )

    # Validate status
    if "status" in plugin:
        if not isinstance(plugin["status"], str):
            errors.append("Field 'status' must be a string")
        elif plugin["status"] not in VALID_STATUSES:
            errors.append(
                f"Invalid status: '{plugin['status']}' "
                f"(expected one of: {', '.join(sorted(VALID_STATUSES))})"
            )

    # Validate api_version
    if "api_version" in plugin:
        if not isinstance(plugin["api_version"], str):
            errors.append("Field 'api_version' must be a string")
        elif not API_VERSION_PATTERN.match(plugin["api_version"]):
            errors.append(
                f"Invalid API version: '{plugin['api_version']}' "
                f"(expected format: v1, v2, etc.)"
            )

    # Validate owner
    if "owner" in plugin:
        if not isinstance(plugin["owner"], str):
            errors.append("Field 'owner' must be a string")
        elif not plugin["owner"].strip():
            errors.append("Owner field is empty")

    # Validate permissions
    if "permissions" in plugin:
        if not isinstance(plugin["permissions"], list):
            errors.append("Field 'permissions' must be an array")
        else:
            for perm in plugin["permissions"]:
                if not isinstance(perm, str):
                    errors.append(f"Permission must be a string, got: {type(perm).__name__}")
                elif perm not in VALID_PERMISSIONS:
                    errors.append(
                        f"Invalid permission: '{perm}' "
                        f"(expected one of: {', '.join(sorted(VALID_PERMISSIONS))})"
                    )

    # Validate healthcheck URL
    if "healthcheck_url" in plugin:
        if not isinstance(plugin["healthcheck_url"], str):
            errors.append("Field 'healthcheck_url' must be a string")
        elif not HEALTHCHECK_PATTERN.match(plugin["healthcheck_url"]):
            errors.append(
                f"Invalid healthcheck URL: '{plugin['healthcheck_url']}' "
                f"(must start with /)"
            )

    # Validate SLO
    if "slo" in plugin:
        slo = plugin["slo"]
        if not isinstance(slo, dict):
            errors.append("Field 'slo' must be an object")
        else:
            if "latency_p95_ms" not in slo:
                errors.append("SLO missing required field: latency_p95_ms")
            elif not isinstance(slo["latency_p95_ms"], int):
                errors.append("SLO latency_p95_ms must be an integer")
            elif slo["latency_p95_ms"] < 1 or slo["latency_p95_ms"] > 30000:
                errors.append(
                    f"SLO latency_p95_ms out of range: {slo['latency_p95_ms']} "
                    f"(must be 1-30000)"
                )

            if "error_rate_percent" not in slo:
                errors.append("SLO missing required field: error_rate_percent")
            elif not isinstance(slo["error_rate_percent"], (int, float)):
                errors.append("SLO error_rate_percent must be a number")
            elif slo["error_rate_percent"] < 0 or slo["error_rate_percent"] > 100:
                errors.append(
                    f"SLO error_rate_percent out of range: {slo['error_rate_percent']} "
                    f"(must be 0-100)"
                )

    # Validate deprecation_date if present
    if "deprecation_date" in plugin:
        if not DATE_PATTERN.match(str(plugin["deprecation_date"])):
            errors.append(
                f"Invalid deprecation_date: '{plugin['deprecation_date']}' "
                f"(expected YYYY-MM-DD)"
            )

    # Deprecated plugins should have deprecation_date
    if plugin.get("status") == "deprecated":
        if "deprecation_date" not in plugin:
            errors.append(
                "Deprecated plugins must have a deprecation_date set"
            )

    return errors


def validate_registry(path, schema_path=None):
    """Validate an entire plugin registry file.

    Returns:
        dict: {
            'valid': bool,
            'plugins': list of plugin dicts,
            'errors': dict mapping plugin names to error lists,
            'summary': str
        }
    """
    try:
        plugins = load_registry(path)
    except (json.JSONDecodeError, ValueError) as e:
        return {
            "valid": False,
            "plugins": [],
            "errors": {"_global": [f"Failed to load registry: {e}"]},
            "summary": f"Registry load failed: {e}",
        }

    if not plugins:
        return {
            "valid": False,
            "plugins": [],
            "errors": {"_global": ["No plugins found in registry"]},
            "summary": "No plugins found",
        }

    all_errors = {}
    names_seen = set()

    for i, plugin in enumerate(plugins):
        name = plugin.get("name", f"plugin_{i}")

        # Check for duplicate names
        if name in names_seen:
            all_errors.setdefault(name, []).append(
                f"Duplicate plugin name: '{name}'"
            )
        names_seen.add(name)

        errors = validate_plugin(plugin)
        if errors:
            all_errors.setdefault(name, []).extend(errors)

    is_valid = len(all_errors) == 0
    total_errors = sum(len(e) for e in all_errors.values())

    summary = (
        f"Validated {len(plugins)} plugin(s): "
        f"{len(plugins) - len(all_errors)} passed, "
        f"{len(all_errors)} failed ({total_errors} error(s))"
    )

    return {
        "valid": is_valid,
        "plugins": plugins,
        "errors": all_errors,
        "summary": summary,
    }

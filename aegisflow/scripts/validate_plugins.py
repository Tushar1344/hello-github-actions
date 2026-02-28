#!/usr/bin/env python3
"""Standalone plugin validation script.

Validates all plugins in registry.json against the plugin schema.
Exits with code 0 on success, 1 on validation errors.

Usage:
    python validate_plugins.py [--registry-path PATH] [--schema-path PATH]
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugins.validators.plugin_validator import validate_registry


def find_aegisflow_root():
    """Find the aegisflow root directory by searching upward."""
    current = os.path.dirname(os.path.abspath(__file__))
    while current != "/":
        if os.path.basename(current) == "aegisflow":
            return current
        if os.path.isdir(os.path.join(current, "aegisflow")):
            return os.path.join(current, "aegisflow")
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description="Validate AegisFlow plugins")
    parser.add_argument(
        "--registry-path",
        default=None,
        help="Path to registry.json file",
    )
    parser.add_argument(
        "--schema-path",
        default=None,
        help="Path to plugin_schema.json file",
    )
    args = parser.parse_args()

    root = find_aegisflow_root()
    registry_path = args.registry_path or os.path.join(
        root, "plugins", "registry.json"
    )
    schema_path = args.schema_path or os.path.join(
        root, "plugins", "plugin_schema.json"
    )

    if not os.path.exists(registry_path):
        print(f"Error: Registry file not found: {registry_path}")
        sys.exit(1)

    print(f"Validating plugins: {registry_path}")
    print(f"Using schema: {schema_path}")
    print()

    result = validate_registry(registry_path, schema_path)

    print(result["summary"])
    print()

    if result["errors"]:
        for plugin_name, errors in result["errors"].items():
            print(f"  Plugin '{plugin_name}':")
            for error in errors:
                print(f"    [X] {error}")
            print()
        sys.exit(1)
    else:
        for plugin in result["plugins"]:
            print(
                f"  [+] {plugin['name']}: OK "
                f"(v{plugin.get('version', '?')}, {plugin.get('status', '?')})"
            )
        print()
        print("All plugins validated successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()

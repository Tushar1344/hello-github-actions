"""Tests for the plugin validator module."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugins.validators.plugin_validator import (
    validate_plugin,
    validate_registry,
    load_registry,
)


VALID_PLUGIN = {
    "name": "test_plugin",
    "version": "1.0.0",
    "status": "active",
    "api_version": "v1",
    "owner": "test-team",
    "permissions": ["external_api"],
    "healthcheck_url": "/health",
    "slo": {
        "latency_p95_ms": 500,
        "error_rate_percent": 1,
    },
}

VALID_REGISTRY = [
    VALID_PLUGIN,
    {
        "name": "another_plugin",
        "version": "2.0.0",
        "status": "draft",
        "api_version": "v2",
        "owner": "platform-team",
        "permissions": ["database", "network"],
        "healthcheck_url": "/healthz",
        "slo": {
            "latency_p95_ms": 200,
            "error_rate_percent": 0.5,
        },
    },
]


class TestValidatePlugin(unittest.TestCase):
    def test_valid_plugin(self):
        errors = validate_plugin(VALID_PLUGIN)
        self.assertEqual(errors, [])

    def test_missing_required_fields(self):
        errors = validate_plugin({})
        self.assertTrue(len(errors) >= 8)
        missing_fields = [e for e in errors if "Missing" in e]
        self.assertEqual(len(missing_fields), 8)

    def test_invalid_name(self):
        plugin = {**VALID_PLUGIN, "name": "Invalid Name!"}
        errors = validate_plugin(plugin)
        self.assertTrue(any("name" in e.lower() for e in errors))

    def test_invalid_version(self):
        plugin = {**VALID_PLUGIN, "version": "v1.0"}
        errors = validate_plugin(plugin)
        self.assertTrue(any("version" in e.lower() for e in errors))

    def test_invalid_status(self):
        plugin = {**VALID_PLUGIN, "status": "unknown"}
        errors = validate_plugin(plugin)
        self.assertTrue(any("status" in e.lower() for e in errors))

    def test_invalid_api_version(self):
        plugin = {**VALID_PLUGIN, "api_version": "1.0"}
        errors = validate_plugin(plugin)
        self.assertTrue(any("api" in e.lower() for e in errors))

    def test_empty_owner(self):
        plugin = {**VALID_PLUGIN, "owner": "  "}
        errors = validate_plugin(plugin)
        self.assertTrue(any("owner" in e.lower() for e in errors))

    def test_invalid_permission(self):
        plugin = {**VALID_PLUGIN, "permissions": ["fly_to_moon"]}
        errors = validate_plugin(plugin)
        self.assertTrue(any("permission" in e.lower() for e in errors))

    def test_invalid_healthcheck_url(self):
        plugin = {**VALID_PLUGIN, "healthcheck_url": "no-slash"}
        errors = validate_plugin(plugin)
        self.assertTrue(any("healthcheck" in e.lower() for e in errors))

    def test_missing_slo_fields(self):
        plugin = {**VALID_PLUGIN, "slo": {}}
        errors = validate_plugin(plugin)
        self.assertTrue(any("latency" in e.lower() for e in errors))
        self.assertTrue(any("error_rate" in e.lower() for e in errors))

    def test_slo_out_of_range(self):
        plugin = {
            **VALID_PLUGIN,
            "slo": {"latency_p95_ms": 50000, "error_rate_percent": 200},
        }
        errors = validate_plugin(plugin)
        self.assertTrue(any("out of range" in e.lower() for e in errors))

    def test_deprecated_without_date(self):
        plugin = {**VALID_PLUGIN, "status": "deprecated"}
        errors = validate_plugin(plugin)
        self.assertTrue(
            any("deprecation_date" in e.lower() for e in errors)
        )

    def test_deprecated_with_date(self):
        plugin = {
            **VALID_PLUGIN,
            "status": "deprecated",
            "deprecation_date": "2026-03-01",
        }
        errors = validate_plugin(plugin)
        self.assertEqual(errors, [])

    def test_valid_all_permissions(self):
        plugin = {
            **VALID_PLUGIN,
            "permissions": [
                "external_api",
                "database",
                "filesystem",
                "network",
                "secrets",
                "compute",
            ],
        }
        errors = validate_plugin(plugin)
        self.assertEqual(errors, [])


class TestValidateRegistry(unittest.TestCase):
    def test_valid_registry(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(VALID_REGISTRY, f)
            path = f.name

        try:
            result = validate_registry(path)
            self.assertTrue(result["valid"])
            self.assertEqual(len(result["plugins"]), 2)
        finally:
            os.unlink(path)

    def test_invalid_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{invalid json")
            path = f.name

        try:
            result = validate_registry(path)
            self.assertFalse(result["valid"])
        finally:
            os.unlink(path)

    def test_empty_registry(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump([], f)
            path = f.name

        try:
            result = validate_registry(path)
            self.assertFalse(result["valid"])
        finally:
            os.unlink(path)

    def test_duplicate_names(self):
        registry = [VALID_PLUGIN, {**VALID_PLUGIN}]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(registry, f)
            path = f.name

        try:
            result = validate_registry(path)
            self.assertFalse(result["valid"])
            # Should detect duplicate
            self.assertTrue(
                any("duplicate" in str(e).lower() for errors in result["errors"].values() for e in errors)
            )
        finally:
            os.unlink(path)


class TestLoadRegistry(unittest.TestCase):
    def test_load_array_format(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump([VALID_PLUGIN], f)
            path = f.name

        try:
            plugins = load_registry(path)
            self.assertEqual(len(plugins), 1)
        finally:
            os.unlink(path)

    def test_load_object_format(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({"plugins": [VALID_PLUGIN]}, f)
            path = f.name

        try:
            plugins = load_registry(path)
            self.assertEqual(len(plugins), 1)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()

"""SkillForge Healthcheck Utility

Provides functions to check the health of plugin endpoints
and report their status. Used by CI pipelines and the audit command.
"""

import json
import urllib.request
import urllib.error
import time


def check_health(url, timeout=5):
    """Check the health of a plugin endpoint.

    Args:
        url: Full URL to the healthcheck endpoint.
        timeout: Request timeout in seconds.

    Returns:
        dict: {
            'url': str,
            'healthy': bool,
            'status_code': int or None,
            'response_time_ms': float,
            'error': str or None
        }
    """
    start = time.monotonic()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = (time.monotonic() - start) * 1000
            return {
                "url": url,
                "healthy": 200 <= resp.status < 300,
                "status_code": resp.status,
                "response_time_ms": round(elapsed, 2),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        elapsed = (time.monotonic() - start) * 1000
        return {
            "url": url,
            "healthy": False,
            "status_code": e.code,
            "response_time_ms": round(elapsed, 2),
            "error": str(e),
        }
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return {
            "url": url,
            "healthy": False,
            "status_code": None,
            "response_time_ms": round(elapsed, 2),
            "error": str(e),
        }


def check_all_plugins(registry_path, base_url="http://localhost:8080"):
    """Check health of all plugins in the registry.

    Args:
        registry_path: Path to registry.json.
        base_url: Base URL for healthcheck endpoints.

    Returns:
        list[dict]: List of healthcheck results.
    """
    with open(registry_path, "r") as f:
        data = json.load(f)

    plugins = data if isinstance(data, list) else data.get("plugins", [])
    results = []

    for plugin in plugins:
        if plugin.get("status") == "retired":
            continue
        name = plugin.get("name", "unknown")
        hc_path = plugin.get("healthcheck_url", "/health")
        url = f"{base_url}{hc_path}"

        result = check_health(url)
        result["plugin"] = name
        results.append(result)

    return results


def format_health_report(results):
    """Format healthcheck results as a human-readable report.

    Args:
        results: List of healthcheck result dicts.

    Returns:
        str: Formatted report string.
    """
    lines = ["SkillForge Plugin Health Report", "=" * 40]
    healthy_count = sum(1 for r in results if r["healthy"])

    for result in results:
        status = "OK" if result["healthy"] else "FAIL"
        icon = "+" if result["healthy"] else "X"
        line = f"  [{icon}] {result.get('plugin', 'unknown')}: {status}"
        if result["response_time_ms"]:
            line += f" ({result['response_time_ms']}ms)"
        if result["error"]:
            line += f" - {result['error']}"
        lines.append(line)

    lines.append("")
    lines.append(f"Summary: {healthy_count}/{len(results)} healthy")
    return "\n".join(lines)

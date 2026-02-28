# AegisFlow Security Policy

## Purpose

This policy defines security requirements and controls for all artifacts
managed under the AegisFlow governance framework.

## Permission Model

### Plugin Permissions
Plugins must explicitly declare all required permissions:

| Permission | Description | Risk Level |
|-----------|------------|-----------|
| `external_api` | Access to external APIs | Medium |
| `database` | Database read/write access | High |
| `filesystem` | Local filesystem access | Medium |
| `network` | Network socket access | Medium |
| `secrets` | Access to secrets/credentials | High |
| `compute` | Heavy compute resource usage | Low |

### Permission Review
- Plugins requesting `secrets` or `database` permissions require additional review
- Permission changes require version bump and re-approval
- Unused permissions should be removed during review

## Secret Handling

### Prohibited
- Hardcoded credentials in any source file
- API keys in configuration files
- Private keys in the repository
- Passwords in test fixtures

### Required
- Use environment variables for secrets
- Use secret management services (e.g., GitHub Secrets)
- Rotate credentials on a regular schedule
- Audit secret access logs

### CI Enforcement
The `security_scan.yml` workflow checks for:
- Hardcoded passwords and API keys
- Private key material
- Common secret patterns
- Overly permissive file permissions

## Vulnerability Response

### Severity Levels

| Severity | Response Time | Action Required |
|---------|--------------|----------------|
| Critical | 4 hours | Immediate patch, consider retirement |
| High | 24 hours | Patch within sprint |
| Medium | 1 week | Schedule for next release |
| Low | 30 days | Address during regular maintenance |

### Response Process
1. **Identify:** Vulnerability discovered via audit, scan, or report
2. **Assess:** Determine severity and affected artifacts
3. **Contain:** Disable affected artifacts if Critical/High
4. **Fix:** Develop and test patch
5. **Deploy:** Release patched version with version bump
6. **Review:** Post-incident review and policy update

## SLO Security

- Plugin SLOs must include error rate monitoring
- Abnormal error rate spikes may indicate security incidents
- Alert thresholds are defined in telemetry configurations
- SLO violations trigger automatic notification to owners

## Compliance

- All artifacts must pass security scan before promotion to Active
- Security reviews are part of the standard review cadence
- Audit trail maintained for all lifecycle transitions

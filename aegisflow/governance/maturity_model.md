# AegisFlow Maturity Model

## Purpose

This document defines the maturity levels for AegisFlow governance adoption.
Organizations can use this model to assess their current governance posture
and identify areas for improvement.

## Maturity Levels

### Level 0: No Governance
- No structured skill or plugin management
- No schema validation
- No lifecycle controls
- Ad-hoc artifact management

### Level 1: Basic Structure
**Criteria:**
- Skills registry (`skills.md`) exists with structured metadata
- Skill schema (`skill_schema.yaml`) is defined
- Plugin registry (`registry.json`) exists
- Plugin schema (`plugin_schema.json`) is defined

**Assessment:**
```bash
aegis score
```

### Level 2: Validation Enabled
**Criteria (all of Level 1 plus):**
- Skill validator is implemented and functional
- Plugin validator is implemented and functional
- Validation scripts are available
- All current artifacts pass validation

**Key Indicators:**
- `validate_skills.py` runs without errors
- `validate_plugins.py` runs without errors
- All metadata fields are populated and valid

### Level 3: CI Enforcement
**Criteria (all of Level 2 plus):**
- CI workflow for skill validation is configured
- CI workflow for plugin validation is configured
- Security scan CI is configured
- Validation runs automatically on push/PR

**Key Indicators:**
- `.github/workflows/aegisflow.yml` exists and runs
- PRs are blocked on validation failure
- Version increment enforcement is active

### Level 4: Observability
**Criteria (all of Level 3 plus):**
- Telemetry configurations exist for plugins
- Healthcheck utility is available
- SLO monitoring is enabled for all active plugins
- Alert thresholds are defined

**Key Indicators:**
- Telemetry YAML configs in `plugins/telemetry/`
- All active plugins have SLO definitions
- Healthcheck runner can verify plugin status

### Level 5: Full Governance
**Criteria (all of Level 4 plus):**
- Lifecycle policy is documented and enforced
- Deprecation policy is documented with automated retirement
- Security policy is documented and enforced
- Orphan detection is operational
- Version enforcement is automated
- Maturity model is documented (this document)
- Complete audit trail

**Key Indicators:**
- `aegis audit` returns zero issues
- All governance documents exist
- Automated retirement workflows are enabled
- Regular review cadence is maintained

## Assessment

Run the maturity assessment:

```bash
aegis score
```

Example output:
```
AegisFlow Maturity: Level 3
Score: 78.5% (22/28 checks passed)
==================================================

Level 1: Basic Structure
------------------------------
  [+] Skills registry exists
  [+] Skill schema exists
  [+] Plugin registry exists
  [+] Plugin schema exists

Level 2: Validation
------------------------------
  [+] Skill validator exists
  [+] Plugin validator exists
  [+] Validation scripts exist
  [+] Skills validation passes
  [+] Plugin validation passes

Level 3: CI Enforcement
------------------------------
  [+] CI enforcement enabled
  [+] Skill validation CI exists
  [+] Plugin validation CI exists
  [+] Security scan CI exists

Level 4: Observability
------------------------------
  [+] Telemetry active
  [+] Healthcheck utility exists
  [+] SLO monitoring enabled

Level 5: Full Governance
------------------------------
  [+] Lifecycle policy exists
  [+] Deprecation policy exists
  [+] Security policy exists
  [+] Maturity model documented
  [+] Orphan detection available
  [+] Version enforcement available
  [X] Automated retirement enabled
```

## Improvement Roadmap

To progress from one level to the next:

| From | To | Key Actions |
|------|-----|------------|
| 0 | 1 | Run `aegis init`, define schemas, create registries |
| 1 | 2 | Implement validators, run `aegis validate` |
| 2 | 3 | Set up CI workflows, enable PR blocking |
| 3 | 4 | Add telemetry configs, define SLOs, set up healthchecks |
| 4 | 5 | Document all policies, enable automated retirement |

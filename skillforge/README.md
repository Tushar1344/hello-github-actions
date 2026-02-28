# SkillForge

**Unified Lifecycle Governance System for Skills and Plug-Ins**

SkillForge is a production-grade lifecycle governance framework that manages:
- **`skills.md`** as a structured, versioned capability registry
- **Plug-ins** as secure, observable, versioned runtime artifacts

## Features

- Structured metadata validation with YAML/JSON schemas
- Semantic versioning enforcement
- CI/CD policy enforcement via GitHub Actions
- Automated lifecycle transitions (Draft → Active → Deprecated → Retired)
- Observability and SLO tracking
- Governance and risk controls
- Deprecation and retirement workflows
- Maturity scoring (Level 0-5)
- CLI tool with 12 operational commands

## Quick Start

### Prerequisites

- Python 3.8+
- PyYAML (`pip install pyyaml`)

### Setup

```bash
# Set up a convenient alias
alias forge='python skillforge/scripts/forge_cli.py'

# Or initialize in a new repository
forge init
```

### Validate Everything

```bash
forge validate
```

### Add a Skill

```bash
forge add-skill "Data Processing" --owner platform-team --risk Medium
```

### List Skills and Plugins

```bash
forge list skills
forge list plugins
```

### Run Governance Audit

```bash
forge audit
```

### Check Maturity Score

```bash
forge score
```

## CLI Reference

| Command | Description | Example |
|---------|------------|---------|
| `init` | Initialize SkillForge in repo | `forge init` |
| `add-skill` | Create new skill entry | `forge add-skill "Name" --owner team --risk Medium` |
| `validate` | Run all validations | `forge validate` |
| `promote` | Move Draft → Active | `forge promote skill "Name"` |
| `deprecate` | Mark as Deprecated | `forge deprecate plugin name --replacement new_name` |
| `retire` | Retire artifact | `forge retire skill "Name"` |
| `review` | Update review date | `forge review skill "Name"` |
| `bump` | Increment version | `forge bump skill "Name" --type minor` |
| `list` | List artifacts | `forge list skills` |
| `score` | Show maturity score | `forge score` |
| `audit` | Run governance audit | `forge audit` |
| `telemetry` | Show runtime metrics | `forge telemetry plugin_name` |

## Repository Structure

```
skillforge/
├── skills/                    # Skill governance
│   ├── skills.md              # Skill registry
│   ├── skill_schema.yaml      # Schema definition
│   ├── validators/            # Validation logic
│   └── tests/                 # Skill validator tests
├── plugins/                   # Plugin governance
│   ├── registry.json          # Plugin registry
│   ├── plugin_schema.json     # Schema definition
│   ├── validators/            # Validation logic
│   ├── telemetry/             # Telemetry configs
│   └── healthchecks/          # Health check utilities
├── ci/                        # CI workflow templates
│   ├── validate_skills.yml
│   ├── validate_plugins.yml
│   └── security_scan.yml
├── governance/                # Policy documents
│   ├── lifecycle_policy.md
│   ├── deprecation_policy.md
│   ├── security_policy.md
│   └── maturity_model.md
├── scripts/                   # CLI and utilities
│   ├── forge_cli.py           # Main CLI entry point
│   ├── validate_skills.py
│   ├── validate_plugins.py
│   ├── enforce_versioning.py
│   ├── detect_orphans.py
│   └── maturity_score.py
└── tests/                     # Integration tests
```

## Skill Metadata Format

Each skill in `skills.md` must include:

```markdown
## Skill: Data Processing
- Owner: platform-team
- Version: 1.2.0
- Status: Active
- Dependencies: pandas>=2.0
- Last Reviewed: 2026-02-01
- Test Coverage: 93%
- Risk Level: Medium
- Deprecation Date: N/A
```

### Lifecycle States

| State | Meaning |
|-------|---------|
| Draft | In development |
| Active | Production ready |
| Deprecated | Replacement available |
| Retired | Disabled and archived |

## Plugin Registry Format

Each plugin in `registry.json`:

```json
{
  "name": "weather_plugin",
  "version": "2.1.0",
  "status": "active",
  "api_version": "v1",
  "owner": "platform-team",
  "permissions": ["external_api"],
  "healthcheck_url": "/health",
  "slo": {
    "latency_p95_ms": 800,
    "error_rate_percent": 1
  }
}
```

## Maturity Model

SkillForge tracks governance maturity across 5 levels:

| Level | Name | Key Requirements |
|-------|------|-----------------|
| 1 | Basic Structure | Registries and schemas exist |
| 2 | Validation | Validators implemented and passing |
| 3 | CI Enforcement | CI workflows configured |
| 4 | Observability | Telemetry, SLOs, healthchecks |
| 5 | Full Governance | All policies, automated retirement |

## Running Tests

```bash
# All tests
cd skillforge
python -m unittest discover -s skills/tests -v
python -m unittest discover -s tests -v

# Individual test files
python -m unittest skills.tests.test_skill_validator -v
python -m unittest tests.test_plugin_validator -v
python -m unittest tests.test_cli -v
python -m unittest tests.test_maturity -v
```

## CI/CD Integration

SkillForge includes GitHub Actions workflows that automatically:

1. Validate skills and plugins on push/PR
2. Enforce version increments
3. Detect orphaned artifacts
4. Run security scans
5. Execute test suites

The main workflow is at `.github/workflows/skillforge.yml`.

## Governance Policies

See the `governance/` directory for:

- **Lifecycle Policy** - State transitions, approvals, review cadence
- **Deprecation Policy** - Deprecation timeline, migration requirements
- **Security Policy** - Permission model, secret handling, vulnerability response
- **Maturity Model** - Level definitions and improvement roadmap

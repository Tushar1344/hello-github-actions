# AegisFlow Lifecycle Policy

## Purpose

This policy defines the lifecycle states, transitions, and governance controls
for all artifacts managed under AegisFlow (skills and plugins).

## Lifecycle States

| State | Description | Allowed Actions |
|-------|------------|----------------|
| **Draft** | In development, not production-ready | Edit, Test, Promote, Retire |
| **Active** | Production-ready, fully supported | Edit, Deprecate, Retire, Bump |
| **Deprecated** | Replacement available, migration underway | Retire only |
| **Retired** | Disabled and archived, no longer functional | None (read-only) |

## State Transitions

```
Draft ──────► Active ──────► Deprecated ──────► Retired
  │                              │
  └──────────────────────────────┴──────────► Retired
```

### Draft to Active
- **Requirements:**
  - All required metadata fields populated
  - Schema validation passes
  - Test coverage meets minimum threshold (80%)
  - Owner assigned and confirmed
  - Risk level assessed
  - Review completed within 90 days
- **Approval:** Owner + one reviewer
- **Action:** `aegis promote skill "Name"` or `aegis promote plugin name`

### Active to Deprecated
- **Requirements:**
  - Replacement artifact identified (recommended)
  - Deprecation date set
  - Migration plan documented
  - Stakeholders notified
- **Approval:** Owner + governance team
- **Action:** `aegis deprecate skill "Name" --replacement "New Name"`

### Any to Retired
- **Requirements:**
  - No active consumers (for plugins)
  - Deprecation period completed (if previously deprecated)
  - Data migration complete
- **Approval:** Governance team
- **Action:** `aegis retire skill "Name"` or `aegis retire plugin name`

## Review Cadence

- All Active artifacts must be reviewed at least every **90 days**
- Reviews must update the `Last Reviewed` date
- Stale reviews are flagged during audit and CI

## Version Management

- All artifacts use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- **MAJOR:** Breaking changes or incompatible API modifications
- **MINOR:** New features, backward-compatible
- **PATCH:** Bug fixes, backward-compatible
- Version must be incremented on every change (enforced by CI)

## Ownership

- Every artifact must have an assigned owner
- Orphaned artifacts (no owner) are flagged during audit
- Ownership transfers require explicit reassignment

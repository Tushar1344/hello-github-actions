# SkillForge Deprecation Policy

## Purpose

This policy defines the process for deprecating and retiring artifacts
(skills and plugins) within the SkillForge governance framework.

## Deprecation Process

### Step 1: Initiation
- Owner identifies the artifact for deprecation
- Replacement artifact is identified (if applicable)
- Deprecation request is submitted via:
  ```bash
  forge deprecate skill "Old Artifact" --replacement "New Artifact"
  ```

### Step 2: Notification
- All consumers/stakeholders are notified
- Deprecation date is recorded in the artifact metadata
- Migration documentation is created or updated

### Step 3: Migration Period
- Minimum deprecation period: **30 days** for Low risk artifacts
- Minimum deprecation period: **60 days** for Medium risk artifacts
- Minimum deprecation period: **90 days** for High risk artifacts
- During this period:
  - The deprecated artifact remains functional
  - New usage is blocked/discouraged
  - Migration support is provided

### Step 4: Automated Retirement
- After the deprecation period expires, the artifact is eligible for retirement
- Retirement is triggered via:
  ```bash
  forge retire skill "Old Artifact"
  ```
- Automated retirement checks verify:
  - Deprecation period has elapsed
  - No active consumers remain (for plugins)
  - Replacement is available and Active

## Deprecation Timeline

| Risk Level | Min Deprecation Period | Review Frequency |
|-----------|----------------------|-----------------|
| Low | 30 days | Monthly |
| Medium | 60 days | Bi-weekly |
| High | 90 days | Weekly |

## Responsibilities

### Artifact Owner
- Initiate deprecation request
- Create migration documentation
- Support consumers during migration
- Monitor migration progress

### Governance Team
- Approve deprecation requests
- Enforce deprecation timelines
- Trigger automated retirement when eligible
- Track deprecation metrics

### Consumers
- Acknowledge deprecation notices
- Plan and execute migration
- Report migration blockers
- Confirm migration completion

## Audit Integration

The deprecation status is checked during governance audits:
- `forge audit` flags deprecated artifacts approaching retirement
- CI pipelines warn on usage of deprecated artifacts
- Stale deprecations (past deadline) are escalated

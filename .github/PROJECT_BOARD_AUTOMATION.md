# Project Board Automation System

## Overview

This document describes the comprehensive automation system for managing GitHub project boards, issues, pull requests, and workflows. The system provides intelligent triage, autonomous fixes, and automated item movement through project board columns.

## ⚠️ Important: Organization Project Access

**For organization-level project boards (GitHub Projects v2):**

The standard `GITHUB_TOKEN` provided to workflows only has repository-level permissions and **cannot access organization projects**. To enable organization project board automation:

1. **Create a Personal Access Token (PAT)** or **GitHub App token** with:
   - `project` scope (read/write project boards)
   - `read:org` scope (read organization data)

2. **Store the token as a repository secret:**
   ```bash
   # Go to repository Settings > Secrets and variables > Actions
   # Create new secret: ORG_PROJECT_TOKEN
   ```

3. **Update the workflow to use the secret:**
   ```yaml
   # In .github/workflows/project-board-sync.yml, line 53
   github-token: ${{ secrets.ORG_PROJECT_TOKEN }}
   ```

**Alternative: Use repository-level projects** if organization access is not available. Change the GraphQL queries to use `repository` instead of `organization`.

## Architecture

### Core Components

1. **Project Board Sync** (`project-board-sync.yml`)
   - Automatically adds new issues/PRs to project board
   - Moves items through board columns based on status
   - Integrates with GitHub Projects v2 API

2. **Project Board Automation** (`project-board-automation.yml`)
   - Advanced auto-labeling with AI-like pattern matching
   - Smart auto-assignment based on expertise areas
   - Stale issue management
   - Metrics and reporting

3. **Autonomous Board** (`autonomous-board.yml`)
   - Auto-fix capabilities for common issues
   - Auto-merge for approved PRs
   - Documentation generation
   - Full automation orchestration

4. **Issue Management** (`issue-management.yml`)
   - Issue triage and classification
   - PR-issue integration
   - Automated responses and notifications

## Features

### 1. Automatic Board Item Addition

**Trigger:** New issue or PR created

**Actions:**
- Item is automatically added to the organization project board
- Initial triage comment is posted
- Appropriate labels are applied
- Item is placed in "Triage" column

**Configuration:**
```yaml
env:
  ORG_NAME: 'Universal-Standard'
  PROJECT_NUMBER: 3
```

### 2. AI-Powered Triage

**Trigger:** New issue opened

**Analysis:**
- **Priority Detection**: Critical, High, Medium, Low
  - Critical: security breach, data loss, production down
  - High: blocking issues, regressions, major bugs
  - Medium: standard bugs and enhancements
  - Low: cosmetic issues, documentation

- **Type Classification**: Bug, Enhancement, Documentation, Question
- **Component Detection**: API, Database, Frontend, Backend, Security, CI/CD, etc.
- **Auto-Fix Detection**: Typos, formatting, imports, syntax errors

**Labels Applied:**
- Priority: `critical`, `high-priority`, `medium-priority`, `low-priority`
- Type: `bug`, `enhancement`, `documentation`, `question`
- Component: `api`, `database`, `frontend`, `backend`, `security`, `ci-cd`, etc.
- Status: `needs-triage`, `auto-fixable`, `quick-fix`
- Special: `automated` (for bot-created issues)

### 3. Autonomous Issue Fixing

**Trigger:** Issue labeled with `auto-fixable` or `quick-fix`

**Capabilities:**
- **Spelling/Typos**: Automatic correction using spell checkers
- **Code Formatting**: Apply Black, isort, autopep8
- **Import Optimization**: Remove unused imports, organize imports
- **Whitespace**: Remove trailing whitespace, fix line endings
- **Syntax Errors**: Basic syntax error corrections

**Workflow:**
1. Analyze issue content to determine fix type
2. Checkout repository
3. Apply appropriate fixes
4. Run validation tests
5. Create pull request with fixes
6. Link PR to original issue

### 4. Smart Board Movement

**Column Flow:**
```
Triage → Analysis → Ready for Work → In Progress → Review → Testing → Ready to Merge → Merged/Closed
```

**Movement Rules:**

| Event | Source Column | Target Column | Trigger |
|-------|--------------|---------------|---------|
| Issue opened | - | Triage | `action: opened` |
| PR opened | - | Review | `action: opened` |
| Analysis needed | Triage | Analysis | `label: needs-analysis` |
| Ready to start | Analysis | Ready for Work | `label: ready-for-dev` |
| Work begins | Ready for Work | In Progress | `label: in-progress` or branch created |
| PR created | In Progress | Review | `label: needs-review` |
| Review approved | Review | Testing | All reviews approved |
| Tests pass | Testing | Ready to Merge | `label: approved-for-merge` |
| PR merged | Ready to Merge | Merged | `action: closed` + merged |
| Issue closed | Any | Closed | `action: closed` |

### 5. Workflow Failure Tracking

**Trigger:** Any workflow fails

**Actions:**
1. Create issue with workflow details
2. Label as `automated`, `ci-cd`, `workflow-failure`, `high-priority`
3. Add to project board
4. Assign to DevOps team
5. Auto-close when workflow succeeds

**Issue Content:**
- Workflow name and branch
- Run ID and attempt number
- Link to failed run
- Triggered by information
- Error logs and context

### 6. Auto-Assignment

**Assignment Rules:**

| Condition | Assignee |
|-----------|----------|
| Priority: Critical | Immediate assignment to maintainer |
| Priority: High + Security | Security team |
| Labels: backend, api, database | Backend team |
| Labels: frontend, ui | Frontend team |
| Labels: ci-cd, infrastructure | DevOps team |
| Labels: payment-integration | Integration specialists |

### 7. Stale Issue Management

**Daily Maintenance:**
- Issues with no activity for 30 days → Add `stale` label + comment
- Stale issues with no response for 7 days → Close as `not_planned`
- Automated report issues older than 7 days → Auto-close

### 8. Metrics and Reporting

**Daily Reports:**
- Total open issues
- Issues by priority (Critical, High, Medium, Low)
- Issues by type (Bug, Enhancement, Documentation, Question)
- Issues by status (Triage, In Progress, Review, Testing)
- Issues by component
- Assignment statistics
- Automated issue count

**Report Location:** 
- Created as GitHub issue: "📊 Repository Issue Statistics"
- Updated daily at 3 AM UTC

## Usage

### Manual Triggers

All automation workflows support manual triggering:

#### Project Board Sync
```yaml
workflow_dispatch:
  inputs:
    action:
      - sync-all-items         # Add all items to board
      - auto-triage-new        # Triage new issues
      - auto-fix-issues        # Analyze issues for fixes
      - move-items-by-status   # Update board positions
      - full-automation        # Run all automation
```

#### Project Board Automation
```yaml
workflow_dispatch:
  inputs:
    action:
      - sync-all           # Sync all items
      - cleanup-stale      # Clean up stale issues
      - generate-report    # Generate metrics
      - bulk-triage        # Triage multiple issues
```

#### Autonomous Board
```yaml
workflow_dispatch:
  inputs:
    action:
      - sync-all-issues    # Sync GitHub issues
      - auto-fix-issues    # Apply auto-fixes
      - auto-merge-prs     # Merge approved PRs
      - generate-docs      # Generate documentation
      - full-automation    # Full autonomous workflow
```

### Label-Based Triggers

Add these labels to issues for specific actions:

| Label | Action |
|-------|--------|
| `auto-fixable` | Triggers autonomous fix workflow |
| `quick-fix` | Triggers autonomous fix workflow |
| `auto-merge` | Enables auto-merge for PRs (when checks pass) |
| `auto-document` | Triggers documentation generation |
| `needs-analysis` | Moves to Analysis column |
| `ready-for-dev` | Moves to Ready for Work column |
| `in-progress` | Moves to In Progress column |
| `needs-review` | Moves to Review column |
| `needs-testing` | Moves to Testing column |
| `approved-for-merge` | Moves to Ready to Merge column |

### Comment Triggers

Post comments with these keywords to trigger actions:

| Comment | Action |
|---------|--------|
| "Analysis complete" | Move from Analysis to Ready for Work |
| "/auto-fix" | Trigger autonomous fix |
| "/auto-merge" | Enable auto-merge (if authorized) |
| "/triage" | Re-run triage analysis |

## Configuration

### Environment Variables

Set these in workflow files or repository settings:

```yaml
env:
  ORG_NAME: 'Universal-Standard'      # Organization name
  PROJECT_NUMBER: 3                    # Project board number
```

### Permissions Required

```yaml
permissions:
  contents: write         # For creating branches/commits
  issues: write          # For managing issues
  pull-requests: write   # For managing PRs
  checks: read          # For checking CI status
```

### Project Board Setup

1. **Create Project Board**
   - Go to https://github.com/orgs/Universal-Standard/projects
   - Create new project (Projects v2)
   - Number it (e.g., Project #3)

2. **Add Columns**
   - Triage
   - Analysis
   - Ready for Work
   - In Progress
   - Review
   - Testing
   - Ready to Merge
   - Merged
   - Closed

3. **Configure Status Field**
   - Add "Status" field to project
   - Use single-select with above column names

## Advanced Features

### 1. Auto-Fix Capabilities

The system can automatically fix:

**Code Quality:**
- Apply Black formatter
- Sort imports with isort
- Fix PEP8 violations with autopep8
- Remove unused imports
- Fix trailing whitespace

**Documentation:**
- Fix spelling errors
- Update outdated links
- Generate API documentation

**Configuration:**
- Update dependency versions
- Fix YAML/JSON syntax
- Normalize file formats

### 2. Auto-Merge Conditions

PRs are auto-merged when ALL conditions are met:
- Labeled with `auto-merge` or `safe-to-merge`
- All CI checks pass
- All required reviews approved
- No merge conflicts
- From trusted source (maintainers, dependabot)

### 3. Security Integration

**Automatic Security Response:**
- Security issues get `critical` priority
- Immediate assignment to security team
- Added to top of project board
- Notifications sent to maintainers

**Workflow Failures:**
- Security scan failures create high-priority issues
- CodeQL alerts automatically tracked
- Dependency vulnerabilities flagged

### 4. Integration with External Tools

**Supports:**
- Dependabot PRs (auto-labeled and triaged)
- CodeQL alerts (converted to issues)
- Security advisories (auto-prioritized)
- CI/CD notifications (tracked and closed automatically)

## Monitoring and Maintenance

### Health Checks

**Daily (3 AM UTC):**
- Sync all items to project board
- Update stale issues
- Generate metrics report
- Clean up old automated issues

**Every 6 Hours:**
- Sync new items
- Update item positions
- Check for stuck items

### Metrics Tracked

1. **Time to Triage** - Creation to first label
2. **Time to First Response** - Creation to first comment
3. **Time to Assignment** - Creation to first assignee
4. **Time to Resolution** - Creation to closure
5. **Auto-Fix Success Rate** - % of successful automated fixes
6. **Board Flow Efficiency** - Time in each column

### Troubleshooting

**Issue not added to board:**
- Check ORG_NAME and PROJECT_NUMBER in workflow
- Verify GITHUB_TOKEN has project access
- Check workflow run logs for GraphQL errors

**Auto-fix not working:**
- Verify issue has `auto-fixable` or `quick-fix` label
- Check workflow permissions (needs write access)
- Review workflow run logs

**Board movements not happening:**
- Ensure labels match movement rules exactly
- Check if item is already in target column
- Verify status field exists in project

## Best Practices

1. **Label Hygiene**
   - Use consistent label names
   - Apply priority labels to all issues
   - Remove outdated labels promptly

2. **Issue Quality**
   - Write clear, descriptive titles
   - Include reproduction steps for bugs
   - Tag relevant components

3. **PR Management**
   - Link PRs to issues with "Fixes #123"
   - Keep PRs small and focused
   - Ensure all checks pass before requesting merge

4. **Board Maintenance**
   - Review items in each column weekly
   - Move stuck items manually if automation misses them
   - Archive completed items monthly

## Security Considerations

1. **Secrets Management**
   - Never commit tokens or secrets
   - Use GitHub Secrets for sensitive data
   - Rotate tokens regularly

2. **Auto-Merge Safety**
   - Only enable for trusted sources
   - Require reviews for sensitive changes
   - Monitor auto-merged PRs

3. **Autonomous Fixes**
   - Always review auto-fix PRs before merge
   - Test fixes in CI/CD pipeline
   - Limit auto-fix scope to safe operations

## Support

**For issues with automation:**
1. Check workflow run logs
2. Review this documentation
3. Open issue with `ci-cd` and `automation` labels
4. Tag @maintainers for urgent issues

**Resources:**
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [GitHub Projects v2 API](https://docs.github.com/graphql/reference/objects#projectv2)
- [GitHub Script Action](https://github.com/actions/github-script)

---

**Document Version:** 2.0  
**Last Updated:** 2026-01-05  
**Maintained By:** DevOps & Automation Team  
**Next Review:** 2026-02-05

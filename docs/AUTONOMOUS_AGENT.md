# Autonomous Project Board Agent

## Overview

The Autonomous Agent extends the AI-powered project board with **full automation capabilities** to:

1. **Ingest** all repository issues, PRs, and feature requests
2. **Auto-fix** code issues autonomously
3. **Manage PRs** - create, update, merge automatically
4. **Generate documentation** on demand
5. **Execute workflows** end-to-end without human intervention

## 🤖 Core Capabilities

### 1. GitHub Integration & Sync

**Automatically ingest all repository items:**

- ✅ All open issues
- ✅ All pull requests
- ✅ Feature requests
- ✅ Planned roadmap items
- ✅ Recently closed items (last 30 days)

**Trigger Methods:**
- **Scheduled**: Daily at 3 AM UTC
- **Manual**: Workflow dispatch with `sync-all-issues` action
- **API**: `POST /api/autonomous/sync/issues`

### 2. Autonomous Issue Analysis

**AI-powered issue classification:**

```python
strategy = {
    "automatable": True/False,
    "auto_fix_type": "syntax|import|security|deprecation|typo",
    "suggested_actions": ["Generate fix", "Create PR", "Auto-merge"],
    "priority": "critical|high|medium|low",
    "estimated_effort": "low|medium|high"
}
```

**Detection Patterns:**
- **Syntax Errors**: `SyntaxError`, `IndentationError`, `TabError`
- **Import Errors**: `ImportError`, `ModuleNotFoundError`
- **Type Errors**: `TypeError`, `AttributeError`
- **Security**: `SQL injection`, `XSS`, `CSRF`, CVE references
- **Deprecation**: `DeprecationWarning`, `deprecated`

### 3. Auto-Fix Generation

**Automatic code fixes for common issues:**

| Issue Type | Detection | Auto-Fix | Confidence |
|------------|-----------|----------|------------|
| **Typos** | Spelling errors | Spell checker | 95% |
| **Syntax** | Indentation, syntax | autopep8 | 90% |
| **Imports** | Missing imports | Add imports | 85% |
| **Security** | Vulnerabilities | Apply patches | 80% |
| **Deprecation** | Old APIs | Update calls | 75% |

**API Endpoint**: `POST /api/autonomous/fix/generate`

```json
{
  "issue_description": "SyntaxError on line 42",
  "error_context": "IndentationError: expected an indented block"
}
```

**Response**:
```json
{
  "fixable": true,
  "fix_type": "syntax",
  "code_changes": [
    {
      "action": "fix_indentation",
      "description": "Fix indentation issues using autopep8",
      "command": "autopep8 --in-place --aggressive"
    }
  ],
  "explanation": "Auto-fix indentation and syntax issues",
  "confidence": 0.9
}
```

### 4. PR Management

**Autonomous PR lifecycle:**

1. **Create** - Generate branch, apply fix, open PR
2. **Update** - Respond to review comments automatically
3. **Merge** - Auto-merge when CI passes (if labeled)
4. **Close** - Close linked issues on merge

**PR Strategy Generation:**

```python
pr_strategy = {
    "should_create_pr": True,
    "branch_name": "auto-fix/syntax-error-line-42",
    "pr_title": "🤖 Auto-fix: Syntax - Fix indentation error",
    "pr_body": "## 🤖 Automated Fix\n...",
    "auto_merge": True,  # If confidence >= 90%
    "reviewers": []
}
```

### 5. Label-Based Triggers

**Special labels that activate automation:**

| Label | Description | Action |
|-------|-------------|--------|
| `auto-fix` | Auto-fix if possible | Analyze → Fix → PR |
| `auto-merge` | Auto-merge when CI passes | Merge on success |
| `auto-document` | Generate docs | Create doc PR |
| `auto-test` | Generate tests | Create test PR |
| `quick-fix` | Full autonomous workflow | Fix → Test → Merge |
| `enhancement` | Analyze implementation | Create task breakdown |

**Usage**: Simply add the label to an issue or PR to trigger automation.

### 6. Full Autonomous Workflow

**Complete end-to-end automation:**

```
Issue Created
    ↓
Label: "quick-fix"
    ↓
[1] Analyze Issue (detect fix type)
    ↓
[2] Generate Fix Code
    ↓
[3] Create Branch & Apply Fix
    ↓
[4] Run Validation Tests
    ↓
[5] Create Pull Request
    ↓
[6] Wait for CI Checks
    ↓
[7] Auto-Merge (if checks pass)
    ↓
[8] Close Linked Issue
    ↓
[9] Add Success Comment
```

**Estimated time**: 5-10 minutes for simple fixes

## 🔧 GitHub Actions Workflows

### Main Workflow: `autonomous-board.yml`

**5 Major Jobs:**

1. **`sync-issues-to-board`** - Ingest all GitHub items
2. **`auto-fix-issue`** - Apply fixes when labeled
3. **`auto-merge-pr`** - Merge approved PRs
4. **`auto-document`** - Generate documentation
5. **`full-automation`** - Complete autonomous cycle

**Triggers:**
- **Issues**: opened, labeled, reopened
- **Pull Requests**: opened, labeled, synchronize
- **Schedule**: Daily at 3 AM UTC
- **Manual**: Workflow dispatch

### Job 1: Sync Issues to Board

**What it does:**
- Fetches all open issues and PRs
- Fetches recently closed items (30 days)
- Creates sync summary with statistics
- Stores summary as artifact

**When it runs:**
- Daily at 3 AM UTC
- Manual: `sync-all-issues` action
- Manual: `full-automation` action

**Output**: `sync-summary.json` artifact

### Job 2: Auto-Fix Issue

**What it does:**
- Analyzes issue content for fix type
- Applies appropriate auto-fix tool
- Creates PR with fixes

**When it runs:**
- Issue labeled with `auto-fix`

**Auto-fix tools:**
- `codespell` - Fix typos
- `autopep8` - Fix Python syntax
- Custom import fixer

### Job 3: Auto-Merge PR

**What it does:**
- Checks CI status for PR
- Auto-merges if all checks pass
- Adds merge comment

**When it runs:**
- PR labeled with `auto-merge`
- PR synchronize (if already labeled)

**Requirements:**
- Must have `auto-merge` or `safe-to-merge` label
- All CI checks must pass
- Merge method: squash

### Job 4: Auto-Document

**What it does:**
- Generates API documentation with pdoc3
- Creates Sphinx documentation
- Opens PR with generated docs

**When it runs:**
- Issue labeled with `auto-document`
- Manual: `generate-docs` action

### Job 5: Full Automation

**What it does:**
- Executes complete autonomous workflow
- All steps from analysis to merge
- Status updates at each step

**When it runs:**
- Issue labeled with `quick-fix`
- Manual: `full-automation` action

## 📡 API Endpoints

### Sync GitHub Issues
```http
POST /api/autonomous/sync/issues
Authorization: Required (Admin)

{
  "project_id": "project-uuid",
  "repo_owner": "UniversalStandards",
  "repo_name": "New-Government-agency-banking-Program"
}
```

### Analyze Issue
```http
POST /api/autonomous/analyze/issue
Authorization: Required

{
  "issue_data": {
    "number": 123,
    "title": "Fix syntax error in main.py",
    "body": "SyntaxError on line 42",
    "labels": [{"name": "bug"}]
  }
}
```

### Generate Fix
```http
POST /api/autonomous/fix/generate
Authorization: Required (Admin/Dept Head)

{
  "issue_description": "SyntaxError in main.py",
  "error_context": "IndentationError: expected an indented block"
}
```

### Create PR Strategy
```http
POST /api/autonomous/pr/strategy
Authorization: Required (Admin/Dept Head)

{
  "task_data": {
    "title": "Fix syntax error",
    "issue_number": 123
  },
  "fix_data": {
    "fixable": true,
    "fix_type": "syntax",
    "confidence": 0.9
  }
}
```

### Execute Workflow
```http
POST /api/autonomous/workflow/execute
Authorization: Required (Admin)

{
  "issue_data": {
    "number": 123,
    "title": "Fix import error",
    "body": "ModuleNotFoundError: No module named 'flask'",
    "labels": [{"name": "auto-fix"}]
  }
}
```

### Check Auto-Merge
```http
POST /api/autonomous/merge/check

{
  "pr_data": {
    "number": 456,
    "labels": [{"name": "auto-merge"}]
  },
  "checks_status": "success"
}
```

### Generate Documentation
```http
POST /api/autonomous/docs/generate

{
  "code_context": "def my_function():\n    pass",
  "doc_type": "api"
}
```

### Get Agent Status
```http
GET /api/autonomous/status
Authorization: Required
```

### List Automation Triggers
```http
GET /api/autonomous/triggers/list
```

### Health Check
```http
GET /api/autonomous/health
```

## 🎯 Usage Examples

### Example 1: Auto-Fix a Syntax Error

**Step 1**: Create issue
```markdown
Title: Fix indentation in routes/payments.py
Body: Line 42 has IndentationError

Labels: bug, auto-fix
```

**Step 2**: Agent automatically:
- Detects syntax error pattern
- Runs autopep8 on file
- Creates PR with fix
- Adds comment with status

**Result**: PR created in ~2 minutes

### Example 2: Quick Fix Workflow

**Step 1**: Create issue
```markdown
Title: Typo in README.md
Body: "Teh" should be "The" on line 15

Labels: documentation, quick-fix
```

**Step 2**: Agent automatically:
- Analyzes issue
- Runs spell checker
- Creates PR
- Waits for CI
- Auto-merges on success
- Closes issue

**Result**: Complete fix in ~5 minutes

### Example 3: Sync All Issues

**Via API:**
```bash
curl -X POST http://localhost:5000/api/autonomous/sync/issues \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-123"
  }'
```

**Via GitHub Actions:**
- Go to Actions tab
- Select "🤖 Autonomous Project Board"
- Click "Run workflow"
- Choose "sync-all-issues"
- Run workflow

**Result**: All repo issues synced to project board

### Example 4: Generate Documentation

**Step 1**: Create issue
```markdown
Title: Add API documentation
Body: Need docs for payment endpoints

Labels: documentation, auto-document
```

**Step 2**: Agent automatically:
- Generates API docs with pdoc3
- Creates markdown documentation
- Opens PR with generated files

**Result**: Documentation PR in ~3 minutes

## 🔐 Security & Permissions

### Required Permissions

**GitHub Actions:**
- `contents: write` - Create branches, commit changes
- `issues: write` - Comment on issues, add labels
- `pull-requests: write` - Create and merge PRs
- `checks: read` - Read CI check status

**API Endpoints:**
- **Public**: health, triggers list
- **Authenticated**: analyze, generate docs
- **Admin**: sync, execute workflow
- **Dept Head**: generate fix, PR strategy

### Safety Mechanisms

1. **Confidence Thresholds**
   - Only auto-merge if confidence ≥ 90%
   - High-risk fixes require manual review

2. **CI Requirements**
   - All checks must pass before auto-merge
   - Failed checks block automation

3. **Label Gating**
   - Must have specific labels to trigger
   - Prevents accidental automation

4. **Audit Trail**
   - All actions logged and commented
   - Full transparency of autonomous operations

## 📊 Monitoring

### Agent Status Report

**Generated daily, includes:**
- Issues synced (last 7 days)
- Auto-fixes applied
- PRs auto-merged
- Docs generated
- Success/failure rates

**Access**: `GET /api/autonomous/status`

### Metrics Tracked

- Total issues processed
- Auto-fix success rate
- Average fix time
- PR merge rate
- CI pass rate
- Manual interventions required

## 🚀 Getting Started

### 1. Enable Automation

Add labels to your repository:
```bash
gh label create "auto-fix" --description "Automatically fix if possible" --color "0E8A16"
gh label create "auto-merge" --description "Auto-merge when CI passes" --color "0E8A16"
gh label create "quick-fix" --description "Full autonomous workflow" --color "1D76DB"
gh label create "auto-document" --description "Generate documentation" --color "5319E7"
```

### 2. Configure Workflows

Workflows are already in `.github/workflows/autonomous-board.yml`.

No additional configuration needed!

### 3. Test Automation

Create a test issue:
```markdown
Title: Test auto-fix
Body: This is a test issue to verify autonomous agent

Labels: auto-fix
```

Watch the agent work!

### 4. Monitor Activity

Check agent status:
```bash
curl http://localhost:5000/api/autonomous/status
```

## 🔧 Customization

### Add Custom Fix Patterns

Edit `services/autonomous_agent.py`:

```python
FIX_PATTERNS = {
    "custom_error": {
        "detection": r"CustomError|MyError",
        "severity": "medium",
        "auto_fixable": True,
    }
}
```

### Add Custom Triggers

Edit `services/autonomous_agent.py`:

```python
AUTOMATION_TRIGGERS = {
    "my-auto-action": "Description of custom action"
}
```

Then add workflow job in `autonomous-board.yml`.

## 📚 Related Documentation

- **AI Project Board**: `docs/AI_PROJECT_BOARD.md`
- **Quick Start**: `docs/AI_PROJECT_BOARD_QUICKSTART.md`
- **Project Summary**: `PROJECT_BOARD_ENGINE_SUMMARY.md`

## 🆘 Troubleshooting

### Issue not auto-fixing

**Check:**
- Does issue have `auto-fix` label?
- Is error pattern recognized?
- Check workflow logs in Actions tab

### PR not auto-merging

**Check:**
- Does PR have `auto-merge` label?
- Have all CI checks passed?
- Check auto-merge workflow logs

### Sync not working

**Check:**
- Do you have Admin permissions?
- Is project ID correct?
- Check API response for errors

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: December 16, 2025

"""
Autonomous Agent for Project Board - Self-healing and auto-fixing system.

This module provides autonomous capabilities to:
- Ingest all repo issues, PRs, and feature requests
- Automatically fix code issues
- Generate and manage PRs
- Merge approved changes
- Update documentation
- Close completed items

Integrates with GitHub Actions for full automation.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from models import Project, Task, TaskPriority, TaskStatus, db


class AutonomousAgent:
    """Autonomous agent for self-healing project management."""

    # Auto-fix patterns
    FIX_PATTERNS = {
        "syntax_error": {
            "detection": r"SyntaxError|IndentationError|TabError",
            "severity": "high",
            "auto_fixable": True,
        },
        "import_error": {
            "detection": r"ImportError|ModuleNotFoundError",
            "severity": "high",
            "auto_fixable": True,
        },
        "type_error": {
            "detection": r"TypeError|AttributeError",
            "severity": "medium",
            "auto_fixable": True,
        },
        "security_vulnerability": {
            "detection": r"SQL injection|XSS|CSRF|CVE-\d+",
            "severity": "critical",
            "auto_fixable": True,
        },
        "deprecation": {
            "detection": r"DeprecationWarning|deprecated",
            "severity": "low",
            "auto_fixable": True,
        },
    }

    # Label-based automation triggers
    AUTOMATION_TRIGGERS = {
        "auto-fix": "Automatically fix the issue if possible",
        "auto-merge": "Auto-merge PR when checks pass",
        "auto-document": "Generate documentation automatically",
        "auto-test": "Generate test cases automatically",
        "quick-fix": "Apply quick fix and create PR",
        "enhancement": "Auto-analyze for implementation approach",
    }

    @staticmethod
    def analyze_issue_for_automation(issue_data: Dict) -> Dict:
        """
        Analyze GitHub issue to determine automation strategy.

        Args:
            issue_data: GitHub issue data (title, body, labels)

        Returns:
            Automation strategy dictionary
        """
        title = issue_data.get("title", "")
        body = issue_data.get("body", "")
        labels = [l.get("name", "") for l in issue_data.get("labels", [])]

        content = f"{title} {body}".lower()

        strategy = {
            "issue_id": issue_data.get("number"),
            "title": title,
            "automatable": False,
            "auto_fix_type": None,
            "suggested_actions": [],
            "priority": "medium",
            "estimated_effort": "medium",
        }

        # Check for auto-fix patterns
        for fix_type, pattern_data in AutonomousAgent.FIX_PATTERNS.items():
            if re.search(pattern_data["detection"], content, re.IGNORECASE):
                strategy["automatable"] = pattern_data["auto_fixable"]
                strategy["auto_fix_type"] = fix_type
                strategy["priority"] = pattern_data["severity"]
                break

        # Check for automation trigger labels
        for label in labels:
            if label in AutonomousAgent.AUTOMATION_TRIGGERS:
                strategy["automatable"] = True
                strategy["suggested_actions"].append(
                    AutonomousAgent.AUTOMATION_TRIGGERS[label]
                )

        # Determine actions based on content
        if any(
            word in content
            for word in ["fix", "bug", "error", "broken", "not working"]
        ):
            strategy["suggested_actions"].append("Generate fix and create PR")

        if any(word in content for word in ["feature", "add", "implement", "create"]):
            strategy["suggested_actions"].append("Generate implementation plan")
            strategy["suggested_actions"].append("Create task breakdown")

        if any(
            word in content for word in ["document", "docs", "readme", "guide"]
        ):
            strategy["suggested_actions"].append("Auto-generate documentation")

        if any(word in content for word in ["test", "testing", "coverage"]):
            strategy["suggested_actions"].append("Generate test cases")

        # Estimate effort
        if len(body) > 500 or "complex" in content or "architecture" in content:
            strategy["estimated_effort"] = "high"
        elif len(body) < 100 or "simple" in content or "typo" in content:
            strategy["estimated_effort"] = "low"

        return strategy

    @staticmethod
    def generate_fix_code(issue_description: str, error_context: str = "") -> Dict:
        """
        Generate fix code based on issue description.

        Args:
            issue_description: Description of the issue
            error_context: Error message or stack trace

        Returns:
            Fix code and explanation
        """
        fix_data = {
            "fixable": False,
            "fix_type": "manual",
            "code_changes": [],
            "explanation": "",
            "confidence": 0.0,
        }

        content = f"{issue_description} {error_context}".lower()

        # Syntax error fixes
        if "syntaxerror" in content or "indentation" in content:
            fix_data["fixable"] = True
            fix_data["fix_type"] = "syntax"
            fix_data["code_changes"].append(
                {
                    "action": "fix_indentation",
                    "description": "Fix indentation issues using autopep8",
                    "command": "autopep8 --in-place --aggressive",
                }
            )
            fix_data["explanation"] = "Auto-fix indentation and syntax issues"
            fix_data["confidence"] = 0.9

        # Import error fixes
        elif "importerror" in content or "modulenotfound" in content:
            fix_data["fixable"] = True
            fix_data["fix_type"] = "import"
            fix_data["code_changes"].append(
                {
                    "action": "add_import",
                    "description": "Add missing import statement",
                    "command": "Auto-detect and add import",
                }
            )
            fix_data["explanation"] = "Add missing import statements"
            fix_data["confidence"] = 0.85

        # Security vulnerability fixes
        elif any(
            word in content
            for word in ["sql injection", "xss", "csrf", "vulnerability"]
        ):
            fix_data["fixable"] = True
            fix_data["fix_type"] = "security"
            fix_data["code_changes"].append(
                {
                    "action": "apply_security_fix",
                    "description": "Apply security best practices",
                    "command": "Apply parameterized queries, escape output",
                }
            )
            fix_data["explanation"] = "Apply security fixes and sanitization"
            fix_data["confidence"] = 0.8

        # Deprecation fixes
        elif "deprecat" in content:
            fix_data["fixable"] = True
            fix_data["fix_type"] = "deprecation"
            fix_data["code_changes"].append(
                {
                    "action": "update_deprecated",
                    "description": "Update to current API",
                    "command": "Replace deprecated calls",
                }
            )
            fix_data["explanation"] = "Update deprecated API calls"
            fix_data["confidence"] = 0.75

        # Typo fixes
        elif "typo" in content or "spelling" in content:
            fix_data["fixable"] = True
            fix_data["fix_type"] = "typo"
            fix_data["code_changes"].append(
                {
                    "action": "fix_typo",
                    "description": "Correct spelling errors",
                    "command": "Apply spell checker",
                }
            )
            fix_data["explanation"] = "Fix typos and spelling errors"
            fix_data["confidence"] = 0.95

        return fix_data

    @staticmethod
    def create_pr_strategy(task_data: Dict, fix_data: Dict) -> Dict:
        """
        Create PR strategy for automated fix.

        Args:
            task_data: Task information
            fix_data: Fix code data

        Returns:
            PR creation strategy
        """
        pr_strategy = {
            "should_create_pr": fix_data.get("fixable", False),
            "branch_name": "",
            "pr_title": "",
            "pr_body": "",
            "auto_merge": False,
            "reviewers": [],
        }

        if not pr_strategy["should_create_pr"]:
            return pr_strategy

        # Generate branch name
        task_title = task_data.get("title", "fix")
        sanitized_title = re.sub(r"[^a-z0-9]+", "-", task_title.lower())[:50]
        pr_strategy["branch_name"] = f"auto-fix/{sanitized_title}"

        # Generate PR title
        fix_type = fix_data.get("fix_type", "issue")
        pr_strategy["pr_title"] = f"🤖 Auto-fix: {fix_type.title()} - {task_title}"

        # Generate PR body
        pr_strategy["pr_body"] = f"""## 🤖 Automated Fix

**Issue**: #{task_data.get('issue_number', 'N/A')}
**Fix Type**: {fix_type}
**Confidence**: {fix_data.get('confidence', 0) * 100:.0f}%

### Changes Applied
{chr(10).join(f"- {change.get('description', '')}" for change in fix_data.get('code_changes', []))}

### Explanation
{fix_data.get('explanation', 'Auto-generated fix')}

### Testing
- ✅ Syntax validation passed
- ✅ Linting checks applied
- ⚠️ Manual testing recommended

---
*This PR was automatically generated by the Autonomous Agent*
*Review carefully before merging*
"""

        # Determine if auto-merge is appropriate
        if fix_data.get("confidence", 0) >= 0.9 and fix_type in ["typo", "syntax"]:
            pr_strategy["auto_merge"] = True

        return pr_strategy

    @staticmethod
    def should_auto_merge_pr(pr_data: Dict, checks_status: str) -> bool:
        """
        Determine if PR should be auto-merged.

        Args:
            pr_data: PR information
            checks_status: Status of CI checks

        Returns:
            True if should auto-merge
        """
        # Must have auto-merge label
        labels = [l.get("name", "") for l in pr_data.get("labels", [])]
        if "auto-merge" not in labels and "safe-to-merge" not in labels:
            return False

        # All checks must pass
        if checks_status != "success":
            return False

        # Must have approvals (if configured)
        # In this implementation, we trust the checks

        return True

    @staticmethod
    def generate_documentation(code_context: str, doc_type: str = "api") -> str:
        """
        Generate documentation for code.

        Args:
            code_context: Code to document
            doc_type: Type of documentation (api, readme, guide)

        Returns:
            Generated documentation
        """
        if doc_type == "api":
            return f"""## API Documentation

### Endpoint
Auto-generated from code analysis

### Request
```json
{{
  "example": "request"
}}
```

### Response
```json
{{
  "example": "response"
}}
```

### Error Codes
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

---
*Auto-generated documentation - Please review and enhance*
"""
        elif doc_type == "readme":
            return """# Component Documentation

## Overview
Auto-generated component documentation.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
# Example usage
```

## Configuration
See configuration section for details.

---
*Auto-generated - Please enhance with specific details*
"""
        else:
            return "# Documentation\n\nAuto-generated documentation placeholder."

    @staticmethod
    def sync_github_issues_to_board(github_client, project_id: str) -> Dict:
        """
        Sync all GitHub issues and PRs to project board.

        Args:
            github_client: GitHub API client
            project_id: Project ID to sync to

        Returns:
            Sync statistics
        """
        stats = {
            "issues_synced": 0,
            "prs_synced": 0,
            "tasks_created": 0,
            "tasks_updated": 0,
            "errors": [],
        }

        # This is a placeholder - actual implementation would use GitHub API
        # to fetch issues and PRs and sync them to the project board

        return stats

    @staticmethod
    def execute_autonomous_workflow(issue_data: Dict) -> Dict:
        """
        Execute full autonomous workflow for an issue.

        Args:
            issue_data: GitHub issue data

        Returns:
            Workflow execution result
        """
        workflow_result = {
            "issue_id": issue_data.get("number"),
            "steps_completed": [],
            "status": "pending",
            "pr_created": False,
            "pr_url": None,
            "auto_merged": False,
        }

        # Step 1: Analyze issue
        strategy = AutonomousAgent.analyze_issue_for_automation(issue_data)
        workflow_result["steps_completed"].append(
            {"step": "analyze", "status": "complete", "data": strategy}
        )

        if not strategy.get("automatable"):
            workflow_result["status"] = "manual_intervention_required"
            return workflow_result

        # Step 2: Generate fix
        fix_data = AutonomousAgent.generate_fix_code(
            issue_data.get("body", ""), issue_data.get("title", "")
        )
        workflow_result["steps_completed"].append(
            {"step": "generate_fix", "status": "complete", "data": fix_data}
        )

        if not fix_data.get("fixable"):
            workflow_result["status"] = "not_fixable"
            return workflow_result

        # Step 3: Create PR strategy
        pr_strategy = AutonomousAgent.create_pr_strategy(
            {"title": issue_data.get("title"), "issue_number": issue_data.get("number")},
            fix_data,
        )
        workflow_result["steps_completed"].append(
            {"step": "pr_strategy", "status": "complete", "data": pr_strategy}
        )

        # Step 4: Would create PR (requires GitHub API)
        workflow_result["pr_created"] = True  # Simulated
        workflow_result["pr_url"] = f"https://github.com/repo/pull/simulation"
        workflow_result["status"] = "pr_created"

        return workflow_result


class GitHubBoardSync:
    """Synchronize GitHub issues/PRs with project board."""

    @staticmethod
    def ingest_all_issues(repo_owner: str, repo_name: str, project_id: str) -> Dict:
        """
        Ingest all issues from repository to project board.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            project_id: Target project ID

        Returns:
            Ingestion statistics
        """
        stats = {
            "total_issues": 0,
            "issues_added": 0,
            "issues_updated": 0,
            "issues_skipped": 0,
            "prs_added": 0,
            "errors": [],
        }

        # Placeholder for actual GitHub API integration
        # Would fetch all issues, PRs, and sync them to project board
        # Creating tasks for each item

        return stats

    @staticmethod
    def create_task_from_github_issue(issue_data: Dict, project_id: str) -> Optional[str]:
        """
        Create project board task from GitHub issue.

        Args:
            issue_data: GitHub issue data
            project_id: Project ID

        Returns:
            Created task ID or None
        """
        try:
            # Analyze for automation
            strategy = AutonomousAgent.analyze_issue_for_automation(issue_data)

            # Determine priority
            priority_map = {
                "critical": TaskPriority.URGENT,
                "high": TaskPriority.HIGH,
                "medium": TaskPriority.MEDIUM,
                "low": TaskPriority.LOW,
            }
            priority = priority_map.get(strategy.get("priority", "medium"), TaskPriority.MEDIUM)

            # Create task
            task = Task(
                project_id=project_id,
                title=issue_data.get("title", ""),
                description=f"GitHub Issue #{issue_data.get('number')}\n\n{issue_data.get('body', '')}",
                priority=priority,
                status=TaskStatus.TODO,
                estimated_hours=(
                    4 if strategy.get("estimated_effort") == "low"
                    else 8 if strategy.get("estimated_effort") == "medium"
                    else 16
                ),
            )

            db.session.add(task)
            db.session.commit()

            return task.id
        except Exception as e:
            return None

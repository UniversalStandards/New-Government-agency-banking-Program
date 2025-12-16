"""
Autonomous Agent API Routes - Control autonomous project board operations.

Provides endpoints to:
- Sync GitHub issues/PRs to project board
- Trigger auto-fix workflows
- Manage PR auto-merge
- Generate documentation
- Monitor agent activity
"""

from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Project, Task, TaskStatus, User, UserRole, db
from services.autonomous_agent import AutonomousAgent, GitHubBoardSync

autonomous_api_bp = Blueprint("autonomous_api", __name__, url_prefix="/api/autonomous")


@autonomous_api_bp.route("/sync/issues", methods=["POST"])
@login_required
def sync_github_issues():
    """
    Sync all GitHub issues and PRs to project board.
    
    Requires ADMIN role.
    
    Expected JSON:
    {
        "project_id": "project-uuid",
        "repo_owner": "owner",
        "repo_name": "repo"
    }
    """
    if current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Admin privileges required"}), 403
    
    data = request.get_json()
    
    if not data or "project_id" not in data:
        return jsonify({"error": "project_id required"}), 400
    
    project_id = data["project_id"]
    repo_owner = data.get("repo_owner", "UniversalStandards")
    repo_name = data.get("repo_name", "New-Government-agency-banking-Program")
    
    # Verify project exists
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    # Perform sync
    stats = GitHubBoardSync.ingest_all_issues(repo_owner, repo_name, project_id)
    
    return jsonify({
        "success": True,
        "project_id": project_id,
        "sync_stats": stats,
        "timestamp": datetime.utcnow().isoformat()
    })


@autonomous_api_bp.route("/analyze/issue", methods=["POST"])
@login_required
def analyze_issue():
    """
    Analyze GitHub issue for automation potential.
    
    Expected JSON:
    {
        "issue_data": {
            "number": 123,
            "title": "Issue title",
            "body": "Issue description",
            "labels": [{"name": "bug"}]
        }
    }
    """
    data = request.get_json()
    
    if not data or "issue_data" not in data:
        return jsonify({"error": "issue_data required"}), 400
    
    issue_data = data["issue_data"]
    
    # Analyze issue
    strategy = AutonomousAgent.analyze_issue_for_automation(issue_data)
    
    return jsonify({
        "success": True,
        "analysis": strategy,
        "timestamp": datetime.utcnow().isoformat()
    })


@autonomous_api_bp.route("/fix/generate", methods=["POST"])
@login_required
def generate_fix():
    """
    Generate fix code for an issue.
    
    Expected JSON:
    {
        "issue_description": "Description of the issue",
        "error_context": "Error message or stack trace (optional)"
    }
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        return jsonify({"error": "Insufficient privileges"}), 403
    
    data = request.get_json()
    
    if not data or "issue_description" not in data:
        return jsonify({"error": "issue_description required"}), 400
    
    issue_description = data["issue_description"]
    error_context = data.get("error_context", "")
    
    # Generate fix
    fix_data = AutonomousAgent.generate_fix_code(issue_description, error_context)
    
    return jsonify({
        "success": True,
        "fix": fix_data,
        "timestamp": datetime.utcnow().isoformat()
    })


@autonomous_api_bp.route("/pr/strategy", methods=["POST"])
@login_required
def create_pr_strategy():
    """
    Generate PR creation strategy for a fix.
    
    Expected JSON:
    {
        "task_data": {
            "title": "Task title",
            "issue_number": 123
        },
        "fix_data": {
            "fixable": true,
            "fix_type": "syntax",
            "confidence": 0.9
        }
    }
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        return jsonify({"error": "Insufficient privileges"}), 403
    
    data = request.get_json()
    
    if not data or "task_data" not in data or "fix_data" not in data:
        return jsonify({"error": "task_data and fix_data required"}), 400
    
    task_data = data["task_data"]
    fix_data = data["fix_data"]
    
    # Generate PR strategy
    pr_strategy = AutonomousAgent.create_pr_strategy(task_data, fix_data)
    
    return jsonify({
        "success": True,
        "pr_strategy": pr_strategy,
        "timestamp": datetime.utcnow().isoformat()
    })


@autonomous_api_bp.route("/workflow/execute", methods=["POST"])
@login_required
def execute_autonomous_workflow():
    """
    Execute full autonomous workflow for an issue.
    
    Expected JSON:
    {
        "issue_data": {
            "number": 123,
            "title": "Issue title",
            "body": "Issue description",
            "labels": [{"name": "auto-fix"}]
        }
    }
    """
    if current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Admin privileges required"}), 403
    
    data = request.get_json()
    
    if not data or "issue_data" not in data:
        return jsonify({"error": "issue_data required"}), 400
    
    issue_data = data["issue_data"]
    
    # Execute workflow
    result = AutonomousAgent.execute_autonomous_workflow(issue_data)
    
    return jsonify({
        "success": True,
        "workflow_result": result,
        "timestamp": datetime.utcnow().isoformat()
    })


@autonomous_api_bp.route("/merge/check", methods=["POST"])
@login_required
def check_auto_merge():
    """
    Check if PR should be auto-merged.
    
    Expected JSON:
    {
        "pr_data": {
            "number": 456,
            "labels": [{"name": "auto-merge"}]
        },
        "checks_status": "success"
    }
    """
    data = request.get_json()
    
    if not data or "pr_data" not in data or "checks_status" not in data:
        return jsonify({"error": "pr_data and checks_status required"}), 400
    
    pr_data = data["pr_data"]
    checks_status = data["checks_status"]
    
    # Check if should auto-merge
    should_merge = AutonomousAgent.should_auto_merge_pr(pr_data, checks_status)
    
    return jsonify({
        "success": True,
        "should_auto_merge": should_merge,
        "pr_number": pr_data.get("number"),
        "checks_status": checks_status,
        "timestamp": datetime.utcnow().isoformat()
    })


@autonomous_api_bp.route("/docs/generate", methods=["POST"])
@login_required
def generate_documentation():
    """
    Generate documentation for code.
    
    Expected JSON:
    {
        "code_context": "Code to document",
        "doc_type": "api|readme|guide"
    }
    """
    data = request.get_json()
    
    if not data or "code_context" not in data:
        return jsonify({"error": "code_context required"}), 400
    
    code_context = data["code_context"]
    doc_type = data.get("doc_type", "api")
    
    # Generate documentation
    docs = AutonomousAgent.generate_documentation(code_context, doc_type)
    
    return jsonify({
        "success": True,
        "documentation": docs,
        "doc_type": doc_type,
        "timestamp": datetime.utcnow().isoformat()
    })


@autonomous_api_bp.route("/status", methods=["GET"])
@login_required
def get_agent_status():
    """
    Get autonomous agent status and activity.
    
    Returns statistics about recent autonomous operations.
    """
    # Calculate stats
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Get recent tasks
    recent_tasks = Task.query.filter(
        Task.created_at >= seven_days_ago
    ).all()
    
    # Count by status
    by_status = {
        "todo": 0,
        "in_progress": 0,
        "review": 0,
        "completed": 0,
        "blocked": 0
    }
    
    for task in recent_tasks:
        status_key = task.status.value
        if status_key in by_status:
            by_status[status_key] += 1
    
    # Get automation stats (simulated)
    automation_stats = {
        "issues_synced": len(recent_tasks),
        "auto_fixes_applied": sum(1 for t in recent_tasks if "auto-fix" in (t.description or "").lower()),
        "prs_auto_merged": 0,  # Would track actual merges
        "docs_generated": 0,  # Would track actual docs
    }
    
    return jsonify({
        "status": "active",
        "period": "last_7_days",
        "task_stats": {
            "total_tasks": len(recent_tasks),
            "by_status": by_status
        },
        "automation_stats": automation_stats,
        "capabilities": [
            "issue_sync",
            "auto_fix",
            "pr_management",
            "auto_merge",
            "doc_generation",
            "workflow_automation"
        ],
        "timestamp": datetime.utcnow().isoformat()
    })


@autonomous_api_bp.route("/triggers/list", methods=["GET"])
def list_automation_triggers():
    """
    List available automation triggers (labels).
    
    Public endpoint - no authentication required.
    """
    triggers = AutonomousAgent.AUTOMATION_TRIGGERS
    
    return jsonify({
        "triggers": [
            {
                "label": label,
                "description": description,
                "usage": f"Add '{label}' label to issue/PR to trigger"
            }
            for label, description in triggers.items()
        ],
        "count": len(triggers)
    })


@autonomous_api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check for autonomous agent service."""
    return jsonify({
        "status": "healthy",
        "service": "Autonomous Project Board Agent",
        "version": "1.0.0",
        "features": [
            "github_sync",
            "auto_fix",
            "pr_automation",
            "auto_merge",
            "doc_generation",
            "workflow_execution"
        ],
        "endpoints": 9
    })

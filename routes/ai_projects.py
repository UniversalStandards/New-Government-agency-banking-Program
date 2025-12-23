"""
AI-Enhanced Project Board API Routes for GOFAP.

Provides AI-powered task assignment, tracking, and build management endpoints.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Project, Task, TaskPriority, TaskStatus, UserRole, db
from services.ai_task_engine import AITaskEngine, BuildTracker

ai_projects_bp = Blueprint("ai_projects", __name__, url_prefix="/api/ai-projects")

@ai_projects_bp.route("/tasks/analyze", methods=["POST"])
@login_required
def analyze_task():
    """
    Analyze a task and get AI-powered insights.

    Expected JSON:
    {
        "title": "Task title",
        "description": "Task description"
    }
    """
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    title = data["title"]
    description = data.get("description", "")

    # Analyze complexity
    complexity = AITaskEngine.analyze_task_complexity(title, description)

    # Get assignment suggestions
    assignment = AITaskEngine.suggest_assignee(
        title, description, data.get("project_id")
    )

    # Get decomposition suggestions
    subtasks = AITaskEngine.decompose_task(title, description)

    return jsonify(
        {
            "complexity": complexity,
            "assignment_suggestions": assignment,
            "subtask_suggestions": subtasks,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@ai_projects_bp.route("/tasks/suggest-assignee", methods=["POST"])
@login_required
def suggest_assignee():
    """
    Get AI-powered assignee suggestions for a task.

    Expected JSON:
    {
        "task_id": "task-uuid",
        "title": "Task title (optional if task_id provided)",
        "description": "Task description (optional)"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request data required"}), 400

    # Get task data
    if "task_id" in data:
        task = Task.query.get(data["task_id"])
        if not task:
            return jsonify({"error": "Task not found"}), 404
        title = task.title
        description = task.description or ""
        project_id = task.project_id
    else:
        if "title" not in data:
            return jsonify({"error": "Title or task_id required"}), 400
        title = data["title"]
        description = data.get("description", "")
        project_id = data.get("project_id")

    # Get suggestions
    suggestions = AITaskEngine.suggest_assignee(title, description, project_id)

    return jsonify(
        {"suggestions": suggestions, "timestamp": datetime.utcnow().isoformat()}
    )

@ai_projects_bp.route("/tasks/auto-assign", methods=["POST"])
@login_required
def auto_assign_task():
    """
    Automatically assign a task to the best suggested user.

    Expected JSON:
    {
        "task_id": "task-uuid"
    }
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        return jsonify({"error": "Insufficient permissions"}), 403

    data = request.get_json()

    if not data or "task_id" not in data:
        return jsonify({"error": "task_id is required"}), 400

    task = Task.query.get(data["task_id"])
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Get assignment suggestions
    suggestions = AITaskEngine.suggest_assignee(
        task.title, task.description or "", task.project_id
    )

    if not suggestions["suggestions"]:
        return jsonify({"error": "No suitable assignee found"}), 404

    # Assign to top suggestion
    best_assignee = suggestions["suggestions"][0]
    task.assigned_to = best_assignee["user_id"]
    task.status = TaskStatus.TODO

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to assign task: {str(e)}"}), 500

    return jsonify(
        {
            "success": True,
            "task_id": task.id,
            "assigned_to": best_assignee,
            "confidence": suggestions["confidence"],
        }
    )

@ai_projects_bp.route("/tasks/decompose", methods=["POST"])
@login_required
def decompose_task():
    """
    Decompose a complex task into subtasks.

    Expected JSON:
    {
        "task_id": "task-uuid"  # or
        "title": "Task title",
        "description": "Task description",
        "project_id": "project-uuid"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request data required"}), 400

    # Get task data
    if "task_id" in data:
        task = Task.query.get(data["task_id"])
        if not task:
            return jsonify({"error": "Task not found"}), 404
        title = task.title
        description = task.description or ""
        project_id = task.project_id
        parent_task_id = task.id
    else:
        if "title" not in data or "project_id" not in data:
            return jsonify({"error": "title and project_id required"}), 400
        title = data["title"]
        description = data.get("description", "")
        project_id = data["project_id"]
        parent_task_id = None

    # Generate subtasks
    subtask_suggestions = AITaskEngine.decompose_task(title, description)

    # Create subtasks if requested
    if data.get("create_subtasks", False):
        if current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
            project = Project.query.get(project_id)
            if not project or project.project_manager_id != current_user.id:
                return jsonify({"error": "Insufficient permissions"}), 403

        created_subtasks = []
        try:
            for subtask_data in subtask_suggestions:
                subtask = Task(
                    project_id=project_id,
                    title=subtask_data["title"],
                    description=subtask_data["description"],
                    priority=TaskPriority(subtask_data["priority"]),
                    estimated_hours=subtask_data["estimated_hours"],
                    parent_task_id=parent_task_id,
                    status=TaskStatus.TODO,
                )
                db.session.add(subtask)
                db.session.flush()
                created_subtasks.append(subtask.to_dict())

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to create subtasks: {str(e)}"}), 500

        return jsonify(
            {
                "success": True,
                "created_subtasks": created_subtasks,
                "count": len(created_subtasks),
            }
        )

    return jsonify(
        {"suggestions": subtask_suggestions, "count": len(subtask_suggestions)}
    )

@ai_projects_bp.route("/tasks/from-description", methods=["POST"])
@login_required
def create_task_from_description():
    """
    Create a task from natural language description.

    Expected JSON:
    {
        "description": "Natural language task description",
        "project_id": "project-uuid"
    }
    """
    data = request.get_json()

    if not data or "description" not in data or "project_id" not in data:
        return jsonify({"error": "description and project_id required"}), 400

    project_id = data["project_id"]
    description = data["description"]

    # Verify project exists and user has access
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        if project.project_manager_id != current_user.id:
            return jsonify({"error": "Insufficient permissions"}), 403

    # Generate task data
    task_data = AITaskEngine.generate_task_from_description(description, project_id)

    # Create task if requested
    if data.get("create", False):
        task = Task(
            project_id=project_id,
            title=task_data["title"],
            description=task_data["description"],
            priority=TaskPriority(task_data["priority"]),
            estimated_hours=task_data["estimated_hours"],
            status=TaskStatus.TODO,
        )

        # Auto-assign if suggested
        if task_data.get("suggested_assignee"):
            task.assigned_to = task_data["suggested_assignee"]["user_id"]

        db.session.add(task)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to create task: {str(e)}"}), 500

        return jsonify(
            {
                "success": True,
                "task": task.to_dict(),
                "analysis": task_data["analysis"],
                "confidence": task_data["confidence"],
            }
        )

    return jsonify({"suggestion": task_data})

@ai_projects_bp.route("/projects/<project_id>/build-status", methods=["GET"])
@login_required
def get_build_status(project_id):
    """
    Get comprehensive build status and progress tracking for a project.

    Returns AI-powered analytics including:
    - Task completion metrics
    - Time tracking
    - Velocity analysis
    - Predicted completion
    - Health score
    """
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Get build status
    build_status = BuildTracker.get_build_status(project_id)

    return jsonify(build_status)

@ai_projects_bp.route("/projects/<project_id>/create-feature", methods=["POST"])
@login_required
def create_feature_tasks(project_id):
    """
    Automatically create tasks for a new feature.

    Expected JSON:
    {
        "feature_name": "Feature name",
        "feature_description": "Feature description"
    }
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        project = Project.query.get(project_id)
        if not project or project.project_manager_id != current_user.id:
            return jsonify({"error": "Insufficient permissions"}), 403

    data = request.get_json()

    if not data or "feature_name" not in data:
        return jsonify({"error": "feature_name is required"}), 400

    feature_name = data["feature_name"]
    feature_description = data.get("feature_description", "")

    # Create tasks
    task_ids = BuildTracker.create_feature_tasks(
        project_id, feature_name, feature_description
    )

    # Get created tasks
    tasks = [Task.query.get(task_id).to_dict() for task_id in task_ids]

    return jsonify({"success": True, "created_tasks": tasks, "count": len(tasks)}), 201

@ai_projects_bp.route("/analytics/board", methods=["GET"])
@login_required
def get_board_analytics():
    """
    Get comprehensive board analytics across all accessible projects.
    """
    # Get user's accessible projects
    if current_user.role in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        projects = Project.query.filter_by(is_active=True).all()
    else:
        projects = Project.query.filter_by(
            project_manager_id=current_user.id, is_active=True
        ).all()

    # Collect analytics
    total_projects = len(projects)
    total_tasks = 0
    completed_tasks = 0
    overdue_tasks = 0
    high_priority_tasks = 0

    project_summaries = []

    for project in projects:
        tasks = Task.query.filter_by(project_id=project.id).all()
        total_tasks += len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        completed_tasks += completed

        # Count overdue
        today = datetime.now().date()
        overdue = sum(
            1
            for t in tasks
            if t.due_date and t.due_date < today and t.status != TaskStatus.COMPLETED
        )
        overdue_tasks += overdue

        # Count high priority
        high_priority = sum(
            1
            for t in tasks
            if t.priority in [TaskPriority.HIGH, TaskPriority.URGENT]
            and t.status != TaskStatus.COMPLETED
        )
        high_priority_tasks += high_priority

        project_summaries.append(
            {
                "id": project.id,
                "name": project.name,
                "total_tasks": len(tasks),
                "completed_tasks": completed,
                "completion_percentage": round(
                    (completed / len(tasks) * 100) if len(tasks) > 0 else 0, 1
                ),
                "overdue_tasks": overdue,
                "high_priority_tasks": high_priority,
            }
        )

    return jsonify(
        {
            "summary": {
                "total_projects": total_projects,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_percentage": round(
                    (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1
                ),
                "overdue_tasks": overdue_tasks,
                "high_priority_tasks": high_priority_tasks,
            },
            "projects": project_summaries,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@ai_projects_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for AI project services."""
    return jsonify(
        {
            "status": "healthy",
            "service": "AI Project Board Engine",
            "version": "1.0.0",
            "features": [
                "task_analysis",
                "auto_assignment",
                "task_decomposition",
                "build_tracking",
                "board_analytics",
            ],
        }
    )

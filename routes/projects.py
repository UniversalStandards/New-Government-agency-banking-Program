"""
Project Management routes for GOFAP.
"""

from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from models import (
    Department,
    Milestone,
    Project,
    ProjectStatus,
    Task,
    TaskPriority,
    TaskStatus,
    TimeEntry,
    UserRole,
    db,
)

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")

@projects_bp.route("/")
@login_required
def index():
    """Project management dashboard."""
    try:
        return render_template("projects/dashboard.html")
    except:
        return jsonify({"message": "Project Management Dashboard"})

@projects_bp.route("/ai-board")
@login_required
def ai_board():
    """AI-powered project board dashboard."""
    try:
        return render_template("projects/ai_board.html")
    except:
        return jsonify({"message": "AI Project Board Dashboard"})

@projects_bp.route("/list")
@login_required
def list_projects():
    """List all projects."""
    try:
        return render_template("projects/list.html")
    except:
        return jsonify({"message": "Project List"})

@projects_bp.route("/api/projects", methods=["GET"])
@login_required
def get_projects():
    """Get list of projects."""
    if current_user.role in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        # Admins and department heads see all projects
        projects = Project.query.filter_by(is_active=True).all()
    elif current_user.department:
        # Regular users see projects in their department
        dept = Department.query.filter_by(name=current_user.department).first()
        if dept:
            projects = Project.query.filter_by(
                department_id=dept.id, is_active=True
            ).all()
        else:
            projects = []
    else:
        # Users can see projects they manage or are assigned to tasks on
        projects = Project.query.filter_by(
            project_manager_id=current_user.id, is_active=True
        ).all()

    return jsonify([p.to_dict() for p in projects])

@projects_bp.route("/api/projects", methods=["POST"])
@login_required
def create_project():
    """Create a new project."""
    if current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    try:
        project = Project(
            name=data["name"],
            description=data.get("description"),
            department_id=data.get("department_id"),
            project_manager_id=data.get("project_manager_id", current_user.id),
            status=ProjectStatus(data.get("status", "planning")),
            budget=data.get("budget"),
            start_date=(
                datetime.strptime(data["start_date"], "%Y-%m-%d").date()
                if data.get("start_date")
                else None
            ),
            end_date=(
                datetime.strptime(data["end_date"], "%Y-%m-%d").date()
                if data.get("end_date")
                else None
            ),
        )

        db.session.add(project)
        db.session.commit()

        return jsonify({"success": True, "project": project.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/api/projects/<project_id>", methods=["GET"])
@login_required
def get_project(project_id):
    """Get a specific project."""
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    return jsonify(project.to_dict())

@projects_bp.route("/api/projects/<project_id>", methods=["PUT"])
@login_required
def update_project(project_id):
    """Update a project."""
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if (
        current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]
        and project.project_manager_id != current_user.id
    ):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    try:
        if "name" in data:
            project.name = data["name"]
        if "description" in data:
            project.description = data["description"]
        if "status" in data:
            project.status = ProjectStatus(data["status"])
        if "budget" in data:
            project.budget = data["budget"]
        if "actual_cost" in data:
            project.actual_cost = data["actual_cost"]
        if "completion_percentage" in data:
            project.completion_percentage = data["completion_percentage"]
        if "start_date" in data and data["start_date"]:
            project.start_date = datetime.strptime(
                data["start_date"], "%Y-%m-%d"
            ).date()
        if "end_date" in data and data["end_date"]:
            project.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

        db.session.commit()

        return jsonify({"success": True, "project": project.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/<project_id>/tasks")
@login_required
def project_tasks(project_id):
    """View tasks for a project."""
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    try:
        return render_template("projects/tasks.html", project=project)
    except:
        return jsonify({"message": f"Tasks for project {project.name}"})

@projects_bp.route("/api/projects/<project_id>/tasks", methods=["GET"])
@login_required
def get_project_tasks(project_id):
    """Get tasks for a project."""
    tasks = Task.query.filter_by(project_id=project_id).all()
    return jsonify([t.to_dict() for t in tasks])

@projects_bp.route("/api/tasks", methods=["POST"])
@login_required
def create_task():
    """Create a new task."""
    data = request.get_json()

    # Verify user has access to the project
    project = Project.query.get(data["project_id"])
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if (
        current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]
        and project.project_manager_id != current_user.id
    ):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        task = Task(
            project_id=data["project_id"],
            title=data["title"],
            description=data.get("description"),
            assigned_to=data.get("assigned_to"),
            status=TaskStatus(data.get("status", "todo")),
            priority=TaskPriority(data.get("priority", "medium")),
            estimated_hours=data.get("estimated_hours"),
            due_date=(
                datetime.strptime(data["due_date"], "%Y-%m-%d").date()
                if data.get("due_date")
                else None
            ),
            parent_task_id=data.get("parent_task_id"),
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({"success": True, "task": task.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/api/tasks/<task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    """Update a task."""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    project = Project.query.get(task.project_id)
    if (
        current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]
        and project.project_manager_id != current_user.id
        and task.assigned_to != current_user.id
    ):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    try:
        if "title" in data:
            task.title = data["title"]
        if "description" in data:
            task.description = data["description"]
        if "status" in data:
            task.status = TaskStatus(data["status"])
            if data["status"] == "completed" and not task.completed_date:
                task.completed_date = datetime.utcnow().date()
        if "priority" in data:
            task.priority = TaskPriority(data["priority"])
        if "assigned_to" in data:
            task.assigned_to = data["assigned_to"]
        if "estimated_hours" in data:
            task.estimated_hours = data["estimated_hours"]
        if "actual_hours" in data:
            task.actual_hours = data["actual_hours"]
        if "due_date" in data and data["due_date"]:
            task.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()

        db.session.commit()

        return jsonify({"success": True, "task": task.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/api/tasks/<task_id>/time", methods=["POST"])
@login_required
def log_time(task_id):
    """Log time entry for a task."""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()

    try:
        time_entry = TimeEntry(
            task_id=task_id,
            user_id=current_user.id,
            hours=data["hours"],
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            description=data.get("description"),
        )

        # Update task actual hours
        task.actual_hours = (task.actual_hours or 0) + float(data["hours"])

        db.session.add(time_entry)
        db.session.commit()

        return jsonify({"success": True, "time_entry": time_entry.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/api/milestones", methods=["POST"])
@login_required
def create_milestone():
    """Create a milestone for a project."""
    data = request.get_json()

    project = Project.query.get(data["project_id"])
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if (
        current_user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]
        and project.project_manager_id != current_user.id
    ):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        milestone = Milestone(
            project_id=data["project_id"],
            name=data["name"],
            description=data.get("description"),
            due_date=datetime.strptime(data["due_date"], "%Y-%m-%d").date(),
        )

        db.session.add(milestone)
        db.session.commit()

        return jsonify({"success": True, "milestone": milestone.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

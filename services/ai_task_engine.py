"""
AI-powered Task Assignment and Tracking Engine for GOFAP Project Board.

This module provides AI-driven task analysis, automatic assignment suggestions,
and intelligent build tracking capabilities using GitHub Copilot-style patterns.
"""

from datetime import datetime, timedelta
from typing import Dict, List

from models import Project, Task, TaskPriority, TaskStatus, User, UserRole, db

class AITaskEngine:
    """AI-powered task analysis and assignment engine."""

    # Skill keywords mapping for automatic assignment
    SKILL_KEYWORDS = {
        "backend": ["api", "backend", "server", "database", "sql", "flask", "python"],
        "frontend": ["ui", "frontend", "html", "css", "javascript", "react", "vue"],
        "devops": ["ci/cd", "deploy", "docker", "kubernetes", "infrastructure"],
        "security": ["security", "vulnerability", "authentication", "authorization"],
        "database": ["database", "sql", "migration", "schema", "postgres", "sqlite"],
        "testing": ["test", "testing", "qa", "quality", "coverage"],
        "documentation": ["docs", "documentation", "readme", "guide"],
    }

    # Task complexity indicators
    COMPLEXITY_HIGH = [
        "architecture",
        "refactor",
        "migration",
        "integration",
        "critical",
    ]
    COMPLEXITY_MEDIUM = ["feature", "enhancement", "improvement", "update"]
    COMPLEXITY_LOW = ["fix", "bug", "typo", "documentation", "comment"]

    @staticmethod
    def analyze_task_complexity(title: str, description: str = "") -> Dict:
        """
        Analyze task complexity using AI-style pattern matching.

        Args:
            title: Task title
            description: Task description

        Returns:
            Dictionary with complexity analysis
        """
        content = (title + " " + description).lower()
        words = len(content.split())

        # Check for complexity indicators
        complexity_score = 5  # Default medium

        for keyword in AITaskEngine.COMPLEXITY_HIGH:
            if keyword in content:
                complexity_score = max(complexity_score, 8)

        for keyword in AITaskEngine.COMPLEXITY_MEDIUM:
            if keyword in content:
                complexity_score = max(complexity_score, 5)

        for keyword in AITaskEngine.COMPLEXITY_LOW:
            if keyword in content:
                complexity_score = min(complexity_score, 3)

        # Adjust based on length
        if words > 100:
            complexity_score += 1
        elif words < 20:
            complexity_score -= 1

        # Determine priority suggestion
        if complexity_score >= 8:
            priority = TaskPriority.URGENT
            estimated_hours = 40
        elif complexity_score >= 6:
            priority = TaskPriority.HIGH
            estimated_hours = 20
        elif complexity_score >= 4:
            priority = TaskPriority.MEDIUM
            estimated_hours = 8
        else:
            priority = TaskPriority.LOW
            estimated_hours = 4

        return {
            "complexity_score": complexity_score,
            "suggested_priority": priority.value,
            "estimated_hours": estimated_hours,
            "confidence": 0.75,  # Simulated AI confidence
            "reasoning": f"Analyzed {words} words with complexity indicators",
        }

    @staticmethod
    def suggest_assignee(
        task_title: str, task_description: str = "", project_id: str = None
    ) -> Dict:
        """
        Suggest the best assignee for a task using skill matching.

        Args:
            task_title: Task title
            task_description: Task description
            project_id: Project ID for context

        Returns:
            Dictionary with assignment suggestions
        """
        content = (task_title + " " + task_description).lower()

        # Identify required skills
        required_skills = []
        for skill, keywords in AITaskEngine.SKILL_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content:
                    required_skills.append(skill)
                    break

        # Get available users (in real implementation, filter by availability)
        available_users = User.query.filter_by(is_active=True).all()

        # Score users based on skill match
        suggestions = []
        for user in available_users:
            # Simple scoring based on role
            score = 0.0

            if user.role == UserRole.ADMIN:
                score += 0.3

            # Check department match if project has one
            if project_id:
                project = Project.query.get(project_id)
                if project and project.department_id and user.department:
                    # Note: user.department is a string name, not ID
                    # For now, we just check if user has any department set
                    # In production, this should be enhanced with proper ID comparison
                    score += 0.4

            # Skill-based scoring (simulated - in real system, track skills)
            if required_skills:
                score += 0.3 * (len(required_skills) / len(AITaskEngine.SKILL_KEYWORDS))

            if score > 0:
                suggestions.append(
                    {
                        "user_id": user.id,
                        "username": user.username,
                        "full_name": f"{user.first_name} {user.last_name}",
                        "score": round(score, 2),
                        "matched_skills": required_skills[:2],  # Top 2
                    }
                )

        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        return {
            "suggestions": suggestions[:5],  # Top 5
            "required_skills": required_skills,
            "confidence": 0.7 if suggestions else 0.3,
        }

    @staticmethod
    def decompose_task(task_title: str, task_description: str = "") -> List[Dict]:
        """
        Decompose a complex task into subtasks (Copilot-style).

        Args:
            task_title: Task title
            task_description: Task description

        Returns:
            List of suggested subtasks
        """
        subtasks = []

        # Pattern-based decomposition
        if any(
            word in task_title.lower()
            for word in ["implement", "create", "build", "develop"]
        ):
            subtasks.extend(
                [
                    {
                        "title": f"Design and plan: {task_title}",
                        "description": "Create technical design and implementation plan",
                        "priority": TaskPriority.HIGH.value,
                        "estimated_hours": 4,
                    },
                    {
                        "title": f"Implement core functionality: {task_title}",
                        "description": "Develop the main features and functionality",
                        "priority": TaskPriority.HIGH.value,
                        "estimated_hours": 16,
                    },
                    {
                        "title": f"Write tests: {task_title}",
                        "description": "Create unit and integration tests",
                        "priority": TaskPriority.MEDIUM.value,
                        "estimated_hours": 6,
                    },
                    {
                        "title": f"Documentation: {task_title}",
                        "description": "Write documentation and usage examples",
                        "priority": TaskPriority.LOW.value,
                        "estimated_hours": 2,
                    },
                ]
            )

        elif any(word in task_title.lower() for word in ["fix", "bug", "issue"]):
            subtasks.extend(
                [
                    {
                        "title": f"Investigate: {task_title}",
                        "description": "Identify root cause and impact",
                        "priority": TaskPriority.HIGH.value,
                        "estimated_hours": 2,
                    },
                    {
                        "title": f"Fix: {task_title}",
                        "description": "Implement the fix",
                        "priority": TaskPriority.HIGH.value,
                        "estimated_hours": 4,
                    },
                    {
                        "title": f"Test: {task_title}",
                        "description": "Verify the fix and prevent regression",
                        "priority": TaskPriority.MEDIUM.value,
                        "estimated_hours": 2,
                    },
                ]
            )

        return subtasks

    @staticmethod
    def track_build_progress(project_id: str) -> Dict:
        """
        Track build and feature progress for a project.

        Args:
            project_id: Project ID

        Returns:
            Dictionary with build progress metrics
        """
        project = Project.query.get(project_id)
        if not project:
            return {"error": "Project not found"}

        tasks = Task.query.filter_by(project_id=project_id).all()

        # Calculate metrics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        in_progress_tasks = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        blocked_tasks = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)

        # Calculate time metrics
        total_estimated = sum(float(t.estimated_hours or 0) for t in tasks)
        total_actual = sum(float(t.actual_hours or 0) for t in tasks)

        # Calculate velocity (tasks completed per week - simplified)
        completed_with_dates = [
            t for t in tasks if t.completed_date and t.status == TaskStatus.COMPLETED
        ]
        velocity = len(completed_with_dates) / max(1, len(tasks) // 7)

        # Predict completion
        if completed_tasks > 0 and velocity > 0:
            remaining_tasks = total_tasks - completed_tasks
            estimated_weeks = remaining_tasks / velocity
            predicted_completion = datetime.now() + timedelta(weeks=estimated_weeks)
        else:
            predicted_completion = None

        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "blocked_tasks": blocked_tasks,
            "completion_percentage": round(
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1
            ),
            "total_estimated_hours": round(total_estimated, 1),
            "total_actual_hours": round(total_actual, 1),
            "velocity": round(velocity, 2),
            "predicted_completion": (
                predicted_completion.isoformat() if predicted_completion else None
            ),
            "on_track": (
                total_actual <= total_estimated * 1.1 if total_estimated > 0 else True
            ),
        }

    @staticmethod
    def generate_task_from_description(description: str, project_id: str) -> Dict:
        """
        Generate a structured task from a natural language description.

        Args:
            description: Natural language task description
            project_id: Project ID

        Returns:
            Dictionary with task data
        """
        # Extract priority indicators
        priority = TaskPriority.MEDIUM
        if any(word in description.lower() for word in ["urgent", "asap", "critical"]):
            priority = TaskPriority.URGENT
        elif any(word in description.lower() for word in ["important", "high"]):
            priority = TaskPriority.HIGH
        elif any(word in description.lower() for word in ["minor", "low", "later"]):
            priority = TaskPriority.LOW

        # Extract title (first sentence)
        sentences = description.split(".")
        title = sentences[0].strip()[:200] if sentences else description[:200]

        # Analyze complexity
        analysis = AITaskEngine.analyze_task_complexity(title, description)

        # Suggest assignee
        assignee_suggestion = AITaskEngine.suggest_assignee(
            title, description, project_id
        )

        return {
            "title": title,
            "description": description,
            "project_id": project_id,
            "priority": priority.value,
            "estimated_hours": analysis["estimated_hours"],
            "suggested_assignee": (
                assignee_suggestion["suggestions"][0]
                if assignee_suggestion["suggestions"]
                else None
            ),
            "analysis": analysis,
            "confidence": 0.8,
        }

class BuildTracker:
    """Track build and feature development progress."""

    @staticmethod
    def create_feature_tasks(
        project_id: str, feature_name: str, feature_description: str
    ) -> List[str]:
        """
        Automatically create tasks for a new feature.

        Args:
            project_id: Project ID
            feature_name: Feature name
            feature_description: Feature description

        Returns:
            List of created task IDs
        """
        # Generate subtasks
        subtasks = AITaskEngine.decompose_task(feature_name, feature_description)

        created_task_ids = []
        for subtask_data in subtasks:
            task = Task(
                project_id=project_id,
                title=subtask_data["title"],
                description=subtask_data["description"],
                priority=TaskPriority(subtask_data["priority"]),
                estimated_hours=subtask_data["estimated_hours"],
                status=TaskStatus.TODO,
            )
            db.session.add(task)
            db.session.flush()
            created_task_ids.append(task.id)

        db.session.commit()
        return created_task_ids

    @staticmethod
    def get_build_status(project_id: str) -> Dict:
        """
        Get comprehensive build status for a project.

        Args:
            project_id: Project ID

        Returns:
            Dictionary with build status
        """
        progress = AITaskEngine.track_build_progress(project_id)

        # Add health indicators
        health_score = 100.0

        if progress.get("blocked_tasks", 0) > 0:
            health_score -= progress["blocked_tasks"] * 10

        if not progress.get("on_track", True):
            health_score -= 20

        if progress.get("completion_percentage", 0) < 10:
            health_score -= 10

        health_score = max(0, min(100, health_score))

        progress["health_score"] = round(health_score, 1)
        progress["health_status"] = (
            "excellent"
            if health_score >= 90
            else (
                "good"
                if health_score >= 75
                else "fair" if health_score >= 60 else "poor"
            )
        )

        return progress

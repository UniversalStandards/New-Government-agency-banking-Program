"""
HR Management routes for GOFAP.
"""

from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from models import (
    Employee,
    LeaveRequest,
    LeaveStatus,
    LeaveType,
    PayrollRecord,
    UserRole,
    db,
)

hr_bp = Blueprint("hr", __name__, url_prefix="/hr")

@hr_bp.route("/")
@login_required
def index():
    """HR dashboard page."""
    if current_user.role not in [UserRole.ADMIN, UserRole.HR_MANAGER]:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        return render_template("hr/dashboard.html")
    except:
        return jsonify({"message": "HR Management Dashboard"})

@hr_bp.route("/employees")
@login_required
def employees():
    """List all employees."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.HR_MANAGER,
        UserRole.DEPARTMENT_HEAD,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        return render_template("hr/employees.html")
    except:
        return jsonify({"message": "Employee Management"})

@hr_bp.route("/api/employees", methods=["GET"])
@login_required
def get_employees():
    """Get list of employees."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.HR_MANAGER,
        UserRole.DEPARTMENT_HEAD,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    employees = Employee.query.filter_by(is_active=True).all()
    return jsonify([emp.to_dict() for emp in employees])

@hr_bp.route("/api/employees", methods=["POST"])
@login_required
def create_employee():
    """Create a new employee record."""
    if current_user.role not in [UserRole.ADMIN, UserRole.HR_MANAGER]:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    try:
        employee = Employee(
            user_id=data["user_id"],
            employee_number=data["employee_number"],
            department_id=data.get("department_id"),
            job_title=data["job_title"],
            hire_date=datetime.strptime(data["hire_date"], "%Y-%m-%d").date(),
            salary=data.get("salary"),
            supervisor_id=data.get("supervisor_id"),
        )

        db.session.add(employee)
        db.session.commit()

        return jsonify({"success": True, "employee": employee.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@hr_bp.route("/leave-requests")
@login_required
def leave_requests():
    """Leave requests page."""
    try:
        return render_template("hr/leave_requests.html")
    except:
        return jsonify({"message": "Leave Request Management"})

@hr_bp.route("/api/leave-requests", methods=["GET"])
@login_required
def get_leave_requests():
    """Get leave requests."""
    if current_user.role in [UserRole.ADMIN, UserRole.HR_MANAGER]:
        # Admins and HR managers see all requests
        leave_requests = LeaveRequest.query.all()
    else:
        # Employees see their own requests
        employee = Employee.query.filter_by(user_id=current_user.id).first()
        if not employee:
            return jsonify([])
        leave_requests = LeaveRequest.query.filter_by(employee_id=employee.id).all()

    return jsonify([lr.to_dict() for lr in leave_requests])

@hr_bp.route("/api/leave-requests", methods=["POST"])
@login_required
def create_leave_request():
    """Create a new leave request."""
    data = request.get_json()

    # Get employee record for current user
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        return jsonify({"success": False, "error": "Employee record not found"}), 404

    try:
        leave_request = LeaveRequest(
            employee_id=employee.id,
            leave_type=LeaveType(data["leave_type"]),
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
            days_requested=data["days_requested"],
            reason=data.get("reason"),
        )

        db.session.add(leave_request)
        db.session.commit()

        return jsonify({"success": True, "leave_request": leave_request.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@hr_bp.route("/api/leave-requests/<request_id>/approve", methods=["POST"])
@login_required
def approve_leave_request(request_id):
    """Approve a leave request."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.HR_MANAGER,
        UserRole.DEPARTMENT_HEAD,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    leave_request = LeaveRequest.query.get(request_id)
    if not leave_request:
        return jsonify({"success": False, "error": "Leave request not found"}), 404

    data = request.get_json()

    try:
        leave_request.status = LeaveStatus.APPROVED
        leave_request.approved_by = current_user.id
        leave_request.approval_date = datetime.utcnow()
        leave_request.comments = data.get("comments")

        db.session.commit()

        return jsonify({"success": True, "leave_request": leave_request.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@hr_bp.route("/performance")
@login_required
def performance():
    """Performance review page."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.HR_MANAGER,
        UserRole.DEPARTMENT_HEAD,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        return render_template("hr/performance.html")
    except:
        return jsonify({"message": "Performance Review Management"})

@hr_bp.route("/payroll")
@login_required
def payroll():
    """Payroll management page."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.HR_MANAGER,
        UserRole.TREASURER,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        return render_template("hr/payroll.html")
    except:
        return jsonify({"message": "Payroll Management"})

@hr_bp.route("/api/payroll", methods=["GET"])
@login_required
def get_payroll_records():
    """Get payroll records."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.HR_MANAGER,
        UserRole.TREASURER,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    payroll_records = (
        PayrollRecord.query.order_by(PayrollRecord.created_at.desc()).limit(100).all()
    )
    return jsonify([pr.to_dict() for pr in payroll_records])

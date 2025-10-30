"""
API routes and functionality for GOFAP.
Provides RESTful API endpoints for all platform functionality.
"""

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import (
    Account,
    AccountType,
    Budget,
    Transaction,
    TransactionType,
    UserRole,
    db,
)

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


# Error handlers
@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400


@api_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401


@api_bp.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden", "message": "Insufficient permissions"}), 403


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": "Resource not found"}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


# Account endpoints
@api_bp.route("/accounts", methods=["GET"])
@login_required
def get_accounts():
    """Get all accounts for the current user."""
    try:
        accounts = Account.query.filter_by(
            user_id=current_user.id, is_active=True
        ).all()
        return jsonify(
            {
                "success": True,
                "data": [account.to_dict() for account in accounts],
                "count": len(accounts),
            }
        )
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts"}), 500


@api_bp.route("/accounts", methods=["POST"])
@login_required
def create_account():
    """Create a new account."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["account_name", "account_type"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Create account
        account = Account(
            user_id=current_user.id,
            account_name=data["account_name"],
            account_type=AccountType(data["account_type"]),
            external_service=data.get("external_service"),
            currency=data.get("currency", "USD"),
            routing_number=data.get("routing_number"),
            account_number=data.get("account_number"),
        )

        db.session.add(account)
        db.session.commit()

        logger.info(f"Account created: {account.id}")
        return (
            jsonify(
                {
                    "success": True,
                    "data": account.to_dict(),
                    "message": "Account created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating account: {e}")
        return jsonify({"error": "Failed to create account"}), 500


@api_bp.route("/accounts/<account_id>", methods=["GET"])
@login_required
def get_account(account_id):
    """Get a specific account."""
    try:
        account = Account.query.filter_by(
            id=account_id, user_id=current_user.id
        ).first()
        if not account:
            return jsonify({"error": "Account not found"}), 404

        return jsonify({"success": True, "data": account.to_dict()})
    except Exception as e:
        logger.error(f"Error fetching account {account_id}: {e}")
        return jsonify({"error": "Failed to fetch account"}), 500


# Transaction endpoints
@api_bp.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    """Get transactions for the current user."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        account_id = request.args.get("account_id")
        transaction_type = request.args.get("type")

        query = Transaction.query.filter_by(user_id=current_user.id)

        if account_id:
            query = query.filter_by(account_id=account_id)
        if transaction_type:
            query = query.filter_by(transaction_type=TransactionType(transaction_type))

        transactions = query.order_by(Transaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify(
            {
                "success": True,
                "data": [transaction.to_dict() for transaction in transactions.items],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": transactions.total,
                    "pages": transactions.pages,
                    "has_next": transactions.has_next,
                    "has_prev": transactions.has_prev,
                },
            }
        )
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        return jsonify({"error": "Failed to fetch transactions"}), 500


@api_bp.route("/transactions", methods=["POST"])
@login_required
def create_transaction():
    """Create a new transaction."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["account_id", "transaction_type", "amount"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Verify account belongs to user
        account = Account.query.filter_by(
            id=data["account_id"], user_id=current_user.id
        ).first()
        if not account:
            return jsonify({"error": "Account not found"}), 404

        # Create transaction
        transaction = Transaction(
            account_id=data["account_id"],
            user_id=current_user.id,
            transaction_type=TransactionType(data["transaction_type"]),
            amount=data["amount"],
            currency=data.get("currency", "USD"),
            description=data.get("description"),
            reference_number=data.get("reference_number"),
            metadata=data.get("metadata"),
        )

        db.session.add(transaction)

        # Update account balance
        if transaction.transaction_type in [
            TransactionType.DEPOSIT,
            TransactionType.PAYMENT,
        ]:
            account.balance += transaction.amount
        else:
            account.balance -= transaction.amount

        db.session.commit()

        logger.info(f"Transaction created: {transaction.id}")
        return (
            jsonify(
                {
                    "success": True,
                    "data": transaction.to_dict(),
                    "message": "Transaction created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating transaction: {e}")
        return jsonify({"error": "Failed to create transaction"}), 500


# Budget endpoints
@api_bp.route("/budgets", methods=["GET"])
@login_required
def get_budgets():
    """Get budgets for the current user."""
    try:
        if current_user.role in [
            UserRole.ADMIN,
            UserRole.TREASURER,
            UserRole.ACCOUNTANT,
        ]:
            budgets = Budget.query.filter_by(is_active=True).all()
        else:
            budgets = Budget.query.filter_by(
                department=current_user.department, is_active=True
            ).all()

        return jsonify(
            {
                "success": True,
                "data": [budget.to_dict() for budget in budgets],
                "count": len(budgets),
            }
        )
    except Exception as e:
        logger.error(f"Error fetching budgets: {e}")
        return jsonify({"error": "Failed to fetch budgets"}), 500


@api_bp.route("/budgets", methods=["POST"])
@login_required
def create_budget():
    """Create a new budget."""
    try:
        # Check permissions
        if current_user.role not in [
            UserRole.ADMIN,
            UserRole.TREASURER,
            UserRole.ACCOUNTANT,
        ]:
            return jsonify({"error": "Insufficient permissions"}), 403

        data = request.get_json()

        # Validate required fields
        required_fields = ["name", "fiscal_year", "total_budget"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Create budget
        budget = Budget(
            name=data["name"],
            description=data.get("description"),
            fiscal_year=data["fiscal_year"],
            department=data.get("department", current_user.department),
            total_budget=data["total_budget"],
            currency=data.get("currency", "USD"),
            created_by=current_user.id,
        )

        db.session.add(budget)
        db.session.commit()

        logger.info(f"Budget created: {budget.id}")
        return (
            jsonify(
                {
                    "success": True,
                    "data": budget.to_dict(),
                    "message": "Budget created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating budget: {e}")
        return jsonify({"error": "Failed to create budget"}), 500


# Dashboard statistics
@api_bp.route("/dashboard/stats", methods=["GET"])
@login_required
def get_dashboard_stats():
    """Get dashboard statistics for the current user."""
    try:
        # Get account statistics
        accounts = Account.query.filter_by(
            user_id=current_user.id, is_active=True
        ).all()
        total_balance = sum(float(account.balance) for account in accounts)

        # Get transaction statistics
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)

        monthly_transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.created_at >= month_start,
        ).all()

        monthly_income = sum(
            float(t.amount)
            for t in monthly_transactions
            if t.transaction_type in [TransactionType.DEPOSIT, TransactionType.PAYMENT]
        )

        monthly_expenses = sum(
            float(t.amount)
            for t in monthly_transactions
            if t.transaction_type
            in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT]
        )

        return jsonify(
            {
                "success": True,
                "data": {
                    "total_balance": total_balance,
                    "account_count": len(accounts),
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "monthly_net": monthly_income - monthly_expenses,
                    "transaction_count": len(monthly_transactions),
                },
            }
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return jsonify({"error": "Failed to fetch dashboard statistics"}), 500


# Health check
@api_bp.route("/health", methods=["GET"])
def health_check():
    """API health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }
    )

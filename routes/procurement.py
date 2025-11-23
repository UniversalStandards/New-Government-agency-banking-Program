"""
Procurement and Purchasing routes for GOFAP.
"""

from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from models import (
    Department,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderStatus,
    Requisition,
    UserRole,
    Vendor,
    VendorStatus,
    db,
)

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")

@procurement_bp.route("/")
@login_required
def index():
    """Procurement dashboard."""
    try:
        return render_template("procurement/dashboard.html")
    except:
        return jsonify({"message": "Procurement Management Dashboard"})

@procurement_bp.route("/vendors")
@login_required
def vendors():
    """Vendor management page."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.TREASURER,
        UserRole.ACCOUNTANT,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        return render_template("procurement/vendors.html")
    except:
        return jsonify({"message": "Vendor Management"})

@procurement_bp.route("/api/vendors", methods=["GET"])
@login_required
def get_vendors():
    """Get list of vendors."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.TREASURER,
        UserRole.ACCOUNTANT,
        UserRole.DEPARTMENT_HEAD,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    vendors = Vendor.query.filter_by(is_active=True).all()
    return jsonify([v.to_dict() for v in vendors])

@procurement_bp.route("/api/vendors", methods=["POST"])
@login_required
def create_vendor():
    """Create a new vendor."""
    if current_user.role not in [UserRole.ADMIN, UserRole.TREASURER]:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    try:
        vendor = Vendor(
            name=data["name"],
            vendor_code=data["vendor_code"],
            contact_name=data.get("contact_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            tax_id=data.get("tax_id"),
            payment_terms=data.get("payment_terms"),
            rating=data.get("rating"),
        )

        db.session.add(vendor)
        db.session.commit()

        return jsonify({"success": True, "vendor": vendor.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@procurement_bp.route("/api/vendors/<vendor_id>", methods=["PUT"])
@login_required
def update_vendor(vendor_id):
    """Update a vendor."""
    if current_user.role not in [UserRole.ADMIN, UserRole.TREASURER]:
        return jsonify({"error": "Unauthorized"}), 403

    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404

    data = request.get_json()

    try:
        if "name" in data:
            vendor.name = data["name"]
        if "contact_name" in data:
            vendor.contact_name = data["contact_name"]
        if "email" in data:
            vendor.email = data["email"]
        if "phone" in data:
            vendor.phone = data["phone"]
        if "address" in data:
            vendor.address = data["address"]
        if "tax_id" in data:
            vendor.tax_id = data["tax_id"]
        if "status" in data:
            vendor.status = VendorStatus(data["status"])
        if "payment_terms" in data:
            vendor.payment_terms = data["payment_terms"]
        if "rating" in data:
            vendor.rating = data["rating"]

        db.session.commit()

        return jsonify({"success": True, "vendor": vendor.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@procurement_bp.route("/requisitions")
@login_required
def requisitions():
    """Requisition management page."""
    try:
        return render_template("procurement/requisitions.html")
    except:
        return jsonify({"message": "Purchase Requisitions"})

@procurement_bp.route("/api/requisitions", methods=["GET"])
@login_required
def get_requisitions():
    """Get purchase requisitions."""
    if current_user.role in [UserRole.ADMIN, UserRole.TREASURER, UserRole.ACCOUNTANT]:
        # Admins and finance staff see all requisitions
        requisitions = Requisition.query.order_by(Requisition.created_at.desc()).all()
    else:
        # Regular users see their own requisitions
        requisitions = (
            Requisition.query.filter_by(requester_id=current_user.id)
            .order_by(Requisition.created_at.desc())
            .all()
        )

    return jsonify([r.to_dict() for r in requisitions])

@procurement_bp.route("/api/requisitions", methods=["POST"])
@login_required
def create_requisition():
    """Create a new purchase requisition."""
    data = request.get_json()

    try:
        # Generate requisition number
        import uuid

        req_number = f"REQ-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        requisition = Requisition(
            requisition_number=req_number,
            requester_id=current_user.id,
            department_id=data.get("department_id"),
            title=data["title"],
            description=data.get("description"),
            estimated_cost=data.get("estimated_cost"),
            justification=data.get("justification"),
        )

        db.session.add(requisition)
        db.session.commit()

        return jsonify({"success": True, "requisition": requisition.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@procurement_bp.route("/api/requisitions/<req_id>/approve", methods=["POST"])
@login_required
def approve_requisition(req_id):
    """Approve a requisition."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.TREASURER,
        UserRole.DEPARTMENT_HEAD,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    requisition = Requisition.query.get(req_id)
    if not requisition:
        return jsonify({"error": "Requisition not found"}), 404

    try:
        requisition.status = PurchaseOrderStatus.APPROVED
        requisition.approved_by = current_user.id
        requisition.approval_date = datetime.utcnow()

        db.session.commit()

        return jsonify({"success": True, "requisition": requisition.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@procurement_bp.route("/purchase-orders")
@login_required
def purchase_orders():
    """Purchase order management page."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.TREASURER,
        UserRole.ACCOUNTANT,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        return render_template("procurement/purchase_orders.html")
    except:
        return jsonify({"message": "Purchase Orders"})

@procurement_bp.route("/api/purchase-orders", methods=["GET"])
@login_required
def get_purchase_orders():
    """Get purchase orders."""
    if current_user.role in [UserRole.ADMIN, UserRole.TREASURER, UserRole.ACCOUNTANT]:
        # Admins and finance staff see all POs
        purchase_orders = PurchaseOrder.query.order_by(
            PurchaseOrder.created_at.desc()
        ).all()
    else:
        # Department heads see POs for their department
        dept = Department.query.filter_by(name=current_user.department).first()
        if dept:
            purchase_orders = (
                PurchaseOrder.query.filter_by(department_id=dept.id)
                .order_by(PurchaseOrder.created_at.desc())
                .all()
            )
        else:
            purchase_orders = []

    return jsonify([po.to_dict() for po in purchase_orders])

@procurement_bp.route("/api/purchase-orders", methods=["POST"])
@login_required
def create_purchase_order():
    """Create a new purchase order."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.TREASURER,
        UserRole.ACCOUNTANT,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    try:
        # Generate PO number
        import uuid

        po_number = (
            f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        )

        purchase_order = PurchaseOrder(
            po_number=po_number,
            vendor_id=data["vendor_id"],
            department_id=data.get("department_id"),
            requester_id=data.get("requester_id", current_user.id),
            order_date=datetime.strptime(data["order_date"], "%Y-%m-%d").date(),
            expected_delivery_date=(
                datetime.strptime(data["expected_delivery_date"], "%Y-%m-%d").date()
                if data.get("expected_delivery_date")
                else None
            ),
            total_amount=data["total_amount"],
            tax_amount=data.get("tax_amount", 0),
            shipping_cost=data.get("shipping_cost", 0),
            currency=data.get("currency", "USD"),
            notes=data.get("notes"),
            budget_id=data.get("budget_id"),
        )

        db.session.add(purchase_order)
        db.session.flush()  # Get the PO ID

        # Add line items
        if "items" in data:
            for idx, item_data in enumerate(data["items"], start=1):
                item = PurchaseOrderItem(
                    purchase_order_id=purchase_order.id,
                    item_number=idx,
                    description=item_data["description"],
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                    total_price=item_data["quantity"] * item_data["unit_price"],
                    unit_of_measure=item_data.get("unit_of_measure"),
                )
                db.session.add(item)

        db.session.commit()

        return (
            jsonify({"success": True, "purchase_order": purchase_order.to_dict()}),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@procurement_bp.route("/api/purchase-orders/<po_id>", methods=["GET"])
@login_required
def get_purchase_order(po_id):
    """Get a specific purchase order."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.TREASURER,
        UserRole.ACCOUNTANT,
        UserRole.DEPARTMENT_HEAD,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    po = PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify({"error": "Purchase order not found"}), 404

    po_dict = po.to_dict()
    po_dict["items"] = [item.to_dict() for item in po.items]

    return jsonify(po_dict)

@procurement_bp.route("/api/purchase-orders/<po_id>/status", methods=["PUT"])
@login_required
def update_po_status(po_id):
    """Update purchase order status."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.TREASURER,
        UserRole.ACCOUNTANT,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    po = PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify({"error": "Purchase order not found"}), 404

    data = request.get_json()

    try:
        po.status = PurchaseOrderStatus(data["status"])

        if data["status"] == "approved":
            po.approver_id = current_user.id
        elif data["status"] == "received" and data.get("actual_delivery_date"):
            po.actual_delivery_date = datetime.strptime(
                data["actual_delivery_date"], "%Y-%m-%d"
            ).date()

        db.session.commit()

        return jsonify({"success": True, "purchase_order": po.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@procurement_bp.route("/api/purchase-orders/<po_id>/receive", methods=["POST"])
@login_required
def receive_po_items(po_id):
    """Receive items from a purchase order."""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.TREASURER,
        UserRole.ACCOUNTANT,
    ]:
        return jsonify({"error": "Unauthorized"}), 403

    po = PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify({"error": "Purchase order not found"}), 404

    data = request.get_json()

    try:
        # Update received quantities for items
        for item_data in data.get("items", []):
            item = PurchaseOrderItem.query.get(item_data["id"])
            if item and item.purchase_order_id == po_id:
                item.received_quantity = item_data["received_quantity"]

        # Check if all items are received
        all_received = all(item.received_quantity >= item.quantity for item in po.items)

        if all_received:
            po.status = PurchaseOrderStatus.RECEIVED
            po.actual_delivery_date = datetime.utcnow().date()

        db.session.commit()

        return jsonify({"success": True, "purchase_order": po.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

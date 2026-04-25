from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Item

inventory_bp = Blueprint('inventory', __name__)

# ---------------- CREATE ITEM ----------------
@inventory_bp.route('/items', methods=['POST'])
@login_required
def add_item():
    data = request.json

    item = Item(
        name=data['name'],
        quantity=int(data['quantity']),
        price=float(data['price']),
        expiry_date=data.get('expiry_date'),
        user_id=current_user.id   # 🔥 FIXED (VERY IMPORTANT)
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


# ---------------- GET ITEMS ----------------
@inventory_bp.route('/items', methods=['GET'])
@login_required
def get_items():
    items = Item.query.filter_by(user_id=current_user.id).all()  # 🔥 FIXED

    return jsonify([item.to_dict() for item in items])


# ---------------- UPDATE ITEM ----------------
@inventory_bp.route('/items/<int:id>', methods=['PUT'])
@login_required
def update_item(id):
    item = Item.query.get_or_404(id)

    if item.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json

    item.name = data.get('name', item.name)
    item.quantity = data.get('quantity', item.quantity)
    item.price = data.get('price', item.price)
    item.expiry_date = data.get('expiry_date', item.expiry_date)

    db.session.commit()

    return jsonify(item.to_dict())


# ---------------- DELETE ITEM ----------------
@inventory_bp.route('/items/<int:id>', methods=['DELETE'])
@login_required
def delete_item(id):
    item = Item.query.get_or_404(id)

    if item.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Item deleted"})
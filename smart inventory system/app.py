from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'secret123'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- MODELS ----------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    expiry_date = db.Column(db.String(20))
    user_id = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "expiry_date": self.expiry_date,
            "low_stock": self.quantity <= 5
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- AUTH ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        user = User.query.filter_by(username=data["username"]).first()

        if user and user.password == data["password"]:
            login_user(user)
            return redirect("/")
        return "Invalid login"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        user = User(username=data["username"], password=data["password"])
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

# ---------------- FRONTEND ----------------

@app.route("/")
@login_required
def home():
    return render_template("index.html")

# ---------------- API ----------------

@app.route("/items", methods=["GET"])
@login_required
def get_items():
    items = Item.query.filter_by(user_id=current_user.id).all()
    return jsonify([i.to_dict() for i in items])


@app.route("/items", methods=["POST"])
@login_required
def add_item():
    data = request.json

    if not data:
        return {"error": "No data received"}, 400

    item = Item(
        name=data["name"],
        quantity=int(data["quantity"]),
        price=float(data["price"]),
        expiry_date=data.get("expiry_date"),
        user_id=current_user.id  
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict())


@app.route("/items/<int:id>", methods=["DELETE"])
@login_required
def delete_item(id):
    item = Item.query.get(id)

    if not item or item.user_id != current_user.id:
        return {"error": "Not allowed"}, 403

    db.session.delete(item)
    db.session.commit()
    return {"message": "deleted"}


# ---------------- RUN ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
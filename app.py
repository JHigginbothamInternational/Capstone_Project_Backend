from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://xwnaiaitppoyqu:0e42ecc55dfc84506f8528848093341064f9c140c5ec31d04777fbf6e791f27c@ec2-44-193-188-118.compute-1.amazonaws.com:5432/d9jc3e3itgov4d"

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password") #TODO Remove sensitive fields

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

@app.route("/user/add", methods=["POST"])
def add_user():
    print("This is working", request.content_type)
    if request.content_type != "application/json;charset=UTF-8":
        return jsonify("ERROR: Data must be sent as JSON")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    print(post_data, username, password)
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    record_check = db.session.query(User).filter(User.username == username).first()
    if record_check is not None:
        return jsonify("Error: Name's taken")

    record = User(username, hashed_password)
    db.session.add(record)
    db.session.commit()
    
    return jsonify("Account added")
    return jsonify(user_schema.dump(record))

@app.route("/user/get", methods=["GET"])
def get_all_users():
    records = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(records))

@app.route("/user/login", methods=["POST"])
def login():
    if request.content_type != "application/json;charset=UTF-8":
        print("test2")
        return jsonify("ERROR: Data must be sent as JSON")
    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    record = db.session.query(User).filter(User.username == username).first()
    if record is None:
        return jsonify("Login failed")

    if not bcrypt.check_password_hash(record.password, password):
        return jsonify("Login failed")

    return jsonify("Login success")


if __name__ == "__main__":
    app.run(debug=True)
from flask import Blueprint, jsonify, request
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

# we could expand on the errors later
@users_api_blueprint.route('/', methods=['POST'])
def create():
    data = request.json
    user = User(username=data.get("username"), email=data.get("email"), password=data.get("password"))
    create = user.save()
    if create:
        # Successful save
        token = create_access_token(identity=user.id)
        return jsonify({
            "token": token,
            "message": "Successfully created a user and signed in.",
            "status": "success",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        })
    else:
        return jsonify({"Error": "Invalid credentials"})


# get all users
# maybe include "profileImage"
@users_api_blueprint.route('/', methods=['GET'])
def index():
    users = User.select()
    return jsonify([{"id": user.id, "email": user.email, "username": user.username} for user in users])

# retrieve information of currently LOGGED-IN user
# please include profile_picture
@users_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    user_id = get_jwt_identity()
    # what the line below means
    user = User.get_or_none(User.id == user_id)
    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })
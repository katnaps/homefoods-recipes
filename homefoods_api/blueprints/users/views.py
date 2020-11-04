from flask import Blueprint, jsonify, request
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

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
            "id": user.id,
            "username": user.username
        })
    else:
        return jsonify({"Error": "Invalid credentials"})


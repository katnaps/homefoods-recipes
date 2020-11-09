from flask import Blueprint, jsonify, request
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from app import app

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/', methods=['POST'])
def create():
    data = request.json
    user = User(username=data.get("username"), email=data.get("email"), password=data.get("password"))
    # Set default user profile image
    user.image_path = "profile_img.png"
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
                "email": user.email,
                "image_path": user.image_path
            }
        })
    else:
        return jsonify({"status": "failed", "message": user.errors})



# get all users
# include "profileImage"
@users_api_blueprint.route('/', methods=['GET'])
def index():
    users = User.select()
    return jsonify([{
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "image_path": app.config.get("AWS_S3_DOMAIN") + user.image_path
        } for user in users])

# get information from specific user id
#  please include profileImage
@users_api_blueprint.route('/<id>', methods=['GET'])
def find(id):
    user = User.get_or_none(User.id == id)
    if user:
        return jsonify({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "image_path": app.config.get("AWS_S3_DOMAIN") + user.image_path
        })
    else:
        return jsonify({
            "message": "User does not exist",
            "status": "failed"
        })

# retrieve information of currently LOGGED-IN user
# include profile_picture
@users_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    user_id = get_jwt_identity()
    user = User.get_or_none(User.id == user_id)
    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "image_path": app.config.get("AWS_S3_DOMAIN") + user.image_path
        })

@users_api_blueprint.route('/<id>', methods=['POST'])
@jwt_required
def update(id):
    user_id = get_jwt_identity()
    user = User.get_or_none(User.id == user_id)
    if user:
        data = request.json
    
        hash_password = user.password_hash
        result = check_password_hash(hash_password, data.get('old_password'))
        print(result)
        # login user if password correct
        if result:
            user.username = data.get("username")
            user.email = data.get("email")

            if data.get("password") != "":
                user.password = data.get("password")

            if user.save():
                # weird i can use both token
                token = create_access_token(identity=user.id)
                return jsonify({
                    "username": user.username,
                    "email": user.email,
                    "token": token
                })
            else:
                return jsonify({
                "message": user.errors
                })    
        else:
            return jsonify({
                "Error": "Wrong password"
            })    
    return jsonify({
        "Error": "Invalid credentials"
    })





from flask import Blueprint, jsonify, request
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers import upload_to_s3

images_api_blueprint = Blueprint('images_api',
                             __name__,
                             template_folder='templates')

@images_api_blueprint.route("/", methods=["POST"])
@jwt_required
def create():
    from app import app
    user_id = get_jwt_identity()
    user = User.get_or_none(User.id == user_id)
    if user:
        if 'image' not in request.files:
            return jsonify({
            "message": "No image provided",
            "status": "failed"
            })
        file = request.files['image']

        if file.filename == '':
            return jsonify({"Error": "No File selected"})

        if file and allowed_file(file.filename):
            file_path = upload_to_s3(file, user_id)
            user.image_path = file_path
            if user.save():
                return jsonify({
                    "image_path": app.config.get("AWS_S3_DOMAIN") + user.image_path,
                    "success": "image uploaded"
                })
            else:
                print(user.errors)
                return jsonify({"Error": "Failed to upload image"})

    

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
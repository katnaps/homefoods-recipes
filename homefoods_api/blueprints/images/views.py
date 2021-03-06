from flask import Blueprint, jsonify, request
from models.user import User
from models.image import Image

from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers import upload_to_s3
from app import app

images_api_blueprint = Blueprint('images_api',
                             __name__,
                             template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# upload profile image
@images_api_blueprint.route("/", methods=["POST"])
@jwt_required
def create():
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
        else:
            return jsonify({
                "message": "Not supported file format or file doesn't exist"
            })

# post user images
@images_api_blueprint.route("/new", methods=["POST"])
@jwt_required
def post():
    user_id = get_jwt_identity()
    user = User.get_or_none(User.id == user_id)
    if "image" not in request.files:
        return jsonify({
                    "message": "No image provided",
                    "status": "failed"
                    })
    file = request.files["image"]

    if file.filename == "":
        return jsonify({"message":"Please select a file"})

    if file and allowed_file(file.filename):
        file_path = upload_to_s3(file, user_id)

        new_image = Image(image_url=file_path, user=user_id)

        if new_image.save():
            return jsonify({
                "image_path": app.config.get("AWS_S3_DOMAIN") + file_path,
                "success": "image uploaded"
            })
        else:
            return jsonify({"Error": "Failed to save"})  
    else:
        return jsonify({
                "message": "Not supported file format or file doesn't exist"
            })

# retrieve user images
@images_api_blueprint.route("/<id>", methods=["GET"])
def retrieve(id):
    user = User.get_or_none(User.id==id)
    images = Image.select().where(Image.user==user)
    return jsonify([{
        "id": image.id,
        "url": app.config.get("AWS_S3_DOMAIN") + image.image_url
        } for image in images])

# same as above, but lists all the urls instead (different format)
# requires token
@images_api_blueprint.route("/me", methods=["GET"])
@jwt_required
def answer():
    user_id = get_jwt_identity()
    user = User.get_or_none(User.id == user_id)
    if user:
        images = Image.select().where(Image.user==user)
        return jsonify([ app.config.get("AWS_S3_DOMAIN") + image.image_url for image in images])
    else:
        return jsonify({
                "message": "Authentication failed",
                "status": "failed"
                })

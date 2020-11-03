from flask import Blueprint
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity


users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/', methods=['GET'])
def index():
    users = User.select()
    return jsonify([{"id": user.id, "email": user.email} for user in users])

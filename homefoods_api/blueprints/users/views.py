from flask import Blueprint
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity


users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/', methods=['GET'])
def index():
    return "USERS API"

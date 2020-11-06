from models.user import User
from flask import Blueprint, jsonify, request, url_for
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from helpers import oauth

login_api_blueprint = Blueprint('login_api',
                             __name__,
                             template_folder='templates')

# do include profile_picture
@login_api_blueprint.route('/', methods=['POST'])
def login():
    data = request.json
    # retrieve the user that want to sign in from database
    user = User.get_or_none(username=data.get('username'))
    if user:
        # check password
        hash_password = user.password_hash
        result = check_password_hash(hash_password, data.get('password'))
        # login user if password correct
        if result:
            # session["user_id"] = user.id
            token = create_access_token(identity=user.id)
            return jsonify({"token": token,
            "message": "Successfully signed in.",
            "status": "success",
            "users": {
                "id":user.id,
                "username":user.username
            }
            })
    return jsonify({
    "message": "Some error occurred. Please try again.",
    "status": "fail"
    })

# google OAuth2
@login_api_blueprint.route("/google_login", methods=['GET'])
def google_login():
    redirect_uri = url_for('login_api.authorize', _external = True)
    return oauth.google.authorize_redirect(redirect_uri)

@login_api_blueprint.route("/authorize/google", methods=['GET'])
def authorize():
    oauth.google.authorize_access_token()
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    user = User.get_or_none(User.email == email)
    if user:
        token = create_access_token(identity=user.id)
        return jsonify({"token": token,
        "message": "Successfully signed in.",
        "status": "success",
        "users": {
            "id":user.id,
            "username":user.username
        }
        })
    else:
        return jsonify({
        "message": "Some error occurred. Please try again.",
        "status": "fail"
        })
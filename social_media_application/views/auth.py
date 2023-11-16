from flask import request, jsonify, make_response
from flask import current_app as app

from social_media_application.models import (
    db,
    User,
    Profile,
    BlacklistToken,
)
from social_media_application.serializers import user_schema
from social_media_application.helpers.permissions import authenticate_user


@app.route("/register", methods=["POST"])
def new_user():
    """
    Register new user, from username and password that comes from body json
    Returns json where noticed details about this user that was registered(user_schema)
    :param username: str
    :param password:  str
    :return: json
    """
    try:
        username = request.json["username"]
        password = request.json["password"]
        email = request.json["email"]
        first_name = request.json["first_name"]
        last_name = request.json["last_name"]
        bio = request.json["bio"]
        profile_pic = request.json["profile_pic"]
        if username and password:
            if User.query.filter_by(username=username).first():
                response_object = {"error": "User Already exists!"}
                return make_response(jsonify(response_object)), 400

            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            profile = Profile(
                user=user.id,
                first_name=first_name,
                last_name=last_name,
                bio=bio,
                profile_pic=profile_pic,
            )
            db.session.add(profile)
            db.session.commit()
            data_dict = user_schema.dump(user)
            response_object = data_dict
            return make_response(jsonify(response_object)), 201
        response_object = {"error": "Invalid credentials"}
        return make_response(jsonify(response_object)), 400
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/login", methods=["Post"])
def login():
    """
    Returns json in which is token based on expired-time PyJWT
    :return: json
    """

    try:
        post_data = request.get_json()
        # fetch the user data
        user = User.query.filter_by(username=post_data.get("username")).first()
        if (
            user
            and user.verify_password(post_data.get("password"))
            and (not user.archive)
        ):
            auth_token = user.generate_auth_token()
        else:
            response_object = {"error": "incorrect credentials"}
            return make_response(jsonify(response_object)), 400
        if auth_token:
            response_object = {
                "token": auth_token,
            }
            return make_response(jsonify(response_object)), 200
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/logout", methods=["Post"])
@authenticate_user
def logout(**kwargs):
    """
    Makes logout from current account,
    :return: response
    """
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = None
        if auth_token:
            resp = User.verify_auth_token(auth_token)
            if User.query.filter_by(username=resp).first():
                blacklist_token = BlacklistToken(token=auth_token)
                db.session.add(blacklist_token)
                db.session.commit()
                response_object = {}
                return make_response(jsonify(response_object)), 205
            else:
                response_object = {"error": "user not found"}
                return make_response(jsonify(response_object)), 400
        else:
            response_object = {"error": "Unauthenticated"}
            return make_response(jsonify(response_object)), 401
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400

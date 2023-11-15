from flask import request, jsonify, make_response
from flask import current_app as app
from sqlalchemy import or_
from ..models import (
    db,
    User,
    user_schema,
    users_schema,
    Profile,
    BlacklistToken,
    Post,
    Follow,
)
from .permissions import authenticate_user, is_owner


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
                responseObject = {"status": "fail", "message": "User Already exists!"}
                return make_response(jsonify(responseObject)), 400

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
            responseObject = {"status": "Success", "message": data_dict}
            return make_response(jsonify(responseObject)), 201
        responseObject = {"status": "Fail", "message": "Invalid credentials"}
        return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/login", methods=["Post"])
def login():
    """
    Returns json in which is token based on expired-time PyJWT
    :return: json
    """

    post_data = request.get_json()
    try:
        # fetch the user data
        user = User.query.filter_by(username=post_data.get("username")).first()
        if (
            user
            and user.verify_password(post_data.get("password"))
            and (not user.archive)
        ):
            auth_token = user.generate_auth_token()
        else:
            responseObject = {"status": "fail", "message": "incorrect credentials"}
            return make_response(jsonify(responseObject)), 400
        if auth_token:
            responseObject = {
                "status": "success",
                "message": "Successfully logged in.",
                "token": auth_token,
            }
            return make_response(jsonify(responseObject)), 200
    except Exception as e:
        responseObject = {"status": "fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


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
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    "status": "success",
                    "message": "Successfully logged out.",
                }
                return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {"status": "fail", "message": "invalid user"}
                return make_response(jsonify(responseObject)), 400
        else:
            responseObject = {"status": "fail", "message": "Unauthenticated"}
            return make_response(jsonify(responseObject)), 401
    except Exception as e:
        responseObject = {"status": "fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/users", methods=["GET"])
@authenticate_user
def get_all_users(**kwargs):
    """
    Returns json where noticed details about all users (users_schema)
    :return: json
    """
    responseObject = {
        "status": "Success",
        "message": users_schema.dump(User.query.filter_by(archive=False)),
    }
    return make_response(jsonify(responseObject)), 200


@app.route("/users/<username>", methods=["GET"])
@authenticate_user
def get_user(username, **kwargs):
    """
    Returns json where noticed details about this user (user_schema)
    :param username: str
    :return:  json
    """
    try:
        user = User.query.filter_by(username=username).first()
        if user:
            responseObject = {"status": "Success", "message": user_schema.dump(user)}
            return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {
                "status": "fail",
                "message": "user not found",
            }
        return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {
            "status": "fail",
            "message": str(e),
        }
        return make_response(jsonify(responseObject)), 400


@app.route("/users/<id>", methods=["PUT", "PATCH"])
@is_owner
def update_user(id):
    post_data = request.get_json()
    try:
        # fetch the user data
        user = User.query.filter_by(id=id).first()
        profile = Profile.query.filter_by(user=id).first()
        for k, v in post_data.items():
            if k in user_schema.fields.keys():
                setattr(user, k, v)
            else:
                setattr(profile, k, v)
        db.session.commit()
        # data_dict = profile_schema.dump(profile)
        data_dict = user_schema.dump(user)
        responseObject = {
            "status": "successf",
            "message": "successfully updated details",
            "data": data_dict,
        }
        return make_response(jsonify(responseObject)), 200

    except Exception as e:
        responseObject = {"status": "fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/users/<id>", methods=["DELETE"])
@is_owner
@authenticate_user
def delete_user(id, **kwargs):
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = None
        if auth_token:
            blacklist_token = BlacklistToken(token=auth_token)
        # fetch the user data
        user = User.query.filter_by(id=id).first()
        profile = Profile.query.filter_by(user=id).first()
        posts = Post.query.filter_by(creator=user.id).all()
        for i in posts:
            setattr(i, "archive", True)
        connections = (
            db.session.execute(
                db.select(Follow)
                .where(Follow.accepted == True)
                .where(or_(Follow.user1 == user.id, Follow.user2 == user.id))
                .where(Follow.archive == False)
            )
            .scalars()
            .all()
        )
        for i in connections:
            setattr(i, "archive", True)
        setattr(user, "archive", True)
        setattr(profile, "archive", True)
        db.session.add(blacklist_token)
        db.session.commit()

        responseObject = {
            "status": "Success",
            "message": f"User {user.username} deleted successfully!!",
        }
        return make_response(jsonify(responseObject)), 204
    except Exception as e:
        responseObject = {"status": "fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400

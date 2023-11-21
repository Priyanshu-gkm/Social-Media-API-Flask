from flask import request, jsonify, make_response
from flask import current_app as app

from sqlalchemy import or_

from social_media_application.models import (
    db,
    User,
    Profile,
    BlacklistToken,
    Post,
    Connection,
)
from social_media_application.serializers import user_schema, users_schema
from social_media_application.helpers.permissions import authenticate_user, is_owner


@app.route("/users", methods=["GET"])
@authenticate_user
def get_all_users(**kwargs):
    """
    Returns json where noticed details about all users (users_schema)
    :return: json
    """
    response_object = users_schema.dump(User.query.filter_by(archive=False))
    return make_response(jsonify(response_object)), 200


@app.route("/users/<id>", methods=["GET"])
@authenticate_user
def get_user(id, **kwargs):
    """
    Returns json where noticed details about this user (user_schema)
    :param username: str
    :return:  json
    """
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            response_object = user_schema.dump(user)
            return make_response(jsonify(response_object)), 200
        else:
            response_object = {"error": "user not found"}
        return make_response(jsonify(response_object)), 400
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/users/<id>", methods=["PUT", "PATCH"])
@is_owner
def update_user(id):
    try:
        post_data = request.get_json()
        # fetch the user data
        user = User.query.filter_by(id=id).first()
        profile = Profile.query.filter_by(user=id).first()
        for k, v in post_data.items():
            if k in user_schema.fields.keys():
                setattr(user, k, v)
            else:
                setattr(profile, k, v)
        db.session.commit()
        data_dict = user_schema.dump(user)
        response_object = data_dict
        return make_response(jsonify(response_object)), 200

    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/users/<id>", methods=["DELETE"])
@authenticate_user
@is_owner
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
        posts = Post.query.filter_by(creator=id).all()
        for post in posts:
            setattr(post, "archive", True)
        connections = (
            db.session.execute(
                db.select(Connection)
                .where(Connection.accepted == True)
                .where(
                    or_(Connection.sender == user.id, Connection.receiver == user.id)
                )
                .where(Connection.archive == False)
            )
            .scalars()
            .all()
        )
        for connection in connections:
            setattr(connection, "archive", True)
        setattr(user, "archive", True)
        setattr(profile, "archive", True)
        db.session.add(blacklist_token)
        db.session.commit()

        response_object = {}
        return make_response(jsonify(response_object)), 204
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400

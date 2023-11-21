from flask import jsonify, make_response
from flask import current_app as app

from sqlalchemy import or_

from social_media_application.models import (
    db,
    User,
    Post,
    Connection,
)
from social_media_application.serializers import (
    posts_schema,
    connections_schema,
)
from social_media_application.helpers.permissions import authenticate_user


@app.route("/feed", methods=["GET"])
@authenticate_user
def get_user_feed(**kwargs):
    """
    Returns json where posts from Connectioning users are listed (posts_schema)
    :return: json
    """
    try:
        user = kwargs.get("current_user")
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
        connections = connections_schema.dump(connections)
        if len(connections) != 0:
            users = set()
            for connection in connections:
                users.add(connection["sender"])
                users.add(connection["receiver"])
            users.remove(user.username)
            creators = [
                User.query.filter_by(username=user).first().id for user in users
            ]
            response_object = posts_schema.dump(
                db.session.query(Post).filter(Post.creator.in_(creators)).all()
            )
        else:
            response_object = []
        return make_response(jsonify(response_object)), 200
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400

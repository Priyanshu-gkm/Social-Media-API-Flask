from flask import  jsonify, make_response
from flask import current_app as app
from ..models import (
    db,
    User,
    Post,
    Connection,
)
from ..serializers import (
    posts_schema,
    connections_schema,
)
from ..helpers.permissions import  authenticate_user
from sqlalchemy import or_

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
                .where(or_(Connection.sender == user.id, Connection.receiver == user.id))
                .where(Connection.archive == False)
            )
            .scalars()
            .all()
        )
        cons = connections_schema.dump(connections)
        users = set()
        for i in cons:
            for k, v in i.items():
                if k == "sender" or k == "receiver":
                    users.add(v)
        users.remove(user.username)
        creators = [User.query.filter_by(username=user).first().id for user in users]
        response_object = {
            "status": "Success",
            "message": posts_schema.dump(
                db.session.query(Post).filter(Post.creator.in_(creators)).all()
            ),
        }
        return make_response(jsonify(response_object)), 200
    except Exception as e:
        response_object = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(response_object)), 400

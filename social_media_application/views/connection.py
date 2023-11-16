from flask import jsonify, make_response
from flask import current_app as app

from sqlalchemy import or_

from social_media_application.models import db, Connection
from social_media_application.serializers import connections_schema
from social_media_application.helpers.permissions import authenticate_user


@app.route("/connections", methods=["GET"])
@authenticate_user
def get_connections(**kwargs):
    try:
        user = kwargs.get("current_user")
        if user:
            connections = (
                db.session.execute(
                    db.select(Connection)
                    .where(Connection.accepted == True)
                    .where(
                        or_(
                            Connection.sender == user.id, Connection.receiver == user.id
                        )
                    )
                    .where(Connection.archive == False)
                )
                .scalars()
                .all()
            )
            connections = connections_schema.dump(connections)
            for connection in connections:
                delete_key = ""
                rename_key = ""
                for k, v in connection.items():
                    if v == user.username:
                        delete_key = k
                    elif (
                        k.startswith("sender")
                        or k.startswith("receiver")
                        and v != user.username
                    ):
                        rename_key = k
                del connection[delete_key]
                connection["user"] = connection.pop(rename_key)
            response_object = connections
            return make_response(jsonify(response_object)), 200

        else:
            response_object = {"error": "user not found"}
            return make_response(jsonify(response_object)), 400
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/connections/<id>", methods=["DELETE"])
@authenticate_user
def unfollow(id, **kwargs):
    try:
        user = kwargs.get("current_user")
        connection = Connection.query.filter_by(id=id).first()
        if connection:
            if connection.sender == user.id or connection.receiver == user.id:
                Connection.query.filter_by(id=id).delete()
                db.session.commit()
                response_object = {}
                return make_response(jsonify(response_object)), 204
            else:
                response_object = {"error": "you are not authorised!"}
                return make_response(jsonify(response_object)), 403
        else:
            response_object = {"error": "no such connection exists!"}
            return make_response(jsonify(response_object)), 400
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400

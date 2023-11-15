from flask import  jsonify, make_response
from flask import current_app as app
from sqlalchemy import or_
from ..models import db, Connection
from ..serializers import connections_schema
from ..helpers.permissions import authenticate_user

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
                    .where(or_(Connection.sender == user.id, Connection.receiver == user.id))
                    .where(Connection.archive == False)
                )
                .scalars()
                .all()
            )
            cons = connections_schema.dump(connections)
            for i in cons:
                del_name = ""
                rename = ""
                for k, v in i.items():
                    if v == user.username:
                        del_name = k
                    elif (k.startswith("sender") or k.startswith("receiver") and v != user.username):
                        rename = k
                del i[del_name]
                i["user"] = i.pop(rename)
            response_object = {"status": "success", "message": cons}
            return make_response(jsonify(response_object)), 200

        else:
            response_object = {"status": "Fail", "message": "user not found"}
            return make_response(jsonify(response_object)), 400
    except Exception as e:
        response_object = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(response_object)), 400

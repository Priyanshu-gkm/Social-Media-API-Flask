from flask import request, jsonify, make_response
from flask import current_app as app

from social_media_application.models import db, User, Connection, Notification
from social_media_application.serializers import connections_schema, connection_schema
from social_media_application.helpers.permissions import authenticate_user


@app.route("/follow-requests", methods=["GET"])
@authenticate_user
def get_my_follow_requests(**kwargs):
    try:
        user = kwargs.get("current_user")
        follow_requests = Connection.query.filter_by(
            receiver=user.id, accepted=False
        ).all()

        if len(follow_requests) == 0:
            response_object = []
            return make_response(jsonify(response_object)), 200

        follow_requests = connections_schema.dump(follow_requests)
        for follow_request in follow_requests:
            follow_request.pop("receiver")
            follow_request["user"] = follow_request.pop("sender")
        response_object = follow_requests
        return make_response(jsonify(response_object)), 200
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/follow-requests", methods=["POST"])
@authenticate_user
def follow(**kwargs):
    try:
        sender = kwargs.get("current_user")
        req_data = request.get_json()
        user = req_data.get("user")
        receiver = User.query.filter_by(username=user, archive=False).first()
        if receiver:
            if user == sender.username:
                response_object = {"error": "You can't send follow request to yourself"}
                return make_response(jsonify(response_object)), 400
            elif (
                Connection.query.filter_by(
                    sender=sender.id, receiver=receiver.id
                ).first()
                or Connection.query.filter_by(
                    sender=receiver.id, receiver=sender.id
                ).first()
            ):
                response_object = {"error": "connection already exists"}
                return make_response(jsonify(response_object)), 400

            follow_request = Connection(sender=sender.id, receiver=receiver.id)
            db.session.add(follow_request)
            db.session.commit()
            notification_object = Notification(
                user=receiver.id,
                msg="You have a new follow request from {}".format(sender.username),
            )
            db.session.add(notification_object)
            db.session.commit()
            response_object = connection_schema.dump(follow_request)
            return make_response(jsonify(response_object)), 200
        else:
            response_object = {"error": "unknown username {}".format(user)}
            return make_response(jsonify(response_object)), 400
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/follow-requests/<id>", methods=["PATCH", "PUT"])
@authenticate_user
def respond_to_follow_request(id, **kwargs):
    try:
        user = kwargs.get("current_user")
        follow_request = Connection.query.filter_by(id=id).first()
        if follow_request.receiver == user.id:
            if follow_request.accepted == True:
                response_object = {
                    "error": "you cant do this, already accepted!",
                }
                return make_response(jsonify(response_object)), 400
            else:
                if request.get_json()["response"] == "accept":
                    setattr(follow_request, "accepted", True)
                    db.session.commit()
                    notification_object = Notification(
                        user=follow_request.sender,
                        msg="{} accepted your follow request ".format(user.username),
                    )
                    db.session.add(notification_object)
                    db.session.commit()
                    response_object = connection_schema.dump(follow_request)
                    return make_response(jsonify(response_object)), 200
                elif request.get_json()["response"] == "reject":
                    notification_object = Notification(
                        user=follow_request.sender,
                        msg="{} rejected your follow request ".format(user.username),
                    )
                    db.session.add(notification_object)
                    db.session.commit()
                    Connection.query.filter_by(id=id).delete()
                    db.session.commit()
                    response_object = {}
                    return make_response(jsonify(response_object)), 200
        else:
            response_object = {
                "error": "you are not authorised for this follow request!"
            }
            return make_response(jsonify(response_object)), 403
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400

from flask import request, jsonify, make_response
from flask import current_app as app
from sqlalchemy import or_
from ..models import db, User, Follow, follows_schema, Notification, follow_schema
from .permissions import authenticate_user


@app.route("/follow", methods=["GET"])
@authenticate_user
def get_my_follow_requests(**kwargs):
    try:
        user = kwargs.get("current_user")
        if user:
            follow_requests = Follow.query.filter_by(
                user2=user.id, accepted=False
            ).all()
            if len(follow_requests) == 0:
                responseObject = {
                    "status": "success",
                    "message": "no requests for {}".format(user.username),
                }
                return make_response(jsonify(responseObject)), 200
            requests = follows_schema.dump(follow_requests)
            for req in requests:
                req.pop("user2")
                req["user"] = req.pop("user1")
            responseObject = {"status": "success", "message": requests}
            return make_response(jsonify(responseObject)), 200

        else:
            responseObject = {"status": "Fail", "message": "user not found"}
            return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/follow", methods=["POST"])
@authenticate_user
def follow(**kwargs):
    try:
        user1 = kwargs.get("current_user")
        req_data = request.get_json()
        user = req_data.get("user")
        user2 = User.query.filter_by(username=user).first()
        if user2:
            if user == user1.username:
                responseObject = {
                    "status": "Fail",
                    "message": "You can't send follow request to yourself",
                }
                return make_response(jsonify(responseObject)), 400
            elif (
                Follow.query.filter_by(user1=user1.id, user2=user2.id).first()
                or Follow.query.filter_by(user1=user2.id, user2=user1.id).first()
            ):
                responseObject = {
                    "status": "Success",
                    "message": "connection already exists",
                }
                return make_response(jsonify(responseObject)), 200
            follow_request = Follow(user1=user1.id, user2=user2.id)
            db.session.add(follow_request)
            db.session.commit()
            notification_obj = Notification(
                user=user2.id,
                msg="You have a new follow request from {}".format(user1.username),
            )
            db.session.add(notification_obj)
            db.session.commit()
            responseObject = {
                "status": "Success",
                "message": "Follow request sent to {}".format(user),
                "data": follow_schema.dump(follow_request),
            }
            return make_response(jsonify(responseObject)), 201
        else:
            responseObject = {
                "status": "Fail",
                "message": "unknown username {}".format(user),
            }
            return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/follow/<id>", methods=["PATCH", "PUT"])
@authenticate_user
def respond_to_follow_request(id, **kwargs):
    try:
        user = kwargs.get("current_user")
        follow_request = Follow.query.filter_by(id=id).first()
        if follow_request.user2 == user.id:
            if follow_request.accepted == True:
                responseObject = {
                    "status": "Fail",
                    "message": "you cant do this, already accepted!",
                }
                return make_response(jsonify(responseObject)), 400
            else:
                if request.get_json()["response"] == "accept":
                    setattr(follow_request, "accepted", True)
                    db.session.commit()
                    notification_obj = Notification(
                        user=follow_request.user1,
                        msg="{} accepted your follow request ".format(user.username),
                    )
                    db.session.add(notification_obj)
                    db.session.commit()
                    responseObject = {"message": "request accepted successfully"}
                    return make_response(jsonify(responseObject)), 200
                elif request.get_json()["response"] == "reject":
                    user1 = follow_request.user1
                    notification_obj = Notification(
                        user=user1,
                        msg="{} rejected your follow request ".format(user.username),
                    )
                    db.session.add(notification_obj)
                    db.session.commit()
                    Follow.query.filter_by(id=id).delete()
                    db.session.commit()
                    responseObject = {"message": "request deleted successfully"}
                    return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {
                "status": "Fail",
                "message": "you are not authorised for this follow request!",
            }
            return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/follow/<id>", methods=["DELETE"])
@authenticate_user
def unfollow(id, **kwargs):
    try:
        user = kwargs.get("current_user")
        conection = Follow.query.filter_by(id=id).first()
        if conection:
            if conection.user1 == user.id or conection.user2 == user.id:
                Follow.query.filter_by(id=id).delete()
                db.session.commit()
                responseObject = {"status": "success", "message": "connection deleted"}
                return make_response(jsonify(responseObject)), 204
            else:
                responseObject = {
                    "status": "Fail",
                    "message": "you are not authorised!",
                }
                return make_response(jsonify(responseObject)), 403
        else:
            responseObject = {"status": "Fail", "message": "no such connection exists!"}
            return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/connections", methods=["GET"])
@authenticate_user
def get_connections(**kwargs):
    try:
        user = kwargs.get("current_user")
        if user:
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
            cons = follows_schema.dump(connections)
            for i in cons:
                del_name = ""
                rename = ""
                for k, v in i.items():
                    if v == user.username:
                        del_name = k
                    elif k.startswith("user"):
                        rename = k
                del i[del_name]
                i["user"] = i.pop(rename)
            responseObject = {"status": "success", "message": cons}
            return make_response(jsonify(responseObject)), 200

        else:
            responseObject = {"status": "Fail", "message": "user not found"}
            return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400

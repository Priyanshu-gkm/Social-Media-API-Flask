from flask import jsonify, make_response
from flask import current_app as app
from ..models import db, Notification
from ..serializers import notifications_schema
from ..helpers.permissions import authenticate_user


@app.route("/notifications", methods=["GET"])
@authenticate_user
def get_all_notifications(**kwargs):
    try:
        user = kwargs.get("current_user")
        if user:
            notifications = Notification.query.filter_by(user=user.id).all()
            notifications_object = notifications_schema.dump(notifications)
            responseObject = {"status": "success", "message": notifications_object}
            return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {"status": "Fail", "message": "no such user!"}
            return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/notifications/<id>", methods=["PUT", "PATCH"])
@authenticate_user
def mark_read_notification(id, **kwargs):
    try:
        user = kwargs.get("current_user")
        if user:
            notification = Notification.query.filter_by(id=id).first()
            if notification.user == user.id:
                setattr(notification, "read", True)
                db.session.commit()
                responseObject = {
                    "status": "success",
                    "message": "notification mark as read",
                }
                return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    "status": "Fail",
                    "message": "This notification does not belongs to you",
                }
                return make_response(jsonify(responseObject)), 400
        else:
            responseObject = {"status": "Fail", "message": "no such user!"}
            return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/notifications", methods=["PUT", "PATCH"])
@authenticate_user
def mark_all_notifications_as_read(**kwargs):
    try:
        user = kwargs.get("current_user")
        # print(user)
        if user:
            notifications = Notification.query.filter_by(user=user.id, read=False).all()
            for notification in notifications:
                if notification.user == user.id:
                    setattr(notification, "read", True)
                    db.session.commit()
            responseObject = {
                "status": "success",
                "message": "notifications marked as read",
            }
            return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {"status": "Fail", "message": "no such user!"}
            return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


# @app.route("/notifications/<id>", methods=["DELETE"])
# @authenticate_user
# def delete_read_notification(**kwargs):
#     try:
#         user = kwargs.get("current_user")
#         if user:
#             notification = Notification.query.filter_by(id=id)
#             if notification.user == user.id:
#                 notification.delete()
#                 db.session.commit()
#                 responseObject = {
#                     "status": "success",
#                     "message": "notification deleted!",
#                 }
#                 return make_response(jsonify(responseObject)), 204
#             else:
#                 responseObject = {
#                     "status": "Fail",
#                     "message": "This notification does not belongs to you",
#                 }
#                 return make_response(jsonify(responseObject)), 400
#         else:
#             responseObject = {"status": "Fail", "message": "no such user!"}
#             return make_response(jsonify(responseObject)), 400
#     except Exception as e:
#         responseObject = {"status": "Fail", "message": str(e)}
#         return make_response(jsonify(responseObject)), 400

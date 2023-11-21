from flask import jsonify, make_response
from flask import current_app as app

from social_media_application.models import db, Notification
from social_media_application.serializers import notifications_schema
from social_media_application.helpers.permissions import authenticate_user


@app.route("/notifications", methods=["GET"])
@authenticate_user
def get_all_notifications(**kwargs):
    try:
        user = kwargs.get("current_user")
        notifications = Notification.query.filter_by(user=user.id).all()
        notifications_object = notifications_schema.dump(notifications)
        response_object = notifications_object
        return make_response(jsonify(response_object)), 200
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/notifications/<id>", methods=["PUT", "PATCH"])
@authenticate_user
def mark_read_notification(id, **kwargs):
    try:
        user = kwargs.get("current_user")
        notification = Notification.query.filter_by(id=id).first()
        if notification.user == user.id:
            setattr(notification, "read", True)
            db.session.commit()
            response_object = {"message": "notification mark as read"}
            return make_response(jsonify(response_object)), 200
        else:
            response_object = {
                "error": "Unauthorized",
            }
            return make_response(jsonify(response_object)), 403
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/notifications", methods=["PUT", "PATCH"])
@authenticate_user
def mark_all_notifications_as_read(**kwargs):
    try:
        user = kwargs.get("current_user")
        notifications = Notification.query.filter_by(user=user.id, read=False).all()
        for notification in notifications:
            if notification.user == user.id:
                setattr(notification, "read", True)
                db.session.commit()
        response_object = {"message": "notifications marked as read"}
        return make_response(jsonify(response_object)), 200
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400

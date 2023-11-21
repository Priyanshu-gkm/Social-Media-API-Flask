from marshmallow import fields

from social_media_application import ma
from social_media_application.models import User


class NotificationSchema(ma.Schema):
    user = fields.Method("get_user")

    def get_user(self, obj):
        return User.query.filter_by(id=obj.user).first().username

    class Meta:
        fields = ["id", "user", "msg", "read", "published_at"]


notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)

from .. import db, ma
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime as dt
from application.models import User
from marshmallow import fields


class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )  # Private id
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    msg = db.Column(db.String(500))
    read = db.Column(db.Boolean, default=False, nullable=False)
    published_at = db.Column(db.DateTime, nullable=False, default=dt.now())

    def __init__(self, user, msg):
        self.user = user
        self.msg = msg
        self.read = False
        self.published_at = dt.now()


class NotificationSchema(ma.Schema):
    user = fields.Method("get_user")

    def get_user(self, obj):
        return User.query.filter_by(id=obj.user).first().username

    class Meta:
        fields = ["id", "user", "msg", "read", "published_at"]


notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)

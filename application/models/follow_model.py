from .. import db, ma
import uuid
from sqlalchemy.dialects.postgresql import UUID
from application.models import User
from marshmallow import fields


class Follow(db.Model):
    __tablename__ = "follow"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )  # Private id
    user1 = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    user2 = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    accepted = db.Column(db.Boolean, default=False, nullable=False)
    archive = archive = db.Column(db.Boolean, default=False)

    def __init__(self, user1, user2):
        self.user1 = user1
        self.user2 = user2
        self.accepted = False
        self.archive = False


class FollowSchema(ma.Schema):
    user2 = fields.Method("get_user2")
    user1 = fields.Method("get_user1")

    def get_user1(self, obj):
        return User.query.filter_by(id=obj.user1).first().username

    def get_user2(self, obj):
        return User.query.filter_by(id=obj.user2).first().username

    class Meta:
        fields = ("id", "user1", "user2", "accepted", "archive")


follow_schema = FollowSchema()
follows_schema = FollowSchema(many=True)

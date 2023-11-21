import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime as dt

from social_media_application import db


class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    msg = db.Column(db.String(500))
    read = db.Column(db.Boolean, default=False, nullable=False)
    published_at = db.Column(db.DateTime, nullable=False, default=dt.now())

    def __init__(self, user, msg):
        self.user = user
        self.msg = msg
        self.read = False
        self.published_at = dt.now()

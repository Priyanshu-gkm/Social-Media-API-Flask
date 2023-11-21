import uuid
from sqlalchemy.dialects.postgresql import UUID

from social_media_application import db


class Profile(db.Model):
    __tablename__ = "profile"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    bio = db.Column(db.String(255))
    profile_pic = db.Column(db.String(500), default=None)
    archive = db.Column(db.Boolean, default=False, nullable=False)

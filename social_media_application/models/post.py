import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime as dt

from social_media_application import db


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    creator = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    title = db.Column(db.String(50))
    url = db.Column(db.String(500), default=None)
    content = db.Column(db.Text)
    tags = db.Column(db.String(500))
    pub_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    post_type = db.Column(db.String(50), db.ForeignKey("posttype.name"))
    archive = db.Column(db.Boolean, default=False)

import uuid
from sqlalchemy.dialects.postgresql import UUID

from social_media_application import db


class PostType(db.Model):
    __tablename__ = "posttype"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.String(50), unique=True)

    def __str__(self) -> str:
        return str(self.name)

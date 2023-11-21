from sqlalchemy.dialects.postgresql import UUID
import uuid

from social_media_application import db


class Connection(db.Model):
    __tablename__ = "connection"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    sender = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    receiver = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    accepted = db.Column(db.Boolean, default=False, nullable=False)
    archive = archive = db.Column(db.Boolean, default=False)

    def __init__(self, sender, receiver, accepted=False):
        self.sender = sender
        self.receiver = receiver
        self.accepted = accepted
        self.archive = False

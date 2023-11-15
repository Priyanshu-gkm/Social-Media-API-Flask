from SocialMediaApplication.models import User
from marshmallow import fields
from .. import  ma

class ConnectionSchema(ma.Schema):
    sender = fields.Method("get_sender")
    receiver = fields.Method("get_receiver")

    def get_sender(self, obj):
        return User.query.filter_by(id=obj.sender).first().username

    def get_receiver(self, obj):
        return User.query.filter_by(id=obj.receiver).first().username

    class Meta:
        fields = ("id", "sender", "receiver", "accepted", "archive")


connection_schema = ConnectionSchema()
connections_schema = ConnectionSchema(many=True)
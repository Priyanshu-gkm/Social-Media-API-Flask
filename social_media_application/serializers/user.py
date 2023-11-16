from marshmallow import fields
from .. import ma
from ..serializers import profile_schema
from ..models import Profile

class UserSchema(ma.Schema):
    profile = fields.Method("get_profile")

    def get_profile(self, obj):
        return profile_schema.dump(Profile.query.filter_by(user=obj.id).first())

    class Meta:
        fields = ("id", "username", "email", "profile")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
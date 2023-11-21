from social_media_application import ma


class ProfileSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "bio", "profile_pic")


profile_schema = ProfileSchema()
profiles_schema = ProfileSchema(many=True)

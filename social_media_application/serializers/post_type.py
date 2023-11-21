from social_media_application import ma


class PostTypeSchema(ma.Schema):
    class Meta:
        fields = ("name",)


post_type_schema = PostTypeSchema()
post_types_schema = PostTypeSchema(many=True)

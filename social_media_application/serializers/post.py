from social_media_application import ma


class PostSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "title",
            "url",
            "content",
            "pub_date",
            "creator",
            "post_type",
            "archive",
            "tags",
        )


post_schema = PostSchema()
posts_schema = PostSchema(many=True)

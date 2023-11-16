from .. import ma

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
        )


post_schema = PostSchema()
posts_schema = PostSchema(many=True)
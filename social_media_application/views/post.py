from flask import request, jsonify, make_response
from flask import current_app as app

from social_media_application.models import (
    db,
    Post,
)
from social_media_application.serializers import (
    post_schema,
    posts_schema,
)
from social_media_application.helpers.permissions import (
    is_post_owner,
    authenticate_user,
)


@app.route("/posts", methods=["GET"])
@authenticate_user
def get_all_posts(**kwargs):
    """
    Returns json where noticed details about all posts (posts_schema)
    :return: json
    """
    response_object = posts_schema.dump(Post.query.all())
    return make_response(jsonify(response_object)), 200


@app.route("/posts", methods=["POST"])
@authenticate_user
def new_post(**kwargs):
    """
    Register new post, from title, url, content,user, that comes from body json
    Returns json where noticed details about this post type that was registered(post_type_schema)
    :param name: str
    :return: json
    """
    try:
        user = kwargs.get("current_user")
        if user:
            title = request.json["title"]
            url = request.json["url"]
            content = request.json["content"]
            post_type = request.json["post_type"]
            tags = request.json["tags"]
            if post_type == "text":
                url = None

            post_object = Post(
                title=title,
                url=url,
                content=content,
                post_type=post_type,
                tags=tags,
                creator=user.id,
            )
            db.session.add(post_object)
            db.session.commit()
            response_object = post_schema.dump(post_object)
            return make_response(jsonify(response_object)), 201

        response_object = {"error": "user not found"}
        return make_response(jsonify(response_object)), 400

    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/posts/<id>", methods=["GET"])
def get_post(id):
    try:
        post_object = Post.query.get({"id": id})
        response_object = post_schema.dump(post_object)
        return make_response(jsonify(response_object)), 200

    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/posts/<id>", methods=["PUT", "PATCH"])
@is_post_owner
def update_post(id):
    try:
        post_data = request.get_json()
        if "post_type" in post_data.keys():
            if post_data["post_type"] == "text":
                if "url" in post_data.keys():
                    post_data["url"] = None
        post_object = Post.query.get({"id": id})
        for k, v in post_data.items():
            setattr(post_object, k, v)
        db.session.commit()
        response_object = post_schema.dump(post_object)
        return make_response(jsonify(response_object)), 200
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400


@app.route("/posts/<id>", methods=["DELETE"])
@is_post_owner
def delete_post(id):
    try:
        post_object = Post.query.get({"id": id})
        if post_object:
            Post.query.filter_by(id=id).delete()
            db.session.commit()
            response_object = {}
        return make_response(jsonify(response_object)), 204
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400

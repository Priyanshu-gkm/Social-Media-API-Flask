from flask import request, jsonify, make_response
from flask import current_app as app
from ..models import (
    db,
    User,
    Post,
    post_schema,
    posts_schema,
    post_type_schema,
    post_types_schema,
    PostType,
    Follow,
    follows_schema,
)
from .permissions import is_post_owner, authenticate_user
from sqlalchemy import or_


@app.route("/post-types", methods=["GET"])
def get_all_post_types():
    """
    Returns json where noticed details about all post types (post_types_schema)
    :return: json
    """
    responseObject = {
        "status": "Success",
        "message": post_types_schema.dump(PostType.query.all()),
    }
    return make_response(jsonify(responseObject)), 200


@app.route("/post-types", methods=["POST"])
@authenticate_user
def new_post_type(**kwargs):
    """
    Register new post type, from name that comes from body json
    Returns json where noticed details about this post type that was registered(post_type_schema)
    :param name: str
    :return: json
    """
    try:
        name = request.json["name"]
        if name:
            if PostType.query.filter_by(name=name).first():
                responseObject = {
                    "status": "Fail",
                    "message": "Post Type already exists",
                }
                return make_response(jsonify(responseObject)), 400

            pt = PostType(name=name)
            db.session.add(pt)
            db.session.commit()
            responseObject = {
                "status": "Success",
                "message": "Post Type Created successfully",
                "data": post_type_schema.dump(pt),
            }
            return make_response(jsonify(responseObject)), 201
        responseObject = {"status": "Fail", "message": "no name"}
        return make_response(jsonify(responseObject)), 400
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/posts", methods=["GET"])
def get_all_posts():
    """
    Returns json where noticed details about all posts (posts_schema)
    :return: json
    """
    responseObject = {
        "status": "Success",
        "message": posts_schema.dump(Post.query.all()),
    }
    return make_response(jsonify(responseObject)), 200


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
            post = Post(
                title=title,
                url=url,
                content=content,
                post_type=post_type,
                tags=tags,
                creator=user.id,
            )
            db.session.add(post)
            db.session.commit()
            responseObject = {
                "status": "Success",
                "message": "Post Created successfully",
                "data": post_schema.dump(post),
            }
            return make_response(jsonify(responseObject)), 201
        responseObject = {"status": "Fail", "message": "invalid user"}
        return make_response(jsonify(responseObject)), 400

    except Exception as e:
        print(e.args)
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/posts/<id>", methods=["GET"])
def get_post(id):
    try:
        post = Post.query.get({"id": id})
        responseObject = {"status": "Success", "message": post_schema.dump(post)}
        return make_response(jsonify(responseObject)), 200

    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/posts/<id>", methods=["PUT", "PATCH"])
@is_post_owner
def update_post(id):
    try:
        post_data = request.get_json()
        if "post_type" in post_data.keys():
            if post_data["post_type"] == "text":
                if "url" in post_data.keys():
                    post_data["url"] = None
        post = Post.query.get({"id": id})
        for k, v in post_data.items():
            setattr(post, k, v)
        db.session.commit()
        responseObject = {
            "status": "Success",
            "message": "Post updated successfully",
            "data": post_schema.dump(post),
        }
        return make_response(jsonify(responseObject)), 200
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/posts/<id>", methods=["DELETE"])
@is_post_owner
def delete_post(id):
    try:
        post = Post.query.get({"id": id})
        if post:
            Post.query.filter_by(id=id).delete()
            db.session.commit()
            responseObject = {
                "status": "Success",
                "message": "successfully deleted post",
            }
        return make_response(jsonify(responseObject)), 204
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400


@app.route("/feed", methods=["GET"])
@authenticate_user
def get_user_feed(**kwargs):
    """
    Returns json where posts from following users are listed (posts_schema)
    :return: json
    """
    try:
        user = kwargs.get("current_user")
        connections = (
            db.session.execute(
                db.select(Follow)
                .where(Follow.accepted == True)
                .where(or_(Follow.user1 == user.id, Follow.user2 == user.id))
                .where(Follow.archive == False)
            )
            .scalars()
            .all()
        )
        cons = follows_schema.dump(connections)
        users = set()
        for i in cons:
            for k, v in i.items():
                if k == "user1" or k == "user2":
                    users.add(v)
        users.remove(user.username)
        creators = [User.query.filter_by(username=user).first().id for user in users]
        responseObject = {
            "status": "Success",
            "message": posts_schema.dump(
                db.session.query(Post).filter(Post.creator.in_(creators)).all()
            ),
        }
        return make_response(jsonify(responseObject)), 200
    except Exception as e:
        responseObject = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400

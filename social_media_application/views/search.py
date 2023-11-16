from flask import jsonify, make_response, request
from flask import current_app as app

from social_media_application.models import User, Post
from social_media_application.serializers import user_schema, posts_schema


@app.route("/search", methods=["GET"])
def search():
    try:
        username = request.args.get("username")
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                data = user_schema.dump(user)
                data.pop("email")
                response_object = data
                return make_response(jsonify(response_object)), 200
            else:
                response_object = {"error": "user not found"}
                return make_response(jsonify(response_object)), 400
        elif request.args.get("tag"):
            tag = request.args.get("tag")
            posts = Post.query.filter(Post.tags.like("%" + tag + "%")).all()
            if posts:
                data = posts_schema.dump(posts)
                response_object = data
                return make_response(jsonify(response_object)), 200
            else:
                response_object = {"error": "no posts by such tag"}
                return make_response(jsonify(response_object)), 400
        elif request.args.get("post"):
            title = request.args.get("post")
            posts = Post.query.filter(Post.title == title).all()
            if posts:
                data = posts_schema.dump(posts)
                response_object = data
                return make_response(jsonify(response_object)), 200
            else:
                response_object = {"error": "no posts by this title"}
                return make_response(jsonify(response_object)), 400
        else:
            response_object = {"error": "incorrect search parameters"}
            return make_response(jsonify(response_object)), 400
    except Exception as e:
        response_object = {"error": str(e)}
        return make_response(jsonify(response_object)), 400

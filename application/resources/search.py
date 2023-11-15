from ..models import (
    User,
    user_schema,
    Post,
    posts_schema,
)
from flask import jsonify, make_response, request, current_app as app
from .permissions import authenticate_user


@app.route("/search", methods=["GET"])
def search():
    try:
        username = request.args.get("username")
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                data = user_schema.dump(user)
                data.pop("email")
                responseObject = {"user": data}
                return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {"error": "no such user"}
                return make_response(jsonify(responseObject)), 400
        elif request.args.get("tag"):
            tag = request.args.get("tag")
            posts = Post.query.filter(Post.tags.like("%" + tag + "%")).all()
            if posts:
                data = posts_schema.dump(posts)
                return jsonify(data), 200
            else:
                responseObject = {"error": "no posts by such tag"}
                return make_response(jsonify(responseObject)), 400
        elif request.args.get("post"):
            title = request.args.get("post")
            posts = Post.query.filter(Post.title == title).all()
            if posts:
                data = posts_schema.dump(posts)
                return jsonify(data), 200
            else:
                responseObject = {"error": "no posts by this title"}
                return make_response(jsonify(responseObject)), 400
        else:
            responseObject = {"error": "incorrect search parameters"}
            return jsonify(responseObject), 400
    except Exception as e:
        responseObject = {"status": "fail", "message": str(e)}
        return make_response(jsonify(responseObject)), 400

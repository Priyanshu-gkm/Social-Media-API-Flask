from flask import request, jsonify

from functools import wraps

from social_media_application.models import User, Post


def authenticate_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if Authorization header is present in the request
            if "Authorization" not in request.headers.keys():
                return jsonify({"error": "Unauthenticated"}), 401

            # Extract the token from the Authorization header
            auth_header = request.headers.get("Authorization")
            # Extract the token value
            token = auth_header.split(" ")[1]

            if token:
                username = User.verify_auth_token(token)
                if User.query.filter_by(username=username).first():
                    # If the token is valid, proceed with the original function
                    kwargs["current_user"] = User.query.filter_by(
                        username=username
                    ).first()
                    return f(*args, **kwargs)
                else:
                    return jsonify({"error": "Unauthenticated"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return decorated_function


def is_owner(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if "Authorization" not in request.headers.keys():
                return jsonify({"error": "Unauthenticated"}), 401
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(" ")[1]
            username = User.verify_auth_token(token)
            user = User.query.filter_by(username=username).first()
            if user and str(user.id) == kwargs.get("id"):
                return f(*args, **kwargs)
            return jsonify({"error": "Unauthorized"}), 403
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return decorated_function


def is_post_owner(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if "Authorization" not in request.headers.keys():
                return jsonify({"error": "Unauthenticated"}), 401
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(" ")[1]
            username = User.verify_auth_token(token)
            post_id = kwargs.get("id")
            post = Post.query.filter_by(id=post_id).first()
            if post:
                if User.query.filter_by(username=username).first().id == post.creator:
                    return f(*args, **kwargs)
                return jsonify({"error": "Unauthorized"}), 403
            return jsonify({"error": "Invalid post id"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return decorated_function

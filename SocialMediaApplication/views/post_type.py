from flask import request, jsonify, make_response
from flask import current_app as app
from ..models import (
    db,
    PostType,
)
from ..serializers import (
    post_type_schema,
    post_types_schema,
)
from ..helpers.permissions import authenticate_user


@app.route("/post-types", methods=["GET"])
def get_all_post_types():
    """
    Returns json where noticed details about all post types (post_types_schema)
    :return: json
    """
    response_object = {
        "status": "Success",
        "message": post_types_schema.dump(PostType.query.all()),
    }
    return make_response(jsonify(response_object)), 200


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
                response_object = {
                    "status": "Fail",
                    "message": "Post Type already exists",
                }
                return make_response(jsonify(response_object)), 400

            post_type_object = PostType(name=name)
            db.session.add(post_type_object)
            db.session.commit()
            response_object = {
                "status": "Success",
                "message": "Post Type Created successfully",
                "data": post_type_schema.dump(post_type_object),
            }
            return make_response(jsonify(response_object)), 201
        response_object = {"status": "Fail", "message": "no name"}
        return make_response(jsonify(response_object)), 400
    except Exception as e:
        response_object = {"status": "Fail", "message": str(e)}
        return make_response(jsonify(response_object)), 400
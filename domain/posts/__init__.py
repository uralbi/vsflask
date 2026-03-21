from flask import Blueprint

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")

from domain.posts import routes  # noqa: F401, E402

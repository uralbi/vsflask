from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from domain.posts import posts_bp
from domain.db.models import db, Post


@posts_bp.route("/create", methods=["POST"])
@login_required
def create():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        flash("Title and content are required.", "danger")
        return redirect(url_for("home"))

    post = Post(title=title, content=content, author_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    flash("Post created.", "success")
    return redirect(url_for("home"))


@posts_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash("Not allowed.", "danger")
        return redirect(url_for("home"))
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "success")
    return redirect(url_for("home"))

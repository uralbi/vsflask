import os
import uuid
from flask import request, redirect, url_for, flash, current_app, render_template
from flask_login import login_required, current_user
from PIL import Image
from domain.posts import posts_bp
from domain.db.models import db, Post, PostImage

MAX_WIDTH = 1200
UPLOAD_FOLDER = os.path.join("static", "uploads", "posts")


def save_image(file):
    """Resize to max 1200px wide, convert to WebP, save. Returns filename."""
    img = Image.open(file)
    img = img.convert("RGB")

    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

    filename = "{}.webp".format(uuid.uuid4().hex)
    upload_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(upload_dir, exist_ok=True)
    img.save(os.path.join(upload_dir, filename), "WEBP", quality=82, method=6)
    return filename


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
    db.session.flush()  # get post.id before commit

    images = request.files.getlist("images")
    for file in images:
        if file and file.filename:
            try:
                filename = save_image(file)
                db.session.add(PostImage(post_id=post.id, filename=filename))
            except Exception as e:
                current_app.logger.error("Image save error: %s", e)

    db.session.commit()
    flash("Post created.", "success")
    return redirect(url_for("home"))


@posts_bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash("Not allowed.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or not content:
            flash("Title and content are required.", "danger")
            return render_template("posts/edit.html", post=post)

        post.title = title
        post.content = content

        # handle new images
        images = request.files.getlist("images")
        for file in images:
            if file and file.filename:
                try:
                    filename = save_image(file)
                    db.session.add(PostImage(post_id=post.id, filename=filename))
                except Exception as e:
                    current_app.logger.error("Image save error: %s", e)

        # handle removed images
        remove_ids = request.form.getlist("remove_image")
        if remove_ids:
            upload_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
            for img_id in remove_ids:
                img = PostImage.query.get(int(img_id))
                if img and img.post_id == post.id:
                    path = os.path.join(upload_dir, img.filename)
                    if os.path.exists(path):
                        os.remove(path)
                    db.session.delete(img)

        db.session.commit()
        flash("Post updated.", "success")
        return redirect(url_for("home"))

    return render_template("posts/edit.html", post=post)


@posts_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash("Not allowed.", "danger")
        return redirect(url_for("home"))

    # delete image files from disk
    upload_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    for img in post.images:
        path = os.path.join(upload_dir, img.filename)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "success")
    return redirect(url_for("home"))

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum, Column, Integer, String, TIMESTAMP, Boolean, text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    verification_code = db.Column(db.String(6), nullable=True)
    created_at = db.Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    posts = relationship("Post", back_populates="author", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    modified_at = db.Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)

    search_vector = db.Column(TSVECTOR, nullable=True)

    author = relationship("User", back_populates="posts")
    images = relationship("PostImage", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")


class PostImage(db.Model):
    __tablename__ = "post_images"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, ForeignKey("posts.id"), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    created_at = db.Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    post = relationship("Post", back_populates="images")


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False, unique=True)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    source = db.Column(db.String, nullable=True)
    author_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=True)
    year_month = db.Column(db.String, nullable=True)
    search_vector = db.Column(TSVECTOR, nullable=True)

    author = relationship("User", backref="news")

    __table_args__ = (
        UniqueConstraint('title', 'year_month', name='uix_title_year_month'),
    )
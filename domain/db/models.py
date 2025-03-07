from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum, Column, Integer, String, TIMESTAMP, Boolean, text, UniqueConstraint, Computed
from sqlalchemy.dialects.postgresql import TSVECTOR

db = SQLAlchemy()


class UserStatus(PyEnum):
    USER = "USER"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(Enum(UserStatus), default=UserStatus.USER, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.username}, {self.email}, Status: {self.status}>"


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False, unique=True)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    source = db.Column(db.String, nullable=True)
    year_month = db.Column(db.String, Computed("to_char(created_at, 'YYYY-MM')", persisted=True))
    search_vector = db.Column(
        TSVECTOR,
        Computed("to_tsvector('russian', coalesce(title, '') || ' ' || coalesce(content, ''))", persisted=True)
    )

    __table_args__ = (
        UniqueConstraint('title', 'year_month', name='uix_title_year_month'),
    )
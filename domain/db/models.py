from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum, Column, Integer, String, TIMESTAMP, Boolean, text, UniqueConstraint, Computed
from sqlalchemy.dialects.postgresql import TSVECTOR

db = SQLAlchemy()


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
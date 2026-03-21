from app import app
from domain.db.database import engine
from sqlalchemy import text

STATEMENTS = [
    """
    CREATE OR REPLACE FUNCTION news_columns_update() RETURNS trigger AS $$
    BEGIN
      NEW.year_month := to_char(NEW.created_at, 'YYYY-MM');
      NEW.search_vector := to_tsvector('russian', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, ''));
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql
    """,
    "DROP TRIGGER IF EXISTS news_columns_trigger ON news",
    """
    CREATE TRIGGER news_columns_trigger
    BEFORE INSERT OR UPDATE ON news
    FOR EACH ROW EXECUTE PROCEDURE news_columns_update()
    """,
    """
    CREATE OR REPLACE FUNCTION posts_search_vector_update() RETURNS trigger AS $$
    BEGIN
      NEW.search_vector := to_tsvector('russian', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, ''));
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql
    """,
    "DROP TRIGGER IF EXISTS posts_search_vector_trigger ON posts",
    """
    CREATE TRIGGER posts_search_vector_trigger
    BEFORE INSERT OR UPDATE ON posts
    FOR EACH ROW EXECUTE PROCEDURE posts_search_vector_update()
    """,
]

if __name__ == "__main__":
    with engine.connect() as conn:
        for stmt in STATEMENTS:
            conn.execute(text(stmt))
        print("Triggers created successfully.")

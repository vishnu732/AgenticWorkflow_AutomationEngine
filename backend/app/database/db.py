from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///./workflow_runs.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

    # Lightweight SQLite migration for existing local database
    with engine.connect() as connection:
        columns = [
            row[1]
            for row in connection.execute(text("PRAGMA table_info(workflow_runs)")).fetchall()
        ]

        if "review_status" not in columns:
            connection.execute(
                text("ALTER TABLE workflow_runs ADD COLUMN review_status VARCHAR DEFAULT 'pending' NOT NULL")
            )

        if "human_override" not in columns:
            connection.execute(
                text("ALTER TABLE workflow_runs ADD COLUMN human_override BOOLEAN DEFAULT 0 NOT NULL")
            )

        if "override_reason" not in columns:
            connection.execute(
                text("ALTER TABLE workflow_runs ADD COLUMN override_reason TEXT")
            )

        connection.commit()
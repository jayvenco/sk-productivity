import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Data directory: one level up from app/ (project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'swissknife.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Create all tables and migrate existing data.
    Import Base from app.models as side-effect to load all model classes.
    """
    from app.models import Base  # noqa: F811
    Base.metadata.create_all(bind=engine)

    # ── Migrate schema: add missing columns to existing tables ──
    _migrate_schema()

    # ── Migrate: create default columns if none exist ──────────
    db = SessionLocal()
    try:
        _migrate_kanban_columns(db)
        _migrate_default_admin(db)
    finally:
        db.close()


def _get_columns(table_name: str) -> set:
    """Get set of existing column names for a table."""
    from sqlalchemy import inspect
    inspector = inspect(engine)
    return {c["name"] for c in inspector.get_columns(table_name)}


def _migrate_schema():
    """Add missing columns to existing tables. SQLAlchemy's create_all
    only creates new tables, it does not ALTER existing ones.
    """
    import logging

    columns_to_add = {
        "kanban": [
            ("due_date", "datetime"),
            ("swimlane_id", "integer"),
        ],
        "notes": [
            ("color", "varchar(7)"),
        ],
        "tasks": [
            ("color", "varchar(7)"),
        ],
    }

    for table, cols in columns_to_add.items():
        existing = _get_columns(table)
        for col_name, col_type in cols:
            if col_name not in existing:
                sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                try:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    logging.info(f"Migrated: added {table}.{col_name}")
                except Exception as e:
                    logging.warning(f"Could not add {table}.{col_name}: {e}")


def _migrate_default_admin(db):
    """Ensure default admin user exists."""
    from app.models.settings import Setting
    import hashlib
    existing = db.query(Setting).filter(Setting.key == "password_hash").first()
    if not existing:
        pw_hash = hashlib.sha256(b"admin123").hexdigest()
        db.add(Setting(key="password_hash", value=pw_hash))
        existing_username = db.query(Setting).filter(Setting.key == "username").first()
        if not existing_username:
            db.add(Setting(key="username", value="admin"))
        db.commit()


def _migrate_kanban_columns(db):
    """Ensure default Kanban columns exist and migrate old cards without column_id."""
    from app.models.kanban import KanbanCard, KanbanColumn, KanbanStatus

    existing = db.query(KanbanColumn).count()
    if existing > 0:
        # Still migrate cards that have no column_id but have a status
        _backfill_column_ids(db)
        return

    defaults = [
        {"name": "Te doen", "position": 0, "color": "#6b7280"},
        {"name": "Bezig", "position": 1, "color": "#3b82f6"},
        {"name": "Klaar", "position": 2, "color": "#22c55e"},
    ]
    for cfg in defaults:
        col = KanbanColumn(**cfg)
        db.add(col)
    db.flush()  # get IDs

    # Get the created columns by position
    columns = db.query(KanbanColumn).order_by(KanbanColumn.position).all()
    status_map = {
        KanbanStatus.todo: columns[0].id,
        KanbanStatus.doing: columns[1].id,
        KanbanStatus.done: columns[2].id,
    }

    # Migrate existing cards
    for card in db.query(KanbanCard).all():
        if card.column_id is None and card.status in status_map:
            card.column_id = status_map[card.status]
    db.commit()


def _backfill_column_ids(db):
    """For cards that have a status but no column_id, find the matching column."""
    from app.models.kanban import KanbanColumn, KanbanCard, KanbanStatus
    columns = {c.name.lower(): c.id for c in db.query(KanbanColumn).all()}
    status_to_name = {
        KanbanStatus.todo: "te doen",
        KanbanStatus.doing: "bezig",
        KanbanStatus.done: "klaar",
    }
    for card in db.query(KanbanCard).filter(KanbanCard.column_id == None).all():
        if card.status in status_to_name:
            name = status_to_name[card.status]
            if name in columns:
                card.column_id = columns[name]
    db.commit()


def get_db():
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
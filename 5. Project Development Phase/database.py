import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

import tempfile

load_dotenv()

# Build absolute path to ensure sqlite can always open it
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
default_db_path = os.path.join(BASE_DIR, "vbcua.db")

# Streamlit Community Cloud mounts repositories as read-only. Fall back to /tmp if not writable.
try:
    test_path = os.path.join(BASE_DIR, ".write_test")
    with open(test_path, 'w') as f:
        f.write("test")
    os.remove(test_path)
except (IOError, OSError):
    default_db_path = os.path.join(tempfile.gettempdir(), "vbcua.db")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

# For SQLite, we need to allow multithreading for Streamlit's concurrent requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

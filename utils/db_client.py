from typing import Any, Sequence

from sqlalchemy import create_engine, text
from utils.config import DB

def _engine_for_db(db_name: str):
    url = (
        f"mysql+pymysql://{DB['user']}:{DB['password']}"
        f"@{DB['host']}:{DB['port']}/{db_name}"
    )
    return create_engine(url)

def fetch_one(db_name: str, sql: str) -> Any:
    engine = _engine_for_db(db_name)
    with engine.connect() as conn:
        return conn.execute(text(sql)).fetchone()

def fetch_all(db_name: str, sql: str) -> Sequence[Any]:
    engine = _engine_for_db(db_name)
    with engine.connect() as conn:
        return conn.execute(text(sql)).fetchall()

def execute(db_name: str, sql: str) -> None:
    engine = _engine_for_db(db_name)
    with engine.begin() as conn:
        conn.execute(text(sql))
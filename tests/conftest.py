import pytest
import sqlite3
from datetime import datetime

def adapt_datetime(val):
    """Adapt datetime to SQLite format"""
    return val.isoformat()

def convert_datetime(val):
    """Convert SQLite value to datetime"""
    return datetime.fromisoformat(val.decode())

@pytest.fixture(autouse=True)
def setup_sqlite_adapters():
    """Configure SQLite adapters for datetime handling"""
    sqlite3.register_adapter(datetime, adapt_datetime)
    sqlite3.register_converter("datetime", convert_datetime)
    
    # Register the adapters
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    sqlite3.enable_callback_tracebacks(True)
    yield 
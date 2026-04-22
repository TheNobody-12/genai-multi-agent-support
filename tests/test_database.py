"""Tests for SQLite database schema and seed integrity."""

import os
import sqlite3
import pytest
from setup_database import setup_database, DB_PATH

@pytest.fixture(scope="module")
def setup_test_db():
    """Setup and teardown a test database."""
    # Ensure fresh state
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    setup_database()
    yield DB_PATH
    
    # Cleanup after tests
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_database_creation(setup_test_db):
    """Test standard database creation and data ingestion sizes."""
    assert os.path.exists(setup_test_db)
    
    conn = sqlite3.connect(setup_test_db)
    cursor = conn.cursor()
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "customers" in tables
    assert "products" in tables
    assert "support_tickets" in tables
    
    # Verify counts roughly match our seed expectations (not exact hardcoding to allow slight data tweaks)
    cursor.execute("SELECT COUNT(*) FROM customers")
    assert cursor.fetchone()[0] == 15
    
    cursor.execute("SELECT COUNT(*) FROM products")
    assert cursor.fetchone()[0] == 10
    
    conn.close()

def test_db_foreign_keys(setup_test_db):
    """Test schema validity with foreign keys on tickets table."""
    conn = sqlite3.connect(setup_test_db)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_key_list(support_tickets)")
    fks = cursor.fetchall()
    
    # Expect FKs pointing to customers and products
    fk_tables = {fk[2] for fk in fks}
    assert "customers" in fk_tables
    assert "products" in fk_tables
    conn.close()

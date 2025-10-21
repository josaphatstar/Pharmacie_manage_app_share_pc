"""Database access layer for the pharmacy stock app.
Uses SQLite and provides simple CRUD functions.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from typing import List, Optional, Tuple, Any, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacy.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the products table and history table with triggers if they don't exist."""
    with closing(get_connection()) as conn, conn:  # type: ignore[attr-defined]
        # Create products table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                expiry_date TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        
        # Create history table for audit trail
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                product_id INTEGER,
                product_name TEXT,
                old_quantity INTEGER,
                new_quantity INTEGER,
                old_expiry_date TEXT,
                new_expiry_date TEXT,
                timestamp TEXT DEFAULT (datetime('now')),
                details TEXT
            )
            """
        )
        
        # Helpful index for ordering by expiry date
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_expiry ON products(expiry_date)"
        )
        
        # Index for history table
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp DESC)"
        )
        
        # Trigger for INSERT operations
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_product_insert
            AFTER INSERT ON products
            FOR EACH ROW
            BEGIN
                INSERT INTO history (
                    operation, product_id, product_name, new_quantity, new_expiry_date, details
                ) VALUES (
                    'AJOUT', NEW.id, NEW.name, NEW.quantity, NEW.expiry_date,
                    'Produit ajouté: ' || NEW.name || ' (Qté: ' || NEW.quantity || ', Exp: ' || NEW.expiry_date || ')'
                );
            END;
            """
        )
        
        # Trigger for UPDATE operations
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_product_update
            AFTER UPDATE ON products
            FOR EACH ROW
            BEGIN
                INSERT INTO history (
                    operation, product_id, product_name, old_quantity, new_quantity, 
                    old_expiry_date, new_expiry_date, details
                ) VALUES (
                    'MODIFICATION', NEW.id, NEW.name, OLD.quantity, NEW.quantity,
                    OLD.expiry_date, NEW.expiry_date,
                    'Produit modifié: ' || NEW.name || 
                    CASE WHEN OLD.name != NEW.name THEN ' (Nom: ' || OLD.name || ' → ' || NEW.name || ')' ELSE '' END ||
                    CASE WHEN OLD.quantity != NEW.quantity THEN ' (Qté: ' || OLD.quantity || ' → ' || NEW.quantity || ')' ELSE '' END ||
                    CASE WHEN OLD.expiry_date != NEW.expiry_date THEN ' (Exp: ' || OLD.expiry_date || ' → ' || NEW.expiry_date || ')' ELSE '' END
                );
            END;
            """
        )
        
        # Trigger for DELETE operations
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_product_delete
            BEFORE DELETE ON products
            FOR EACH ROW
            BEGIN
                INSERT INTO history (
                    operation, product_id, product_name, old_quantity, old_expiry_date, details
                ) VALUES (
                    'SUPPRESSION', OLD.id, OLD.name, OLD.quantity, OLD.expiry_date,
                    'Produit supprimé: ' || OLD.name || ' (Qté: ' || OLD.quantity || ', Exp: ' || OLD.expiry_date || ')'
                );
            END;
            """
        )


def add_product(name: str, quantity: int, expiry_date: str) -> int:
    """Insert a new product. Returns the created row id.

    Args:
        name: Unique product name.
        quantity: Non-negative integer.
        expiry_date: ISO date string YYYY-MM-DD
    """
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO products (name, quantity, expiry_date) VALUES (?, ?, ?)",
            (name.strip(), quantity, expiry_date),
        )
        return int(cur.lastrowid)


def get_products(search: Optional[str] = None) -> List[sqlite3.Row]:
    """Fetch all products optionally filtered by a search string on name."""
    with closing(get_connection()) as conn:
        if search:
            like = f"%{search.strip()}%"
            rows = conn.execute(
                "SELECT * FROM products WHERE name LIKE ? ORDER BY id ASC",
                (like,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM products ORDER BY id ASC"
            ).fetchall()
    return rows


def get_product_by_id(product_id: int) -> Optional[sqlite3.Row]:
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
    return row


def update_product(product_id: int, name: str, quantity: int, expiry_date: str) -> None:
    with closing(get_connection()) as conn, conn:
        conn.execute(
            "UPDATE products SET name = ?, quantity = ?, expiry_date = ? WHERE id = ?",
            (name.strip(), quantity, expiry_date, product_id),
        )


def delete_product(product_id: int) -> None:
    with closing(get_connection()) as conn, conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))


def get_history(limit: Optional[int] = 100) -> List[sqlite3.Row]:
    """Fetch history records, most recent first."""
    with closing(get_connection()) as conn:
        if limit:
            rows = conn.execute(
                "SELECT * FROM history ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM history ORDER BY timestamp DESC"
            ).fetchall()
    return rows


def get_history_by_operation(operation: str, limit: Optional[int] = 50) -> List[sqlite3.Row]:
    """Fetch history records filtered by operation type."""
    with closing(get_connection()) as conn:
        if limit:
            rows = conn.execute(
                "SELECT * FROM history WHERE operation = ? ORDER BY timestamp DESC LIMIT ?",
                (operation, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM history WHERE operation = ? ORDER BY timestamp DESC",
                (operation,),
            ).fetchall()
    return rows


__all__ = [
    "DB_PATH",
    "init_db",
    "add_product",
    "get_products",
    "get_product_by_id",
    "update_product",
    "delete_product",
    "get_history",
    "get_history_by_operation",
]

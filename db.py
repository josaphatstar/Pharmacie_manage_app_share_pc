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
        # Check if products table exists already
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'").fetchone()
        if cur:
            # Check indexes to see if there's a unique index on 'name' only and not on (name, expiry_date)
            idxs = conn.execute("PRAGMA index_list('products')").fetchall()
            has_unique_name = False
            has_unique_pair = False
            for idx in idxs:
                if not idx['unique']:
                    continue
                info = conn.execute(f"PRAGMA index_info('{idx['name']}')").fetchall()
                cols = [i['name'] for i in info]
                if cols == ['name']:
                    has_unique_name = True
                if cols == ['name', 'expiry_date'] or cols == ['expiry_date', 'name']:
                    has_unique_pair = True

            if has_unique_name and not has_unique_pair:
                # Perform migration: create new table, copy aggregated data grouped by (name, expiry_date)
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL CHECK(quantity >= 0),
                        expiry_date TEXT NOT NULL,
                        created_at TEXT DEFAULT (datetime('now')),
                        UNIQUE(name, expiry_date)
                    )
                    """
                )

                # Aggregate existing rows by (name, expiry_date) to avoid duplicates
                rows = conn.execute(
                    "SELECT name, expiry_date, SUM(quantity) as quantity, MIN(created_at) as created_at "
                    "FROM products GROUP BY name, expiry_date"
                ).fetchall()

                for r in rows:
                    conn.execute(
                        "INSERT INTO products_new (name, quantity, expiry_date, created_at) VALUES (?, ?, ?, ?)",
                        (r['name'], r['quantity'], r['expiry_date'], r['created_at']),
                    )

                # Drop old table and rename new
                conn.execute("DROP TABLE products")
                conn.execute("ALTER TABLE products_new RENAME TO products")
        else:
            # Table does not exist: create with desired schema
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity >= 0),
                    expiry_date TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    UNIQUE(name, expiry_date)
                )
                """
            )

        # Create or ensure history table exists
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
                    'Produit ajout\u00e9: ' || NEW.name || ' (Qt\u00e9: ' || NEW.quantity || ', Exp: ' || NEW.expiry_date || ')'
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
                    'Produit modifi\u00e9: ' || NEW.name || 
                    CASE WHEN OLD.name != NEW.name THEN ' (Nom: ' || OLD.name || ' \u2192 ' || NEW.name || ')' ELSE '' END ||
                    CASE WHEN OLD.quantity != NEW.quantity THEN ' (Qt\u00e9: ' || OLD.quantity || ' \u2192 ' || NEW.quantity || ')' ELSE '' END ||
                    CASE WHEN OLD.expiry_date != NEW.expiry_date THEN ' (Exp: ' || OLD.expiry_date || ' \u2192 ' || NEW.expiry_date || ')' ELSE '' END
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
                    'Produit supprim\u00e9: ' || OLD.name || ' (Qt\u00e9: ' || OLD.quantity || ', Exp: ' || OLD.expiry_date || ')'
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
        # Normalize inputs
        nm = name.strip()
        exp = expiry_date

        # If a product with same name and expiry_date exists, increment its quantity instead of inserting a new row
        existing = conn.execute(
            "SELECT id, quantity FROM products WHERE name = ? AND expiry_date = ?",
            (nm, exp),
        ).fetchone()

        if existing:
            existing_id = int(existing['id'])
            existing_qty = int(existing['quantity'])
            added_qty = int(quantity)
            new_qty = existing_qty + added_qty
            conn.execute(
                "UPDATE products SET quantity = ? WHERE id = ?",
                (new_qty, existing_id),
            )

            # The UPDATE will fire the trg_product_update trigger which inserts a MODIFICATION row.
            # We prefer to record this operation as an AJOUT (fusion) in history. To avoid duplicate entries,
            # delete the most-recent trigger-created MODIFICATION row for this product (if any),
            # then insert our own AJOUT record describing the fusion.
            last_hist = conn.execute(
                "SELECT id, operation FROM history WHERE product_id = ? ORDER BY id DESC LIMIT 1",
                (existing_id,),
            ).fetchone()

            if last_hist and last_hist['operation'] == 'MODIFICATION':
                # remove the trigger-generated modification entry
                conn.execute("DELETE FROM history WHERE id = ?", (int(last_hist['id']),))

            details = f"Produit ajout (fusion): {nm} (Qté précédent: {existing_qty}, +{added_qty}) - Exp: {exp}"
            conn.execute(
                "INSERT INTO history (operation, product_id, product_name, old_quantity, new_quantity, old_expiry_date, new_expiry_date, details) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ('AJOUT', existing_id, nm, existing_qty, new_qty, exp, exp, details),
            )
            return existing_id
        else:
            cur = conn.execute(
                "INSERT INTO products (name, quantity, expiry_date) VALUES (?, ?, ?)",
                (nm, int(quantity), exp),
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


def remove_stock(product_id: int, quantity: int, reason: str = "") -> None:
    """Remove a quantity from a product's stock and record it as a SORTIE operation.
    
    Args:
        product_id: The ID of the product to update
        quantity: The quantity to remove (positive number)
        reason: Optional reason for the stock removal
    
    Raises:
        ValueError: If quantity is negative or zero
        ValueError: If product doesn't exist
        ValueError: If not enough stock available
    """
    if quantity <= 0:
        raise ValueError("La quantité à retirer doit être positive")

    with closing(get_connection()) as conn, conn:
        # Get current product info
        product = conn.execute(
            "SELECT name, quantity, expiry_date FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()
        
        if not product:
            raise ValueError("Produit non trouvé")
        
        current_qty = int(product['quantity'])
        if current_qty < quantity:
            raise ValueError(f"Stock insuffisant (disponible: {current_qty}, demandé: {quantity})")
        
        new_qty = current_qty - quantity
        
        # Si le stock atteint zéro, supprimer le produit
        if new_qty == 0:
            # Supprimer le produit
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            
            # Remove the automatic SUPPRESSION history entry that will be created by the trigger
            last_hist = conn.execute(
                "SELECT id, operation FROM history WHERE product_id = ? ORDER BY id DESC LIMIT 1",
                (product_id,)
            ).fetchone()
            
            if last_hist and last_hist['operation'] == 'SUPPRESSION':
                conn.execute("DELETE FROM history WHERE id = ?", (int(last_hist['id']),))
            
            # Add custom SORTIE history entry with stock depletion notice
            details = f"🔴 Sortie de stock finale: {product['name']} (-{quantity}) - STOCK ÉPUISÉ - Produit supprimé"
            if reason:
                details += f" - Motif: {reason}"
            details += f" - Exp: {product['expiry_date']}"
            
            conn.execute(
                """INSERT INTO history (
                    operation, product_id, product_name, old_quantity, new_quantity,
                    old_expiry_date, new_expiry_date, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    'SORTIE',
                    product_id,
                    product['name'],
                    current_qty,
                    0,
                    product['expiry_date'],
                    product['expiry_date'],
                    details
                )
            )
        else:
            # Update stock normally
            conn.execute(
                "UPDATE products SET quantity = ? WHERE id = ?",
                (new_qty, product_id)
            )
            
            # Remove the automatic MODIFICATION history entry
            last_hist = conn.execute(
                "SELECT id, operation FROM history WHERE product_id = ? ORDER BY id DESC LIMIT 1",
                (product_id,)
            ).fetchone()
            
            if last_hist and last_hist['operation'] == 'MODIFICATION':
                conn.execute("DELETE FROM history WHERE id = ?", (int(last_hist['id']),))
            
            # Add SORTIE history entry
            details = f"Sortie de stock: {product['name']} (-{quantity})"
            if reason:
                details += f" - Motif: {reason}"
            details += f" - Exp: {product['expiry_date']}"
            
            conn.execute(
                """INSERT INTO history (
                    operation, product_id, product_name, old_quantity, new_quantity,
                    old_expiry_date, new_expiry_date, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    'SORTIE',
                    product_id,
                    product['name'],
                    current_qty,
                    new_qty,
                    product['expiry_date'],
                    product['expiry_date'],
                    details
                )
            )


__all__ = [
    "DB_PATH",
    "init_db",
    "add_product",
    "get_products",
    "get_product_by_id",
    "update_product",
    "delete_product",
    "remove_stock",
    "get_history",
    "get_history_by_operation",
]
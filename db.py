"""Database access layer for the pharmacy stock app.
Uses SQLite via SQLAlchemy and provides simple CRUD functions.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env (pour DATABASE_URL)
load_dotenv(override=True)

# Récupérer l'URL de connexion PostgreSQL depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
    raise ValueError(
        "DATABASE_URL pour PostgreSQL non définie. Créez un fichier .env avec DATABASE_URL=postgresql+psycopg2://user:password@host:port/database"
    )

# Créer l'engine SQLAlchemy pour PostgreSQL
engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    pool_recycle=3600,   # Recycler les connexions après 1h
    echo=False           # Mettre à True pour debug SQL
)

@contextmanager
def get_connection():
    """Context manager pour obtenir une connexion à la base de données."""
    conn = engine.connect()
    trans = conn.begin()
    try:
        yield conn
        trans.commit()
    except:
        trans.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the products table and history table if they don't exist."""
    with get_connection() as conn:
        # Create products table
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL CHECK(quantity >= 0),
                expiry_date DATE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (name, expiry_date)
            )
            """
        ))

        # Create or ensure history table exists
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                operation VARCHAR(50) NOT NULL,
                product_id INT,
                product_name VARCHAR(255),
                old_quantity INT,
                new_quantity INT,
                old_expiry_date DATE,
                new_expiry_date DATE,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
            """
        ))

        # Créer les index s'ils n'existent pas (syntaxe PostgreSQL)
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_timestamp ON history(timestamp DESC)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_products_expiry ON products(expiry_date)"))


def add_product(name: str, quantity: int, expiry_date: str) -> int:
    """Insert a new product. Returns the created row id.

    Args:
        name: Product name.
        quantity: Non-negative integer.
        expiry_date: ISO date string YYYY-MM-DD
    """
    with get_connection() as conn:
        # Normalize inputs
        nm = name.strip()
        exp = expiry_date

        # If a product with same name and expiry_date exists, increment its quantity instead of inserting a new row
        existing = conn.execute(text(
            "SELECT id, quantity FROM products WHERE name = :name AND expiry_date = :exp"
        ), {"name": nm, "exp": exp}).fetchone()

        if existing:
            existing_id = int(existing[0])
            existing_qty = int(existing[1])
            added_qty = int(quantity)
            new_qty = existing_qty + added_qty
            
            conn.execute(text(
                "UPDATE products SET quantity = :qty WHERE id = :id"
            ), {"qty": new_qty, "id": existing_id})

            # Record AJOUT (fusion) in history
            details = f"Produit ajouté (fusion): {nm} (Qté précédente: {existing_qty}, +{added_qty}) - Exp: {exp}"
            conn.execute(text(
                "INSERT INTO history (operation, product_id, product_name, old_quantity, new_quantity, old_expiry_date, new_expiry_date, details) "
                "VALUES (:op, :pid, :name, :old_qty, :new_qty, :old_exp, :new_exp, :details)"
            ), {
                "op": 'AJOUT', "pid": existing_id, "name": nm,
                "old_qty": existing_qty, "new_qty": new_qty,
                "old_exp": exp, "new_exp": exp, "details": details
            })
            return existing_id
        else:
            result = conn.execute(text(
                "INSERT INTO products (name, quantity, expiry_date) VALUES (:name, :qty, :exp) RETURNING id"
            ), {"name": nm, "qty": int(quantity), "exp": exp})
            
            # Récupérer l'ID retourné par PostgreSQL
            new_id = result.scalar_one_or_none()
            if new_id is None:
                raise RuntimeError("Impossible de récupérer l'ID du produit nouvellement inséré.")
            
            # Record AJOUT in history
            details = f"Produit ajouté: {nm} (Qté: {quantity}, Exp: {exp})"
            conn.execute(text(
                "INSERT INTO history (operation, product_id, product_name, new_quantity, new_expiry_date, details) "
                "VALUES (:op, :pid, :name, :qty, :exp, :details)"
            ), {
                "op": 'AJOUT', "pid": new_id, "name": nm,
                "qty": int(quantity), "exp": exp, "details": details
            })
            return int(new_id)

def get_products(search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Récupère tous les produits, avec filtrage optionnel par nom."""
    with get_connection() as conn:
        if search:
            result = conn.execute(
                text("SELECT * FROM products WHERE name ILIKE :search ORDER BY id ASC"),
                {"search": f"%{search.strip()}%"}
            )
        else:
            result = conn.execute(
                text("SELECT * FROM products ORDER BY id ASC")
            )
        
        # Correction : utiliser ._mapping pour chaque ligne
        return [dict(row._mapping) for row in result]

def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Récupère un produit par son ID."""
    with get_connection() as conn:
        result = conn.execute(
            text("SELECT * FROM products WHERE id = :id"),
            {"id": product_id}
        ).fetchone()
        
        # Correction : utiliser ._mapping pour convertir en dict
        return dict(result._mapping) if result else None


def update_product(product_id: int, name: str, quantity: int, expiry_date: str) -> None:
    with get_connection() as conn:
        # Get old values for history
        old = conn.execute(text(
            "SELECT name, quantity, expiry_date FROM products WHERE id = :id"
        ), {"id": product_id}).fetchone()
        
        if old:
            # Correction : accéder par index
            old_name, old_qty, old_exp = old[0], old[1], str(old[2])


def delete_product(product_id: int) -> None:
    with get_connection() as conn:
        # Get product info for history
        product = conn.execute(text(
            "SELECT name, quantity, expiry_date FROM products WHERE id = :id"
        ), {"id": product_id}).fetchone()
        
        if product:
            # Correction : accéder par index
            name, qty, exp = product[0], product[1], str(product[2])


def get_history(limit: Optional[int] = 100) -> List[Dict[str, Any]]:
    """Fetch history records, most recent first."""
    with get_connection() as conn:
        if limit:
            rows = conn.execute(text(
                "SELECT * FROM history ORDER BY timestamp DESC LIMIT :limit"
            ), {"limit": limit}).fetchall()
        else:
            rows = conn.execute(text(
                "SELECT * FROM history ORDER BY timestamp DESC"
            )).fetchall()
    
    # Correction : convertir chaque ligne en dict
    return [dict(row._mapping) for row in rows]


def get_history_by_operation(operation: str, limit: Optional[int] = 50) -> List[Any]:
    """Fetch history records filtered by operation type."""
    with get_connection() as conn:
        if limit:
            rows = conn.execute(text(
                "SELECT * FROM history WHERE operation = :op ORDER BY timestamp DESC LIMIT :limit"
            ), {"op": operation, "limit": limit}).fetchall()
        else:
            rows = conn.execute(text(
                "SELECT * FROM history WHERE operation = :op ORDER BY timestamp DESC"
            ), {"op": operation}).fetchall()
    return rows


def remove_stock(product_id: int, quantity: int, reason: str = "") -> None:
    if quantity <= 0:
        raise ValueError("La quantité à retirer doit être positive")

    with get_connection() as conn:
        # Get current product info
        product = conn.execute(text(
            "SELECT name, quantity, expiry_date FROM products WHERE id = :id"
        ), {"id": product_id}).fetchone()
        
        if not product:
            raise ValueError("Produit non trouvé")
        
        # Correction : accéder par index au lieu de noms
        name, current_qty, exp = product[0], int(product[1]), str(product[2])

__all__ = [
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
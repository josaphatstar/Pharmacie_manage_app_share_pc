"""Database access layer for the pharmacy stock app.
Uses MySQL (Railway) via SQLAlchemy and provides simple CRUD functions.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env (avec override pour forcer le rechargement)
load_dotenv(override=True)

# Récupérer l'URL de connexion MySQL depuis database_config.txt, .env ou Streamlit secrets
DATABASE_URL = None

# Essayer de lire depuis database_config.txt
config_file = os.path.join(os.path.dirname(__file__), 'database_config.txt')
if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATABASE_URL=') and len(line) > 13:
                DATABASE_URL = line[13:]  # Après "DATABASE_URL="
                break

# Si pas trouvé dans database_config.txt, essayer .env
if not DATABASE_URL:
    DATABASE_URL = os.getenv("DATABASE_URL")

# Si pas trouvé dans .env, essayer st.secrets (pour Streamlit Cloud)
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except:
        pass

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL non définie. Créez un fichier .env avec DATABASE_URL=mysql+pymysql://user:password@host:port/database?charset=utf8mb4"
    )

# Créer l'engine SQLAlchemy avec support SSL pour Aiven
connect_args = {}
if 'ssl-ca=' in DATABASE_URL:
    # Extraire le chemin du certificat SSL pour Aiven
    import urllib.parse
    parsed = urllib.parse.urlparse(DATABASE_URL)
    query_params = urllib.parse.parse_qs(parsed.query)
    ssl_ca = query_params.get('ssl-ca', [None])[0]
    if ssl_ca:
        connect_args['ssl'] = {'ca': ssl_ca}
    # Nettoyer l'URL en supprimant les paramètres de requête SSL
    clean_url = DATABASE_URL.split('?')[0]
else:
    clean_url = DATABASE_URL

engine: Engine = create_engine(
    clean_url,
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    pool_recycle=3600,   # Recycler les connexions après 1h
    echo=False,          # Mettre à True pour debug SQL
    connect_args=connect_args
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
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL CHECK(quantity >= 0),
                expiry_date DATE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_product (name, expiry_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        ))

        # Create or ensure history table exists
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                operation VARCHAR(50) NOT NULL,
                product_id INT,
                product_name VARCHAR(255),
                old_quantity INT,
                new_quantity INT,
                old_expiry_date DATE,
                new_expiry_date DATE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                INDEX idx_timestamp (timestamp DESC)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        ))

        # Helpful index for ordering by expiry date
        # MySQL ne supporte pas IF NOT EXISTS pour les index, on ignore l'erreur si l'index existe déjà
        try:
            conn.execute(text(
                "CREATE INDEX idx_products_expiry ON products(expiry_date)"
            ))
        except Exception:
            # L'index existe déjà, on continue
            pass


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
            details = f"Produit ajouté (fusion): {nm} (Qté précédent: {existing_qty}, +{added_qty}) - Exp: {exp}"
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
                "INSERT INTO products (name, quantity, expiry_date) VALUES (:name, :qty, :exp)"
            ), {"name": nm, "qty": int(quantity), "exp": exp})
            
            new_id = result.lastrowid
            
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


def get_products(search: Optional[str] = None) -> List[Any]:
    """Fetch all products optionally filtered by a search string on name."""
    with get_connection() as conn:
        if search:
            like = f"%{search.strip()}%"
            rows = conn.execute(text(
                "SELECT * FROM products WHERE name LIKE :search ORDER BY id ASC"
            ), {"search": like}).fetchall()
        else:
            rows = conn.execute(text(
                "SELECT * FROM products ORDER BY id ASC"
            )).fetchall()
    return rows


def get_product_by_id(product_id: int) -> Optional[Any]:
    with get_connection() as conn:
        row = conn.execute(text(
            "SELECT * FROM products WHERE id = :id"
        ), {"id": product_id}).fetchone()
    return row


def update_product(product_id: int, name: str, quantity: int, expiry_date: str) -> None:
    with get_connection() as conn:
        # Get old values for history
        old = conn.execute(text(
            "SELECT name, quantity, expiry_date FROM products WHERE id = :id"
        ), {"id": product_id}).fetchone()
        
        if old:
            old_name, old_qty, old_exp = old[0], old[1], str(old[2])
            
            conn.execute(text(
                "UPDATE products SET name = :name, quantity = :qty, expiry_date = :exp WHERE id = :id"
            ), {"name": name.strip(), "qty": quantity, "exp": expiry_date, "id": product_id})
            
            # Record MODIFICATION in history
            details_parts = []
            if old_name != name.strip():
                details_parts.append(f"Nom: {old_name} → {name.strip()}")
            if old_qty != quantity:
                details_parts.append(f"Qté: {old_qty} → {quantity}")
            if old_exp != expiry_date:
                details_parts.append(f"Exp: {old_exp} → {expiry_date}")
            
            details = f"Produit modifié: {name.strip()}" + (f" ({', '.join(details_parts)})" if details_parts else "")
            
            conn.execute(text(
                "INSERT INTO history (operation, product_id, product_name, old_quantity, new_quantity, old_expiry_date, new_expiry_date, details) "
                "VALUES (:op, :pid, :name, :old_qty, :new_qty, :old_exp, :new_exp, :details)"
            ), {
                "op": 'MODIFICATION', "pid": product_id, "name": name.strip(),
                "old_qty": old_qty, "new_qty": quantity,
                "old_exp": old_exp, "new_exp": expiry_date, "details": details
            })


def delete_product(product_id: int) -> None:
    with get_connection() as conn:
        # Get product info for history
        product = conn.execute(text(
            "SELECT name, quantity, expiry_date FROM products WHERE id = :id"
        ), {"id": product_id}).fetchone()
        
        if product:
            name, qty, exp = product[0], product[1], str(product[2])
            
            conn.execute(text("DELETE FROM products WHERE id = :id"), {"id": product_id})
            
            # Record SUPPRESSION in history
            details = f"Produit supprimé: {name} (Qté: {qty}, Exp: {exp})"
            conn.execute(text(
                "INSERT INTO history (operation, product_id, product_name, old_quantity, old_expiry_date, details) "
                "VALUES (:op, :pid, :name, :qty, :exp, :details)"
            ), {
                "op": 'SUPPRESSION', "pid": product_id, "name": name,
                "qty": qty, "exp": exp, "details": details
            })


def get_history(limit: Optional[int] = 100) -> List[Any]:
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
    return rows


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

    with get_connection() as conn:
        # Get current product info
        product = conn.execute(text(
            "SELECT name, quantity, expiry_date FROM products WHERE id = :id"
        ), {"id": product_id}).fetchone()
        
        if not product:
            raise ValueError("Produit non trouvé")
        
        name, current_qty, exp = product[0], int(product[1]), str(product[2])
        
        if current_qty < quantity:
            raise ValueError(f"Stock insuffisant (disponible: {current_qty}, demandé: {quantity})")
        
        new_qty = current_qty - quantity
        
        # Si le stock atteint zéro, supprimer le produit
        if new_qty == 0:
            # Supprimer le produit
            conn.execute(text("DELETE FROM products WHERE id = :id"), {"id": product_id})
            
            # Add custom SORTIE history entry with stock depletion notice
            details = f"🔴 Sortie de stock finale: {name} (-{quantity}) - STOCK ÉPUISÉ - Produit supprimé"
            if reason:
                details += f" - Motif: {reason}"
            details += f" - Exp: {exp}"
            
            conn.execute(text(
                "INSERT INTO history (operation, product_id, product_name, old_quantity, new_quantity, "
                "old_expiry_date, new_expiry_date, details) "
                "VALUES (:op, :pid, :name, :old_qty, :new_qty, :old_exp, :new_exp, :details)"
            ), {
                "op": 'SORTIE', "pid": product_id, "name": name,
                "old_qty": current_qty, "new_qty": 0,
                "old_exp": exp, "new_exp": exp, "details": details
            })
        else:
            # Update stock normally
            conn.execute(text(
                "UPDATE products SET quantity = :qty WHERE id = :id"
            ), {"qty": new_qty, "id": product_id})
            
            # Add SORTIE history entry
            details = f"Sortie de stock: {name} (-{quantity})"
            if reason:
                details += f" - Motif: {reason}"
            details += f" - Exp: {exp}"
            
            conn.execute(text(
                "INSERT INTO history (operation, product_id, product_name, old_quantity, new_quantity, "
                "old_expiry_date, new_expiry_date, details) "
                "VALUES (:op, :pid, :name, :old_qty, :new_qty, :old_exp, :new_exp, :details)"
            ), {
                "op": 'SORTIE', "pid": product_id, "name": name,
                "old_qty": current_qty, "new_qty": new_qty,
                "old_exp": exp, "new_exp": exp, "details": details
            })


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
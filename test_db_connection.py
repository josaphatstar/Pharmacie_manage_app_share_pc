#!/usr/bin/env python3
"""Test script to verify database connection."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from db import engine, init_db
    print("✅ Import réussi")

    # Test connection
    with engine.connect() as conn:
        result = conn.execute("SELECT 1 as test")
        row = result.fetchone()
        if row and row[0] == 1:
            print("✅ Connexion à la base de données réussie")
        else:
            print("❌ Test de connexion échoué")

    # Test init_db
    init_db()
    print("✅ Initialisation de la base de données réussie")

    print("🎉 Tout est correct ! La configuration de la base de données fonctionne.")

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("Vérifiez votre DATABASE_URL dans le fichier .env")
    sys.exit(1)

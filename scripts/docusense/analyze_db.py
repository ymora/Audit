"""
Script pour analyser la base de données SQLite de DocuSense
"""

import sqlite3
from pathlib import Path

db_path = Path(r"d:\Windsurf\DocuSense-AI-v2\backend\database\docsense.db")

print(f"Analyse de la base de données: {db_path}")
print(f"Taille du fichier: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Lister toutes les tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"Tables trouvées: {len(tables)}")
for table in tables:
    print(f"  - {table[0]}")
print()

# Analyser chaque table
for table_name, in tables:
    print(f"{'='*60}")
    print(f"Table: {table_name}")
    print(f"{'='*60}")
    
    # Nombre de lignes
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"Nombre de lignes: {row_count}")
    
    # Colonnes
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"Colonnes: {len(columns)}")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Taille approximative de la table
    cursor.execute(f"SELECT COUNT(*) * 100 FROM {table_name}")
    print(f"Taille approximative: ~{row_count * 100 / 1024:.2f} KB")
    print()

conn.close()

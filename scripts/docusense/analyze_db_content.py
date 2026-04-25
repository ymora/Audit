"""
Script pour analyser le contenu des colonnes TEXT dans la base de données
"""

import sqlite3
from pathlib import Path

db_path = Path(r"d:\Windsurf\DocuSense-AI-v2\backend\database\docsense.db")

print(f"Analyse détaillée du contenu TEXT: {db_path}")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Analyser la table proofs
print(f"{'='*60}")
print(f"Table: proofs")
print(f"{'='*60}")

# Colonnes TEXT à analyser
text_columns = [
    'extracted_text', 'ai_summary', 'key_dates', 'key_amounts', 'key_people',
    'ai_results', 'processing_steps', 'error_message', 'analysis', 'risk_detection'
]

cursor.execute("SELECT id FROM proofs")
proof_ids = cursor.fetchall()

print(f"Nombre de proofs: {len(proof_ids)}")
print()

total_size = 0

for proof_id, in proof_ids:
    print(f"Proof ID: {proof_id}")
    cursor.execute(f"SELECT {', '.join(text_columns)} FROM proofs WHERE id = ?", (proof_id,))
    row = cursor.fetchone()
    
    for i, col in enumerate(text_columns):
        content = row[i]
        if content:
            size = len(content.encode('utf-8'))
            total_size += size
            print(f"  {col}: {size / 1024:.2f} KB ({len(content)} caractères)")
    
    print()

print(f"{'='*60}")
print(f"Taille totale des données TEXT: {total_size / 1024 / 1024:.2f} MB")
print(f"{'='*60}")

conn.close()

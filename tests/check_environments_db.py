#!/usr/bin/env python3
"""
Script pour vérifier et nettoyer la table environnements
"""

import sqlite3
import os
from pathlib import Path

# Trouver la base de données
temp_dir = os.environ.get('TEMP') or os.environ.get('TMP') or '/tmp'
db_path = Path(temp_dir) / "prompts_manager.db"

print(f"📂 Connexion à la base: {db_path}")

if not db_path.exists():
    print("❌ Base de données introuvable")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("\n" + "="*60)
print("📊 CONTENU DE LA TABLE environnements")
print("="*60)

# Récupérer tous les environnements
cursor.execute("""
    SELECT id, name, path, description, last_analysis, created_at, updated_at
    FROM environnements
    ORDER BY created_at
""")

environments = cursor.fetchall()

print(f"\n✅ {len(environments)} enregistrement(s) trouvé(s)\n")

for idx, env in enumerate(environments, 1):
    env_id, name, path, desc, last_analysis, created_at, updated_at = env
    print(f"Environnement #{idx}:")
    print(f"  ID: '{env_id}'")
    print(f"  Nom: '{name}'")
    print(f"  Chemin: '{path}'")
    print(f"  Description: '{desc}'")
    print(f"  Dernière analyse: {last_analysis}")
    print(f"  Créé: {created_at}")
    print(f"  Modifié: {updated_at}")
    print(f"  Chemin existe: {os.path.exists(path)}")
    print()

# Détecter les lignes invalides
print("="*60)
print("🔍 VÉRIFICATION DES DONNÉES INVALIDES")
print("="*60)

invalid_envs = []
for env in environments:
    env_id, name, path, *rest = env
    # Si l'ID est littéralement "id" ou le nom "name", c'est invalide
    if env_id in ['id', 'env_id', 'environment_id'] or name in ['name', 'nom']:
        invalid_envs.append(env)
        print(f"❌ Ligne invalide détectée: ID='{env_id}', Nom='{name}'")

if invalid_envs:
    print(f"\n⚠️ {len(invalid_envs)} ligne(s) invalide(s) trouvée(s)")
    response = input("\n❓ Voulez-vous supprimer ces lignes ? (oui/non): ").strip().lower()
    
    if response in ['oui', 'o', 'yes', 'y']:
        for env in invalid_envs:
            env_id = env[0]
            cursor.execute("DELETE FROM environnements WHERE id = ?", (env_id,))
            print(f"🗑️ Supprimé: ID='{env_id}'")
        
        conn.commit()
        print("\n✅ Lignes invalides supprimées")
        
        # Réafficher le contenu
        cursor.execute("SELECT id, name, path FROM environnements ORDER BY created_at")
        remaining = cursor.fetchall()
        print(f"\n📊 Environnements restants: {len(remaining)}")
        for env in remaining:
            print(f"  - ID: '{env[0]}', Nom: '{env[1]}'")
    else:
        print("❌ Aucune suppression effectuée")
else:
    print("✅ Aucune donnée invalide détectée")

conn.close()
print("\n✅ Vérification terminée")

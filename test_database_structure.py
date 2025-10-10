"""
Script de test pour vérifier et réparer la base de données
"""
import sys
import os

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager
from cy8_paths import get_default_db_path

def test_database():
    """Tester et réparer la base de données"""
    print("=" * 60)
    print("TEST ET RÉPARATION DE LA BASE DE DONNÉES")
    print("=" * 60)

    # Obtenir le chemin de la base par défaut
    db_path = get_default_db_path()
    print(f"\n📁 Chemin de la base: {db_path}")

    # Créer le gestionnaire de base de données
    db = cy8_database_manager(db_path)

    # Initialiser en mode dev (ne recrée pas si elle existe)
    print("\n🔧 Initialisation de la base de données...")
    db.init_database(mode="dev")

    # Vérifier la structure
    print("\n🔍 Vérification de la structure...")
    is_valid, message = db.validate_database_structure()

    if is_valid:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        print("\n🔧 Tentative de réparation...")
        success, repair_message = db.fix_database_structure()
        if success:
            print(f"✅ {repair_message}")
        else:
            print(f"❌ {repair_message}")
            return False

    # Vérifier les colonnes
    print("\n📋 Vérification des colonnes...")
    db.cursor.execute("PRAGMA table_info(prompts)")
    columns = db.cursor.fetchall()

    print(f"\nNombre de colonnes: {len(columns)}")
    for col in columns:
        col_id, name, type_str, notnull, default_val, pk = col
        print(f"  - {name:20} {type_str:10} {'(PK)' if pk else ''}")

    # Vérifier les colonnes requises
    column_names = [col[1] for col in columns]
    required = ['id', 'name', 'prompt_values', 'workflow', 'url', 'parent', 'model', 'comment', 'status', 'file', 'id_env']

    print("\n✅ Vérification des colonnes requises:")
    all_present = True
    for req in required:
        if req in column_names:
            print(f"  ✅ {req}")
        else:
            print(f"  ❌ {req} MANQUANT!")
            all_present = False

    if not all_present:
        print("\n❌ Des colonnes sont manquantes! Tentative d'ajout...")
        db.ensure_additional_columns()
        print("✅ Colonnes ajoutées")

    # Test d'un prompt
    print("\n🧪 Test de récupération d'un prompt...")
    db.cursor.execute("SELECT COUNT(*) FROM prompts")
    count = db.cursor.fetchone()[0]
    print(f"Nombre de prompts: {count}")

    if count > 0:
        prompt = db.get_prompt_by_id(1)
        if prompt:
            print(f"✅ Prompt ID 1 récupéré:")
            print(f"  Nombre de champs: {len(prompt)}")
            if len(prompt) >= 10:
                name, prompt_values, workflow, url, parent, model, comment, status, file, id_env = prompt
                print(f"  - Nom: {name}")
                print(f"  - Model: {model}")
                print(f"  - Status: {status}")
                print(f"  - ID Env: {id_env if id_env else '(vide)'}")
                print(f"  - File: {file if file else '(vide)'}")
            else:
                print(f"  ⚠️ Format ancien: {len(prompt)} champs au lieu de 10")

    # Fermer la connexion
    db.close()

    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ")
    print("=" * 60)

    return True

if __name__ == "__main__":
    try:
        success = test_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

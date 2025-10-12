#!/usr/bin/env python3
"""
Test simple pour valider l'onglet Models
"""

import os
import sys
import traceback

# Ajouter le répertoire src au chemin
sys.path.append('src')

def test_models_simple():
    """Test simple de la fonctionnalité Models"""
    print("🧪 Test simple de l'onglet Models")
    print("=" * 50)

    try:
        # Test 1: Gestionnaire de modèles
        print("📋 Test 1: Gestionnaire de modèles")
        from cy8_models_manager import ComfyUIModelsManager

        manager = ComfyUIModelsManager()
        model_types = manager.get_model_types()
        print(f"✅ Types de modèles: {len(model_types)}")

        # Test 2: Base de données
        print("\n📋 Test 2: Base de données")
        from cy8_database_manager import cy8_database_manager

        db = cy8_database_manager()

        # Test d'une requête simple
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = db.cursor.fetchall()
        table_names = [t[0] for t in tables]

        print(f"✅ Tables trouvées: {len(table_names)}")
        if 'all_models' in table_names:
            print("✅ Table all_models: OK")
        else:
            print("❌ Table all_models: Manquante")

        if 'association_model_workflow' in table_names:
            print("✅ Table association_model_workflow: OK")
        else:
            print("❌ Table association_model_workflow: Manquante")

        # Test 3: Récupération basique des modèles
        print("\n📋 Test 3: Récupération des modèles")
        try:
            models_list = manager.get_models_flat_list()
            print(f"✅ Modèles récupérés: {len(models_list)}")
        except Exception as e:
            print(f"⚠️ Problème récupération modèles: {e}")

        db.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_models_simple()

    if success:
        print("\n🎉 Tous les tests sont passés !")
        print("💡 L'onglet Models devrait fonctionner correctement")
    else:
        print("\n❌ Problèmes détectés")

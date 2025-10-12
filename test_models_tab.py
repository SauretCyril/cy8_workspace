#!/usr/bin/env python3
"""
Test de validation de l'onglet Models
"""

import sys
import os
sys.path.append('src')

def test_models_functionality():
    """Tester la fonctionnalité Models"""
    print("🧪 Test de l'onglet Models")
    print("=" * 50)

    try:
        # Test 1: Gestionnaire de modèles
        print("📋 Test 1: Gestionnaire de modèles")
        sys.path.append('src')
        from cy8_models_manager import ComfyUIModelsManager

        manager = ComfyUIModelsManager()
        model_types = manager.get_model_types()
        print(f"✅ Types de modèles: {len(model_types)}")

        # Test 2: Base de données
        print("\n📋 Test 2: Tables de base de données")
        from cy8_database_manager import CY8DatabaseManager

        db = CY8DatabaseManager()

        # S'assurer que les tables sont créées
        db.ensure_models_tables()

        # Vérifier les tables
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%model%'")
        tables = db.cursor.fetchall()
        print(f"✅ Tables modèles trouvées: {[t[0] for t in tables]}")

        # Test 3: Récupération des modèles
        print("\n📋 Test 3: Récupération et stockage des modèles")
        models_list = manager.get_models_flat_list()
        print(f"✅ Modèles récupérés: {len(models_list)}")

        # Mettre à jour la base
        db.update_all_models(models_list)

        # Vérifier le stockage
        stored_models = db.get_all_models()
        print(f"✅ Modèles stockés: {len(stored_models)}")

        # Test 4: Types uniques
        unique_types = db.get_unique_model_types()
        print(f"✅ Types uniques: {unique_types}")

        # Test 5: Filtrage par type
        print("\n📋 Test 5: Filtrage par type")
        for model_type in ['checkpoints', 'loras', 'vae']:
            models_by_type = db.get_models_by_type(model_type)
            print(f"✅ {model_type}: {len(models_by_type)} modèles")

        db.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

        print("\n🎉 Tous les tests réussis !")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_models_functionality()
    if success:
        print("✅ L'onglet Models est prêt à l'emploi !")
    else:
        print("❌ Problèmes détectés")

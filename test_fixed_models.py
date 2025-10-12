#!/usr/bin/env python3
"""
Test corrigé avec initialisation de la base de données
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager
from cy8_models_manager import ComfyUIModelsManager

def test_with_database_init():
    """Test avec initialisation correcte de la base"""
    print("🚀 TEST CORRIGÉ - Avec initialisation de la base")
    print("=" * 60)

    # 1. Initialiser le gestionnaire de base
    print("1️⃣ Initialisation de la base de données...")
    db_manager = cy8_database_manager()

    # CRUCIAL: Initialiser la base de données
    print("🔧 Initialisation de la base...")
    db_manager.init_database("dev")  # Mode dev pour ne pas effacer

    print(f"📊 Connexion après init: {db_manager.conn is not None}")
    print(f"🎯 Cursor après init: {db_manager.cursor is not None}")

    # 2. S'assurer que les tables modèles existent
    print("\n2️⃣ Vérification/création des tables modèles...")
    try:
        db_manager.ensure_models_tables()

        # Vérifier que la table existe
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='all_models';")
        table_exists = cursor.fetchone()
        print(f"📋 Table all_models: {'✅ Existe' if table_exists else '❌ Manquante'}")

    except Exception as e:
        print(f"❌ Erreur tables: {e}")
        return

    # 3. Récupérer les modèles et sauvegarder
    print("\n3️⃣ Récupération et sauvegarde des modèles...")
    try:
        models_manager = ComfyUIModelsManager()

        # Récupérer les modèles
        all_models = models_manager.get_all_models()
        flat_list = models_manager.get_models_flat_list()

        print(f"📊 Modèles récupérés: {len(flat_list)}")

        # Compter les LoRAs
        loras_count = len([m for m in flat_list if m['type'] == 'loras'])
        print(f"🎯 LoRAs récupérés: {loras_count}")

        # Sauvegarder en base
        print("💾 Sauvegarde en base...")
        db_manager.update_all_models(flat_list)

        print("✅ Sauvegarde terminée")

    except Exception as e:
        print(f"❌ Erreur récupération/sauvegarde: {e}")
        return

    # 4. Vérifier la sauvegarde
    print("\n4️⃣ Vérification de la sauvegarde...")
    try:
        # Récupérer tous les modèles de la base
        saved_models = db_manager.get_all_models()
        print(f"📂 Modèles en base: {len(saved_models)}")

        # Compter les LoRAs sauvegardés
        saved_loras = [m for m in saved_models if m['type'] == 'loras']
        print(f"🎯 LoRAs en base: {len(saved_loras)}")

        if saved_loras:
            print("✅ Premiers LoRAs en base:")
            for i, lora in enumerate(saved_loras[:5]):
                print(f"   {i+1}. {lora['name']}")
        else:
            print("❌ Aucun LoRA en base!")

        # Test de récupération par type
        print("\n🔍 Test récupération par type...")
        loras_by_type = db_manager.get_models_by_type('loras')
        print(f"🎯 LoRAs par type: {len(loras_by_type)}")

    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        import traceback
        traceback.print_exc()

    # 5. Test de filtrage
    print("\n5️⃣ Test des fonctions de filtrage...")
    try:
        # Récupérer les types uniques
        unique_types = db_manager.get_unique_model_types()
        print(f"📋 Types uniques: {len(unique_types)}")
        print(f"🎯 LoRAs dans les types: {'loras' in unique_types}")

        if unique_types:
            print("📊 Types disponibles:", unique_types[:10])  # Limiter l'affichage

    except Exception as e:
        print(f"❌ Erreur filtrage: {e}")

    print("\n" + "=" * 60)
    print("🎯 RÉSULTAT DU TEST")

    # Résumé final
    try:
        final_loras = db_manager.get_models_by_type('loras')
        print(f"✅ LORAS FINAUX EN BASE: {len(final_loras)}")

        if len(final_loras) > 0:
            print("🎉 LES LORAS SONT CORRECTEMENT RÉCUPÉRÉS ET SAUVEGARDÉS!")
        else:
            print("❌ Problème: Aucun LoRA en base")

    except Exception as e:
        print(f"❌ Erreur résumé: {e}")

if __name__ == "__main__":
    test_with_database_init()

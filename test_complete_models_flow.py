#!/usr/bin/env python3
"""
Test complet de la récupération et affichage des LoRAs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager
from cy8_models_manager import ComfyUIModelsManager

def test_complete_flow():
    """Test du flux complet de récupération des modèles"""
    print("🚀 TEST COMPLET - Flux de récupération des modèles")
    print("=" * 60)

    # 1. Initialiser les gestionnaires
    print("1️⃣ Initialisation des gestionnaires...")
    db_manager = cy8_database_manager()
    models_manager = ComfyUIModelsManager()

    # 2. Vérifier la connexion DB
    print("\n2️⃣ Vérification de la base de données...")
    try:
        # La base devrait s'initialiser automatiquement
        print(f"📂 Chemin de la base: {db_manager.db_path}")
        print(f"📊 Connexion: {db_manager.conn is not None}")
        print(f"🎯 Cursor: {db_manager.cursor is not None}")

        if db_manager.conn:
            # Vérifier les tables
            cursor = db_manager.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='all_models';")
            table_exists = cursor.fetchone()
            print(f"📋 Table all_models existe: {table_exists is not None}")

            if not table_exists:
                print("⚠️ Table all_models manquante - Création...")
                db_manager.ensure_models_tables()
        else:
            print("❌ Pas de connexion à la base")

    except Exception as e:
        print(f"❌ Erreur DB: {e}")

    # 3. Récupérer les modèles depuis ComfyUI
    print("\n3️⃣ Récupération des modèles depuis ComfyUI...")
    try:
        all_models = models_manager.get_all_models()
        total_models = sum(len(models) for models in all_models.values())
        print(f"📊 Total modèles récupérés: {total_models}")

        if 'loras' in all_models:
            loras_count = len(all_models['loras'])
            print(f"🎯 LoRAs récupérés: {loras_count}")

            if loras_count > 0:
                print("✅ Premiers LoRAs:")
                for i, lora in enumerate(all_models['loras'][:3]):
                    print(f"   {i+1}. {lora['name']}")
        else:
            print("❌ Aucun LoRA récupéré!")

    except Exception as e:
        print(f"❌ Erreur récupération: {e}")
        return

    # 4. Convertir en liste plate
    print("\n4️⃣ Conversion en liste plate...")
    try:
        flat_list = models_manager.get_models_flat_list()
        print(f"📊 Modèles en liste plate: {len(flat_list)}")

        # Compter les LoRAs
        loras_flat = [m for m in flat_list if m['type'] == 'loras']
        print(f"🎯 LoRAs en liste plate: {len(loras_flat)}")

        if loras_flat:
            print("✅ Exemples LoRAs (liste plate):")
            for i, lora in enumerate(loras_flat[:3]):
                print(f"   {i+1}. {lora['name']} (ID: {lora['id']})")

    except Exception as e:
        print(f"❌ Erreur liste plate: {e}")
        return

    # 5. Sauvegarder en base
    print("\n5️⃣ Sauvegarde en base de données...")
    try:
        if db_manager.conn:
            # S'assurer que la table existe
            db_manager.ensure_models_tables()

            # Sauvegarder
            db_manager.update_all_models(flat_list)

            # Vérifier
            saved_models = db_manager.get_all_models()
            print(f"📊 Modèles sauvegardés: {len(saved_models)}")

            # Compter les LoRAs sauvegardés
            saved_loras = [m for m in saved_models if m['type'] == 'loras']
            print(f"🎯 LoRAs sauvegardés: {len(saved_loras)}")

            if saved_loras:
                print("✅ LoRAs en base:")
                for i, lora in enumerate(saved_loras[:3]):
                    print(f"   {i+1}. {lora['name']}")
            else:
                print("❌ Aucun LoRA sauvegardé!")

        else:
            print("❌ Impossible de sauvegarder - Pas de connexion DB")

    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        import traceback
        traceback.print_exc()

    # 6. Test de récupération par type
    print("\n6️⃣ Test de récupération par type...")
    try:
        if db_manager.conn:
            loras_by_type = db_manager.get_models_by_type('loras')
            print(f"🎯 LoRAs récupérés par type: {len(loras_by_type)}")

            if loras_by_type:
                print("✅ LoRAs par type:")
                for i, lora in enumerate(loras_by_type[:3]):
                    print(f"   {i+1}. {lora.get('name', 'N/A')}")

    except Exception as e:
        print(f"❌ Erreur récupération par type: {e}")

    print("\n" + "=" * 60)
    print("🎯 FIN DU TEST")

if __name__ == "__main__":
    test_complete_flow()

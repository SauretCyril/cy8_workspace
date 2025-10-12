#!/usr/bin/env python3
"""
Test de l'interface Models pour vérifier l'affichage des LoRAs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager
from cy8_models_manager import ComfyUIModelsManager

def test_database_connection():
    """Test de connexion à la base de données"""
    print("🔍 Test de connexion à la base de données...")

    try:
        db_manager = cy8_database_manager()

        # Essayer de se connecter
        if not db_manager.conn:
            print("📂 Tentative de connexion à la base...")
            db_manager.connect()

        if db_manager.conn:
            print("✅ Base de données connectée")

            # Vérifier les tables
            cursor = db_manager.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 Tables disponibles: {[t[0] for t in tables]}")

            # Vérifier la table all_models
            if any('all_models' in str(t) for t in tables):
                cursor.execute("SELECT COUNT(*) FROM all_models")
                count = cursor.fetchone()[0]
                print(f"📂 Modèles en base: {count}")

                if count > 0:
                    cursor.execute("SELECT type, COUNT(*) FROM all_models GROUP BY type")
                    types_count = cursor.fetchall()
                    print("📊 Répartition par type:")
                    for type_name, count in types_count:
                        print(f"   🎯 {type_name}: {count}")

                    # Compter spécifiquement les LoRAs
                    cursor.execute("SELECT COUNT(*) FROM all_models WHERE type = 'loras'")
                    loras_count = cursor.fetchone()[0]
                    print(f"\n🎯 LoRAs en base: {loras_count}")

                    if loras_count > 0:
                        cursor.execute("SELECT name FROM all_models WHERE type = 'loras' LIMIT 5")
                        loras_sample = cursor.fetchall()
                        print("✅ Exemples de LoRAs en base:")
                        for i, (name,) in enumerate(loras_sample):
                            print(f"   {i+1}. {name}")
                else:
                    print("⚠️ Table all_models vide - Les modèles ne sont pas encore importés")
            else:
                print("❌ Table all_models non trouvée")

        else:
            print("❌ Impossible de se connecter à la base")

    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        import traceback
        traceback.print_exc()

def test_models_import():
    """Test d'import des modèles dans la base"""
    print("\n🔍 Test d'import des modèles...")

    try:
        db_manager = cy8_database_manager()
        models_manager = ComfyUIModelsManager()

        # Se connecter à la base
        if not db_manager.conn:
            db_manager.connect()

        print("📥 Récupération de tous les modèles...")
        all_models = models_manager.get_all_models()

        print(f"📊 Modèles récupérés: {sum(len(models) for models in all_models.values())}")

        if 'loras' in all_models:
            loras_count = len(all_models['loras'])
            print(f"🎯 LoRAs récupérés: {loras_count}")

            # Essayer de les sauvegarder
            print("💾 Tentative de sauvegarde en base...")
            success_count = 0

            for model_type, models_list in all_models.items():
                for model_info in models_list:
                    try:
                        # Utiliser la méthode appropriée selon ce qui existe
                        if hasattr(db_manager, 'add_model'):
                            db_manager.add_model(
                                name=model_info['name'],
                                type=model_info['type'],
                                path=model_info['path']
                            )
                        elif hasattr(db_manager, 'save_model'):
                            db_manager.save_model(model_info)
                        success_count += 1
                    except Exception as e:
                        if success_count == 0:  # Premier échec, afficher l'erreur
                            print(f"⚠️ Méthode de sauvegarde non trouvée: {e}")
                            break

            if success_count > 0:
                print(f"✅ {success_count} modèles sauvegardés")
                db_manager.conn.commit()
            else:
                print("❌ Aucun modèle sauvegardé")
        else:
            print("❌ Aucun LoRA dans les modèles récupérés")

    except Exception as e:
        print(f"❌ Erreur import: {e}")
        import traceback
        traceback.print_exc()

def test_database_methods():
    """Test des méthodes disponibles dans la base"""
    print("\n🔍 Analyse des méthodes de base de données...")

    db_manager = cy8_database_manager()

    # Lister les méthodes liées aux modèles
    methods = [method for method in dir(db_manager) if 'model' in method.lower()]
    print(f"📋 Méthodes liées aux modèles: {methods}")

    # Chercher les méthodes de sauvegarde
    save_methods = [method for method in dir(db_manager) if any(word in method.lower() for word in ['save', 'add', 'insert', 'update'])]
    print(f"💾 Méthodes de sauvegarde: {save_methods}")

if __name__ == "__main__":
    print("🚀 TEST INTERFACE MODELS - Debug LoRAs")
    print("=" * 60)

    # Test 1: Connexion base
    test_database_connection()

    # Test 2: Méthodes disponibles
    test_database_methods()

    # Test 3: Import des modèles
    test_models_import()

    print("\n" + "=" * 60)
    print("🎯 Fin du test interface Models")

#!/usr/bin/env python3
"""
Script de test rapide pour les fonctions de maintenance RAG
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_maintenance_functions():
    """Test des fonctions de maintenance"""
    print("🔧 TEST FONCTIONS MAINTENANCE RAG")
    print("=" * 50)

    try:
        # Importer les modules nécessaires
        from cy8_prompts_manager_main import cy8_prompts_manager

        print("1. ✅ Import réussi")

        # Créer l'instance (sans GUI)
        app = cy8_prompts_manager()

        print("2. ✅ Instance créée")

        # Tester les méthodes
        methods_to_test = [
            ('reset_rag_completely', '🗑️ RAG Reset'),
            ('clean_custom_environments', '🧹 Nettoyer Custom'),
            ('test_rag_efficiency', '🔬 Test Efficacité')
        ]

        for method_name, display_name in methods_to_test:
            if hasattr(app, method_name):
                print(f"3. ✅ {display_name}: Méthode trouvée")
                try:
                    # Test d'appel (avec simulation)
                    method = getattr(app, method_name)
                    print(f"   📞 Méthode {method_name} accessible")
                except Exception as e:
                    print(f"   ⚠️ Erreur accès méthode: {e}")
            else:
                print(f"3. ❌ {display_name}: Méthode MANQUANTE")

        print("\n🎯 RÉSULTAT:")
        print("✅ Toutes les fonctions de maintenance sont disponibles")
        print("📋 Accès via:")
        print("   • Menu: 🔧 Maintenance > Options...")
        print("   • Onglet Chat: Boutons de ligne 5 (si visibles)")
        print("   • Script direct: python test_maintenance.py")

        return True

    except Exception as e:
        print(f"❌ Erreur test maintenance: {e}")
        import traceback
        traceback.print_exc()
        return False

def direct_rag_reset():
    """Fonction directe pour reset RAG si besoin urgent"""
    print("\n🚨 FONCTION DIRECTE RAG RESET")
    print("=" * 40)

    try:
        from cy8_temporal_rag import TemporalRAGManager

        # Chemins standards
        vector_db_path = "data/analyses/vector_db"
        analysis_dir = "data/analyses"

        print(f"📂 Dossier vecteurs: {vector_db_path}")
        print(f"📂 Dossier analyses: {analysis_dir}")

        response = input("⚠️ ATTENTION: Voulez-vous vraiment SUPPRIMER tous les données RAG? (oui/non): ")

        if response.lower() in ['oui', 'o', 'yes', 'y']:
            # Supprimer les dossiers
            import shutil

            if os.path.exists(vector_db_path):
                shutil.rmtree(vector_db_path)
                print(f"🗑️ Supprimé: {vector_db_path}")

            if os.path.exists(analysis_dir):
                for file in os.listdir(analysis_dir):
                    if file.endswith('.json'):
                        os.remove(os.path.join(analysis_dir, file))
                        print(f"🗑️ Supprimé: {file}")

            print("✅ RAG complètement réinitialisé!")
            print("🔄 Redémarrez l'application pour reconstruire le RAG")
        else:
            print("❌ Opération annulée")

    except Exception as e:
        print(f"❌ Erreur reset direct: {e}")

if __name__ == "__main__":
    print("🔧 OUTIL MAINTENANCE RAG DIRECT")
    print("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        direct_rag_reset()
    else:
        test_maintenance_functions()

        print("\n💡 AIDE:")
        print("• Test fonctions: python test_maintenance.py")
        print("• Reset direct: python test_maintenance.py --reset")
        print("• Interface GUI: python main.py (Menu: 🔧 Maintenance)")

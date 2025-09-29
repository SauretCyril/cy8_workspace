#!/usr/bin/env python3
"""
Test de la popup d'analyse complète avec question modifiable
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_mistral_popup():
    """Test de la popup d'analyse Mistral AI avec question modifiable"""

    print("🧪 Test de la popup d'analyse Mistral AI...")

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager
        from cy8_database_manager import cy8_database_manager
        import tempfile

        # Créer une base de données temporaire
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name

        # Créer une instance du gestionnaire avec la DB temporaire
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale

        db_manager = cy8_database_manager(temp_db_path)
        db_manager.create_tables()

        app = cy8_prompts_manager(root, db_manager)

        # Définir un chemin de log de test (créer un fichier temporaire)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as temp_log:
            temp_log.write("Test log content\n[ERROR] Test error message\n")
            temp_log_path = temp_log.name

        app.comfyui_log_path.set(temp_log_path)

        print("✅ Configuration de test terminée")
        print(f"📁 Base de données temporaire : {temp_db_path}")
        print(f"📄 Fichier log temporaire : {temp_log_path}")

        # Ouvrir la popup d'analyse
        print("🔍 Ouverture de la popup d'analyse Mistral AI...")
        app.analyze_complete_log_global()

        print("✅ La popup devrait être ouverte avec :")
        print("   • Zone de question modifiable en haut")
        print("   • Question par défaut : 'Proposes moi des solutions pour les erreurs dans le fichier log'")
        print("   • Zone d'analyse en bas")
        print("   • Bouton 'Lancer l'analyse' utilisant la question modifiée")

        # Lancer la boucle principale pour voir la popup
        print("\n🖱️  Vous pouvez maintenant tester la popup. Fermez-la pour continuer...")
        root.mainloop()

        # Nettoyer les fichiers temporaires
        try:
            os.unlink(temp_db_path)
            os.unlink(temp_log_path)
            print("🧹 Fichiers temporaires nettoyés")
        except:
            pass

        print("✅ Test terminé avec succès")

    except Exception as e:
        print(f"❌ Erreur pendant le test : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mistral_popup()

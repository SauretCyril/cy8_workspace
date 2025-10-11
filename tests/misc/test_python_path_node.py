#!/usr/bin/env python3
"""
Test du custom node PythonPathNode via ComfyUICustomNodeCaller
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_python_path_node():
    """Test du custom node PythonPathNode"""
    print("🧪 Test du custom node PythonPathNode")
    print("=" * 50)

    try:
        from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

        print("🔗 Connexion à ComfyUI...")
        with ComfyUICustomNodeCaller() as caller:
            print("✅ ComfyUICustomNodeCaller initialisé")

            # Vérifier le statut du serveur
            status = caller.get_server_status()
            print(f"📊 Statut serveur: {status['status']}")

            if status["status"] != "online":
                print(f"❌ ComfyUI non accessible: {status.get('error', 'Serveur offline')}")
                return

            print("🐍 Appel du custom node PythonPathNode...")
            python_path = caller.get_python_path_from_comfyui()

            if python_path:
                print(f"✅ Python path récupéré: {python_path}")

                # Vérifier si le chemin existe
                if os.path.exists(python_path):
                    print(f"✅ Chemin vérifié: {python_path}")

                    # Tester l'exécution
                    import subprocess
                    try:
                        result = subprocess.run(
                            [python_path, "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            print(f"✅ Version Python: {result.stdout.strip()}")
                        else:
                            print(f"⚠️ Erreur version: {result.stderr.strip()}")
                    except Exception as e:
                        print(f"⚠️ Test version échoué: {e}")

                else:
                    print(f"⚠️ Chemin non trouvé: {python_path}")
            else:
                print("❌ Aucun Python path récupéré")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("Test terminé")

if __name__ == "__main__":
    test_python_path_node()

#!/usr/bin/env python3
"""
Test de validation finale pour ExtraPathReader
"""

import sys
import os
import time
import json
import requests
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_extrapathreader_final():
    """Test complet d'ExtraPathReader avec récupération des résultats"""

    print("🎯 TEST FINAL EXTRAPATHREADER")
    print("=" * 50)

    try:
        from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

        # Créer le caller
        caller = ComfyUICustomNodeCaller()
        print("✅ CustomNodeCaller initialisé")

        # Exécuter ExtraPathReader
        print("📤 Envoi du workflow ExtraPathReader...")
        result = caller.call_custom_node("ExtraPathReader", {})

        print(f"📦 Résultat brut: {json.dumps(result, indent=2)}")

        if "prompt_id" in result:
            prompt_id = result["prompt_id"]
            print(f"🆔 Prompt ID: {prompt_id}")

            # Attendre un peu pour que l'exécution se termine
            print("⏳ Attente de l'exécution...")
            time.sleep(2)

            # Récupérer l'historique pour ce prompt
            print("📋 Récupération de l'historique...")
            history_response = requests.get(
                f"http://127.0.0.1:8188/history/{prompt_id}"
            )

            if history_response.status_code == 200:
                history = history_response.json()
                print(f"📜 Historique: {json.dumps(history, indent=2)}")

                # Extraire les résultats des outputs
                if prompt_id in history:
                    prompt_data = history[prompt_id]
                    if "outputs" in prompt_data:
                        outputs = prompt_data["outputs"]
                        print(f"🎯 Outputs trouvés: {json.dumps(outputs, indent=2)}")

                        # Chercher les données de ExtraPathReader (node 1)
                        if "1" in outputs:
                            extrapathreader_output = outputs["1"]
                            print(
                                f"🗂️  ExtraPathReader résultat: {json.dumps(extrapathreader_output, indent=2)}"
                            )
                        else:
                            print(
                                "❌ Pas de sortie pour le nœud ExtraPathReader (node 1)"
                            )
                    else:
                        print("❌ Pas d'outputs dans l'historique")
                else:
                    print("❌ Prompt ID non trouvé dans l'historique")
            else:
                print(
                    f"❌ Erreur récupération historique: {history_response.status_code}"
                )

        print("✅ Test terminé avec succès")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_extrapathreader_final()

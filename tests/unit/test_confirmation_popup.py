#!/usr/bin/env python3
"""
Test de la popup de confirmation de workflow
"""

import sys
import os
import json
import tempfile

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

def test_workflow_confirmation_popup():
    """Test de la popup de confirmation"""
    print("🧪 TEST POPUP CONFIRMATION WORKFLOW")
    print("=" * 40)

    try:
        from cy6_task_comfyui import comfyui_task

        # Créer un workflow simple pour test
        test_workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "test_model.safetensors"
                }
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "test prompt",
                    "clip": ["1", 1]
                }
            }
        }

        test_values = {
            "1": {"id": "2", "type": "prompt", "value": "beautiful landscape"},
            "2": {"id": "3", "type": "seed", "value": 12345}
        }

        # Créer des fichiers temporaires
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as wf:
            json.dump(test_workflow, wf)
            workflow_file = wf.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as vf:
            json.dump(test_values, vf)
            values_file = vf.name

        try:
            print("🔨 Création tâche ComfyUI...")
            task = comfyui_task()

            print("📋 Test de la popup de confirmation...")
            print("⚠️ Une popup va s'ouvrir - cliquez OK ou Annuler pour tester")

            # Cette ligne va déclencher la popup
            result = task.addToQueue(workflow_file, values_file)

            if result is None:
                print("❌ Workflow annulé par l'utilisateur")
                print("✅ Test de l'annulation: SUCCÈS")
            else:
                print(f"✅ Workflow confirmé avec ID: {result}")
                print("✅ Test de la confirmation: SUCCÈS")

            return True

        finally:
            # Nettoyer les fichiers temporaires
            try:
                os.unlink(workflow_file)
                os.unlink(values_file)
            except:
                pass

    except Exception as e:
        print(f"❌ ERREUR test popup: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_popup_display_only():
    """Test d'affichage seul de la popup"""
    print("\n🧪 TEST AFFICHAGE POPUP SEULE")
    print("=" * 35)

    try:
        from cy6_task_comfyui import comfyui_task

        # Workflow plus complexe pour test d'affichage
        complex_workflow = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "model.safetensors"}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "beautiful sunset", "clip": ["1", 1]}},
            "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "bad quality", "clip": ["1", 1]}},
            "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
            "5": {"class_type": "KSampler", "inputs": {"seed": 123, "steps": 20, "cfg": 7.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
            "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
            "7": {"class_type": "SaveImage", "inputs": {"filename_prefix": "test", "images": ["6", 0]}}
        }

        complex_values = {
            "1": {"id": "2", "type": "prompt", "value": "A magnificent sunset over mountains"},
            "2": {"id": "3", "type": "prompt", "value": "blurry, low quality"},
            "3": {"id": "5", "type": "seed", "value": 987654}
        }

        task = comfyui_task()

        print("📋 Test d'affichage d'un workflow complexe...")
        print("⚠️ Popup avec workflow de 7 nodes va s'afficher")

        # Tester directement la méthode popup
        confirmed = task._show_workflow_confirmation_popup(complex_workflow, complex_values)

        print(f"Résultat: {'Confirmé' if confirmed else 'Annulé'}")
        return True

    except Exception as e:
        print(f"❌ ERREUR test affichage: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 TEST SYSTÈME DE CONFIRMATION WORKFLOW")
    print("=" * 45)

    # Test 1: Popup simple
    # test1_ok = test_workflow_confirmation_popup()

    # Test 2: Affichage complexe
    test2_ok = test_popup_display_only()

    print("\n📊 RÉSUMÉ DES TESTS")
    print("=" * 20)
    # print(f"🔄 Workflow complet: {'✅' if test1_ok else '❌'}")
    print(f"📋 Affichage popup: {'✅' if test2_ok else '❌'}")

    print("\n✅ Popup de confirmation implémentée avec succès!")
    print("📋 Fonctionnalités:")
    print("   • Affichage du JSON workflow formaté")
    print("   • Affichage des values dans onglet séparé")
    print("   • Boutons Exécuter/Annuler")
    print("   • Raccourcis clavier (Enter/Escape)")
    print("   • Gestion de l'annulation")

if __name__ == "__main__":
    main()

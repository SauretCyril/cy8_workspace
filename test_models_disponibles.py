#!/usr/bin/env python3
"""
Test pour lister les modèles disponibles dans ComfyUI
"""

import sys
import os
import requests
import json

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def get_available_models():
    """Récupérer la liste des modèles disponibles"""
    print("🔍 RÉCUPÉRATION MODÈLES DISPONIBLES")
    print("=" * 40)

    try:
        # Endpoint pour récupérer les objets de l'api
        url = "http://127.0.0.1:8188/object_info"

        print("📡 Connexion à l'API ComfyUI...")
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Chercher les types de nodes avec des modèles
            checkpoints = []
            if "CheckpointLoaderSimple" in data:
                checkpoint_info = data["CheckpointLoaderSimple"]
                if "input" in checkpoint_info and "required" in checkpoint_info["input"]:
                    if "ckpt_name" in checkpoint_info["input"]["required"]:
                        checkpoints = checkpoint_info["input"]["required"]["ckpt_name"][0]

            print(f"✅ {len(checkpoints)} modèles checkpoint trouvés:")
            for i, model in enumerate(checkpoints[:10], 1):  # Limiter à 10 pour la lisibilité
                print(f"   {i:2d}. {model}")

            if len(checkpoints) > 10:
                print(f"   ... et {len(checkpoints) - 10} autres modèles")

            return checkpoints

        else:
            print(f"❌ Erreur API: {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ Erreur récupération modèles: {e}")
        return []

def create_working_workflow(model_name):
    """Créer un workflow avec un modèle valide"""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": model_name  # Modèle valide
            }
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "a simple red flower",
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "bad quality, blurry",
                "clip": ["1", 1]
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 123456,
                "steps": 20,
                "cfg": 8.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "test_fix",
                "images": ["6", 0]
            }
        }
    }
    return workflow

def test_image_generation_with_valid_model():
    """Test de génération avec un modèle valide"""
    print("\n🎨 TEST GÉNÉRATION AVEC MODÈLE VALIDE")
    print("=" * 45)

    # Récupérer les modèles disponibles
    models = get_available_models()

    if not models:
        print("❌ Aucun modèle disponible")
        return False

    # Utiliser le premier modèle disponible
    selected_model = models[0]
    print(f"\n🎯 Modèle sélectionné: {selected_model}")

    try:
        from cy6_wkf001_Basic import comfyui_basic_task
        import tempfile
        import time

        print("🔨 Création workflow avec modèle valide...")
        workflow = create_working_workflow(selected_model)

        # Sauvegarder temporairement les fichiers
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as wf:
            json.dump(workflow, wf)
            workflow_file = wf.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as vf:
            json.dump({}, vf)
            values_file = vf.name

        try:
            print("📤 Envoi du workflow corrigé...")
            tsk = comfyui_basic_task()

            # Lancer le workflow
            prompt_id = tsk.addToQueue(workflow_file, values_file)
            print(f"✅ Workflow lancé avec ID: {prompt_id}")

            # Attendre la génération
            print("⏳ Attente génération (30s)...")
            time.sleep(30)

            # Récupérer les images
            try:
                images = tsk.GetImages(prompt_id)
                if images and len(images) > 0:
                    print(f"🎉 SUCCÈS! {len(images)} image(s) générée(s)")
                    print("✅ Le serveur ComfyUI fonctionne correctement")
                    return True
                else:
                    print("⚠️ Aucune image récupérée")
                    return False
            except Exception as img_error:
                print(f"❌ Erreur récupération images: {img_error}")
                return False

        finally:
            # Nettoyer
            try:
                os.unlink(workflow_file)
                os.unlink(values_file)
            except:
                pass

    except Exception as e:
        print(f"❌ ERREUR génération: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test principal avec modèle valide"""
    print("🔧 DIAGNOSTIC MODÈLES COMFYUI")
    print("=" * 35)

    # Phase 1: Lister les modèles
    models = get_available_models()

    if not models:
        print("\n❌ PROBLÈME: Aucun modèle disponible")
        print("🔧 ACTIONS REQUISES:")
        print("• Installer des modèles checkpoint dans ComfyUI")
        print("• Vérifier le dossier models/checkpoints/")
        print("• Redémarrer ComfyUI après installation")
        return

    # Phase 2: Test génération
    success = test_image_generation_with_valid_model()

    # Résumé
    print(f"\n📊 RÉSULTAT FINAL")
    print("=" * 20)
    if success:
        print("🎉 GÉNÉRATION D'IMAGE RÉUSSIE!")
        print("✅ Le serveur ComfyUI est pleinement opérationnel")
        print("✅ Aucun problème de plantage détecté")
    else:
        print("❌ GÉNÉRATION D'IMAGE ÉCHOUÉE")
        print("🔧 Problème persiste malgré modèle valide")
        print("📋 Vérifier les logs ComfyUI pour plus de détails")

if __name__ == "__main__":
    main()

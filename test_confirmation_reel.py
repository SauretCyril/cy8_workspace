#!/usr/bin/env python3
"""
Test de confirmation avec modèle valide
"""

import sys
import os

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_with_real_model():
    """Test avec un modèle réel du serveur"""
    print("🧪 TEST AVEC MODÈLE RÉEL")
    print("=" * 25)
    
    try:
        # Récupérer un modèle disponible
        import requests
        response = requests.get("http://127.0.0.1:8188/object_info", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            checkpoints = []
            if "CheckpointLoaderSimple" in data:
                checkpoint_info = data["CheckpointLoaderSimple"]
                if "input" in checkpoint_info and "required" in checkpoint_info["input"]:
                    if "ckpt_name" in checkpoint_info["input"]["required"]:
                        checkpoints = checkpoint_info["input"]["required"]["ckpt_name"][0]
            
            if not checkpoints:
                print("❌ Aucun modèle disponible")
                return False
                
            selected_model = checkpoints[0]
            print(f"🎯 Modèle sélectionné: {selected_model}")
            
            # Créer un workflow avec le modèle valide
            workflow = {
                "1": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {"ckpt_name": selected_model}
                },
                "2": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"text": "a simple test image", "clip": ["1", 1]}
                },
                "3": {
                    "class_type": "CLIPTextEncode", 
                    "inputs": {"text": "bad quality", "clip": ["1", 1]}
                },
                "4": {
                    "class_type": "EmptyLatentImage",
                    "inputs": {"width": 512, "height": 512, "batch_size": 1}
                },
                "5": {
                    "class_type": "KSampler",
                    "inputs": {
                        "seed": 12345, "steps": 8, "cfg": 1.5,
                        "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
                        "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]
                    }
                },
                "6": {
                    "class_type": "VAEDecode",
                    "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
                },
                "7": {
                    "class_type": "SaveImage",
                    "inputs": {"filename_prefix": "test_confirm", "images": ["6", 0]}
                }
            }
            
            values = {}
            
            # Test avec le système de confirmation
            from cy6_task_comfyui import comfyui_task
            import tempfile
            import json
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as wf:
                json.dump(workflow, wf)
                workflow_file = wf.name
                
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as vf:
                json.dump(values, vf)
                values_file = vf.name
            
            try:
                print("📋 Lancement avec popup de confirmation...")
                print("✅ Cliquez 'Exécuter le Workflow' pour confirmer")
                
                task = comfyui_task()
                result = task.addToQueue(workflow_file, values_file)
                
                if result is None:
                    print("❌ Workflow annulé par l'utilisateur")
                    return False
                else:
                    print(f"🎉 Workflow confirmé et lancé avec ID: {result}")
                    print("✅ Le système de confirmation fonctionne!")
                    return True
                    
            finally:
                try:
                    os.unlink(workflow_file)
                    os.unlink(values_file)
                except:
                    pass
        else:
            print("❌ Serveur ComfyUI inaccessible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TEST CONFIRMATION AVEC MODÈLE RÉEL")
    print("=" * 40)
    
    success = test_with_real_model()
    
    print(f"\n📊 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    
    if success:
        print("\n🎉 POPUP DE CONFIRMATION OPÉRATIONNELLE!")
        print("📋 La popup s'affiche avant chaque exécution")
        print("✅ L'utilisateur peut valider ou annuler")
        print("🔄 Le workflow ne s'exécute qu'après confirmation")
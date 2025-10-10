#!/usr/bin/env python3
"""
Test de génération d'image ComfyUI pour diagnostiquer les plantages serveur
"""

import sys
import os
import time
import json

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_server_health():
    """Test de base de la santé du serveur"""
    print("🔍 TEST SANTÉ SERVEUR COMFYUI")
    print("=" * 40)

    try:
        from cy6_websocket_api_client import get_queue_status

        print("📡 Connexion au serveur...")
        status = get_queue_status()

        if status is None:
            print("❌ ERREUR: Serveur inaccessible")
            return False

        print("✅ Serveur accessible")
        print(f"   📊 Queue en attente: {len(status.get('queue_pending', []))}")
        print(f"   🔄 Queue en cours: {len(status.get('queue_running', []))}")
        return True

    except Exception as e:
        print(f"❌ ERREUR connexion: {e}")
        return False

def create_minimal_workflow():
    """Créer un workflow minimal pour test"""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "flux1-dev-fp8.safetensors"
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
                "steps": 8,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
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
                "filename_prefix": "test_diagnostic",
                "images": ["6", 0]
            }
        }
    }
    return workflow

def test_simple_image_generation():
    """Test de génération d'image simple"""
    print("\n🎨 TEST GÉNÉRATION IMAGE SIMPLE")
    print("=" * 40)

    try:
        from cy6_websocket_api_client import socket_queue_prompt
        from cy6_wkf001_Basic import comfyui_basic_task
        import tempfile

        print("🔨 Création workflow minimal...")
        workflow = create_minimal_workflow()

        # Sauvegarder temporairement les fichiers
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as wf:
            json.dump(workflow, wf)
            workflow_file = wf.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as vf:
            json.dump({}, vf)  # Values vides pour ce test simple
            values_file = vf.name

        try:
            print("📤 Envoi du workflow au serveur...")
            tsk = comfyui_basic_task()

            # Lancer le workflow avec la bonne méthode
            prompt_id = tsk.addToQueue(workflow_file, values_file)

            print(f"✅ Workflow lancé avec ID: {prompt_id}")

            # Attendre un peu
            print("⏳ Attente génération (15s)...")
            time.sleep(15)

            # Vérifier si des images ont été générées
            try:
                images = tsk.GetImages(prompt_id)
                if images and len(images) > 0:
                    print(f"✅ {len(images)} image(s) générée(s) avec succès")
                    return True
                else:
                    print("⚠️ Aucune image récupérée")
                    return False
            except Exception as img_error:
                print(f"❌ Erreur récupération images: {img_error}")
                return False

        finally:
            # Nettoyer les fichiers temporaires
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

def test_workflow_monitoring():
    """Test du système de monitoring des workflows"""
    print("\n👁️ TEST MONITORING WORKFLOWS")
    print("=" * 40)

    try:
        from cy8_workflow_monitor import WorkflowQueue, WorkflowMonitor, WorkflowTask, WorkflowStatus

        print("📋 Création pile de surveillance...")
        queue = WorkflowQueue()
        monitor = WorkflowMonitor(queue)

        # Test avec intervalles courts
        monitor.check_interval = 2
        monitor.server_check_interval = 5
        monitor.max_server_errors = 2

        print("🚀 Démarrage monitoring...")
        monitor.start()

        # Ajouter une tâche de test
        test_task = WorkflowTask(
            prompt_id=999,
            execution_id="test_monitoring",
            comfyui_prompt_id="test_monitor_123",
            status=WorkflowStatus.QUEUED,
            prompt_name="Test Monitoring",
            timestamp=time.time(),
            comfyui_task_instance=None
        )

        queue.add_task(test_task)
        print("✅ Tâche de test ajoutée")

        # Surveiller pendant 15 secondes
        print("⏳ Surveillance pendant 15s...")
        start_time = time.time()

        while monitor.running and (time.time() - start_time) < 15:
            tasks = queue.get_all_tasks()
            if tasks:
                for task_id, task in tasks.items():
                    print(f"   📊 Tâche {task_id}: {task.status.value}")
            time.sleep(3)

        print("⏹️ Arrêt monitoring...")
        monitor.stop()

        final_tasks = queue.get_all_tasks()
        print(f"📊 Tâches finales: {len(final_tasks)}")

        return True

    except Exception as e:
        print(f"❌ ERREUR monitoring: {e}")
        import traceback
        traceback.print_exc()
        return False

def diagnose_server_issues():
    """Diagnostiquer les problèmes potentiels du serveur"""
    print("\n🔧 DIAGNOSTIC PROBLÈMES SERVEUR")
    print("=" * 40)

    issues_found = []

    # Test 1: Modèles disponibles
    try:
        print("🔍 Vérification modèles disponibles...")
        # TODO: Ajouter test de disponibilité des modèles
        print("⚠️ Test modèles non implémenté")
        issues_found.append("Modèles non vérifiés")
    except Exception as e:
        print(f"❌ Erreur test modèles: {e}")
        issues_found.append(f"Erreur modèles: {e}")

    # Test 2: Mémoire disponible
    try:
        print("🔍 Vérification mémoire...")
        import psutil
        memory = psutil.virtual_memory()
        gpu_memory = "Non détectée"

        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.free,memory.total', '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_memory = result.stdout.strip()
        except:
            pass

        print(f"   💾 RAM libre: {memory.available // (1024**3)}GB / {memory.total // (1024**3)}GB")
        print(f"   🎮 GPU mémoire: {gpu_memory}")

        if memory.available < 4 * 1024**3:  # Moins de 4GB
            issues_found.append("RAM faible (< 4GB)")

    except Exception as e:
        print(f"❌ Erreur test mémoire: {e}")
        issues_found.append(f"Erreur mémoire: {e}")

    # Test 3: Ports et connexions
    try:
        print("🔍 Vérification ports...")
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 8188))
        sock.close()

        if result == 0:
            print("   ✅ Port 8188 accessible")
        else:
            print("   ❌ Port 8188 inaccessible")
            issues_found.append("Port 8188 fermé")

    except Exception as e:
        print(f"❌ Erreur test ports: {e}")
        issues_found.append(f"Erreur ports: {e}")

    return issues_found

def main():
    """Test principal de diagnostic"""
    print("🚨 DIAGNOSTIC PLANTAGES SERVEUR COMFYUI")
    print("=" * 50)

    # Phase 1: Santé serveur
    server_ok = test_server_health()

    if not server_ok:
        print("\n❌ ARRÊT: Serveur inaccessible")
        return

    # Phase 2: Diagnostic général
    issues = diagnose_server_issues()

    # Phase 3: Test génération simple
    generation_ok = test_simple_image_generation()

    # Phase 4: Test monitoring
    monitoring_ok = test_workflow_monitoring()

    # Résumé
    print("\n📊 RÉSUMÉ DIAGNOSTIC")
    print("=" * 25)
    print(f"🔌 Serveur accessible: {'✅' if server_ok else '❌'}")
    print(f"🎨 Génération image: {'✅' if generation_ok else '❌'}")
    print(f"👁️ Monitoring: {'✅' if monitoring_ok else '❌'}")

    if issues:
        print(f"\n⚠️ PROBLÈMES DÉTECTÉS ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ AUCUN PROBLÈME DÉTECTÉ")

    if not generation_ok:
        print("\n🔧 RECOMMANDATIONS:")
        print("• Vérifier les modèles ComfyUI")
        print("• Contrôler les logs ComfyUI")
        print("• Redémarrer le serveur ComfyUI")
        print("• Vérifier l'espace disque")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test de monitoring en temps réel avec tâche simulée
"""

import sys
import os
import time

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def simulate_workflow_execution():
    """Simuler l'exécution d'un workflow avec monitoring"""
    print("🧪 Simulation d'exécution de workflow avec monitoring")
    print("=" * 60)

    try:
        from cy8_workflow_monitor import WorkflowQueue, WorkflowMonitor, WorkflowTask, WorkflowStatus

        # Créer les instances
        queue = WorkflowQueue()

        # Callbacks détaillés
        def status_callback(execution_id, message, progress):
            timestamp = time.strftime("%H:%M:%S")
            print(f"📊 [{timestamp}] STATUS: {execution_id} -> {message} ({progress}%)")

        def images_callback(prompt_id, images):
            print(f"📸 IMAGES: Reçu {len(images)} images pour prompt {prompt_id}")
            return len(images)

        def prompt_status_callback(prompt_id, status):
            print(f"📝 PROMPT: {prompt_id} -> {status}")

        monitor = WorkflowMonitor(
            queue,
            status_callback=status_callback,
            images_callback=images_callback,
            prompt_status_callback=prompt_status_callback
        )

        # Démarrer le monitoring
        print("🚀 Démarrage du monitoring...")
        monitor.start()
        time.sleep(1)

        # Créer une tâche simulée
        print("📋 Création d'une tâche simulée...")
        simulated_task = WorkflowTask(
            prompt_id=999,
            execution_id="test_exec_999",
            comfyui_prompt_id="simulated_prompt_123",
            status=WorkflowStatus.QUEUED,
            prompt_name="Test Prompt Simulation",
            timestamp=time.time()
        )

        # Ajouter la tâche à la queue
        queue.add_task(simulated_task)

        # Observer le monitoring pendant un moment
        print("👁️ Observation du monitoring (15 secondes)...")
        for i in range(15):
            time.sleep(1)

            # Afficher l'état tous les 3 secondes
            if i % 3 == 0:
                debug_info = monitor.get_debug_info()
                print(f"🔧 [{i+1}s] Tasks: {debug_info['tasks_count']}, Status: {debug_info['monitor_status']}")

                for task_detail in debug_info['tasks_details']:
                    print(f"     📋 {task_detail['comfyui_prompt_id']}: {task_detail['status']} (⏱️ {task_detail['elapsed_seconds']}s)")

            # Simuler le passage du statut après 5 secondes
            if i == 5:
                print("🔄 Simulation: Passage en RUNNING...")
                queue.update_task_status("simulated_prompt_123", WorkflowStatus.RUNNING, progress=50)

            # Simuler la completion après 10 secondes
            if i == 10:
                print("✅ Simulation: Passage en COMPLETED...")
                queue.update_task_status("simulated_prompt_123", WorkflowStatus.COMPLETED, progress=95)

        # Nettoyer
        print("🧹 Nettoyage...")
        queue.clear()
        monitor.stop()

        print("✅ Test de simulation terminé")
        return True

    except Exception as e:
        print(f"❌ Erreur simulation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_comfyui_prompt():
    """Tester avec un vrai prompt ComfyUI si disponible"""
    print("🧪 Test avec un prompt ComfyUI réel")
    print("=" * 60)

    try:
        from cy6_websocket_api_client import get_queue_status, get_history

        # Vérifier s'il y a des prompts dans l'historique récent
        print("🔍 Recherche de prompts récents dans l'historique...")

        # Essayer de récupérer l'historique général (pas d'ID spécifique)
        try:
            import urllib.request
            import json

            with urllib.request.urlopen("http://127.0.0.1:8188/history") as response:
                full_history = json.loads(response.read())

            if full_history:
                # Prendre les 3 prompts les plus récents
                recent_prompts = list(full_history.keys())[-3:]
                print(f"📊 {len(recent_prompts)} prompts récents trouvés:")

                for prompt_id in recent_prompts:
                    prompt_data = full_history[prompt_id]
                    status = prompt_data.get("status", {})
                    outputs = prompt_data.get("outputs", {})

                    print(f"   📝 {prompt_id}:")
                    print(f"      Status: {status.get('status_str', 'unknown')}")
                    print(f"      Completed: {status.get('completed', False)}")
                    print(f"      Outputs: {len(outputs)} nœuds")

                    # Tester la récupération d'images pour ce prompt
                    if outputs:
                        print(f"      🔍 Test récupération images...")
                        try:
                            from cy6_wkf001_Basic import comfyui_basic_task
                            task = comfyui_basic_task()
                            images = task.GetImages(prompt_id)

                            if images:
                                print(f"      ✅ {len(images)} images récupérées")
                            else:
                                print(f"      ⚠️ Aucune image récupérée")

                        except Exception as img_error:
                            print(f"      ❌ Erreur récupération: {img_error}")

                    print()
            else:
                print("📭 Aucun historique trouvé")

        except Exception as hist_error:
            print(f"⚠️ Erreur accès historique: {hist_error}")

        return True

    except Exception as e:
        print(f"❌ Erreur test réel: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Test de monitoring en temps réel")
    print("=" * 80)

    try:
        # Test 1: Simulation
        test1 = simulate_workflow_execution()
        print()

        # Test 2: Données réelles
        test2 = test_real_comfyui_prompt()
        print()

        print("=" * 80)
        if test1 and test2:
            print("🎉 TESTS RÉUSSIS !")
            print("✅ Monitoring simulation OK")
            print("✅ Test données réelles OK")
        else:
            print("⚠️ PROBLÈMES DÉTECTÉS")

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

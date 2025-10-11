#!/usr/bin/env python3
"""
Patch temporaire pour déboguer le WorkflowMonitor dans l'application
"""

import sys
import os

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def patch_workflow_monitor():
    """Appliquer un patch de debugging au WorkflowMonitor"""
    print("🔧 Application du patch de debugging WorkflowMonitor")

    try:
        # Importer le module original
        import cy8_workflow_monitor

        # Sauvegarder les méthodes originales
        original_check_workflow_status = cy8_workflow_monitor.WorkflowMonitor._check_workflow_status
        original_retrieve_images = cy8_workflow_monitor.WorkflowMonitor._retrieve_images
        original_add_task = cy8_workflow_monitor.WorkflowQueue.add_task

        def patched_add_task(self, task):
            """Version patchée de add_task avec debug"""
            print(f"🔧 PATCH DEBUG - add_task appelé:")
            print(f"   - prompt_id: {task.prompt_id}")
            print(f"   - execution_id: {task.execution_id}")
            print(f"   - comfyui_prompt_id: {task.comfyui_prompt_id}")
            print(f"   - status: {task.status}")
            print(f"   - timestamp: {task.timestamp}")

            # Vérifier immédiatement si ce prompt existe dans ComfyUI
            try:
                from cy6_websocket_api_client import is_prompt_in_queue, get_queue_status
                queue_status = get_queue_status()
                in_queue = is_prompt_in_queue(task.comfyui_prompt_id)

                print(f"   🔍 Vérification immédiate ComfyUI:")
                print(f"      - Queue accessible: {queue_status is not None}")
                if queue_status:
                    print(f"      - Pending: {len(queue_status.get('queue_pending', []))}")
                    print(f"      - Running: {len(queue_status.get('queue_running', []))}")
                print(f"      - Prompt en queue: {in_queue}")

            except Exception as e:
                print(f"   ❌ Erreur vérification: {e}")

            # Appeler la méthode originale
            return original_add_task(self, task)

        def patched_check_workflow_status(self, task):
            """Version patchée de _check_workflow_status avec debug"""
            print(f"🔧 PATCH DEBUG - _check_workflow_status appelé:")
            elapsed = time.time() - task.timestamp
            print(f"   - Tâche: {task.comfyui_prompt_id}")
            print(f"   - Statut: {task.status}")
            print(f"   - Temps écoulé: {elapsed:.1f}s")

            # Appeler la méthode originale
            return original_check_workflow_status(self, task)

        def patched_retrieve_images(self, task):
            """Version patchée de _retrieve_images avec debug"""
            print(f"🔧 PATCH DEBUG - _retrieve_images appelé:")
            print(f"   - Tâche: {task.comfyui_prompt_id}")
            print(f"   - Instance ComfyUI: {task.comfyui_task_instance is not None}")
            if task.comfyui_task_instance:
                has_ws = hasattr(task.comfyui_task_instance, 'ws')
                ws_valid = has_ws and task.comfyui_task_instance.ws is not None
                print(f"   - WebSocket disponible: {has_ws}, valide: {ws_valid}")

            # Appeler la méthode originale
            return original_retrieve_images(self, task)

        # Appliquer les patches
        cy8_workflow_monitor.WorkflowQueue.add_task = patched_add_task
        cy8_workflow_monitor.WorkflowMonitor._check_workflow_status = patched_check_workflow_status
        cy8_workflow_monitor.WorkflowMonitor._retrieve_images = patched_retrieve_images

        print("✅ Patch de debugging appliqué avec succès")
        print("💡 Maintenant lancez l'application et démarrez un workflow")

        return True

    except Exception as e:
        print(f"❌ Erreur application patch: {e}")
        import traceback
        traceback.print_exc()
        return False


def monitor_workflow_queue():
    """Monitorer la queue ComfyUI en continu pour voir les vrais workflows"""
    print("👁️ Monitoring de la queue ComfyUI en continu")
    print("💡 Lancez un workflow dans l'application pour voir l'activité")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    print()

    try:
        from cy6_websocket_api_client import get_queue_status
        import time

        previous_state = None

        while True:
            try:
                queue_status = get_queue_status()

                if queue_status:
                    pending = queue_status.get("queue_pending", [])
                    running = queue_status.get("queue_running", [])

                    current_state = {
                        'pending_count': len(pending),
                        'running_count': len(running),
                        'pending_ids': [item[1] for item in pending] if pending else [],
                        'running_ids': [item[1] for item in running] if running else []
                    }

                    # Afficher les changements
                    if current_state != previous_state:
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"📋 [{timestamp}] Queue: {current_state['pending_count']} pending, {current_state['running_count']} running")

                        # Afficher les nouveaux workflows
                        if current_state['pending_ids']:
                            new_pending = set(current_state['pending_ids']) - set(previous_state.get('pending_ids', []) if previous_state else [])
                            if new_pending:
                                print(f"   🆕 Nouveaux en attente: {list(new_pending)}")

                        if current_state['running_ids']:
                            new_running = set(current_state['running_ids']) - set(previous_state.get('running_ids', []) if previous_state else [])
                            if new_running:
                                print(f"   🏃 Nouveaux en cours: {list(new_running)}")

                        # Afficher les workflows terminés
                        if previous_state:
                            finished_pending = set(previous_state.get('pending_ids', [])) - set(current_state['pending_ids'])
                            finished_running = set(previous_state.get('running_ids', [])) - set(current_state['running_ids'])

                            if finished_pending:
                                print(f"   ✅ Sortis de pending: {list(finished_pending)}")
                            if finished_running:
                                print(f"   🏁 Terminés: {list(finished_running)}")

                    previous_state = current_state

                time.sleep(1)

            except KeyboardInterrupt:
                print("\n🛑 Arrêt du monitoring")
                break
            except Exception as e:
                print(f"⚠️ Erreur: {e}")
                time.sleep(1)

    except Exception as e:
        print(f"❌ Erreur monitoring: {e}")


if __name__ == "__main__":
    print("🚀 Patch de debugging WorkflowMonitor")
    print("=" * 60)

    import time

    # Appliquer le patch
    if patch_workflow_monitor():
        print()
        print("🎯 INSTRUCTIONS:")
        print("1. Ce script a patché le WorkflowMonitor avec du debug")
        print("2. Maintenant, lancez l'application cy8_prompts_manager")
        print("3. Démarrez un workflow et observez les logs détaillés")
        print("4. Ou appuyez sur Entrée pour monitorer la queue ComfyUI")
        print()

        choice = input("Appuyez sur Entrée pour monitorer la queue ComfyUI ou Ctrl+C pour quitter: ")
        monitor_workflow_queue()
    else:
        print("❌ Impossible d'appliquer le patch")

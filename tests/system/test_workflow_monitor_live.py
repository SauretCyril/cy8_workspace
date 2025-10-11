#!/usr/bin/env python3
"""
Test en direct du WorkflowMonitor avec l'application principale
"""

import sys
import os
import time
import json

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_with_app_integration():
    """Tester l'intégration avec l'application principale"""
    print("🧪 Test d'intégration avec l'application principale")
    print("=" * 60)

    try:
        # Importer les composants de l'application
        from cy8_workflow_monitor import WorkflowQueue, WorkflowMonitor

        # Créer un monitoring identique à celui de l'application
        workflow_queue = WorkflowQueue()

        def status_callback(execution_id, message, progress):
            timestamp = time.strftime("%H:%M:%S")
            print(f"📊 [{timestamp}] APP STATUS: {execution_id} -> {message} ({progress}%)")

        def images_callback(prompt_id, output_images):
            print(f"📸 APP IMAGES: Prompt {prompt_id} -> {len(output_images)} images")
            return len(output_images)

        def prompt_status_callback(prompt_id, status):
            print(f"📝 APP PROMPT: {prompt_id} -> {status}")

        def server_failure_callback():
            print("🚨 APP SERVER FAILURE: Panne serveur détectée")

        workflow_monitor = WorkflowMonitor(
            workflow_queue,
            status_callback=status_callback,
            images_callback=images_callback,
            prompt_status_callback=prompt_status_callback,
            server_failure_callback=server_failure_callback
        )

        print("🚀 Démarrage du monitoring (comme dans l'app)...")
        workflow_monitor.start()

        # Vérifier l'état initial
        status = workflow_monitor.get_monitor_status()
        debug_info = workflow_monitor.get_debug_info()

        print(f"📊 Status initial:")
        print(f"   - Statut: {status['status']}")
        print(f"   - Thread actif: {status['running']}")
        print(f"   - Tâches actives: {status['active_tasks']}")

        # Instructions pour l'utilisateur
        print("\n" + "="*60)
        print("🎯 INSTRUCTIONS POUR TEST EN DIRECT:")
        print("1. 🚀 Lancez l'application cy8_prompts_manager")
        print("2. ▶️ Démarrez un workflow (cliquez sur Execute)")
        print("3. 👀 Observez les logs de ce script pendant l'exécution")
        print("4. ⏹️ Revenez ici quand le workflow est terminé")
        print("="*60)

        # Surveillance continue
        print("\n👁️ Surveillance en cours... (30 secondes)")
        for i in range(30):
            time.sleep(1)

            # Vérifier les tâches actives
            debug_info = workflow_monitor.get_debug_info()
            if debug_info['tasks_count'] > 0:
                print(f"\n🔍 [{i+1}s] Tâches détectées!")
                for task in debug_info['tasks_details']:
                    print(f"   📋 {task['comfyui_prompt_id']}: {task['status']} (⏱️ {task['elapsed_seconds']}s)")

            # Affichage périodique
            if i % 10 == 0 and i > 0:
                status = workflow_monitor.get_monitor_status()
                print(f"⏱️ [{i}s] Monitor: {status['status']}, Workflows: {status['workflows_processed']}, Images: {status['total_images_retrieved']}")

        # Arrêter le monitoring
        print("\n🛑 Arrêt du monitoring...")
        workflow_monitor.stop()

        # Résumé final
        final_status = workflow_monitor.get_monitor_status()
        print(f"\n📊 Résumé final:")
        print(f"   - Workflows traités: {final_status['workflows_processed']}")
        print(f"   - Images récupérées: {final_status['total_images_retrieved']}")
        print(f"   - Erreurs serveur: {final_status['server_error_count']}")

        print("✅ Test d'intégration terminé")
        return True

    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        import traceback
        traceback.print_exc()
        return False


def monitor_comfyui_queue():
    """Monitorer la queue ComfyUI en continu"""
    print("🧪 Monitoring continu de la queue ComfyUI")
    print("=" * 60)

    try:
        from cy6_websocket_api_client import get_queue_status, get_history

        print("👁️ Surveillance de la queue ComfyUI (20 secondes)...")
        print("💡 Tip: Lancez un workflow dans ComfyUI pour voir l'activité")
        print()

        previous_queue_state = None

        for i in range(20):
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

                    # Afficher seulement les changements
                    if current_state != previous_queue_state:
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"📋 [{timestamp}] Queue: {current_state['pending_count']} pending, {current_state['running_count']} running")

                        if current_state['running_ids']:
                            print(f"   🔄 En cours: {current_state['running_ids']}")
                        if current_state['pending_ids']:
                            print(f"   ⏳ En attente: {current_state['pending_ids'][:3]}{'...' if len(current_state['pending_ids']) > 3 else ''}")

                    previous_queue_state = current_state
                else:
                    if previous_queue_state is not None:  # Afficher seulement si c'était accessible avant
                        print(f"❌ [{time.strftime('%H:%M:%S')}] Queue inaccessible")
                        previous_queue_state = None

            except Exception as e:
                print(f"⚠️ Erreur accès queue: {e}")

            time.sleep(1)

        print("\n✅ Monitoring de la queue terminé")
        return True

    except Exception as e:
        print(f"❌ Erreur monitoring queue: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Test WorkflowMonitor en direct")
    print("=" * 80)

    try:
        # Test 1: Monitoring de la queue ComfyUI
        print("Phase 1: Monitoring de la queue ComfyUI")
        test1 = monitor_comfyui_queue()
        print()

        # Test 2: Intégration avec l'application
        print("Phase 2: Test d'intégration avec l'application")
        test2 = test_with_app_integration()
        print()

        print("=" * 80)
        if test1 and test2:
            print("🎉 TESTS EN DIRECT RÉUSSIS !")
            print("✅ Monitoring queue ComfyUI OK")
            print("✅ Intégration application OK")
            print()
            print("🔧 RECOMMANDATIONS:")
            print("1. Le monitoring fonctionne correctement")
            print("2. Vérifiez que les workflows utilisent les bons prompt_id")
            print("3. Assurez-vous que WebSocket est disponible pour GetImages")
        else:
            print("⚠️ PROBLÈMES DÉTECTÉS LORS DES TESTS")

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

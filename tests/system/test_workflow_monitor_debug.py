#!/usr/bin/env python3
"""
Script de diagnostic du WorkflowMonitor
"""

import sys
import os
import time
import json

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_comfyui_connection():
    """Tester la connexion à ComfyUI"""
    print("🔍 Test de connexion ComfyUI")
    print("=" * 50)

    try:
        from cy6_websocket_api_client import get_queue_status, get_history

        # Test 1: Statut de la queue
        print("📋 Test statut de la queue...")
        queue_status = get_queue_status()

        if queue_status:
            pending = len(queue_status.get("queue_pending", []))
            running = len(queue_status.get("queue_running", []))
            print(f"✅ Queue accessible: {pending} en attente, {running} en cours")

            # Afficher les tâches en cours
            if queue_status.get("queue_running"):
                for item in queue_status["queue_running"]:
                    print(f"   🔄 En cours: {item[1]} (numéro: {item[0]})")

            if queue_status.get("queue_pending"):
                for item in queue_status["queue_pending"][:3]:  # 3 premiers seulement
                    print(f"   ⏳ En attente: {item[1]} (numéro: {item[0]})")

        else:
            print("❌ Impossible d'accéder à la queue ComfyUI")
            return False

        print()
        return True

    except Exception as e:
        print(f"❌ Erreur connexion ComfyUI: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_monitor():
    """Tester le WorkflowMonitor"""
    print("🔍 Test du WorkflowMonitor")
    print("=" * 50)

    try:
        from cy8_workflow_monitor import WorkflowQueue, WorkflowMonitor, WorkflowTask, WorkflowStatus

        # Créer les instances
        queue = WorkflowQueue()

        # Callbacks pour observer les événements
        status_updates = []

        def status_callback(execution_id, message, progress):
            timestamp = time.strftime("%H:%M:%S")
            status_updates.append({
                'time': timestamp,
                'execution_id': execution_id,
                'message': message,
                'progress': progress
            })
            print(f"📊 [{timestamp}] Status: {execution_id} -> {message} ({progress}%)")

        def images_callback(prompt_id, images):
            print(f"📸 Images reçues pour prompt {prompt_id}: {len(images)} images")
            return len(images)  # Simuler l'ajout en base

        def prompt_status_callback(prompt_id, status):
            print(f"📝 Prompt {prompt_id} marqué comme: {status}")

        monitor = WorkflowMonitor(
            queue,
            status_callback=status_callback,
            images_callback=images_callback,
            prompt_status_callback=prompt_status_callback
        )

        # Démarrer le monitoring
        print("🚀 Démarrage du monitoring...")
        monitor.start()

        # Afficher les informations de debug
        debug_info = monitor.get_debug_info()
        print(f"🔧 Info debug: {json.dumps(debug_info, indent=2)}")

        # Attendre un peu pour voir l'activité
        print("⏱️ Observation pendant 10 secondes...")
        for i in range(10):
            time.sleep(1)
            print(f"   {i+1}/10 - Monitoring actif: {monitor.running}")

            # Afficher les tâches actives
            tasks = queue.get_all_tasks()
            if tasks:
                print(f"   📋 {len(tasks)} tâches surveillées:")
                for prompt_id, task in tasks.items():
                    elapsed = time.time() - task.timestamp
                    print(f"      - {prompt_id}: {task.status.value} (⏱️ {elapsed:.1f}s)")

        # Arrêter le monitoring
        print("🛑 Arrêt du monitoring...")
        monitor.stop()

        # Afficher le résumé des mises à jour
        print("\n📊 Résumé des mises à jour de statut:")
        for update in status_updates:
            print(f"   [{update['time']}] {update['execution_id']}: {update['message']}")

        print("✅ Test du WorkflowMonitor terminé")
        return True

    except Exception as e:
        print(f"❌ Erreur test WorkflowMonitor: {e}")
        import traceback
        traceback.print_exc()
        return False


def analyze_issue():
    """Analyser les problèmes potentiels"""
    print("🔍 Analyse des problèmes potentiels")
    print("=" * 50)

    issues_found = []

    # Vérifier la configuration
    try:
        from cy6_websocket_api_client import server_address
        print(f"🌐 Adresse serveur: {server_address}")

        if not server_address or server_address == "127.0.0.1:8188":
            print("✅ Adresse serveur standard")
        else:
            print(f"⚠️ Adresse serveur non-standard: {server_address}")

    except Exception as e:
        issues_found.append(f"Configuration serveur: {e}")

    # Vérifier les fonctions de surveillance
    try:
        from cy6_websocket_api_client import is_prompt_in_queue, get_history
        print("✅ Fonctions de surveillance disponibles")
    except ImportError as e:
        issues_found.append(f"Fonctions manquantes: {e}")

    # Vérifier les workflows en cours
    try:
        from cy6_websocket_api_client import get_queue_status
        queue_status = get_queue_status()

        if queue_status:
            running_tasks = queue_status.get("queue_running", [])
            if running_tasks:
                print(f"📋 {len(running_tasks)} workflows en cours dans ComfyUI")
                for task in running_tasks:
                    print(f"   - ID: {task[1]}")
            else:
                print("📋 Aucun workflow en cours dans ComfyUI")
        else:
            issues_found.append("Impossible d'accéder à la queue ComfyUI")

    except Exception as e:
        issues_found.append(f"Vérification queue: {e}")

    if issues_found:
        print("\n⚠️ Problèmes détectés:")
        for issue in issues_found:
            print(f"   - {issue}")
    else:
        print("\n✅ Aucun problème détecté")

    return len(issues_found) == 0


if __name__ == "__main__":
    print("🚀 Diagnostic WorkflowMonitor")
    print("=" * 80)

    try:
        # Tests en séquence
        test1 = test_comfyui_connection()
        print()

        test2 = analyze_issue()
        print()

        test3 = test_workflow_monitor()
        print()

        print("=" * 80)
        if test1 and test2 and test3:
            print("🎉 DIAGNOSTIC RÉUSSI !")
            print("✅ ComfyUI accessible")
            print("✅ WorkflowMonitor fonctionnel")
            print("✅ Surveillance opérationnelle")
        else:
            print("⚠️ PROBLÈMES DÉTECTÉS")
            if not test1:
                print("❌ Problème de connexion ComfyUI")
            if not test2:
                print("❌ Problème de configuration")
            if not test3:
                print("❌ Problème WorkflowMonitor")

    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

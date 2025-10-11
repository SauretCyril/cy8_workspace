#!/usr/bin/env python3
"""
Diagnostic du problème "10% puis plus rien"
"""

import sys
import os
import time

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def analyze_10_percent_issue():
    """Analyser le problème des 10% qui restent bloqués"""
    print("🔍 Analyse du problème '10% puis plus rien'")
    print("=" * 60)

    print("📋 Étapes de diagnostic:")
    print("1. 🔍 Vérification de la progression normale")
    print("2. 🔍 Identification des points de blocage")
    print("3. 🔍 Test de détection de fin d'exécution")
    print("4. 🔍 Vérification de récupération d'images")
    print()

    # Analyser le flux normal
    print("🔄 FLUX NORMAL D'UN WORKFLOW:")
    print("   0% - Initialisation (add_to_execution_stack)")
    print("  10% - Ajout à la pile WorkflowQueue")
    print("  50% - Détection 'en cours' (QUEUED -> RUNNING)")
    print("  95% - Détection 'terminé' (plus en queue)")
    print("  98% - Récupération des images")
    print(" 100% - Finalisation et nettoyage")
    print()

    # Points de blocage potentiels
    print("❌ POINTS DE BLOCAGE POTENTIELS:")
    print("1. 🚨 Après 10%: Workflow non ajouté à WorkflowQueue")
    print("2. 🚨 Entre 10-50%: is_prompt_in_queue() ne fonctionne pas")
    print("3. 🚨 Entre 50-95%: Workflow jamais détecté comme terminé")
    print("4. 🚨 Après 95%: GetImages() échoue")
    print()

    return True


def check_workflow_progression():
    """Vérifier la progression des workflows"""
    print("🧪 Test de progression des workflows")
    print("=" * 60)

    try:
        from cy8_workflow_monitor import WorkflowQueue, WorkflowMonitor, WorkflowTask, WorkflowStatus

        # Simuler le problème
        queue = WorkflowQueue()

        # Log détaillé des callbacks
        progression_log = []

        def detailed_status_callback(execution_id, message, progress):
            timestamp = time.strftime("%H:%M:%S.%f")[:-3]  # Avec millisecondes
            log_entry = f"[{timestamp}] {execution_id}: {message} ({progress}%)"
            progression_log.append(log_entry)
            print(f"📊 {log_entry}")

        monitor = WorkflowMonitor(
            queue,
            status_callback=detailed_status_callback
        )

        monitor.start()
        time.sleep(1)

        # Simuler les étapes critiques
        print("🎬 Simulation du problème '10% puis blocage':")
        print()

        # Étape 1: Initialisation (10%)
        print("📝 ÉTAPE 1: Ajout d'une tâche (comme dans l'app à 10%)")
        test_task = WorkflowTask(
            prompt_id=123,
            execution_id="test_blocked_456",
            comfyui_prompt_id="test_block_789",
            status=WorkflowStatus.QUEUED,
            prompt_name="Test Workflow Bloqué",
            timestamp=time.time()
        )

        queue.add_task(test_task)
        time.sleep(2)

        # Étape 2: Observer le monitoring
        print("👁️ ÉTAPE 2: Observation du monitoring (10 secondes)")
        for i in range(10):
            time.sleep(1)
            debug_info = monitor.get_debug_info()

            if debug_info['tasks_count'] > 0:
                for task in debug_info['tasks_details']:
                    print(f"   ⏱️ [{i+1}s] {task['comfyui_prompt_id']}: {task['status']} (temps: {task['elapsed_seconds']}s)")

        print()
        print("📊 RÉSUMÉ DE LA PROGRESSION:")
        for entry in progression_log:
            print(f"   {entry}")

        # Nettoyer
        monitor.stop()
        queue.clear()

        # Analyse des résultats
        print()
        print("🔍 ANALYSE:")
        if len(progression_log) == 0:
            print("❌ PROBLÈME: Aucune progression détectée après 10%")
            print("   → Le monitoring ne détecte pas les workflows correctement")
        elif len(progression_log) == 1:
            print("⚠️ PROBLÈME: Progression bloquée après le premier callback")
            print("   → Le workflow n'évolue pas de QUEUED vers RUNNING puis COMPLETED")
        else:
            print("✅ Progression normale détectée")

        return True

    except Exception as e:
        print(f"❌ Erreur test progression: {e}")
        import traceback
        traceback.print_exc()
        return False


def diagnose_comfyui_detection():
    """Diagnostiquer la détection ComfyUI"""
    print("🧪 Diagnostic de détection ComfyUI")
    print("=" * 60)

    try:
        from cy6_websocket_api_client import get_queue_status, is_prompt_in_queue, get_history

        # Test 1: Accès de base
        print("🔍 Test 1: Accès de base à ComfyUI")
        queue_status = get_queue_status()

        if queue_status:
            print("✅ get_queue_status() fonctionne")
            print(f"   - Pending: {len(queue_status.get('queue_pending', []))}")
            print(f"   - Running: {len(queue_status.get('queue_running', []))}")
        else:
            print("❌ get_queue_status() échoue")
            return False

        # Test 2: Fonction is_prompt_in_queue avec ID inexistant
        print("\n🔍 Test 2: is_prompt_in_queue() avec ID inexistant")
        fake_id = "fake_prompt_test_123"
        in_queue = is_prompt_in_queue(fake_id)
        print(f"   is_prompt_in_queue('{fake_id}'): {in_queue}")

        if in_queue == False:
            print("✅ is_prompt_in_queue() détecte correctement les IDs inexistants")
        else:
            print("❌ is_prompt_in_queue() ne fonctionne pas correctement")

        # Test 3: Historique récent
        print("\n🔍 Test 3: Accès à l'historique")
        try:
            import urllib.request
            import json

            with urllib.request.urlopen("http://127.0.0.1:8188/history") as response:
                history = json.loads(response.read())

            if history:
                recent_ids = list(history.keys())[-3:]
                print(f"✅ Historique accessible: {len(history)} entrées")
                print(f"   IDs récents: {recent_ids}")

                # Tester get_history pour un ID spécifique
                if recent_ids:
                    test_id = recent_ids[0]
                    specific_history = get_history(test_id)
                    if specific_history:
                        print(f"✅ get_history('{test_id}') fonctionne")
                    else:
                        print(f"❌ get_history('{test_id}') échoue")
            else:
                print("⚠️ Historique vide")

        except Exception as hist_error:
            print(f"❌ Erreur accès historique: {hist_error}")

        return True

    except Exception as e:
        print(f"❌ Erreur diagnostic ComfyUI: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Diagnostic du problème '10% puis plus rien'")
    print("=" * 80)

    try:
        # Analyse théorique
        analyze_10_percent_issue()
        print()

        # Test de progression
        check_workflow_progression()
        print()

        # Diagnostic ComfyUI
        diagnose_comfyui_detection()
        print()

        print("=" * 80)
        print("🎯 CONCLUSION ET RECOMMANDATIONS:")
        print()
        print("1. 🔍 Le problème '10% puis blocage' provient probablement de:")
        print("   - L'ID du workflow n'est pas correctement transmis")
        print("   - Le monitoring ne trouve pas le workflow dans la queue ComfyUI")
        print("   - La connexion WebSocket pour GetImages échoue")
        print()
        print("2. 🔧 Solutions à implémenter:")
        print("   - Vérifier l'ID transmis au WorkflowMonitor")
        print("   - Améliorer la détection de fin d'exécution")
        print("   - Corriger la récupération d'images")
        print("   - Ajouter plus de logs pour traçabilité")

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

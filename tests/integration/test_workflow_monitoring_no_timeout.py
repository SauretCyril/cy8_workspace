#!/usr/bin/env python3
"""
Test d'intégration pour le système de monitoring sans timeout
"""

import sys
import os
import time
import threading

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from cy8_workflow_monitor import WorkflowQueue, WorkflowMonitor, WorkflowTask, WorkflowStatus


def test_workflow_monitor_no_timeout():
    """Test du monitoring sans timeout"""
    print("🧪 Test du monitoring sans timeout")

    # Créer la pile et le monitor
    queue = WorkflowQueue()
    monitor = WorkflowMonitor(queue)

    # Variables pour les callbacks
    status_updates = []

    def status_callback(execution_id, message, progress):
        status_updates.append({
            'execution_id': execution_id,
            'message': message,
            'progress': progress,
            'timestamp': time.time()
        })
        print(f"📊 Status update: {execution_id} -> {message} ({progress}%)")

    monitor.status_callback = status_callback

    # Démarrer le monitoring
    print("🚀 Démarrage du monitoring")
    monitor.start()

    # Vérifier le statut initial
    status = monitor.get_monitor_status()
    print(f"📋 Statut initial: {status}")

    assert status['status'] == "Actif", f"Monitoring devrait être actif, mais statut = {status['status']}"
    assert status['running'] == True, "Le monitoring devrait être en cours"
    assert status['active_tasks'] == 0, "Aucune tâche active au début"

    # Créer une tâche fictive de test
    test_task = WorkflowTask(
        prompt_id=1,
        execution_id="test_exec_001",
        comfyui_prompt_id="test_prompt_123",
        status=WorkflowStatus.QUEUED,
        prompt_name="Test Prompt",
        timestamp=time.time()
    )

    # Ajouter la tâche
    print("📋 Ajout d'une tâche de test")
    queue.add_task(test_task)

    # Attendre un peu pour voir l'activité
    print("⏱️ Attente de 5 secondes pour observer l'activité...")
    time.sleep(5)

    # Vérifier le statut après ajout
    status = monitor.get_monitor_status()
    print(f"📋 Statut après ajout: {status}")

    assert status['status'] == "Actif", "Le monitoring devrait toujours être actif"
    assert status['active_tasks'] == 1, f"Une tâche active attendue, trouvé: {status['active_tasks']}"

    # Simuler le passage du temps (plus de 10 minutes pour tester l'absence de timeout)
    print("⏱️ Simulation du passage du temps (test absence timeout)")

    # Modifier le timestamp de la tâche pour simuler une tâche ancienne
    test_task.timestamp = time.time() - 700  # 11 minutes et 40 secondes dans le passé

    # Attendre encore pour voir si la tâche est toujours surveillée
    print("⏱️ Attente de 3 secondes avec tâche ancienne...")
    time.sleep(3)

    # Vérifier que la tâche n'a pas été marquée en timeout
    task_in_queue = queue.get_task("test_prompt_123")

    if task_in_queue:
        print(f"✅ Tâche toujours surveillée: {task_in_queue.status}")
        assert task_in_queue.status != WorkflowStatus.FAILED, "La tâche ne devrait pas être en échec par timeout"
        assert task_in_queue.error_message != "Timeout - Workflow trop long", "Pas de message de timeout attendu"
    else:
        print("⚠️ Tâche non trouvée dans la pile")

    # Nettoyer
    print("🧹 Nettoyage")
    queue.remove_task("test_prompt_123")
    monitor.stop()

    # Vérifier l'arrêt
    status = monitor.get_monitor_status()
    print(f"📋 Statut final: {status}")

    assert status['status'] == "Arrêté", "Le monitoring devrait être arrêté"
    assert status['running'] == False, "Le monitoring ne devrait plus être en cours"

    print("✅ Test réussi - Pas de timeout détecté !")
    return True


def test_monitor_status_display():
    """Test de l'affichage du statut du monitoring"""
    print("🧪 Test de l'affichage du statut")

    queue = WorkflowQueue()
    monitor = WorkflowMonitor(queue)

    # Test statut arrêté
    status = monitor.get_monitor_status()
    print(f"📋 Statut arrêté: {status}")
    assert status['status'] == "Arrêté"

    # Test statut actif
    monitor.start()
    time.sleep(1)
    status = monitor.get_monitor_status()
    print(f"📋 Statut actif: {status}")
    assert status['status'] == "Actif"

    # Test avec tâches
    test_task = WorkflowTask(
        prompt_id=1,
        execution_id="test_exec_002",
        comfyui_prompt_id="test_prompt_456",
        status=WorkflowStatus.RUNNING,
        prompt_name="Test Prompt 2",
        timestamp=time.time()
    )
    queue.add_task(test_task)

    status = monitor.get_monitor_status()
    print(f"📋 Statut avec tâche: {status}")
    assert status['active_tasks'] == 1

    # Nettoyer
    monitor.stop()
    queue.clear()

    print("✅ Test affichage statut réussi !")
    return True


if __name__ == "__main__":
    print("🚀 Démarrage des tests de monitoring sans timeout")
    print("=" * 60)

    try:
        # Test principal
        test_workflow_monitor_no_timeout()
        print()

        # Test affichage
        test_monitor_status_display()
        print()

        print("=" * 60)
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ Le système de monitoring fonctionne sans timeout")
        print("✅ L'affichage du statut est fonctionnel")

    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

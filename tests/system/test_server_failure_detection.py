#!/usr/bin/env python3
"""
Test de détection de panne serveur pour WorkflowMonitor
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_workflow_monitor import WorkflowQueue, WorkflowMonitor, WorkflowTask, WorkflowStatus

def test_server_failure_detection():
    """Tester la détection de panne serveur"""
    print("🧪 TEST DÉTECTION DE PANNE SERVEUR")
    print("=" * 50)

    # Créer une pile et un moniteur
    queue = WorkflowQueue()
    monitor = WorkflowMonitor(queue)

    # Configurer des intervalles courts pour le test
    monitor.check_interval = 1  # Vérification chaque seconde
    monitor.server_check_interval = 2  # Check serveur toutes les 2s
    monitor.max_server_errors = 2  # Arrêt après 2 erreurs pour test rapide

    # Ajouter une tâche de test
    test_task = WorkflowTask(
        prompt_id=999,
        execution_id="test_server_failure",
        comfyui_prompt_id="test_failure_123",
        status=WorkflowStatus.QUEUED,
        prompt_name="Test Panne Serveur",
        timestamp=time.time(),
        comfyui_task_instance=None
    )

    queue.add_task(test_task)
    print(f"✅ Tâche de test ajoutée: {test_task.comfyui_prompt_id}")

    # Démarrer le monitoring
    print("🚀 Démarrage du monitoring...")
    monitor.start()

    # Attendre que le système détecte la panne (serveur supposé down)
    print("⏳ Attente de la détection de panne serveur...")
    start_time = time.time()

    while monitor.running and (time.time() - start_time) < 30:  # Max 30s d'attente
        time.sleep(1)
        tasks = queue.get_all_tasks()
        if not tasks:  # Plus de tâches = pile vidée à cause de la panne
            break

    # Vérifier les résultats
    final_tasks = queue.get_all_tasks()

    if not monitor.running:
        print("✅ SUCCÈS: Monitoring arrêté automatiquement")
    else:
        print("❌ ÉCHEC: Monitoring toujours en cours")
        monitor.stop()

    if not final_tasks:
        print("✅ SUCCÈS: Pile vidée automatiquement")
    else:
        print(f"❌ ÉCHEC: {len(final_tasks)} tâches restantes dans la pile")

    print(f"🕒 Test terminé en {time.time() - start_time:.1f}s")
    print("=" * 50)

if __name__ == "__main__":
    test_server_failure_detection()

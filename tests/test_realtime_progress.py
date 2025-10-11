#!/usr/bin/env python3
"""
Test du système de progression en temps réel
Vérifie que les pourcentages ComfyUI et temps écoulés sont affichés correctement
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
import threading
import tkinter as tk
from tkinter import ttk

def test_realtime_progress():
    """Test de la progression en temps réel"""
    print("🚀 Test progression en temps réel WorkflowMonitor")
    print("=" * 60)

    # Créer une interface de test
    root = tk.Tk()
    root.title("Test Progression Temps Réel")
    root.geometry("800x600")

    # Créer un affichage de test
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill="both", expand=True)

    # Titre
    title_label = ttk.Label(main_frame, text="Test Progression Temps Réel ComfyUI",
                           font=("TkDefaultFont", 12, "bold"))
    title_label.pack(pady=(0, 10))

    # Zone de statut
    status_var = tk.StringVar()
    status_var.set("En attente de test...")
    status_label = ttk.Label(main_frame, textvariable=status_var, font=("TkDefaultFont", 10))
    status_label.pack(pady=(0, 10))

    # Zone de log
    log_text = tk.Text(main_frame, wrap="word", font=("Consolas", 9), height=20)
    log_text.pack(fill="both", expand=True, pady=(0, 10))

    # Variables de test
    callbacks_received = []

    def log_message(message):
        """Ajouter un message au log"""
        timestamp = time.strftime("%H:%M:%S")
        log_text.insert("end", f"[{timestamp}] {message}\n")
        log_text.see("end")
        root.update_idletasks()

    def mock_status_callback(execution_id, message, progress):
        """Mock callback pour capturer les mises à jour de statut"""
        try:
            status_var.set(f"{execution_id}: {message}")
            log_message(f"📊 Status: {execution_id} - {message} ({progress}%)")
            callbacks_received.append(("status", execution_id, message, progress))
        except Exception as e:
            log_message(f"❌ Erreur status callback: {e}")

    def simulate_realtime_workflow():
        """Simuler un workflow avec progression en temps réel"""
        def workflow_thread():
            try:
                log_message("🚀 Démarrage simulation workflow...")

                # Importer le système de monitoring
                from cy8_workflow_monitor import WorkflowMonitor, WorkflowQueue, WorkflowTask, WorkflowStatus

                # Créer le système
                queue = WorkflowQueue()
                monitor = WorkflowMonitor(
                    queue,
                    status_callback=mock_status_callback,
                    root_widget=root
                )

                log_message("📋 WorkflowMonitor créé avec surveillance en temps réel")

                # Créer une tâche de test
                test_task = WorkflowTask(
                    prompt_id=123,
                    execution_id="test_realtime",
                    comfyui_prompt_id="test_prompt_123",
                    status=WorkflowStatus.QUEUED,
                    prompt_name="Test Temps Réel",
                    timestamp=time.time()
                )

                queue.add_task(test_task)
                log_message(f"📋 Tâche ajoutée: {test_task.comfyui_prompt_id}")

                # Simuler la progression
                start_time = time.time()

                # Phase 1: Démarrage
                log_message("🔄 Phase 1: Démarrage workflow")
                monitor._safe_callback(mock_status_callback, "test_realtime", "Démarrage du workflow", 0)
                time.sleep(1)

                # Phase 2: Progression simulée
                log_message("🔄 Phase 2: Progression simulée ComfyUI")
                progress_steps = [5, 15, 25, 40, 55, 70, 85, 95]

                for progress in progress_steps:
                    elapsed = time.time() - start_time
                    message = f"Génération en cours {progress}% (⏱️ {elapsed:.1f}s) - Node: {progress//10 + 1}"
                    monitor._safe_callback(mock_status_callback, "test_realtime", message, progress)
                    time.sleep(0.8)  # Simuler le temps de traitement

                # Phase 3: Récupération des images
                log_message("🔄 Phase 3: Récupération des images")
                elapsed = time.time() - start_time
                message = f"Terminé - Récupération des images (⏱️ {elapsed:.1f}s)"
                monitor._safe_callback(mock_status_callback, "test_realtime", message, 95)
                time.sleep(1)

                # Phase 4: Terminé
                log_message("🔄 Phase 4: Workflow terminé")
                elapsed = time.time() - start_time
                message = f"Exécution terminée avec succès (⏱️ {elapsed:.1f}s)"
                monitor._safe_callback(mock_status_callback, "test_realtime", message, 100)

                log_message("✅ Simulation terminée avec succès")

            except Exception as e:
                log_message(f"❌ Erreur simulation: {e}")
                import traceback
                traceback.print_exc()

        # Démarrer le thread de simulation
        thread = threading.Thread(target=workflow_thread, daemon=True)
        thread.start()

    # Boutons de test
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="🚀 Démarrer Test",
              command=simulate_realtime_workflow).pack(side="left", padx=5)

    def clear_log():
        log_text.delete("1.0", "end")
        callbacks_received.clear()
        status_var.set("Log effacé")

    ttk.Button(button_frame, text="🧹 Clear", command=clear_log).pack(side="left", padx=5)

    def show_results():
        log_message("=" * 40)
        log_message("📊 RÉSULTATS:")
        log_message(f"✅ Callbacks reçus: {len(callbacks_received)}")

        for i, (cb_type, exec_id, message, progress) in enumerate(callbacks_received):
            log_message(f"  {i+1}. {cb_type}: {progress}% - {message}")

    ttk.Button(button_frame, text="📊 Résultats", command=show_results).pack(side="left", padx=5)

    log_message("🎯 Interface de test prête")
    log_message("📋 Cliquez sur 'Démarrer Test' pour simuler un workflow avec progression temps réel")
    log_message("📋 Vous devriez voir:")
    log_message("   - Pourcentages précis de ComfyUI")
    log_message("   - Temps écoulé mis à jour en temps réel")
    log_message("   - Messages de statut détaillés")

    # Lancer l'interface
    root.mainloop()

if __name__ == "__main__":
    test_realtime_progress()

#!/usr/bin/env python3
"""
Test de la correction thread-safety pour le WorkflowMonitor
Vérifie que les callbacks sont exécutés sans erreur "main thread is not in main loop"
"""

import sys
import os
import time
import threading

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import tkinter as tk
from tkinter import ttk

# Test thread-safety correction
class TestThreadSafetyFix:
    def __init__(self):
        self.callbacks_received = []
        self.errors_encountered = []
        self.create_test_window()

    def create_test_window(self):
        """Créer une fenêtre de test"""
        self.root = tk.Tk()
        self.root.title("Test Thread-Safety WorkflowMonitor")
        self.root.geometry("600x400")

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Titre
        title_label = ttk.Label(main_frame, text="Test Thread-Safety Correction",
                               font=("TkDefaultFont", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Zone de log
        self.log_text = tk.Text(main_frame, wrap="word", font=("Consolas", 9), height=15)
        self.log_text.pack(fill="both", expand=True, pady=(0, 10))

        # Scrollbar pour le log
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Boutons de test
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Test Thread-Safety",
                  command=self.test_thread_safety).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Simuler Callbacks",
                  command=self.simulate_callbacks).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Log",
                  command=self.clear_log).pack(side="left", padx=5)

    def log(self, message):
        """Ajouter un message au log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def clear_log(self):
        """Effacer le log"""
        self.log_text.delete("1.0", "end")
        self.callbacks_received.clear()
        self.errors_encountered.clear()

    def mock_status_callback(self, execution_id, message, progress):
        """Mock callback pour tester thread-safety"""
        try:
            self.log(f"📊 Status callback: {execution_id} - {message} ({progress}%)")
            self.callbacks_received.append(("status", execution_id, message, progress))
        except Exception as e:
            error_msg = f"❌ Erreur status callback: {e}"
            self.log(error_msg)
            self.errors_encountered.append(error_msg)

    def mock_images_callback(self, prompt_id, images):
        """Mock callback pour tester thread-safety"""
        try:
            self.log(f"📸 Images callback: prompt {prompt_id} - {len(images)} images")
            self.callbacks_received.append(("images", prompt_id, len(images)))
        except Exception as e:
            error_msg = f"❌ Erreur images callback: {e}"
            self.log(error_msg)
            self.errors_encountered.append(error_msg)

    def mock_prompt_status_callback(self, prompt_id, status):
        """Mock callback pour tester thread-safety"""
        try:
            self.log(f"✅ Prompt status callback: {prompt_id} -> {status}")
            self.callbacks_received.append(("prompt_status", prompt_id, status))
        except Exception as e:
            error_msg = f"❌ Erreur prompt status callback: {e}"
            self.log(error_msg)
            self.errors_encountered.append(error_msg)

    def simulate_thread_callbacks(self):
        """Simuler des callbacks depuis un thread séparé"""
        def thread_work():
            try:
                self.log("🧵 Thread séparé démarré")

                # Importer WorkflowMonitor avec correction
                from cy8_workflow_monitor import WorkflowMonitor, WorkflowQueue

                # Créer un monitor avec root_widget
                queue = WorkflowQueue()
                monitor = WorkflowMonitor(
                    queue,
                    status_callback=self.mock_status_callback,
                    images_callback=self.mock_images_callback,
                    prompt_status_callback=self.mock_prompt_status_callback,
                    root_widget=self.root  # IMPORTANT: référence root pour thread-safety
                )

                # Simuler plusieurs callbacks depuis le thread
                for i in range(3):
                    time.sleep(0.5)

                    # Test _safe_callback avec status
                    monitor._safe_callback(self.mock_status_callback, f"exec_{i}", f"Message test {i}", i * 30)

                    # Test _safe_callback avec images
                    mock_images = [f"image_{i}_{j}.png" for j in range(2)]
                    monitor._safe_callback(self.mock_images_callback, f"prompt_{i}", mock_images)

                    # Test _safe_callback avec prompt status
                    monitor._safe_callback(self.mock_prompt_status_callback, f"prompt_{i}", "ok")

                self.log("✅ Thread séparé terminé avec succès")

            except Exception as e:
                error_msg = f"❌ Erreur dans thread séparé: {e}"
                self.log(error_msg)
                self.errors_encountered.append(error_msg)
                import traceback
                traceback.print_exc()

        # Démarrer le thread
        thread = threading.Thread(target=thread_work, daemon=True)
        thread.start()

    def test_thread_safety(self):
        """Test principal de thread-safety"""
        self.log("🚀 DÉBUT - Test Thread-Safety WorkflowMonitor")
        self.log("=" * 50)

        # Reset des compteurs
        self.callbacks_received.clear()
        self.errors_encountered.clear()

        # Lancer les callbacks depuis thread séparé
        self.simulate_thread_callbacks()

        # Programmer une vérification des résultats
        self.root.after(5000, self.check_results)

    def simulate_callbacks(self):
        """Simuler des callbacks directs (thread principal)"""
        self.log("🧪 Simulation callbacks directs")

        # Callbacks directs depuis le thread principal
        self.mock_status_callback("direct_1", "Test direct", 50)
        self.mock_images_callback("direct_prompt", ["test1.png", "test2.png"])
        self.mock_prompt_status_callback("direct_prompt", "ok")

    def check_results(self):
        """Vérifier les résultats du test"""
        self.log("=" * 50)
        self.log("📊 RÉSULTATS DU TEST")

        total_callbacks = len(self.callbacks_received)
        total_errors = len(self.errors_encountered)

        self.log(f"✅ Callbacks reçus: {total_callbacks}")
        self.log(f"❌ Erreurs rencontrées: {total_errors}")

        if total_errors == 0:
            self.log("🎉 TEST RÉUSSI - Aucune erreur thread-safety détectée!")
        else:
            self.log("⚠️ TEST ÉCHOUÉ - Erreurs thread-safety détectées:")
            for error in self.errors_encountered:
                self.log(f"    {error}")

        # Détail des callbacks
        status_callbacks = [c for c in self.callbacks_received if c[0] == "status"]
        images_callbacks = [c for c in self.callbacks_received if c[0] == "images"]
        prompt_callbacks = [c for c in self.callbacks_received if c[0] == "prompt_status"]

        self.log(f"📊 Status callbacks: {len(status_callbacks)}")
        self.log(f"📸 Images callbacks: {len(images_callbacks)}")
        self.log(f"✅ Prompt status callbacks: {len(prompt_callbacks)}")

        self.log("=" * 50)
        self.log("✅ Test terminé")

    def run(self):
        """Lancer le test"""
        print("🚀 Test Thread-Safety WorkflowMonitor")
        print("📋 Ce test vérifie que la correction thread-safety fonctionne")
        print("📋 Surveillez les erreurs 'main thread is not in main loop'")

        self.root.mainloop()

if __name__ == "__main__":
    test = TestThreadSafetyFix()
    test.run()

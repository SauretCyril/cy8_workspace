#!/usr/bin/env python3
"""
Test rapide de la correction thread-safety pour WorkflowMonitor
Simule le scénario spécifique de récupération d'images
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
import threading
import tkinter as tk

def test_thread_safety_correction():
    """Test rapide de la correction thread-safety"""
    print("🚀 Test correction thread-safety WorkflowMonitor")
    print("=" * 50)

    # Créer une instance Tkinter minimale
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre

    callbacks_executed = []
    errors_encountered = []

    def mock_status_callback(execution_id, message, progress):
        try:
            print(f"✅ Status callback exécuté: {execution_id} - {message}")
            callbacks_executed.append("status")
        except Exception as e:
            print(f"❌ Erreur status callback: {e}")
            errors_encountered.append(str(e))

    def mock_images_callback(prompt_id, images):
        try:
            print(f"✅ Images callback exécuté: prompt {prompt_id} - {len(images)} images")
            callbacks_executed.append("images")
        except Exception as e:
            print(f"❌ Erreur images callback: {e}")
            errors_encountered.append(str(e))

    def mock_prompt_callback(prompt_id, status):
        try:
            print(f"✅ Prompt callback exécuté: {prompt_id} -> {status}")
            callbacks_executed.append("prompt")
        except Exception as e:
            print(f"❌ Erreur prompt callback: {e}")
            errors_encountered.append(str(e))

    # Test dans un thread séparé
    def thread_test():
        try:
            print("🧵 Démarrage du thread de test...")

            # Importer et créer WorkflowMonitor
            from cy8_workflow_monitor import WorkflowMonitor, WorkflowQueue

            queue = WorkflowQueue()
            monitor = WorkflowMonitor(
                queue,
                status_callback=mock_status_callback,
                images_callback=mock_images_callback,
                prompt_status_callback=mock_prompt_callback,
                root_widget=root  # CRITIQUE: Passer root pour thread-safety
            )

            print("📋 WorkflowMonitor créé avec succès")

            # Test des callbacks via _safe_callback
            print("🔄 Test callbacks thread-safe...")

            # Simuler les callbacks problématiques
            monitor._safe_callback(mock_status_callback, "test_exec", "Récupération des images", 98)
            time.sleep(0.1)

            monitor._safe_callback(mock_images_callback, "test_prompt", ["img1.png", "img2.png"])
            time.sleep(0.1)

            monitor._safe_callback(mock_prompt_callback, "test_prompt", "ok")
            time.sleep(0.2)  # Attendre plus longtemps

            print("✅ Thread de test terminé")

        except Exception as e:
            print(f"❌ Erreur dans thread de test: {e}")
            errors_encountered.append(str(e))
            import traceback
            traceback.print_exc()

    # Lancer le thread
    test_thread = threading.Thread(target=thread_test, daemon=True)
    test_thread.start()

    # Attendre et traiter les callbacks
    start_time = time.time()
    while time.time() - start_time < 3 and len(callbacks_executed) < 3:  # Attendre max 3 secondes ou 3 callbacks
        root.update()  # Traiter les événements Tkinter
        time.sleep(0.01)

    # Attendre la fin du thread
    test_thread.join(timeout=1)

    # Résultats
    print("=" * 50)
    print("📊 RÉSULTATS:")
    print(f"✅ Callbacks exécutés: {len(callbacks_executed)} {callbacks_executed}")
    print(f"❌ Erreurs: {len(errors_encountered)} {errors_encountered}")

    if len(errors_encountered) == 0 and len(callbacks_executed) >= 3:
        print("🎉 TEST RÉUSSI - Thread-safety corrigée!")
        success = True
    else:
        print("⚠️ TEST ÉCHOUÉ - Problèmes détectés")
        success = False

    # Nettoyer
    root.destroy()

    return success

if __name__ == "__main__":
    success = test_thread_safety_correction()
    if success:
        print("\n✅ La correction thread-safety fonctionne correctement!")
        print("✅ L'erreur 'main thread is not in main loop' devrait être résolue.")
        exit(0)
    else:
        print("\n❌ La correction thread-safety ne fonctionne pas correctement.")
        exit(1)

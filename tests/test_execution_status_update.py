#!/usr/bin/env python3
"""
Test de mise à jour des statuts d'exécution dans le tableau
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import tkinter as tk
from tkinter import ttk

# Test simple pour simuler les mises à jour de statuts
class TestExecutionStatusUpdate:
    def __init__(self):
        self.execution_stack = []
        self.create_test_window()

    def create_test_window(self):
        """Créer une fenêtre de test"""
        self.root = tk.Tk()
        self.root.title("Test Mise à jour Statuts Exécution")
        self.root.geometry("800x400")

        # Créer le TreeView
        columns = ("ID", "Prompt", "Message", "Progrès", "Heure", "Monitoring")
        self.executions_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)

        # Configurer les colonnes
        for col in columns:
            self.executions_tree.heading(col, text=col)
            self.executions_tree.column(col, width=130)

        self.executions_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Boutons de test
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Ajouter Exécution",
                  command=self.add_test_execution).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Simuler Progression",
                  command=self.simulate_progression).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Terminer",
                  command=self.finish_execution).pack(side="left", padx=5)

    def add_to_execution_stack(self, execution_id, message, prompt_name="", progress=0):
        """Ajouter une exécution à la pile - copie de la méthode principale"""
        execution_item = {
            "id": execution_id,
            "message": message,
            "prompt_name": prompt_name,
            "progress": progress,
            "timestamp": time.time(),
            "formatted_time": time.strftime("%H:%M:%S", time.localtime()),
            "details": [],
            "monitor_status": "🔄 En attente",  # Statut de monitoring spécifique à cette exécution
        }
        self.execution_stack.append(execution_item)
        self.update_executions_tree()

    def update_execution_stack_status(self, execution_id, message, progress=None):
        """Mettre à jour le statut d'une exécution - copie de la méthode principale"""
        for item in self.execution_stack:
            if item["id"] == execution_id:
                item["message"] = message
                if progress is not None:
                    item["progress"] = progress

                # Mettre à jour le statut de monitoring basé sur le message
                if "En attente" in message:
                    item["monitor_status"] = "🔄 En attente"
                elif "Génération en cours" in message:
                    item["monitor_status"] = "⚡ En cours"
                elif "Terminé" in message:
                    item["monitor_status"] = "📸 Images"
                elif "Récupération" in message:
                    item["monitor_status"] = "📸 Images"
                elif "Terminé avec succès" in message or "Exécution terminée" in message:
                    item["monitor_status"] = "✅ Terminé"
                elif "Erreur" in message or "Panne" in message:
                    item["monitor_status"] = "❌ Erreur"
                else:
                    item["monitor_status"] = "🔄 Actif"

                # Ajouter aux détails
                detail_entry = f"[{time.strftime('%H:%M:%S')}] {message}"
                item["details"].append(detail_entry)
                break
        self.update_executions_tree()

    def update_executions_tree(self):
        """Mettre à jour le TreeView des exécutions - copie de la méthode principale"""
        if not self.executions_tree:
            return

        # Effacer le contenu actuel
        for item in self.executions_tree.get_children():
            self.executions_tree.delete(item)

        # Ajouter les exécutions (les plus récentes en premier)
        for execution in reversed(self.execution_stack):
            progress_display = (
                f"{execution['progress']}%" if execution["progress"] > 0 else "-"
            )

            # Utiliser le statut de monitoring spécifique à cette exécution
            monitor_status = execution.get("monitor_status", "❓ Inconnu")

            self.executions_tree.insert(
                "",
                "end",
                values=(
                    execution["id"],
                    execution["prompt_name"],
                    execution["message"],
                    progress_display,
                    execution["formatted_time"],
                    monitor_status,
                ),
            )

    def add_test_execution(self):
        """Ajouter une exécution de test"""
        execution_id = f"test_{len(self.execution_stack) + 1}"
        self.add_to_execution_stack(execution_id, "En attente de traitement", "Test Prompt", 0)
        print(f"➕ Ajout exécution {execution_id}")

    def simulate_progression(self):
        """Simuler la progression d'une exécution"""
        if not self.execution_stack:
            print("❌ Aucune exécution à mettre à jour")
            return

        # Prendre la dernière exécution
        last_execution = self.execution_stack[-1]
        execution_id = last_execution["id"]

        # Simuler la progression
        def update_step(step):
            if step == 1:
                self.update_execution_stack_status(execution_id, "Génération en cours (⏱️ 15.2s)", 50)
                self.root.after(2000, lambda: update_step(2))
            elif step == 2:
                self.update_execution_stack_status(execution_id, "Terminé - Récupération des images (⏱️ 45.8s)", 95)
                self.root.after(2000, lambda: update_step(3))
            elif step == 3:
                self.update_execution_stack_status(execution_id, "Exécution terminée avec succès (⏱️ 52.3s)", 100)

        # Démarrer la simulation
        print(f"🔄 Simulation progression pour {execution_id}")
        update_step(1)

    def finish_execution(self):
        """Marquer la dernière exécution comme terminée"""
        if not self.execution_stack:
            print("❌ Aucune exécution à terminer")
            return

        last_execution = self.execution_stack[-1]
        execution_id = last_execution["id"]
        self.update_execution_stack_status(execution_id, "Exécution terminée avec succès", 100)
        print(f"✅ Exécution {execution_id} terminée")

    def run(self):
        """Lancer le test"""
        print("🚀 Test de mise à jour des statuts d'exécution")
        print("📋 Instructions:")
        print("   1. Cliquez sur 'Ajouter Exécution' pour créer une nouvelle exécution")
        print("   2. Cliquez sur 'Simuler Progression' pour voir les mises à jour en temps réel")
        print("   3. Cliquez sur 'Terminer' pour marquer comme terminé")
        print("   4. Observez la colonne 'Monitoring' qui doit se mettre à jour")

        self.root.mainloop()

if __name__ == "__main__":
    test = TestExecutionStatusUpdate()
    test.run()

import sys
import json
import os

# sys.path.append('G:/G_WCS/Comfyui_api')
from cy6_file import log_json
from cy6_websocket_api_client import (
    update_workflow,
    socket_queue_prompt,
    server_connect,
    workflow_is_running,
    socket_get_images,
)


# seed aleatoire
class comfyui_task:
    name = "Default"

    def update_values(self, values):
        self.values = values

    def log_values(self):
        log_json("02_value_to_update", self.values)

    def addToQueue(self, fileworkflow, filevalues):
        """
        Ajoute un workflow à la queue ComfyUI et retourne immédiatement l'ID
        Ne bloque pas en attendant la fin d'exécution
        """
        json, updated_values = update_workflow(filevalues, fileworkflow)
        self.update_values(updated_values)
        self.last_workflow = json

        # POPUP DE CONFIRMATION WORKFLOW
        if not self._show_workflow_confirmation_popup(json, updated_values):
            print("❌ Exécution du workflow annulée par l'utilisateur")
            return None

        # Soumettre le prompt à ComfyUI
        response = socket_queue_prompt(json)
        prompt_id = response["prompt_id"]

        # Établir la connexion WebSocket pour le suivi
        try:
            self.ws = server_connect()
            print(f"DEBUG: Workflow {prompt_id} ajouté à la queue ComfyUI")
        except Exception as e:
            print(f"DEBUG: Erreur connexion WebSocket: {e}")
            self.ws = None

        return prompt_id

    def _show_workflow_confirmation_popup(self, workflow_json, values_dict):
        """
        Affiche une popup de confirmation avec le contenu du workflow
        Retourne True si l'utilisateur confirme, False sinon
        """
        try:
            import tkinter as tk
            from tkinter import ttk, scrolledtext, messagebox
            import json

            print("📋 Affichage popup de confirmation workflow...")

            # Créer la fenêtre popup
            popup = tk.Toplevel()
            popup.title("🔍 Confirmation d'Exécution Workflow")
            popup.geometry("800x600")
            popup.transient()
            popup.grab_set()

            # Centrer la popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (800 // 2)
            y = (popup.winfo_screenheight() // 2) - (600 // 2)
            popup.geometry(f"800x600+{x}+{y}")

            # Variable pour stocker la réponse
            result = {"confirmed": False}

            # Frame principal
            main_frame = ttk.Frame(popup, padding="10")
            main_frame.pack(fill="both", expand=True)

            # Titre
            title_label = ttk.Label(
                main_frame,
                text="⚠️ Confirmation d'exécution du workflow",
                font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 10))

            # Info du workflow
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill="x", pady=(0, 10))

            nodes_count = len(workflow_json) if isinstance(workflow_json, dict) else 0
            values_count = len(values_dict) if isinstance(values_dict, dict) else 0

            info_label = ttk.Label(
                info_frame,
                text=f"📊 Workflow: {nodes_count} nodes • Values: {values_count} entrées",
                font=("Arial", 10)
            )
            info_label.pack()

            # Notebook pour les onglets
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill="both", expand=True, pady=(0, 10))

            # Onglet Workflow
            workflow_frame = ttk.Frame(notebook)
            notebook.add(workflow_frame, text="🔧 Workflow JSON")

            workflow_text = scrolledtext.ScrolledText(
                workflow_frame,
                wrap=tk.WORD,
                width=80,
                height=20,
                font=("Consolas", 9)
            )
            workflow_text.pack(fill="both", expand=True, padx=5, pady=5)

            # Formater et afficher le JSON workflow
            try:
                formatted_workflow = json.dumps(workflow_json, indent=2, ensure_ascii=False)
                workflow_text.insert(tk.END, formatted_workflow)
            except:
                workflow_text.insert(tk.END, str(workflow_json))

            workflow_text.config(state=tk.DISABLED)

            # Onglet Values
            values_frame = ttk.Frame(notebook)
            notebook.add(values_frame, text="📝 Values JSON")

            values_text = scrolledtext.ScrolledText(
                values_frame,
                wrap=tk.WORD,
                width=80,
                height=20,
                font=("Consolas", 9)
            )
            values_text.pack(fill="both", expand=True, padx=5, pady=5)

            # Formater et afficher le JSON values
            try:
                formatted_values = json.dumps(values_dict, indent=2, ensure_ascii=False)
                values_text.insert(tk.END, formatted_values)
            except:
                values_text.insert(tk.END, str(values_dict))

            values_text.config(state=tk.DISABLED)

            # Frame pour les boutons
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill="x", pady=(10, 0))

            # Fonctions des boutons
            def on_confirm():
                result["confirmed"] = True
                popup.destroy()

            def on_cancel():
                result["confirmed"] = False
                popup.destroy()

            # Boutons
            cancel_button = ttk.Button(
                buttons_frame,
                text="❌ Annuler",
                command=on_cancel,
                width=15
            )
            cancel_button.pack(side="left", padx=(0, 10))

            confirm_button = ttk.Button(
                buttons_frame,
                text="✅ Exécuter le Workflow",
                command=on_confirm,
                width=20
            )
            confirm_button.pack(side="right")

            # Focus sur le bouton Exécuter
            confirm_button.focus_set()

            # Gérer la fermeture de la fenêtre
            popup.protocol("WM_DELETE_WINDOW", on_cancel)

            # Raccourcis clavier
            popup.bind("<Return>", lambda e: on_confirm())
            popup.bind("<Escape>", lambda e: on_cancel())

            # Attendre la réponse de l'utilisateur
            popup.wait_window()

            confirmed = result["confirmed"]
            print(f"{'✅ Workflow confirmé' if confirmed else '❌ Workflow annulé'} par l'utilisateur")

            return confirmed

        except Exception as e:
            print(f"❌ Erreur popup confirmation: {e}")
            # En cas d'erreur, demander confirmation via console
            import traceback
            traceback.print_exc()

            try:
                response = input("Exécuter le workflow ? (o/n): ").lower().strip()
                return response in ['o', 'oui', 'y', 'yes']
            except:
                # Si impossible, exécuter par défaut
                print("⚠️ Confirmation automatique - exécution du workflow")
                return True

    def GetImages(self, key):
        output_images = socket_get_images(self.ws, key)
        self.output_images = output_images
        return output_images

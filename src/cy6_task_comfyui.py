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

    def GetImages(self, key):
        output_images = socket_get_images(self.ws, key)
        self.output_images = output_images
        return output_images

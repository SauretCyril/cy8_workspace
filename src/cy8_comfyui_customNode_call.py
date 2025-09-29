#!/usr/bin/env python3
"""
cy8_comfyui_customNode_call.py - Classe pour l'appel et la gestion des custom nodes ComfyUI

Cette classe fournit des méthodes pour interagir avec les custom nodes ComfyUI,
récupérer leurs informations, et exécuter des workflows avec des custom nodes spécifiques.
"""

import json
import requests
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

# Import conditionnel de safetensors (optionnel)
try:
    from safetensors.torch import safe_open
    SAFETENSORS_AVAILABLE = True
except ImportError:
    SAFETENSORS_AVAILABLE = False
    safe_open = None


class ComfyUICustomNodeCaller:
    """Classe pour gérer les appels aux custom nodes ComfyUI"""

    def __init__(
        self, server_url: str = "http://127.0.0.1:8188", api_key: Optional[str] = None
    ):
        """
        Initialiser le gestionnaire de custom nodes ComfyUI

        Args:
            server_url: URL du serveur ComfyUI (défaut: http://127.0.0.1:8188)
            api_key: Clé API ComfyUI si requise
        """
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()

        # Headers par défaut
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "cy8_prompts_manager/1.0",
            }
        )

    def get_custom_nodes_info(self) -> Dict[str, Any]:
        """
        Récupérer les informations sur les custom nodes disponibles

        Returns:
            Dict contenant les informations sur les custom nodes
        """
        try:
            url = urljoin(self.server_url, "/object_info")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Erreur lors de la récupération des informations custom nodes: {e}"
            )

    def get_available_custom_node_types(self) -> List[str]:
        """
        Obtenir la liste des types de custom nodes disponibles

        Returns:
            Liste des noms de classes de custom nodes
        """
        try:
            nodes_info = self.get_custom_nodes_info()
            custom_node_types = []

            for node_type, node_info in nodes_info.items():
                # Filtrer les custom nodes (généralement ils ont des noms spéciaux)
                if self._is_custom_node(node_type, node_info):
                    custom_node_types.append(node_type)

            return sorted(custom_node_types)

        except Exception as e:
            raise Exception(
                f"Erreur lors de la récupération des types de custom nodes: {e}"
            )

    def _is_custom_node(self, node_type: str, node_info: Dict) -> bool:
        """
        Déterminer si un node est un custom node

        Args:
            node_type: Type du node
            node_info: Informations du node

        Returns:
            True si c'est un custom node
        """
        # Critères pour identifier un custom node
        custom_indicators = [
            # Noms typiques de custom nodes
            node_type.startswith(("ComfyUI", "CR ", "WAS ", "IPAdapter", "ControlNet")),
            # Contient des caractères spéciaux
            " " in node_type or "-" in node_type,
            # Commence par une majuscule suivie de minuscules
            (
                node_type[0].isupper() and any(c.islower() for c in node_type[1:])
                if node_type
                else False
            ),
        ]

        return any(custom_indicators)

    def create_custom_node_workflow(
        self, node_type: str, node_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Créer un workflow avec un custom node spécifique

        Args:
            node_type: Type du custom node à utiliser
            node_inputs: Inputs pour le custom node

        Returns:
            Workflow formaté pour ComfyUI
        """
        # Workflow avec le custom node et un node de sortie pour éviter l'erreur "no outputs"
        workflow = {
            "1": {
                "class_type": node_type,
                "inputs": node_inputs,
                "_meta": {"title": f"{node_type}"},
            },
            "2": {
                "class_type": "ShowText|pysssss",
                "inputs": {"text": ["1", 0]},  # Prendre la sortie du node 1
                "_meta": {"title": "Show Output"},
            },
        }

        return workflow

    def execute_custom_node_workflow(
        self, workflow: Dict[str, Any], extra_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Exécuter un workflow contenant des custom nodes

        Args:
            workflow: Workflow à exécuter
            extra_data: Données supplémentaires (API key, etc.)

        Returns:
            Réponse de ComfyUI
        """
        try:
            # Préparer le payload
            payload = {"prompt": workflow}

            # Ajouter les données supplémentaires
            if extra_data:
                payload["extra_data"] = extra_data
            elif self.api_key:
                payload["extra_data"] = {"api_key_comfy_org": self.api_key}

            # Envoyer la requête
            url = urljoin(self.server_url, "/prompt")
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de l'exécution du workflow: {e}")

    def call_custom_node(
        self, node_type: str, inputs: Dict[str, Any], extra_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Appeler directement un custom node avec des inputs

        Args:
            node_type: Type du custom node
            inputs: Inputs pour le node
            extra_data: Données supplémentaires

        Returns:
            Réponse de l'exécution
        """
        workflow = self.create_custom_node_workflow(node_type, inputs)
        return self.execute_custom_node_workflow(workflow, extra_data)

    def get_custom_node_schema(self, node_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtenir le schéma/structure d'un custom node spécifique

        Args:
            node_type: Type du custom node

        Returns:
            Schéma du custom node ou None si non trouvé
        """
        try:
            nodes_info = self.get_custom_nodes_info()
            return nodes_info.get(node_type)

        except Exception as e:
            raise Exception(
                f"Erreur lors de la récupération du schéma pour {node_type}: {e}"
            )

    def validate_custom_node_inputs(
        self, node_type: str, inputs: Dict[str, Any]
    ) -> bool:
        """
        Valider les inputs pour un custom node

        Args:
            node_type: Type du custom node
            inputs: Inputs à valider

        Returns:
            True si les inputs sont valides
        """
        try:
            schema = self.get_custom_node_schema(node_type)
            if not schema:
                return False

            required_inputs = schema.get("input", {}).get("required", {})

            # Vérifier que tous les inputs requis sont présents
            for required_input in required_inputs:
                if required_input not in inputs:
                    return False

            return True

        except Exception:
            return False

    def get_server_status(self) -> Dict[str, Any]:
        """
        Vérifier le statut du serveur ComfyUI

        Returns:
            Informations sur le statut du serveur
        """
        try:
            url = urljoin(self.server_url, "/system_stats")
            response = self.session.get(url, timeout=5)
            response.raise_for_status()

            return {
                "status": "online",
                "response_time": response.elapsed.total_seconds(),
                "system_stats": response.json(),
            }

        except requests.exceptions.RequestException as e:
            return {"status": "offline", "error": str(e)}

    def close(self):
        """Fermer la session"""
        if self.session:
            self.session.close()

    def __enter__(self):
        """Support du context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support du context manager"""
        self.close()


# Exemple d'utilisation
def example_usage():
    """Exemple d'utilisation de la classe"""

    # Utilisation avec context manager
    with ComfyUICustomNodeCaller() as caller:

        # Vérifier le statut du serveur
        status = caller.get_server_status()
        print(f"Statut du serveur: {status['status']}")

        if status["status"] == "online":
            # Obtenir les custom nodes disponibles
            custom_nodes = caller.get_available_custom_node_types()
            print(f"Custom nodes disponibles: {len(custom_nodes)}")

            # Exemple d'appel à un custom node
            if "ExtraPathReader" in custom_nodes:
                try:
                    result = caller.call_custom_node(
                        node_type="ExtraPathReader", inputs={}
                    )
                    print(f"Résultat: {result}")
                except Exception as e:
                    print(f"Erreur: {e}")


if __name__ == "__main__":
    example_usage()

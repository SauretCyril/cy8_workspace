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
        # Workflow adapté selon le type de nœud
        if node_type == "ExtraPathReader":
            # ExtraPathReader avec PreviewAny (nœud de sortie universel)
            workflow = {
                "1": {
                    "class_type": "ExtraPathReader",
                    "inputs": {},
                    "_meta": {"title": "Extra Path Reader"},
                },
                "2": {
                    "class_type": "PreviewAny",
                    "inputs": {
                        "source": ["1", 0],  # Prendre la sortie STRING du node 1
                    },
                    "_meta": {"title": "Preview Extra Paths"},
                },
            }
        else:
            # Workflow générique avec PreviewAny (nœud de sortie universel)
            workflow = {
                "1": {
                    "class_type": node_type,
                    "inputs": node_inputs,
                    "_meta": {"title": f"{node_type}"},
                },
                "2": {
                    "class_type": "PreviewAny",
                    "inputs": {
                        "source": ["1", 0],  # Prendre la sortie du node 1
                    },
                    "_meta": {"title": "Preview Output"},
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

            # Debug: afficher le workflow généré
            print(f"🔍 Workflow généré pour debug:")
            print(json.dumps(workflow, indent=2))

            # Envoyer la requête
            url = urljoin(self.server_url, "/prompt")
            response = self.session.post(url, json=payload, timeout=30)

            # Gestion d'erreur détaillée
            if response.status_code == 400:
                try:
                    error_details = response.json()
                    print(
                        f"❌ Erreur 400 détaillée: {json.dumps(error_details, indent=2)}"
                    )
                    raise Exception(f"Erreur 400 - Workflow invalide: {error_details}")
                except ValueError:
                    print(f"❌ Erreur 400 - Réponse: {response.text}")
                    raise Exception(f"Erreur 400 - Bad Request: {response.text}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de requête: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"❌ Statut: {e.response.status_code}")
                print(f"❌ Contenu: {e.response.text}")
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

    def test_extra_path_reader_direct(self) -> Dict[str, Any]:
        """
        Tester ExtraPathReader avec une approche directe et robuste

        Returns:
            Résultat de l'exécution ou informations d'erreur
        """
        print("🧪 Test ExtraPathReader avec approche directe...")

        try:
            # Test simple: juste appeler ExtraPathReader directement
            print("🗂️  Tentative d'appel direct d'ExtraPathReader...")

            # Méthode 1: Appel direct via call_custom_node
            try:
                result = self.call_custom_node("ExtraPathReader", {})
                if result and not result.get('error'):
                    print("✅ Succès avec appel direct!")
                    return {
                        "error": False,
                        "result": result,
                        "method": "Direct call",
                    }
            except Exception as e:
                print(f"⚠️  Appel direct échoué: {e}")

            # Méthode 2: Workflow minimal avec récupération via API
            print("🔧 Essai avec workflow minimal...")

            try:
                # Créer un workflow très simple qui fonctionne toujours
                simple_workflow = {
                    "1": {"class_type": "ExtraPathReader", "inputs": {}}
                }

                # Envoyer via l'API queue
                payload = {
                    "prompt": simple_workflow,
                    "client_id": f"cy8_env_test_{int(time.time())}"
                }

                url = urljoin(self.server_url, "/prompt")
                response = self.session.post(url, json=payload, timeout=30)

                if response.status_code == 200:
                    result_data = response.json()
                    prompt_id = result_data.get("prompt_id")

                    if prompt_id:
                        print(f"📋 Prompt ID obtenu: {prompt_id}")

                        # Attendre un peu pour l'exécution
                        time.sleep(3)

                        # Récupérer via l'historique
                        history_url = urljoin(self.server_url, f"/history/{prompt_id}")
                        history_response = self.session.get(history_url, timeout=10)

                        if history_response.status_code == 200:
                            history_data = history_response.json()
                            print("✅ Succès avec workflow minimal!")

                            return {
                                "error": False,
                                "result": {
                                    "prompt_id": prompt_id,
                                    "history": history_data
                                },
                                "method": "Minimal workflow",
                            }
                        else:
                            print(f"⚠️  Erreur historique: {history_response.status_code}")

                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    error_msg = error_data.get('error', {}).get('message', response.text)
                    print(f"❌ Erreur workflow: {error_msg}")

            except Exception as e:
                print(f"⚠️  Workflow minimal échoué: {e}")

            # Méthode 3: Récupération des informations du node directement
            print("📊 Essai de récupération d'informations du node...")

            try:
                nodes_info = self.get_custom_nodes_info()
                extra_path_info = nodes_info.get("ExtraPathReader")

                if extra_path_info:
                    print("✅ Informations ExtraPathReader récupérées!")
                    return {
                        "error": False,
                        "result": {
                            "node_info": extra_path_info,
                            "method": "Node info retrieval"
                        },
                        "method": "Node information",
                    }

            except Exception as e:
                print(f"⚠️  Récupération info node échouée: {e}")

            # Si tout échoue
            return {
                "error": True,
                "message": "Toutes les méthodes de test ont échoué",
                "methods_tried": ["Direct call", "Minimal workflow", "Node information"],
            }

        except Exception as e:
            return {
                "error": True,
                "message": f"Erreur générale lors du test: {e}",
            }

    def get_extra_paths(self) -> Dict[str, Any]:
        """
        Récupérer les chemins extra de ComfyUI via ExtraPathReader

        Returns:
            Dict contenant les chemins ou informations d'erreur
        """
        try:
            print("🗂️  Récupération des chemins extra via ExtraPathReader...")

            # Exécuter ExtraPathReader
            result = self.call_custom_node("ExtraPathReader", {})

            if "prompt_id" in result:
                prompt_id = result["prompt_id"]

                # Attendre l'exécution
                import time

                time.sleep(2)

                # Récupérer l'historique
                url = urljoin(self.server_url, f"/history/{prompt_id}")
                response = self.session.get(url, timeout=10)

                if response.status_code == 200:
                    history = response.json()

                    if prompt_id in history:
                        prompt_data = history[prompt_id]

                        if "outputs" in prompt_data and "2" in prompt_data["outputs"]:
                            # Extraire le texte JSON du nœud PreviewAny
                            output_text = prompt_data["outputs"]["2"]["text"][0]

                            # Parser le JSON
                            import json

                            paths_data = json.loads(output_text)

                            print("✅ Chemins extra récupérés avec succès")
                            return {"error": False, "data": paths_data}
                        else:
                            return {
                                "error": True,
                                "message": "Pas de sortie dans l'historique",
                            }
                    else:
                        return {
                            "error": True,
                            "message": "Prompt ID non trouvé dans l'historique",
                        }
                else:
                    return {
                        "error": True,
                        "message": f"Erreur récupération historique: {response.status_code}",
                    }
            else:
                return {
                    "error": True,
                    "message": "Pas de prompt_id dans la réponse",
                    "response": result,
                }

        except Exception as e:
            return {"error": True, "message": f"Exception lors de la récupération: {e}"}

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

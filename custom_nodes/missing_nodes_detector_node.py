#!/usr/bin/env python3
"""
ComfyUI Custom Node: Missing Nodes Detector
Détecte les custom nodes manquants dans un workflow ComfyUI

Ce custom node peut être placé dans le répertoire custom_nodes de ComfyUI
pour détecter automatiquement les nodes manquants dans un workflow.
"""

import json
import os
import sys

# Ajouter le chemin vers notre classe
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from cy8_missing_nodes_detector import MissingNodesDetector
except ImportError:
    # Si la classe n'est pas trouvée, créer une version simplifiée
    class MissingNodesDetector:
        def detect_missing_nodes(self, workflow_path, custom_nodes_dir):
            return {"error": True, "message": "Classe MissingNodesDetector non trouvée"}

        def generate_report(self, result):
            return result.get("message", "Erreur inconnue")


class MissingNodesDetectorNode:
    """Custom node ComfyUI pour détecter les nodes manquants"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "workflow_path": ("STRING", {
                    "default": "/path/to/workflow.json",
                    "multiline": False
                }),
                "custom_nodes_dir": ("STRING", {
                    "default": "ComfyUI/custom_nodes",
                    "multiline": False
                }),
            },
            "optional": {
                "auto_detect_paths": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("report", "missing_nodes_json", "status")

    FUNCTION = "detect_missing_nodes"
    CATEGORY = "cy8_tools"

    DESCRIPTION = """
    Détecte les custom nodes manquants dans un workflow ComfyUI.

    Inputs:
    - workflow_path: Chemin vers le fichier workflow JSON
    - custom_nodes_dir: Chemin vers le répertoire custom_nodes
    - auto_detect_paths: Tenter de détecter automatiquement les chemins

    Outputs:
    - report: Rapport textuel détaillé
    - missing_nodes_json: Liste des nodes manquants en JSON
    - status: Statut de l'analyse (SUCCESS/ERROR)
    """

    def detect_missing_nodes(self, workflow_path, custom_nodes_dir, auto_detect_paths=True):
        """
        Détecter les nodes manquants dans un workflow

        Args:
            workflow_path: Chemin vers le workflow
            custom_nodes_dir: Chemin vers les custom nodes
            auto_detect_paths: Tenter la détection automatique

        Returns:
            Tuple (report, missing_nodes_json, status)
        """
        try:
            # Auto-détection des chemins si demandé
            if auto_detect_paths:
                workflow_path, custom_nodes_dir = self._auto_detect_paths(
                    workflow_path, custom_nodes_dir
                )

            # Initialiser le détecteur
            detector = MissingNodesDetector()

            # Effectuer la détection
            result = detector.detect_missing_nodes(workflow_path, custom_nodes_dir)

            if result["error"]:
                return (
                    f"❌ Erreur: {result['message']}",
                    json.dumps({"error": True, "message": result["message"]}, indent=2),
                    "ERROR"
                )

            # Générer le rapport
            report = detector.generate_report(result)

            # Créer le JSON des nodes manquants
            missing_nodes_data = {
                "missing_nodes": result["missing_nodes"],
                "summary": result["summary"],
                "workflow_path": result["workflow_path"],
                "custom_nodes_dir": result["custom_nodes_dir"],
                "timestamp": self._get_timestamp()
            }

            missing_nodes_json = json.dumps(missing_nodes_data, indent=2)

            # Déterminer le statut
            status = "SUCCESS" if result["summary"]["missing_nodes"] == 0 else "WARNING"

            return (report, missing_nodes_json, status)

        except Exception as e:
            error_msg = f"Erreur lors de la détection: {str(e)}"
            return (
                f"❌ {error_msg}",
                json.dumps({"error": True, "message": error_msg}, indent=2),
                "ERROR"
            )

    def _auto_detect_paths(self, workflow_path, custom_nodes_dir):
        """
        Tenter de détecter automatiquement les chemins corrects

        Args:
            workflow_path: Chemin workflow fourni
            custom_nodes_dir: Chemin custom_nodes fourni

        Returns:
            Tuple (workflow_path_corrected, custom_nodes_dir_corrected)
        """
        # Détecter le répertoire ComfyUI
        comfyui_dir = self._find_comfyui_directory()

        # Corriger le chemin custom_nodes si nécessaire
        if comfyui_dir and not os.path.exists(custom_nodes_dir):
            auto_custom_nodes = os.path.join(comfyui_dir, "custom_nodes")
            if os.path.exists(auto_custom_nodes):
                custom_nodes_dir = auto_custom_nodes

        # Pour le workflow, essayer quelques emplacements courants
        if not os.path.exists(workflow_path):
            possible_locations = []

            if comfyui_dir:
                possible_locations.extend([
                    os.path.join(comfyui_dir, "workflows"),
                    os.path.join(comfyui_dir, "user", "default", "workflows"),
                    comfyui_dir
                ])

            # Chercher les fichiers .json dans ces répertoires
            for location in possible_locations:
                if os.path.exists(location):
                    for file in os.listdir(location):
                        if file.endswith('.json'):
                            test_path = os.path.join(location, file)
                            # Vérifier si c'est un workflow valide
                            if self._is_valid_workflow(test_path):
                                workflow_path = test_path
                                break
                    if os.path.exists(workflow_path):
                        break

        return workflow_path, custom_nodes_dir

    def _find_comfyui_directory(self):
        """
        Trouver le répertoire racine de ComfyUI

        Returns:
            Chemin vers ComfyUI ou None
        """
        # Commencer par le répertoire courant et remonter
        current = os.path.abspath(".")

        for _ in range(5):  # Limiter la recherche
            # Vérifier si on est dans un répertoire ComfyUI
            if any(os.path.exists(os.path.join(current, indicator)) for indicator in
                   ["main.py", "nodes.py", "execution.py", "custom_nodes"]):
                return current

            parent = os.path.dirname(current)
            if parent == current:  # Racine atteinte
                break
            current = parent

        return None

    def _is_valid_workflow(self, file_path):
        """
        Vérifier si un fichier JSON est un workflow valide

        Args:
            file_path: Chemin vers le fichier

        Returns:
            True si c'est un workflow valide
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Vérifier la structure typique d'un workflow ComfyUI
            if isinstance(data, dict):
                # Format avec clés numériques
                for key, value in data.items():
                    if isinstance(value, dict) and "class_type" in value:
                        return True
                # Format avec clé "nodes"
                if "nodes" in data and isinstance(data["nodes"], list):
                    return True

            return False
        except:
            return False

    def _get_timestamp(self):
        """Obtenir un timestamp formaté"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Configuration du node pour ComfyUI
NODE_CLASS_MAPPINGS = {
    "MissingNodesDetector": MissingNodesDetectorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MissingNodesDetector": "🔍 Missing Nodes Detector"
}

# Métadonnées supplémentaires
WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]


# Test du node si exécuté directement
if __name__ == "__main__":
    print("🧪 Test du custom node MissingNodesDetector")

    # Créer une instance de test
    node = MissingNodesDetectorNode()

    # Test avec des paramètres par défaut
    result = node.detect_missing_nodes(
        workflow_path="test_workflow.json",
        custom_nodes_dir="custom_nodes",
        auto_detect_paths=True
    )

    print("\n📋 Résultat du test:")
    print(f"Status: {result[2]}")
    print("\n📄 Rapport:")
    print(result[0])

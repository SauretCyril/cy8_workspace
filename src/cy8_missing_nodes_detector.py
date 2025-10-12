#!/usr/bin/env python3
"""
cy8_missing_nodes_detector.py - Détecteur de nodes manquants dans les workflows ComfyUI

Cette classe analyse les workflows ComfyUI pour détecter les custom nodes manquants
en comparant les nodes utilisés avec ceux disponibles dans l'installation.
"""

import json
import os
import re
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path


class MissingNodesDetector:
    """Détecteur de nodes manquants dans les workflows ComfyUI"""

    def __init__(self, custom_nodes_dir: Optional[str] = None):
        """
        Initialiser le détecteur

        Args:
            custom_nodes_dir: Chemin vers le répertoire custom_nodes de ComfyUI
        """
        self.custom_nodes_dir = custom_nodes_dir
        self.available_nodes = set()
        self.node_mappings = {}

    def scan_available_nodes(self, custom_nodes_dir: str) -> Set[str]:
        """
        Scanner le répertoire custom_nodes pour trouver tous les nodes disponibles

        Args:
            custom_nodes_dir: Chemin vers le répertoire custom_nodes

        Returns:
            Set des noms de nodes disponibles
        """
        available_nodes = set()
        node_mappings = {}

        if not os.path.exists(custom_nodes_dir):
            print(f"⚠️ Répertoire custom_nodes non trouvé: {custom_nodes_dir}")
            return available_nodes

        print(f"🔍 Scan des custom nodes dans: {custom_nodes_dir}")

        for root, dirs, files in os.walk(custom_nodes_dir):
            # Ignorer les répertoires cachés et __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.endswith(".py") and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                        # Rechercher NODE_CLASS_MAPPINGS
                        if "NODE_CLASS_MAPPINGS" in content:
                            nodes_found = self._extract_node_mappings(content, file_path)
                            available_nodes.update(nodes_found.keys())
                            node_mappings.update(nodes_found)

                    except Exception as e:
                        print(f"⚠️ Erreur lecture {file_path}: {e}")

        self.available_nodes = available_nodes
        self.node_mappings = node_mappings
        print(f"✅ {len(available_nodes)} nodes disponibles trouvés")

        return available_nodes

    def _extract_node_mappings(self, content: str, file_path: str) -> Dict[str, str]:
        """
        Extraire les mappings de nodes depuis le contenu d'un fichier

        Args:
            content: Contenu du fichier Python
            file_path: Chemin du fichier pour le debug

        Returns:
            Dict des mappings {nom_node: fichier_source}
        """
        mappings = {}

        try:
            # Pattern pour NODE_CLASS_MAPPINGS
            pattern = r'NODE_CLASS_MAPPINGS\s*=\s*\{([^}]+)\}'
            matches = re.finditer(pattern, content, re.DOTALL)

            for match in matches:
                mapping_content = match.group(1)

                # Extraire les clés (noms des nodes)
                key_pattern = r'["\']([^"\']+)["\']'
                keys = re.findall(key_pattern, mapping_content)

                for key in keys:
                    if key and not key.startswith('__'):
                        mappings[key] = os.path.basename(file_path)

        except Exception as e:
            print(f"⚠️ Erreur extraction mappings dans {file_path}: {e}")

        return mappings

    def analyze_workflow(self, workflow_path: str) -> Dict[str, any]:
        """
        Analyser un workflow pour détecter les nodes utilisés

        Args:
            workflow_path: Chemin vers le fichier workflow JSON

        Returns:
            Dict avec les informations d'analyse
        """
        if not os.path.exists(workflow_path):
            return {
                "error": True,
                "message": f"Fichier workflow non trouvé: {workflow_path}"
            }

        try:
            with open(workflow_path, "r", encoding="utf-8") as f:
                workflow_data = json.load(f)

            # Extraire les nodes selon le format du workflow
            used_nodes = self._extract_used_nodes(workflow_data)

            return {
                "error": False,
                "workflow_path": workflow_path,
                "used_nodes": used_nodes,
                "total_nodes": len(used_nodes)
            }

        except Exception as e:
            return {
                "error": True,
                "message": f"Erreur analyse workflow: {e}"
            }

    def _extract_used_nodes(self, workflow_data: Dict) -> Set[str]:
        """
        Extraire les nodes utilisés depuis les données du workflow

        Args:
            workflow_data: Données JSON du workflow

        Returns:
            Set des types de nodes utilisés
        """
        used_nodes = set()

        # Format 1: workflow avec clé "nodes"
        if "nodes" in workflow_data:
            for node in workflow_data["nodes"]:
                if "type" in node:
                    used_nodes.add(node["type"])

        # Format 2: workflow ComfyUI standard (clés numériques)
        else:
            for key, node_data in workflow_data.items():
                if isinstance(node_data, dict) and "class_type" in node_data:
                    used_nodes.add(node_data["class_type"])

        return used_nodes

    def detect_missing_nodes(self, workflow_path: str, custom_nodes_dir: str) -> Dict[str, any]:
        """
        Détecter les nodes manquants dans un workflow

        Args:
            workflow_path: Chemin vers le workflow
            custom_nodes_dir: Chemin vers le répertoire custom_nodes

        Returns:
            Dict avec les résultats de la détection
        """
        # Analyser le workflow
        workflow_analysis = self.analyze_workflow(workflow_path)
        if workflow_analysis["error"]:
            return workflow_analysis

        # Scanner les nodes disponibles
        if not self.available_nodes or self.custom_nodes_dir != custom_nodes_dir:
            self.custom_nodes_dir = custom_nodes_dir
            self.scan_available_nodes(custom_nodes_dir)

        used_nodes = workflow_analysis["used_nodes"]

        # Built-in nodes ComfyUI (toujours disponibles)
        builtin_nodes = {
            "LoadImage", "SaveImage", "PreviewImage",
            "CLIPTextEncode", "CLIPSetLastLayer",
            "CheckpointLoaderSimple", "VAEDecode", "VAEEncode",
            "KSampler", "KSamplerAdvanced",
            "EmptyLatentImage", "LatentUpscale",
            "ConditioningCombine", "ConditioningAverage",
            "ConditioningConcat", "ConditioningSetArea",
            "ControlNetApply", "ControlNetLoader",
            "LoadImageMask", "ImageScale", "ImageBlur",
            "PreviewAny"  # Node universel pour preview
        }

        # Séparer les built-in des custom nodes
        builtin_used = used_nodes.intersection(builtin_nodes)
        custom_used = used_nodes - builtin_nodes

        # Détecter les manquants
        missing_nodes = []
        available_custom = []

        for node in custom_used:
            if node in self.available_nodes:
                available_custom.append({
                    "name": node,
                    "source": self.node_mappings.get(node, "Inconnu")
                })
            else:
                missing_nodes.append(node)

        # Résultats
        result = {
            "error": False,
            "workflow_path": workflow_path,
            "custom_nodes_dir": custom_nodes_dir,
            "summary": {
                "total_nodes": len(used_nodes),
                "builtin_nodes": len(builtin_used),
                "custom_nodes": len(custom_used),
                "missing_nodes": len(missing_nodes),
                "available_custom": len(available_custom)
            },
            "builtin_used": sorted(list(builtin_used)),
            "custom_available": available_custom,
            "missing_nodes": sorted(missing_nodes),
            "all_available_nodes": len(self.available_nodes)
        }

        return result

    def generate_report(self, detection_result: Dict) -> str:
        """
        Générer un rapport textuel des résultats

        Args:
            detection_result: Résultat de detect_missing_nodes

        Returns:
            Rapport formaté
        """
        if detection_result["error"]:
            return f"❌ Erreur: {detection_result['message']}"

        summary = detection_result["summary"]
        report = []

        report.append("🔍 RAPPORT D'ANALYSE DES NODES")
        report.append("=" * 50)
        report.append(f"📄 Workflow: {os.path.basename(detection_result['workflow_path'])}")
        report.append(f"📁 Custom nodes: {detection_result['custom_nodes_dir']}")
        report.append("")

        report.append("📊 RÉSUMÉ:")
        report.append(f"   • Total nodes utilisés: {summary['total_nodes']}")
        report.append(f"   • Built-in ComfyUI: {summary['builtin_nodes']}")
        report.append(f"   • Custom nodes: {summary['custom_nodes']}")
        report.append(f"   • Custom disponibles: {summary['available_custom']}")
        report.append(f"   • Nodes manquants: {summary['missing_nodes']}")
        report.append("")

        if summary["missing_nodes"] > 0:
            report.append("🧩 NODES MANQUANTS:")
            for node in detection_result["missing_nodes"]:
                report.append(f"   ❌ {node}")
            report.append("")
            report.append("👉 Action recommandée:")
            report.append("   • Installer via ComfyUI-Manager")
            report.append("   • Ou rechercher manuellement les custom nodes")
        else:
            report.append("✅ TOUS LES NODES SONT DISPONIBLES!")

        if detection_result["custom_available"]:
            report.append("")
            report.append("📦 CUSTOM NODES UTILISÉS:")
            for node_info in detection_result["custom_available"]:
                report.append(f"   ✅ {node_info['name']} (source: {node_info['source']})")

        return "\n".join(report)


# Fonction utilitaire pour usage direct
def detect_missing_nodes_simple(workflow_path: str, custom_nodes_dir: str) -> Dict:
    """
    Fonction simple pour détecter les nodes manquants

    Args:
        workflow_path: Chemin vers le workflow
        custom_nodes_dir: Chemin vers les custom nodes

    Returns:
        Résultats de la détection
    """
    detector = MissingNodesDetector()
    return detector.detect_missing_nodes(workflow_path, custom_nodes_dir)


# Test de la classe
if __name__ == "__main__":
    # Test avec des chemins d'exemple
    workflow_test = "test_workflow.json"
    custom_nodes_test = "ComfyUI/custom_nodes"

    detector = MissingNodesDetector()

    # Test avec des données simulées si les fichiers n'existent pas
    if not os.path.exists(workflow_test):
        print("📋 Création d'un workflow de test...")
        test_workflow = {
            "1": {"class_type": "LoadImage", "inputs": {}},
            "2": {"class_type": "ExtraPathReader", "inputs": {}},
            "3": {"class_type": "UnknownCustomNode", "inputs": {}}
        }
        with open(workflow_test, "w") as f:
            json.dump(test_workflow, f, indent=2)

    result = detector.detect_missing_nodes(workflow_test, custom_nodes_test)
    print(detector.generate_report(result))

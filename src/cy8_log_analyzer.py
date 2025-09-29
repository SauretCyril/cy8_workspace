#!/usr/bin/env python3
"""
cy8_log_analyzer.py - Analyseur de logs ComfyUI pour cy8_prompts_manager

Ce module fournit des fonctionnalités d'analyse des fichiers de logs ComfyUI
pour extraire les informations sur les custom nodes, erreurs et états du système.
"""

import os
import re
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class cy8_log_analyzer:
    """Analyseur de logs ComfyUI"""

    def __init__(self):
        """Initialiser l'analyseur de logs"""
        self.log_entries = []
        self.custom_nodes_ok = []
        self.custom_nodes_failed = []
        self.errors = []
        self.warnings = []
        self.info_messages = []
        self.config_id = None

    def analyze_log_file(self, log_file_path: str) -> Dict:
        """
        Analyser un fichier de log ComfyUI

        Args:
            log_file_path: Chemin vers le fichier de log

        Returns:
            Dict contenant les résultats de l'analyse
        """
        if not os.path.exists(log_file_path):
            return {
                "success": False,
                "error": f"Fichier log introuvable: {log_file_path}",
                "entries": [],
            }

        try:
            # Réinitialiser les listes
            self.log_entries = []
            self.custom_nodes_ok = []
            self.custom_nodes_failed = []
            self.errors = []
            self.warnings = []
            self.info_messages = []
            self.config_id = None

            # Lire le fichier de log
            with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()

            # Analyser le contenu
            self._parse_log_content(log_content)

            # Retourner les résultats structurés
            return {
                "success": True,
                "file_path": log_file_path,
                "file_size": os.path.getsize(log_file_path),
                "analysis_time": datetime.now().isoformat(),
                "entries": self._get_analysis_entries(),
                "config_id": self.config_id,
                "summary": {
                    "custom_nodes_ok": len(self.custom_nodes_ok),
                    "custom_nodes_failed": len(self.custom_nodes_failed),
                    "errors": len(self.errors),
                    "warnings": len(self.warnings),
                    "info_messages": len(self.info_messages),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de l'analyse du log: {str(e)}",
                "entries": [],
            }

    def _parse_log_content(self, content: str):
        """Parser le contenu du log"""
        lines = content.split("\n")
        in_custom_nodes_section = False

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Détecter l'ID de configuration depuis "Adding extra search path"
            if "Adding extra search path" in line and "custom_nodes" in line:
                config_id = self._extract_config_id(line)
                if config_id:
                    self.config_id = config_id

            # Détecter le début de la section custom nodes
            if "Import times for custom nodes" in line:
                in_custom_nodes_section = True
                continue

            # Analyser les custom nodes dans la section appropriée
            if in_custom_nodes_section and "custom_nodes" in line:
                node_info = self._extract_custom_node_from_import_line(line)
                if node_info:
                    timestamp = self._extract_timestamp(line)
                    if "(IMPORT FAILED)" in line:
                        self.custom_nodes_failed.append(
                            {
                                "line": line_num,
                                "content": line,
                                "node_name": node_info,
                                "error": "Import failed",
                                "timestamp": timestamp,
                            }
                        )
                    else:
                        self.custom_nodes_ok.append(
                            {
                                "line": line_num,
                                "content": line,
                                "node_name": node_info,
                                "timestamp": timestamp,
                            }
                        )

            # Détecter les erreurs
            elif self._is_error(line):
                error_info = self._extract_error_info(line)
                timestamp = self._extract_timestamp(line)
                self.errors.append(
                    {
                        "line": line_num,
                        "content": line,
                        "error_type": error_info.get("type", "Error"),
                        "message": error_info.get("message", line),
                        "timestamp": timestamp,
                    }
                )

            # Détecter les warnings
            elif self._is_warning(line):
                warning_info = self._extract_warning_info(line)
                timestamp = self._extract_timestamp(line)
                self.warnings.append(
                    {
                        "line": line_num,
                        "content": line,
                        "message": warning_info.get("message", line),
                        "timestamp": timestamp,
                    }
                )

            # Détecter les messages d'information importantes
            elif self._is_important_info(line):
                info = self._extract_info(line)
                timestamp = self._extract_timestamp(line)
                self.info_messages.append(
                    {
                        "line": line_num,
                        "content": line,
                        "message": info,
                        "timestamp": timestamp,
                    }
                )

    def _extract_timestamp(self, line: str) -> Optional[str]:
        """Extraire le timestamp d'une ligne de log avec format détaillé"""
        # Patterns de timestamp courants dans les logs
        timestamp_patterns = [
            # Format ISO: 2025-09-28 14:30:25.123
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{2,3})",
            # Format avec [] : [2025-09-28 14:30:25.123]
            r"\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{2,3})\]",
            # Format avec () : (2025-09-28 14:30:25.123)
            r"\((\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{2,3})\)",
            # Format sans millisecondes mais avec secondes: 2025-09-28 14:30:25
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
            # Format heure seule avec millisecondes: 14:30:25.123
            r"(\d{2}:\d{2}:\d{2}\.\d{2,3})",
            # Format heure seule: 14:30:25
            r"(\d{2}:\d{2}:\d{2})",
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                # Si c'est juste l'heure, ajouter la date actuelle
                if not timestamp_str.startswith('20'):
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    timestamp_str = f"{current_date} {timestamp_str}"

                # S'assurer que le timestamp a des centièmes
                if '.' not in timestamp_str:
                    timestamp_str += ".00"
                elif len(timestamp_str.split('.')[-1]) == 1:
                    timestamp_str += "0"
                elif len(timestamp_str.split('.')[-1]) > 3:
                    # Tronquer à 2 décimales pour les centièmes
                    parts = timestamp_str.split('.')
                    timestamp_str = f"{parts[0]}.{parts[1][:2]}"

                return timestamp_str

        # Si aucun timestamp trouvé, générer un timestamp par défaut
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]

    def _extract_config_id(self, line: str) -> Optional[str]:
        """
        Extraire l'ID de configuration depuis une ligne 'Adding extra search path'
        Format: "Adding extra search path custom_nodes H:\\comfyui\\G11_04\\custom_nodes"
        L'ID est entre "comfyui\\" et "\\custom_nodes"
        """
        # Pattern pour extraire l'ID entre comfyui\ et \custom_nodes
        pattern = r".*comfyui[/\\]([^/\\]+)[/\\]custom_nodes"
        match = re.search(pattern, line, re.IGNORECASE)

        if match:
            config_id = match.group(1)
            # Nettoyer l'ID (enlever les caractères parasites mais garder les caractères valides)
            config_id = re.sub(r"[^\w\-_.]", "", config_id)
            return config_id if config_id else None

        return None

    def _extract_custom_node_from_import_line(self, line: str) -> Optional[str]:
        """
        Extraire le nom du custom node à partir d'une ligne contenant custom_nodes
        Le nom se trouve après le dernier \\ ou / dans le chemin
        """
        # Chercher le chemin contenant custom_nodes
        custom_nodes_pattern = r".*custom_nodes[/\\]([^/\\:\s]+)"
        match = re.search(custom_nodes_pattern, line, re.IGNORECASE)

        if match:
            # Le nom du custom node est après le dernier séparateur
            node_name = match.group(1)
            # Nettoyer le nom (enlever les caractères parasites)
            node_name = re.sub(r"[^\w\-_.]", "", node_name)
            return node_name if node_name else "Unknown Node"

        return None

    def _is_error(self, line: str) -> bool:
        """Détecter si une ligne contient une erreur"""
        patterns = [
            r".*error[:)]",
            r".*exception[:)]",
            r".*traceback",
            r".*failed",
            r".*critical",
        ]

        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in patterns)

    def _extract_error_info(self, line: str) -> Dict:
        """Extraire les informations d'erreur"""
        error_types = {
            "modulenotfounderror": "Module Not Found",
            "importerror": "Import Error",
            "attributeerror": "Attribute Error",
            "typeerror": "Type Error",
            "valueerror": "Value Error",
            "keyerror": "Key Error",
            "filenotfounderror": "File Not Found",
            "permissionerror": "Permission Error",
            "connectionerror": "Connection Error",
            "timeout": "Timeout Error",
        }

        line_lower = line.lower()

        # Détecter le type d'erreur
        error_type = "Error"
        for key, value in error_types.items():
            if key in line_lower:
                error_type = value
                break

        # Extraire le message d'erreur
        message = line
        if ":" in line:
            parts = line.split(":", 1)
            if len(parts) > 1:
                message = parts[1].strip()

        return {"type": error_type, "message": message}

    def _is_warning(self, line: str) -> bool:
        """Détecter si une ligne contient un warning"""
        patterns = [
            r".*warning[:)]",
            r".*warn[:)]",
            r".*deprecated",
            r".*caution",
        ]

        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in patterns)

    def _extract_warning_info(self, line: str) -> Dict:
        """Extraire les informations de warning"""
        message = line
        if "warning:" in line.lower():
            parts = line.lower().split("warning:", 1)
            if len(parts) > 1:
                message = parts[1].strip()

        return {"message": message}

    def _is_important_info(self, line: str) -> bool:
        """Détecter si une ligne contient des informations importantes"""
        patterns = [
            r".*starting.*comfyui",
            r".*server.*started",
            r".*loading.*model",
            r".*total.*vram",
            r".*gpu.*detected",
            r".*torch.*version",
            r".*cuda.*available",
        ]

        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in patterns)

    def _extract_info(self, line: str) -> str:
        """Extraire les informations importantes"""
        return line.strip()

    def _get_analysis_entries(self) -> List[Dict]:
        """Obtenir toutes les entrées d'analyse formatées pour l'affichage"""
        entries = []

        # Custom nodes OK
        for node in self.custom_nodes_ok:
            entries.append(
                {
                    "type": "OK",
                    "category": "Custom Node",
                    "element": node["node_name"],
                    "message": f"Custom node chargé avec succès",
                    "line": node["line"],
                    "details": node["content"],
                    "timestamp": node.get("timestamp", "N/A"),
                }
            )

        # Custom nodes Failed
        for node in self.custom_nodes_failed:
            entries.append(
                {
                    "type": "ERREUR",
                    "category": "Custom Node",
                    "element": node["node_name"],
                    "message": f"Échec du chargement: {node.get('error', 'Erreur inconnue')}",
                    "line": node["line"],
                    "details": node["content"],
                    "timestamp": node.get("timestamp", "N/A"),
                }
            )

        # Erreurs
        for error in self.errors:
            entries.append(
                {
                    "type": "ERREUR",
                    "category": error["error_type"],
                    "element": "Système",
                    "message": error["message"],
                    "line": error["line"],
                    "details": error["content"],
                    "timestamp": error.get("timestamp", "N/A"),
                }
            )

        # Warnings
        for warning in self.warnings:
            entries.append(
                {
                    "type": "ATTENTION",
                    "category": "Warning",
                    "element": "Système",
                    "message": warning["message"],
                    "line": warning["line"],
                    "timestamp": warning.get("timestamp", "N/A"),
                    "details": warning["content"],
                }
            )

        # Infos importantes
        for info in self.info_messages:
            entries.append(
                {
                    "type": "INFO",
                    "category": "Information",
                    "element": "Système",
                    "message": info["message"],
                    "line": info["line"],
                    "details": info["content"],
                    "timestamp": info.get("timestamp", "N/A"),
                }
            )

        # Trier par numéro de ligne
        entries.sort(key=lambda x: x["line"])

        return entries

    def get_all_entries(self) -> List[Dict]:
        """Méthode publique pour obtenir toutes les entrées d'analyse"""
        return self._get_analysis_entries()

    def get_summary_text(self) -> str:
        """Obtenir un résumé textuel de l'analyse"""
        summary = f"""📊 RÉSUMÉ DE L'ANALYSE DES LOGS COMFYUI
{'='*50}

✅ Custom Nodes OK: {len(self.custom_nodes_ok)}
❌ Custom Nodes Failed: {len(self.custom_nodes_failed)}
🔴 Erreurs: {len(self.errors)}
⚠️  Warnings: {len(self.warnings)}
ℹ️  Informations: {len(self.info_messages)}

Total d'éléments analysés: {len(self.custom_nodes_ok) + len(self.custom_nodes_failed) + len(self.errors) + len(self.warnings) + len(self.info_messages)}
"""
        return summary


def test_log_analyzer():
    """Fonction de test pour l'analyseur de logs"""
    analyzer = cy8_log_analyzer()

    # Test avec un fichier factice si disponible
    test_log = "test_comfyui.log"
    if os.path.exists(test_log):
        result = analyzer.analyze_log_file(test_log)
        print("Résultat du test:", json.dumps(result, indent=2))
    else:
        print("Aucun fichier de test disponible")


if __name__ == "__main__":
    test_log_analyzer()

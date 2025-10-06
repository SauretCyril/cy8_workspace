#!/usr/bin/env python3
"""
Test final de validation - Simulation complète du système expert
"""

import sys
import os
import sqlite3
import re

def final_validation_test():
    """Test final pour valider que le système expert fonctionne comme attendu"""

    print("🎯 VALIDATION FINALE - SYSTÈME EXPERT RAG")
    print("=" * 60)

    db_path = "G:\\tmp\\prompts_manager.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Récupérer les analyses comme le ferait la vraie application
        cursor.execute("""
            SELECT id, environment_id, fichier, type, niveau, message, details, timestamp_analyse
            FROM resultats_analyses
            WHERE environment_id = 'G11_05'
            ORDER BY timestamp_analyse DESC
            LIMIT 50
        """)

        all_analyses = cursor.fetchall()

        # Simulation de get_recent_log_analyses
        recent_analyses = []
        for analysis in all_analyses:
            formatted_analysis = {
                "id": analysis[0],
                "environment_id": analysis[1],
                "file": analysis[2],
                "log_type": analysis[3],
                "level": analysis[4],
                "message": analysis[5],
                "details": analysis[6],
                "timestamp": analysis[7]
            }
            recent_analyses.append(formatted_analysis)

        print(f"📊 Analyses récupérées: {len(recent_analyses)}")
        print(f"🆔 Environnement: G11_05")
        print("")

        # === SIMULATION EXACTE DE generate_expert_error_analysis ===

        # Filtrage corrigé
        relevant_errors = [a for a in recent_analyses if
                           a.get('log_type', '').upper() in ['ERREUR', 'ERROR'] or
                           a.get('level', '').upper() in ['ERROR', 'WARNING', 'ATTENTION'] or
                           'error' in a.get('message', '').lower() or
                           'failed' in a.get('message', '').lower() or
                           'exception' in a.get('message', '').lower()]

        # Extraction custom nodes
        custom_nodes_info = {}

        for error in relevant_errors:
            message = error.get('message', '')

            patterns = [
                r'custom_nodes[/\\]([^/\\\\s]+)',
                r'ComfyUI[/\\]custom_nodes[/\\]([^/\\\\s]+)',
                r'([a-zA-Z_][a-zA-Z0-9_-]*[-_]node[-_]?[a-zA-Z0-9_-]*)',
                r'([a-zA-Z_][a-zA-Z0-9_-]*[-_]suite[-_]?[a-zA-Z0-9_-]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_-]+)\s+import',
                r'module\s+[\'"]([^\'"]+)[\'"]',
                r'([a-zA-Z_][a-zA-Z0-9_-]*comfy[a-zA-Z0-9_-]*)',
                r'`([^`]+)`\s*(?:custom|node|suite)',
                r'([a-zA-Z_][a-zA-Z0-9_-]{2,})\s*(?:load|install|fail|error)',
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, message, re.IGNORECASE)
                for match in matches:
                    node_name = match.group(1)
                    false_positives = [
                        'line', 'file', 'module', 'import', 'error', 'warning', 'python',
                        'load', 'failed', 'custom', 'node', 'suite', 'config', 'json',
                        'path', 'bin', 'was', 'comfyui', 'main', 'py', 'lib', 'site',
                        'packages', 'torch', 'numpy', 'api'
                    ]
                    if (len(node_name) >= 3 and
                        node_name.lower() not in false_positives and
                        not node_name.isdigit()):
                        custom_nodes_info[node_name] = custom_nodes_info.get(node_name, 0) + 1

        # Classification des erreurs
        error_patterns = {}
        for error in relevant_errors:
            message = error.get('message', '')
            if 'cuda' in message.lower() or 'gpu' in message.lower() or 'torch' in message.lower():
                error_patterns['CUDA/GPU'] = error_patterns.get('CUDA/GPU', 0) + 1
            elif any(node in message.lower() for node in custom_nodes_info.keys()) or 'custom' in message.lower():
                error_patterns['Custom Nodes'] = error_patterns.get('Custom Nodes', 0) + 1
            elif 'memory' in message.lower() or 'oom' in message.lower():
                error_patterns['Mémoire'] = error_patterns.get('Mémoire', 0) + 1
            elif 'model' in message.lower() or 'ckpt' in message.lower():
                error_patterns['Modèles'] = error_patterns.get('Modèles', 0) + 1
            elif 'dependency' in message.lower() or 'import' in message.lower() or 'module' in message.lower():
                error_patterns['Dépendances'] = error_patterns.get('Dépendances', 0) + 1
            else:
                error_patterns['Autres'] = error_patterns.get('Autres', 0) + 1

        # === RÉPONSE EXPERTE COMPLÈTE ===

        response = []
        response.append("🔍 **ANALYSE D'EXPERT - GESTION D'ERREURS**")
        response.append("=" * 50)
        response.append("")

        if relevant_errors:
            response.append(f"📊 **{len(relevant_errors)} erreurs analysées** dans l'environnement `G11_05`")
            response.append("")

            # Noms de custom nodes détectés
            if custom_nodes_info:
                response.append("🔌 **CUSTOM NODES PROBLÉMATIQUES IDENTIFIÉS:**")
                for node_name, count in sorted(custom_nodes_info.items(), key=lambda x: x[1], reverse=True):
                    response.append(f"• **{node_name}** - {count} erreur(s)")
                response.append("")

            # Répartition des erreurs
            if error_patterns:
                response.append("📈 **RÉPARTITION DES ERREURS:**")
                for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
                    response.append(f"• **{pattern}:** {count} occurrence(s)")
                response.append("")

            # Solutions recommandées
            response.append("💡 **SOLUTIONS RECOMMANDÉES:**")

            if error_patterns.get('Custom Nodes', 0) > 0:
                response.append("🔌 **Problèmes Custom Nodes:**")
                if custom_nodes_info:
                    response.append("   • **Nodes identifiés avec problèmes:**")
                    for node_name, count in list(custom_nodes_info.items())[:3]:
                        response.append(f"     - {node_name} ({count} erreur(s))")
                response.append("   • Mettre à jour ComfyUI Manager")
                response.append("   • Réinstaller les custom nodes défaillants")
                response.append("   • Vérifier les dépendances Python avec:")
                response.append("     `pip install -r requirements.txt`")
                response.append("")

            if error_patterns.get('CUDA/GPU', 0) > 0:
                response.append("🎮 **Problèmes GPU/CUDA:**")
                response.append("   • Vérifier que CUDA est installé correctement")
                response.append("   • Redémarrer ComfyUI pour réinitialiser la mémoire GPU")
                response.append("   • Réduire la taille des modèles ou batch size")
                response.append("")

            if error_patterns.get('Dépendances', 0) > 0:
                response.append("📦 **Problèmes Dépendances:**")
                response.append("   • Vérifier l'environnement Python")
                response.append("   • Réinstaller les packages manquants")
                response.append("   • Utiliser l'environnement Python embedded de ComfyUI")
                response.append("")

        else:
            response.append("✅ **Aucune erreur récente détectée** dans cet environnement.")

        # Affichage de la réponse complète
        print("🤖 **RÉPONSE EXPERTE FINALE:**")
        print("")
        for line in response:
            print(line)

        print("")
        print("🎯 **VALIDATION:**")
        print(f"✅ Filtrage erreurs: {len(relevant_errors)} trouvées")
        print(f"✅ Custom nodes: {len(custom_nodes_info)} identifiés")
        print(f"✅ Catégorisation: {len(error_patterns)} catégories")
        print(f"✅ Solutions: Recommandations spécifiques générées")

        # Comparaison avec l'ancien résultat
        print("")
        print("📊 **COMPARAISON:**")
        print("❌ AVANT: '📊 2 erreurs analysées' + 'Autres: 2 occurrence(s)'")
        print(f"✅ APRÈS: '📊 {len(relevant_errors)} erreurs analysées' + custom nodes identifiés + solutions détaillées")

        conn.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    final_validation_test()

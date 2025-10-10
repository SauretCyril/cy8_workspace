#!/usr/bin/env python3
"""
Test de la fonction generate_expert_error_analysis corrigée
"""

import sys
import os
import sqlite3
import re

def test_corrected_function():
    """Test de la fonction corrigée avec les vraies données"""

    print("🔍 TEST FONCTION CORRIGÉE")
    print("=" * 50)

    db_path = "G:\\tmp\\prompts_manager.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Simuler get_recent_log_analyses - récupération des 50 dernières analyses
        cursor.execute("""
            SELECT id, environment_id, fichier, type, niveau, message, details, timestamp_analyse
            FROM resultats_analyses
            WHERE environment_id = 'G11_05'
            ORDER BY timestamp_analyse DESC
            LIMIT 50
        """)

        all_analyses = cursor.fetchall()

        # Convertir au format attendu par la fonction
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

        print(f"📊 Total analyses récupérées: {len(recent_analyses)}")

        # Appliquer le nouveau filtre corrigé
        relevant_errors = [a for a in recent_analyses if
                           a.get('log_type', '').upper() in ['ERREUR', 'ERROR'] or
                           a.get('level', '').upper() in ['ERROR', 'WARNING', 'ATTENTION'] or
                           'error' in a.get('message', '').lower() or
                           'failed' in a.get('message', '').lower() or
                           'exception' in a.get('message', '').lower()]

        print(f"🔴 Erreurs filtrées: {len(relevant_errors)}")

        # Analyser les custom nodes avec les nouveaux patterns
        custom_nodes_info = {}

        for error in relevant_errors:
            message = error.get('message', '')
            print(f"\n🔍 Analyse: {message[:100]}...")

            # Nouveaux patterns améliorés
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

            found_nodes = []
            for pattern in patterns:
                matches = re.finditer(pattern, message, re.IGNORECASE)
                for match in matches:
                    node_name = match.group(1)
                    # Filtrer les faux positifs
                    false_positives = [
                        'line', 'file', 'module', 'import', 'error', 'warning', 'python',
                        'load', 'failed', 'custom', 'node', 'suite', 'config', 'json',
                        'path', 'bin', 'was', 'comfyui', 'main', 'py', 'lib', 'site',
                        'packages', 'torch', 'numpy', 'api'
                    ]
                    if (len(node_name) >= 3 and
                        node_name.lower() not in false_positives and
                        not node_name.isdigit()):
                        found_nodes.append(node_name)
                        custom_nodes_info[node_name] = custom_nodes_info.get(node_name, 0) + 1

            if found_nodes:
                print(f"🔌 Custom nodes trouvés: {found_nodes}")

        # Classification par catégories
        error_patterns = {}
        for error in relevant_errors:
            message = error.get('message', '')
            # Simplifier le message pour identifier les patterns
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

        # Résumé final style fonction réelle
        print(f"\n🤖 **RÉSULTAT FONCTION CORRIGÉE:**")
        print(f"📊 **{len(relevant_errors)} erreurs analysées** dans l'environnement `G11_05`")

        if custom_nodes_info:
            print(f"\n🔌 **CUSTOM NODES PROBLÉMATIQUES IDENTIFIÉS:**")
            for node_name, count in sorted(custom_nodes_info.items(), key=lambda x: x[1], reverse=True):
                print(f"• **{node_name}** - {count} erreur(s)")

        if error_patterns:
            print(f"\n📈 **RÉPARTITION DES ERREURS:**")
            for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"• **{pattern}:** {count} occurrence(s)")

        conn.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_corrected_function()

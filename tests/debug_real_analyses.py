#!/usr/bin/env python3
"""
Debug des données d'analyse réelles de l'environnement G11_05
"""

import sys
import os

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def debug_real_analyses():
    """Déboguer les vraies données d'analyse"""

    try:
        print("🔍 DEBUG - ANALYSES RÉELLES ENVIRONNEMENT G11_05")
        print("=" * 60)

        # Importer les modules nécessaires
        from cy8_database_manager import cy8_database_manager

        # Utiliser la même base que l'application
        db_path = "G:\\tmp\\prompts_manager.db"
        print(f"📁 Base de données: {db_path}")

        if not os.path.exists(db_path):
            print("❌ Base de données introuvable")
            return

        # Initialiser le gestionnaire de base
        db_manager = cy8_database_manager(db_path)

        # Récupérer les analyses pour G11_05
        print("\n🔍 Récupération des analyses pour G11_05...")
        analyses = db_manager.get_analysis_results("G11_05")

        print(f"📊 Nombre d'analyses trouvées: {len(analyses)}")

        if not analyses:
            print("⚠️ Aucune analyse trouvée pour G11_05")

            # Vérifier tous les environnements disponibles
            print("\n🔍 Vérification des environnements disponibles...")
            all_analyses = db_manager.get_analysis_results()
            env_ids = set()
            for analysis in all_analyses:
                if len(analysis) > 1:
                    env_ids.add(analysis[1])  # environment_id

            print(f"🆔 Environnements trouvés: {list(env_ids)}")
            return

        # Analyser les 10 premières analyses
        print(f"\n📋 Analyse des {min(10, len(analyses))} premières entrées:")
        print("-" * 50)

        error_count = 0
        custom_nodes_found = []

        for i, analysis in enumerate(analyses[:10]):
            print(f"\n**{i+1}.** ID: {analysis[0]}")
            print(f"   Environnement: {analysis[1]}")
            print(f"   Fichier: {analysis[2]}")
            print(f"   Type: {analysis[3]}")
            print(f"   Niveau: {analysis[4]}")
            print(f"   Message: {analysis[5][:100]}...")
            print(f"   Timestamp: {analysis[7]}")

            # Vérifier si c'est une erreur
            if 'error' in analysis[3].lower() or 'failed' in analysis[5].lower():
                error_count += 1

                # Chercher des custom nodes dans le message
                message = analysis[5].lower()
                if 'custom' in message and 'node' in message:
                    custom_nodes_found.append(analysis[5])

        print(f"\n📊 **RÉSUMÉ:**")
        print(f"• Erreurs détectées: {error_count}")
        print(f"• Mentions custom nodes: {len(custom_nodes_found)}")

        if custom_nodes_found:
            print(f"\n🔌 **MESSAGES AVEC CUSTOM NODES:**")
            for j, msg in enumerate(custom_nodes_found[:5], 1):
                print(f"   {j}. {msg[:150]}...")

        # Test de la fonction get_recent_log_analyses
        print(f"\n🧪 Test de la fonction get_recent_log_analyses...")

        # Simuler la méthode de l'application
        formatted_analyses = []
        for analysis in analyses[:20]:  # Limiter à 20
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
            formatted_analyses.append(formatted_analysis)

        print(f"📊 Analyses formatées: {len(formatted_analyses)}")

        # Test de catégorisation
        error_patterns = {}
        custom_nodes_info = {}

        for analysis in formatted_analyses:
            if 'error' in analysis['log_type'].lower() or 'failed' in analysis['message'].lower():
                message = analysis['message'].lower()

                # Catégoriser
                if 'cuda' in message:
                    error_patterns['CUDA/GPU'] = error_patterns.get('CUDA/GPU', 0) + 1
                elif 'custom' in message and 'node' in message:
                    error_patterns['Custom Nodes'] = error_patterns.get('Custom Nodes', 0) + 1
                elif 'memory' in message:
                    error_patterns['Mémoire'] = error_patterns.get('Mémoire', 0) + 1
                elif 'model' in message:
                    error_patterns['Modèles'] = error_patterns.get('Modèles', 0) + 1
                elif 'dependency' in message or 'import' in message:
                    error_patterns['Dépendances'] = error_patterns.get('Dépendances', 0) + 1
                else:
                    error_patterns['Autres'] = error_patterns.get('Autres', 0) + 1

                # Extraire les noms de custom nodes
                if 'custom' in message and 'node' in message:
                    import re
                    patterns = [
                        r"custom node['\s]*['\"]([^'\"]+)['\"]",
                        r"node['\s]*['\"]([^'\"]+)['\"]",
                        r"'([A-Za-z0-9_-]{3,})'[^\w]*(?:custom|node)",
                        r"custom_nodes[/\\]([A-Za-z0-9_-]{3,})",
                    ]

                    for pattern in patterns:
                        matches = re.findall(pattern, analysis['message'], re.IGNORECASE)
                        for match in matches:
                            if (len(match) >= 3 and
                                not match.lower() in ['custom', 'node', 'failed', 'error', 'load', 'import', 'from', 'loading', 'missing'] and
                                not match.isdigit() and
                                ('-' in match or '_' in match or len(match) >= 5)):
                                custom_nodes_info[match] = custom_nodes_info.get(match, 0) + 1

        print(f"\n📈 **PATTERNS D'ERREURS TROUVÉS:**")
        for pattern, count in error_patterns.items():
            print(f"• {pattern}: {count}")

        if custom_nodes_info:
            print(f"\n🔌 **CUSTOM NODES EXTRAITS:**")
            for node, count in custom_nodes_info.items():
                print(f"• {node}: {count}")
        else:
            print(f"\n⚠️ Aucun custom node extrait")

        print(f"\n✅ Debug terminé")

    except Exception as e:
        print(f"\n❌ Erreur durant le debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_real_analyses()

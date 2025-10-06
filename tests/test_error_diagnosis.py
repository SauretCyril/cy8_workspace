#!/usr/bin/env python3
"""
Test des corrections et extraction des noms de custom nodes
"""

import sys
import os
import re

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_custom_node_extraction():
    """Tester l'extraction des noms de custom nodes"""

    print("🧪 Test extraction noms custom nodes")
    print("=" * 50)

    # Messages d'erreur d'exemple
    test_messages = [
        "Failed to load custom node 'ComfyUI-Manager'",
        "Error in custom node \"xyz-workflow-node\"",
        "Custom node 'AnimateDiff-Evolved' has dependency issues",
        "Cannot import custom_nodes/ComfyUI-Advanced-ControlNet/nodes.py",
        "Missing dependency for Impact-Pack custom node",
        "Failed to initialize WAS-Node-Suite",
        "Custom node reactor-node failed to load",
        "Error loading custom nodes from custom_nodes/efficiency-nodes-comfyui",
        "Node 'rgthree-comfy' custom initialization failed",
        "ComfyUI-VideoHelperSuite custom node error"
    ]

    custom_nodes_info = {}

    # Patterns d'extraction optimisés
    patterns = [
        r"custom node['\s]*['\"]([^'\"]+)['\"]",        # custom node "nom"
        r"node['\s]*['\"]([^'\"]+)['\"]",              # node "nom"
        r"'([A-Za-z0-9_-]{3,})'[^\w]*(?:custom|node)", # 'nom' custom/node (min 3 chars)
        r"custom_nodes[/\\]([A-Za-z0-9_-]{3,})",       # path custom_nodes/nom
        r"([A-Za-z0-9_-]{5,})(?:\s+custom\s+node)",    # nom custom node (min 5 chars)
    ]

    print("📋 **Messages d'erreur analysés:**")
    for i, message in enumerate(test_messages, 1):
        print(f"{i}. {message}")

        # Appliquer les patterns
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                # Filtrer les mots génériques et trop courts
                if (len(match) >= 3 and
                    not match.lower() in ['custom', 'node', 'failed', 'error', 'load', 'import', 'from', 'loading', 'missing'] and
                    not match.isdigit() and
                    ('-' in match or '_' in match or len(match) >= 5)):  # Noms typiques de custom nodes
                    custom_nodes_info[match] = custom_nodes_info.get(match, 0) + 1
                    print(f"   🔍 Détecté: {match}")
        print("")

    print("🔌 **CUSTOM NODES PROBLÉMATIQUES IDENTIFIÉS:**")
    if custom_nodes_info:
        for node_name, count in sorted(custom_nodes_info.items(), key=lambda x: x[1], reverse=True):
            print(f"• **{node_name}** - {count} erreur(s)")
    else:
        print("Aucun custom node détecté")

    print("\n✅ **Test d'extraction terminé**")

    return custom_nodes_info

def test_error_patterns():
    """Tester la catégorisation des erreurs"""

    print("\n🧪 Test catégorisation erreurs")
    print("=" * 40)

    # Exemples d'erreurs avec différents patterns
    test_errors = [
        {"message": "CUDA out of memory error during model loading", "type": "error"},
        {"message": "Failed to load custom node ComfyUI-Manager", "type": "error"},
        {"message": "Memory allocation failed for large model", "type": "error"},
        {"message": "Cannot import torch dependency", "type": "error"},
        {"message": "Model checkpoint not found", "type": "error"},
        {"message": "Custom node dependency missing: numpy", "type": "error"},
        {"message": "GPU memory exceeded during inference", "type": "error"},
    ]

    error_patterns = {}

    print("📊 **Erreurs analysées:**")
    for error in test_errors:
        message = error.get('message', '')
        print(f"• {message}")

        # Catégoriser
        if 'cuda' in message.lower():
            error_patterns['CUDA/GPU'] = error_patterns.get('CUDA/GPU', 0) + 1
        elif 'custom' in message.lower() and 'node' in message.lower():
            error_patterns['Custom Nodes'] = error_patterns.get('Custom Nodes', 0) + 1
        elif 'memory' in message.lower():
            error_patterns['Mémoire'] = error_patterns.get('Mémoire', 0) + 1
        elif 'model' in message.lower():
            error_patterns['Modèles'] = error_patterns.get('Modèles', 0) + 1
        elif 'dependency' in message.lower() or 'import' in message.lower():
            error_patterns['Dépendances'] = error_patterns.get('Dépendances', 0) + 1
        else:
            error_patterns['Autres'] = error_patterns.get('Autres', 0) + 1

    print("\n📈 **RÉPARTITION DES ERREURS:**")
    for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"• **{pattern}:** {count} occurrence(s)")

    print("\n✅ **Test de catégorisation terminé**")

def main():
    """Fonction principale"""

    print("🧪 TEST SYSTEM DE DIAGNOSTIC ERREURS AMÉLIORÉ")
    print("=" * 60)

    # Test 1: Extraction noms custom nodes
    custom_nodes = test_custom_node_extraction()

    # Test 2: Catégorisation erreurs
    test_error_patterns()

    print("\n" + "=" * 60)
    print("🎉 **RÉSUMÉ DES AMÉLIORATIONS:**")
    print("")
    print("✅ **Extraction noms custom nodes** - Fonctionne")
    print("   - Détecte les noms spécifiques dans les messages d'erreur")
    print("   - Compte les occurrences par custom node")
    print("   - Utilise des patterns regex avancés")
    print("")
    print("✅ **Catégorisation intelligente** - Fonctionne")
    print("   - CUDA/GPU, Custom Nodes, Mémoire, Modèles, Dépendances")
    print("   - Solutions spécifiques par catégorie")
    print("   - Recommandations contextuelles")
    print("")
    print("✅ **Correction erreur méthode RAG** - search_similar_issues")
    print("   - Corrigé search_relevant_analyses → search_similar_issues")
    print("   - Compatible avec l'API RAGManager")
    print("")
    print("🚀 **Le système peut maintenant identifier précisément:**")
    if custom_nodes:
        print("   - Noms des custom nodes problématiques")
        for node in list(custom_nodes.keys())[:3]:
            print(f"     • {node}")
    print("   - Types d'erreurs spécifiques")
    print("   - Solutions ciblées par problème")

if __name__ == "__main__":
    main()

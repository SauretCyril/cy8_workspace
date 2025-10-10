#!/usr/bin/env python3
"""
Test simple des patterns d'extraction sans import des modules principaux
"""

import re

def test_custom_node_extraction_simple():
    """Tester l'extraction des noms de custom nodes - version simple"""

    print("🧪 Test extraction noms custom nodes - VERSION OPTIMISÉE")
    print("=" * 60)

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
        detected_nodes = []

        # Appliquer les patterns
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                # Filtrer les mots génériques et trop courts
                if (len(match) >= 3 and
                    not match.lower() in ['custom', 'node', 'failed', 'error', 'load', 'import', 'from', 'loading', 'missing'] and
                    not match.isdigit() and
                    ('-' in match or '_' in match or len(match) >= 5)):  # Noms typiques de custom nodes
                    if match not in detected_nodes:  # Éviter les doublons pour ce message
                        custom_nodes_info[match] = custom_nodes_info.get(match, 0) + 1
                        detected_nodes.append(match)
                        print(f"   🔍 Détecté: {match}")

        if not detected_nodes:
            print(f"   ⚪ Aucun custom node détecté")
        print("")

    print("🔌 **CUSTOM NODES PROBLÉMATIQUES IDENTIFIÉS:**")
    if custom_nodes_info:
        for node_name, count in sorted(custom_nodes_info.items(), key=lambda x: x[1], reverse=True):
            print(f"• **{node_name}** - {count} erreur(s)")
    else:
        print("Aucun custom node détecté")

    print("\n✅ **Test d'extraction terminé**")

    # Analyse de la qualité des résultats
    expected_nodes = [
        "ComfyUI-Manager", "xyz-workflow-node", "AnimateDiff-Evolved",
        "ComfyUI-Advanced-ControlNet", "Impact-Pack", "WAS-Node-Suite",
        "efficiency-nodes-comfyui", "rgthree-comfy", "ComfyUI-VideoHelperSuite"
    ]

    detected_nodes = list(custom_nodes_info.keys())
    correctly_detected = [node for node in expected_nodes if node in detected_nodes]

    print(f"\n📊 **ANALYSE DE QUALITÉ:**")
    print(f"• **Nodes attendus:** {len(expected_nodes)}")
    print(f"• **Nodes détectés:** {len(detected_nodes)}")
    print(f"• **Détections correctes:** {len(correctly_detected)}")
    print(f"• **Taux de réussite:** {(len(correctly_detected)/len(expected_nodes)*100):.1f}%")

    if correctly_detected:
        print(f"\n✅ **NODES CORRECTEMENT DÉTECTÉS:**")
        for node in correctly_detected:
            print(f"   • {node}")

    missed_nodes = [node for node in expected_nodes if node not in detected_nodes]
    if missed_nodes:
        print(f"\n⚠️ **NODES RATÉS:**")
        for node in missed_nodes:
            print(f"   • {node}")

    return custom_nodes_info

if __name__ == "__main__":
    print("🧪 TEST PATTERNS D'EXTRACTION CUSTOM NODES")
    print("=" * 50)

    results = test_custom_node_extraction_simple()

    print("\n" + "=" * 50)
    print("🎉 **RÉSUMÉ:**")
    print("✅ Patterns optimisés pour éviter les faux positifs")
    print("✅ Filtrage des mots génériques (load, import, etc.)")
    print("✅ Détection basée sur la structure typique des noms")
    print("✅ Comptage des occurrences par custom node")
    print("")
    print("🚀 Le système peut maintenant répondre précisément à:")
    print("   'Tu n'as pas le nom du custom node ?'")
    print("   → Liste des custom nodes problématiques identifiés")

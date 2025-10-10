#!/usr/bin/env python3
"""
Test de la fonction generate_expert_error_analysis avec les vraies données
"""

import sys
import os
import re

def simulate_expert_analysis():
    """Simule l'analyse experte avec les vraies données trouvées"""

    print("🔍 SIMULATION ANALYSE EXPERTE")
    print("=" * 50)

    # Vraies erreurs de la base de données
    real_errors = [
        "Module 'diffusers' load failed. If you don't have it installed, do it:",
        "`ffmpeg_bin_path` is not set in `h:\\comfyui\\g11_05\\custom_nodes\\was-node-suite-comfyui\\was_suite_config.json` config file. will attempt to use system ffmpeg binaries if available.",
        "File \"E:\\Comfyui_G11\\ComfyUI\\main.py\", line 149, in <module>",
        "Failed to initialize NumPy: _ARRAY_API not found",
        "Warning, you are using an old pytorch version and some ckpt/pt files might be loaded unsafely. Upgrading to 2.4 or above is recommended."
    ]

    print(f"📊 Erreurs à analyser: {len(real_errors)}")

    # Patterns de custom nodes (copié du code principal)
    custom_node_patterns = [
        r'custom_nodes[/\\]([^/\\\\s]+)',
        r'ComfyUI[/\\]custom_nodes[/\\]([^/\\\\s]+)',
        r'([a-zA-Z_][a-zA-Z0-9_-]*[-_]node[-_]?[a-zA-Z0-9_-]*)',
        r'([a-zA-Z_][a-zA-Z0-9_-]*[-_]suite[-_]?[a-zA-Z0-9_-]*)',
        r'from\s+([a-zA-Z_][a-zA-Z0-9_-]+)\s+import',
        r'module\s+[\'"]([^\'"]+)[\'"]',
        r'([a-zA-Z_][a-zA-Z0-9_-]*comfy[a-zA-Z0-9_-]*)',
        r'([a-zA-Z_][a-zA-Z0-9_-]*workflow[a-zA-Z0-9_-]*)',
    ]

    # Classification manuelle pour comparaison
    categories = {
        'Custom Nodes': [],
        'CUDA/GPU': [],
        'Memory': [],
        'Models': [],
        'Dependencies': [],
        'Autres': []
    }

    for i, error in enumerate(real_errors):
        print(f"\n🔍 **ERREUR {i+1}:**")
        print(f"📝 {error[:100]}...")

        # Test extraction custom nodes
        found_nodes = []
        for pattern in custom_node_patterns:
            matches = re.finditer(pattern, error, re.IGNORECASE)
            for match in matches:
                node_name = match.group(1)
                if len(node_name) > 2 and node_name not in found_nodes:
                    # Filtrer les faux positifs
                    false_positives = ['line', 'file', 'module', 'import', 'error', 'warning', 'python']
                    if node_name.lower() not in false_positives:
                        found_nodes.append(node_name)

        print(f"🔌 Custom nodes extraits: {found_nodes}")

        # Classification
        error_lower = error.lower()
        if found_nodes:
            categories['Custom Nodes'].extend(found_nodes)
            print("📂 Catégorie: Custom Nodes")
        elif any(word in error_lower for word in ['cuda', 'gpu', 'nvidia', 'torch']):
            categories['CUDA/GPU'].append(error)
            print("📂 Catégorie: CUDA/GPU")
        elif any(word in error_lower for word in ['memory', 'oom', 'allocation']):
            categories['Memory'].append(error)
            print("📂 Catégorie: Memory")
        elif any(word in error_lower for word in ['model', 'checkpoint', 'ckpt']):
            categories['Models'].append(error)
            print("📂 Catégorie: Models")
        elif any(word in error_lower for word in ['module', 'import', 'package', 'install']):
            categories['Dependencies'].append(error)
            print("📂 Catégorie: Dependencies")
        else:
            categories['Autres'].append(error)
            print("📂 Catégorie: Autres")

    # Résumé final
    print(f"\n📈 **RÉSUMÉ PAR CATÉGORIE:**")
    for category, items in categories.items():
        if items:
            print(f"• {category}: {len(items)} occurrence(s)")
            if category == 'Custom Nodes':
                print(f"  Nodes: {list(set(items))}")

    # Test du format de réponse experte
    print(f"\n🤖 **SIMULATION RÉPONSE EXPERTE:**")
    print("Analyse de l'environnement ComfyUI G11_05:")
    print(f"📊 {len(real_errors)} erreurs analysées")

    for category, items in categories.items():
        if items:
            if category == 'Custom Nodes':
                unique_nodes = list(set(items))
                print(f"• {category}: {unique_nodes}")
            else:
                print(f"• {category}: {len(items)} occurrence(s)")

if __name__ == "__main__":
    simulate_expert_analysis()

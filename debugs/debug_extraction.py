#!/usr/bin/env python3
"""
Debug de l'extraction de l'ID - test avec ligne exacte
"""

import os
import sys
sys.path.append('src')

from cy8_log_analyzer import cy8_log_analyzer


def debug_extraction():
    """Debug détaillé de l'extraction"""
    print("🔍 DEBUG - Analyse du pattern d'extraction")
    print("=" * 50)

    # Ligne exacte fournie par l'utilisateur
    test_line = "Adding extra search path custom_nodes H:\\comfyui\\G11_04\\custom_nodes"
    print(f"📝 Ligne test: {test_line}")
    print(f"📝 Longueur: {len(test_line)} caractères")
    print()

    analyzer = cy8_log_analyzer()

    # Test du pattern actuel
    import re
    current_pattern = r".*comfyui[/\\]([^/\\]+)[/\\]custom_nodes"
    print(f"🔧 Pattern actuel: {current_pattern}")

    match = re.search(current_pattern, test_line, re.IGNORECASE)
    if match:
        print(f"✅ Match trouvé: '{match.group(1)}'")
        print(f"📊 Groupes: {match.groups()}")
    else:
        print("❌ Aucun match trouvé")

    print()

    # Test avec différents patterns
    test_patterns = [
        r".*comfyui[/\\]([^/\\]+)[/\\]custom_nodes",
        r"comfyui[/\\]([^/\\]+)[/\\]custom_nodes",
        r".*\\comfyui\\([^\\]+)\\custom_nodes",
        r".*[/\\]comfyui[/\\]([^/\\]+)[/\\]custom_nodes",
        r"H:[/\\].*[/\\]comfyui[/\\]([^/\\]+)[/\\]custom_nodes"
    ]

    print("🧪 Test de différents patterns:")
    for i, pattern in enumerate(test_patterns, 1):
        match = re.search(pattern, test_line, re.IGNORECASE)
        result = match.group(1) if match else "Pas de match"
        status = "✅" if match else "❌"
        print(f"  {i}. {status} {pattern}")
        print(f"     → Résultat: '{result}'")
        print()


def create_debug_log():
    """Créer un log de debug avec la ligne exacte"""
    content = """2025-09-26 10:00:01,123 - INFO - Starting ComfyUI
Adding extra search path custom_nodes H:\\comfyui\\G11_04\\custom_nodes

Import times for custom nodes:
   0.1 seconds: H:\\comfyui\\G11_04\\custom_nodes\\ComfyUI-Manager
   0.2 seconds: H:\\comfyui\\G11_04\\custom_nodes\\comfyui_controlnet_aux

2025-09-26 10:00:15,123 - INFO - Server started on 127.0.0.1:8188"""

    with open('debug_log.log', 'w', encoding='utf-8') as f:
        f.write(content)

    return 'debug_log.log'


def test_full_analysis():
    """Test de l'analyse complète"""
    print("🔍 DEBUG - Analyse complète du fichier")
    print("=" * 40)

    log_file = create_debug_log()
    print(f"✅ Fichier créé: {log_file}")

    analyzer = cy8_log_analyzer()
    result = analyzer.analyze_log_file(log_file)

    if result["success"]:
        config_id = result.get("config_id")
        print(f"🆔 ID trouvé: '{config_id}'")

        if config_id:
            print("✅ SUCCESS!")
        else:
            print("❌ FAILED - ID non trouvé")

            # Debug pas à pas
            print("\n🔍 Debug pas à pas:")
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                line = line.strip()
                if "Adding extra search path" in line and "custom_nodes" in line:
                    print(f"  Ligne {i}: {line}")
                    extracted = analyzer._extract_config_id(line)
                    print(f"  → ID extrait: '{extracted}'")
    else:
        print(f"❌ Erreur: {result['error']}")

    # Nettoyer
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"\n🧹 Fichier supprimé")


if __name__ == "__main__":
    debug_extraction()
    print()
    test_full_analysis()

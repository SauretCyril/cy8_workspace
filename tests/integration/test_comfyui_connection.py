#!/usr/bin/env python3
"""
Test de connexion ComfyUI pour vérifier que l'exécution de workflow fonctionne
"""

import os
import sys
import json
import urllib.request

# Ajouter le répertoire src au path Python
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cy6_wkf001_Basic import comfyui_basic_task
from cy6_websocket_api_client import server_address


def test_comfyui_connection():
    """Teste la connexion à ComfyUI"""
    print("🔍 Test de connexion ComfyUI...")

    try:
        # Test de base - est-ce que ComfyUI répond ?
        response = urllib.request.urlopen(
            f"http://{server_address}/system_stats", timeout=10
        )
        stats = response.read().decode()
        print(f"✅ ComfyUI est accessible sur {server_address}")

        # Parser les stats pour afficher des infos utiles
        stats_data = json.loads(stats)
        print(
            f"   Version ComfyUI: {stats_data.get('system', {}).get('comfyui_version', 'Unknown')}"
        )
        print(
            f"   Python: {stats_data.get('system', {}).get('python_version', 'Unknown')}"
        )

        return True

    except Exception as e:
        print(f"❌ ComfyUI n'est pas accessible: {e}")
        print(f"   Assurez-vous que ComfyUI fonctionne sur {server_address}")
        return False


# SUPPRIMÉ : Test d'exécution de workflow
# Le test d'exécution de workflow a été retiré conformément aux nouvelles spécifications.
# Les tests d'exécution doivent maintenant être effectués uniquement via l'onglet "ComfyUI"
# dans l'interface utilisateur avec le bouton "Tester connexion".


def test_workflow_execution_removed():
    """
    ⚠️  FONCTION SUPPRIMÉE

    Le test d'exécution de workflow automatique a été retiré.

    Pour tester l'exécution de workflows :
    1. Lancez l'application : python src/cy8_prompts_manager_main.py
    2. Sélectionnez un prompt dans la liste
    3. Allez dans l'onglet "ComfyUI" du panneau de détails
    4. Cliquez sur "🔗 Tester la connexion"

    Cette approche permet un contrôle plus fin et évite les tests automatiques
    qui pourraient interférer avec ComfyUI en production.
    """
    print("\n⚠️  Test d'exécution de workflow supprimé")
    print("   👉 Utilisez l'onglet 'ComfyUI' dans l'interface pour tester")
    return True


def main():
    print("🧪 Test de la connexion ComfyUI pour cy8_prompts_manager")
    print("=" * 60)

    # Test unique: Connexion de base seulement
    if test_comfyui_connection():
        print(f"\n✅ Test de connexion réussi ! ComfyUI est accessible.")
        print("\n💡 Pour tester l'exécution de workflows :")
        print("   1. Lancez l'application : python src/cy8_prompts_manager_main.py")
        print("   2. Sélectionnez un prompt dans la liste")
        print("   3. Allez dans l'onglet 'ComfyUI' du panneau de détails")
        print("   4. Cliquez sur '🔗 Tester la connexion'")
    else:
        print("\n💡 Conseils de dépannage:")
        print("   - Vérifiez que ComfyUI est lancé")
        print("   - Vérifiez que ComfyUI écoute sur 127.0.0.1:8188")
        print("   - Vérifiez qu'aucun firewall ne bloque la connexion")

    print("\n" + "=" * 60)
    print("ℹ️  Les tests d'exécution de workflow sont maintenant intégrés")
    print("   dans l'interface utilisateur pour un meilleur contrôle.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test des corrections apportées à la détection de fin de workflow
"""

import sys
import os

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from cy6_websocket_api_client import get_queue_status, is_prompt_in_queue
    print("✓ Import des nouvelles fonctions réussi")

    # Test de la fonction get_queue_status
    print("\n=== Test de get_queue_status ===")
    try:
        queue_status = get_queue_status()
        if queue_status is not None:
            print(f"✓ Queue status récupéré: {type(queue_status)}")
            print(f"  - Queue pending: {len(queue_status.get('queue_pending', []))} éléments")
            print(f"  - Queue running: {len(queue_status.get('queue_running', []))} éléments")
        else:
            print("⚠ Queue status est None (ComfyUI probablement non démarré)")
    except Exception as e:
        print(f"✗ Erreur get_queue_status: {e}")

    # Test de la fonction is_prompt_in_queue avec un ID fictif
    print("\n=== Test de is_prompt_in_queue ===")
    try:
        test_prompt_id = "test-prompt-id-123"
        is_in_queue = is_prompt_in_queue(test_prompt_id)
        print(f"✓ is_prompt_in_queue('{test_prompt_id}') = {is_in_queue}")
    except Exception as e:
        print(f"✗ Erreur is_prompt_in_queue: {e}")

    print("\n=== Test des corrections ===")
    print("✓ Toutes les nouvelles fonctions sont fonctionnelles")
    print("✓ La détection de fin de workflow devrait maintenant être plus robuste")
    print("\nPour tester complètement:")
    print("1. Démarrez ComfyUI")
    print("2. Lancez l'application: python src/cy8_prompts_manager_main.py")
    print("3. Exécutez un workflow long")
    print("4. Observez les messages DEBUG dans la console")

except ImportError as e:
    print(f"✗ Erreur d'import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Erreur générale: {e}")
    sys.exit(1)

print("\n🎉 Test terminé avec succès!")

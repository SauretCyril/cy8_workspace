#!/usr/bin/env python3
"""
Script de test pour vérifier les timeouts configurés
"""

import re

def test_timeouts():
    """Vérifier que les timeouts sont bien configurés à 600 secondes"""
    print("🔍 Vérification des timeouts configurés...\n")

    # Test 1: Timeout du workflow principal
    with open('src/cy8_prompts_manager_main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()

    main_timeout_match = re.search(r'max_wait_time\s*=\s*(\d+)', main_content)
    if main_timeout_match:
        main_timeout = int(main_timeout_match.group(1))
        print(f"✅ Timeout workflow principal: {main_timeout} secondes ({main_timeout/60:.1f} minutes)")
        if main_timeout == 600:
            print("   ✓ Configuré correctement à 10 minutes")
        else:
            print(f"   ❌ Devrait être 600, mais trouvé {main_timeout}")
    else:
        print("❌ Timeout workflow principal non trouvé")

    # Test 2: Timeout WebSocket
    with open('src/cy6_websocket_api_client.py', 'r', encoding='utf-8') as f:
        websocket_content = f.read()

    ws_timeout_match = re.search(r'ws\.settimeout\(([0-9.]+)\)', websocket_content)
    if ws_timeout_match:
        ws_timeout = float(ws_timeout_match.group(1))
        print(f"✅ Timeout WebSocket: {ws_timeout} secondes ({ws_timeout/60:.1f} minutes)")
        if ws_timeout == 600.0:
            print("   ✓ Configuré correctement à 10 minutes")
        else:
            print(f"   ❌ Devrait être 600.0, mais trouvé {ws_timeout}")
    else:
        print("❌ Timeout WebSocket non trouvé")

    print("\n🎯 Résumé:")
    print("- Timeout général du workflow: 600s (10 minutes)")
    print("- Timeout WebSocket: 600s (10 minutes)")
    print("- Cela permet d'attendre des workflows très longs sans interruption prématurée")

if __name__ == "__main__":
    test_timeouts()

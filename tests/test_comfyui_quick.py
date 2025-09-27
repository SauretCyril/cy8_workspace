#!/usr/bin/env python3
"""
Test de diagnostic rapide ComfyUI
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import urllib.request
import json


def test_comfyui_connection():
    """Test de base de la connexion ComfyUI"""
    server_address = "127.0.0.1:8188"

    print(f"Test de connexion à ComfyUI sur {server_address}...")

    try:
        # Test 1: Vérifier si le serveur répond
        with urllib.request.urlopen(f"http://{server_address}/", timeout=5) as response:
            print("✅ ComfyUI est accessible")

        # Test 2: Tester l'endpoint /prompt avec une requête vide
        test_prompt = {"prompt": {}, "client_id": "test_client"}
        data = json.dumps(test_prompt).encode("utf-8")
        req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read())
                print("✅ Endpoint /prompt accessible")
                print(f"Response: {result}")
        except urllib.error.HTTPError as e:
            print(f"⚠️  HTTP Error {e.code}: {e.reason}")
            if e.code == 400:
                print("   -> C'est normal avec un prompt vide, l'endpoint fonctionne")
            print(f"   Response: {e.read().decode()}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

    return True


if __name__ == "__main__":
    test_comfyui_connection()

#!/usr/bin/env python3
"""
Test spécifique pour déboguer la récupération des LoRAs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json
from cy8_models_manager import ComfyUIModelsManager

def test_comfyui_connection():
    """Test de connexion à ComfyUI"""
    print("🔍 Test de connexion à ComfyUI...")
    try:
        response = requests.get("http://127.0.0.1:8188/models", timeout=10)
        print(f"📡 Statut de connexion: {response.status_code}")
        if response.status_code == 200:
            types = response.json()
            print(f"📋 Types de modèles disponibles: {types}")
            print(f"🎯 LoRAs dans la liste: {'loras' in types}")
            return True, types
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False, []

def test_loras_endpoint():
    """Test spécifique de l'endpoint LoRAs"""
    print("\n🔍 Test spécifique de l'endpoint LoRAs...")
    try:
        response = requests.get("http://127.0.0.1:8188/models/loras", timeout=10)
        print(f"📡 Statut LoRAs: {response.status_code}")
        if response.status_code == 200:
            loras = response.json()
            print(f"📂 Nombre de LoRAs trouvés: {len(loras)}")
            if loras:
                print("🎯 Premiers LoRAs:")
                for i, lora in enumerate(loras[:5]):
                    print(f"   {i+1}. {lora}")
            else:
                print("⚠️ Aucun LoRA trouvé!")
            return loras
        else:
            print(f"❌ Erreur HTTP LoRAs: {response.status_code}")
            print(f"📄 Réponse: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Erreur LoRAs: {e}")
        return []

def test_models_manager():
    """Test du gestionnaire de modèles"""
    print("\n🔍 Test du gestionnaire de modèles...")
    manager = ComfyUIModelsManager()

    # Test des types
    print("📋 Récupération des types...")
    types = manager.get_model_types()
    print(f"📊 Types récupérés: {types}")

    # Test spécifique LoRAs
    if 'loras' in types:
        print("\n🎯 Test spécifique LoRAs...")
        loras = manager.get_models_by_type('loras')
        print(f"📂 LoRAs via manager: {len(loras)}")
        if loras:
            print("🎯 Premiers LoRAs via manager:")
            for i, lora in enumerate(loras[:5]):
                print(f"   {i+1}. {lora}")
    else:
        print("❌ Type 'loras' non trouvé dans les types!")

    # Test de tous les modèles
    print("\n📊 Test de récupération complète...")
    all_models = manager.get_all_models()

    print(f"📋 Types récupérés: {list(all_models.keys())}")

    if 'loras' in all_models:
        loras_count = len(all_models['loras'])
        print(f"🎯 LoRAs dans all_models: {loras_count}")
        if loras_count > 0:
            print("✅ Exemples de LoRAs:")
            for i, lora in enumerate(all_models['loras'][:3]):
                print(f"   {i+1}. {lora['name']}")
    else:
        print("❌ Clé 'loras' non trouvée dans all_models!")

def test_database_integration():
    """Test de l'intégration base de données"""
    print("\n🔍 Test de l'intégration base de données...")
    try:
        from cy8_database_manager import cy8_database_manager

        db_manager = cy8_database_manager()

        # Vérifier les modèles en base
        print("📊 Vérification des modèles en base...")
        models_in_db = db_manager.get_all_models()
        print(f"📂 Modèles en base: {len(models_in_db)}")

        # Compter les LoRAs
        loras_in_db = [m for m in models_in_db if m.get('type') == 'loras']
        print(f"🎯 LoRAs en base: {len(loras_in_db)}")

        if loras_in_db:
            print("✅ Exemples de LoRAs en base:")
            for i, lora in enumerate(loras_in_db[:3]):
                print(f"   {i+1}. {lora.get('name', 'N/A')}")
        else:
            print("⚠️ Aucun LoRA trouvé en base!")

    except Exception as e:
        print(f"❌ Erreur base de données: {e}")

if __name__ == "__main__":
    print("🚀 DEBUG LORAS - Test de récupération des LoRAs")
    print("=" * 60)

    # Test 1: Connexion ComfyUI
    connected, types = test_comfyui_connection()

    if not connected:
        print("❌ Impossible de se connecter à ComfyUI. Vérifiez que le serveur est démarré.")
        sys.exit(1)

    # Test 2: Endpoint LoRAs direct
    loras_direct = test_loras_endpoint()

    # Test 3: Gestionnaire de modèles
    test_models_manager()

    # Test 4: Base de données
    test_database_integration()

    print("\n" + "=" * 60)
    print("🎯 RÉSUMÉ DU DEBUG")
    print(f"📡 Connexion ComfyUI: {'✅' if connected else '❌'}")
    print(f"🎯 LoRAs disponibles (direct): {len(loras_direct)}")
    print(f"📋 Types disponibles: {len(types)}")
    print(f"🔍 Type 'loras' présent: {'✅' if 'loras' in types else '❌'}")

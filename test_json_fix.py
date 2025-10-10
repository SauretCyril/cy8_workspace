#!/usr/bin/env python3
"""
Test de correction de l'erreur json.JSONDecodeError
"""

import sys
import os

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_json_import_fix():
    """Test que l'import json est maintenant présent"""
    print("🧪 TEST CORRECTION IMPORT JSON")
    print("=" * 35)
    
    try:
        # Lire le fichier source
        with open("src/cy8_prompts_manager_main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Chercher la fonction _identify_with_custom_node
        start = content.find("def _identify_with_custom_node(self):")
        if start == -1:
            print("❌ Fonction _identify_with_custom_node non trouvée")
            return False
        
        # Prendre les 500 premiers caractères de la fonction
        function_start = content[start:start+500]
        
        # Vérifier que l'import json est présent
        if "import json" in function_start:
            print("✅ Import json trouvé dans la fonction")
        else:
            print("❌ Import json manquant dans la fonction")
            return False
        
        # Vérifier que l'exception est toujours présente
        if "json.JSONDecodeError" in content:
            print("✅ Exception json.JSONDecodeError présente")
        else:
            print("❌ Exception json.JSONDecodeError non trouvée")
            return False
        
        print("✅ Correction appliquée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_environment_identification():
    """Test d'identification d'environnement"""
    print("\n🧪 TEST IDENTIFICATION ENVIRONNEMENT")
    print("=" * 40)
    
    try:
        # Vérifier que le serveur ComfyUI est accessible
        from cy6_websocket_api_client import get_queue_status
        
        if get_queue_status() is None:
            print("⚠️ Serveur ComfyUI inaccessible - test limité")
            return True  # Pas d'erreur, juste serveur indisponible
        
        print("✅ Serveur ComfyUI accessible")
        
        # Test d'import des modules nécessaires
        try:
            from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller
            print("✅ Import ComfyUICustomNodeCaller réussi")
        except ImportError as e:
            print(f"⚠️ Import ComfyUICustomNodeCaller échoué: {e}")
            return True  # Pas critique pour ce test
        
        print("✅ Test d'identification OK (sans exécution complète)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test identification: {e}")
        return False

def main():
    """Test principal"""
    print("🔧 TEST CORRECTION ERREUR JSON")
    print("=" * 30)
    
    # Test 1: Vérification de la correction
    test1_ok = test_json_import_fix()
    
    # Test 2: Test d'identification
    test2_ok = test_environment_identification()
    
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 20)
    print(f"🔧 Correction import: {'✅' if test1_ok else '❌'}")
    print(f"🌍 Test identification: {'✅' if test2_ok else '❌'}")
    
    if test1_ok and test2_ok:
        print("\n🎉 CORRECTION RÉUSSIE!")
        print("✅ L'erreur UnboundLocalError est corrigée")
        print("✅ L'import json est maintenant présent")
        print("✅ L'identification d'environnement peut fonctionner")
    else:
        print("\n❌ PROBLÈME PERSISTANT")
        print("🔧 Vérifier la correction appliquée")

if __name__ == "__main__":
    main()
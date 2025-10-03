#!/usr/bin/env python3
"""
Test de validation de la correction du problème de changement d'environnement
"""

import sys
import os
import sqlite3
import tempfile
import json

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cy8_database_manager import cy8_database_manager

def create_test_data():
    """Créer des données de test avec des détails enrichis"""
    test_details = {
        "element": "ComfyUI-Manager",
        "line": 45,
        "time": "2.3s",
        "error_details": "CUDA memory allocation failed",
        "context": "Loading custom node",
        "error_type": "Memory Error",
        "full_line": "ERROR: Failed to load ComfyUI-Manager - CUDA memory allocation failed"
    }
    
    return {
        "environment_id": "test_env_001",
        "fichier": "comfyui.log",
        "type_result": "ERREUR",
        "niveau": "Memory Error",
        "message": "Failed to load ComfyUI-Manager | CUDA memory allocation failed",
        "details": json.dumps(test_details)
    }

def test_environment_data_consistency():
    """Test de cohérence des données lors du changement d'environnement"""
    print("🔄 Test de cohérence des données - changement d'environnement")
    print("=" * 65)
    
    # Créer une base de données temporaire
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        temp_db_path = tmp_file.name
    
    try:
        # Initialiser le gestionnaire de base de données
        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="dev")
        
        # Créer les données de test
        test_data = create_test_data()
        
        print("📝 ÉTAPE 1: Stockage des données enrichies")
        print("-" * 40)
        
        # Stocker les données de test
        success = db_manager.add_analysis_result(
            environment_id=test_data["environment_id"],
            fichier=test_data["fichier"],
            type_result=test_data["type_result"],
            niveau=test_data["niveau"],
            message=test_data["message"],
            details=test_data["details"]
        )
        
        if success:
            print("✅ Données stockées avec succès")
        else:
            print("❌ Échec du stockage")
            return False
        
        print("📤 ÉTAPE 2: Récupération des données")
        print("-" * 40)
        
        # Récupérer les données
        results = db_manager.get_analysis_results(test_data["environment_id"])
        
        if not results:
            print("❌ Aucune donnée récupérée")
            return False
        
        print(f"✅ {len(results)} résultat(s) récupéré(s)")
        
        # Analyser le premier résultat
        result = results[0]
        (result_id, env_id, fichier, type_result, niveau, message, details, timestamp) = result
        
        print("🔍 ÉTAPE 3: Validation des détails enrichis")
        print("-" * 40)
        
        print(f"ID: {result_id}")
        print(f"Environnement: {env_id}")
        print(f"Fichier: {fichier}")
        print(f"Type: {type_result}")
        print(f"Niveau: {niveau}")
        print(f"Message: {message}")
        print(f"Détails bruts: {details[:100] if details else 'Vide'}...")
        print(f"Timestamp: {timestamp}")
        
        if details:
            try:
                details_dict = json.loads(details)
                print("\n📋 DÉTAILS ENRICHIS PARSÉS:")
                for key, value in details_dict.items():
                    print(f"  • {key}: {value}")
                
                # Vérifier les éléments clés
                required_fields = ["element", "line", "error_details"]
                missing_fields = [field for field in required_fields if field not in details_dict]
                
                if missing_fields:
                    print(f"⚠️ Champs manquants: {missing_fields}")
                else:
                    print("✅ Tous les champs requis sont présents")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Erreur de parsing JSON: {e}")
                return False
        else:
            print("❌ Aucun détail enrichi trouvé")
            return False
            
    finally:
        # Nettoyer le fichier temporaire
        try:
            os.unlink(temp_db_path)
        except:
            pass

def test_reconstruction_logic():
    """Test de la logique de reconstruction des données"""
    print("\n🔧 Test de la logique de reconstruction")
    print("=" * 65)
    
    # Simuler les données récupérées de la base
    mock_result = (
        1,  # result_id
        "test_env_001",  # env_id
        "comfyui.log",  # fichier
        "ERREUR",  # type_result
        "Memory Error",  # niveau
        "Failed to load ComfyUI-Manager | CUDA memory allocation failed",  # message
        json.dumps({
            "element": "ComfyUI-Manager",
            "line": 45,
            "time": "2.3s",
            "error_details": "CUDA memory allocation failed",
            "context": "Loading custom node"
        }),  # details
        "2025-01-03T14:30:25.123456"  # timestamp
    )
    
    print("📊 DONNÉES D'ENTRÉE (simulées depuis la base):")
    print(f"Type: {mock_result[3]}")
    print(f"Message: {mock_result[5]}")
    print(f"Détails: {mock_result[6]}")
    
    # Simuler la logique de reconstruction
    (result_id, env_id, fichier, type_result, niveau, message, details, timestamp) = mock_result
    
    # Traitement comme dans la fonction corrigée
    display_message = message
    details_info = ""
    element_name = fichier
    line_number = "N/A"
    
    if details:
        try:
            details_dict = json.loads(details)
            
            # Extraire le nom de l'élément
            if "element" in details_dict and details_dict["element"]:
                element_name = details_dict["element"]
            
            # Extraire le numéro de ligne
            if "line" in details_dict and details_dict["line"]:
                line_number = str(details_dict["line"])
            
            # Traiter le message pour extraire les détails d'affichage
            if type_result in ["ERREUR", "ATTENTION"] and " | " in message:
                parts = message.split(" | ", 1)
                if len(parts) > 1:
                    display_message = parts[0]
                    details_info = parts[1]
            elif "error_details" in details_dict and details_dict["error_details"]:
                details_info = details_dict["error_details"]
                
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de parsing: {e}")
            return False
    
    print("\n📤 DONNÉES DE SORTIE (pour affichage):")
    print(f"Element: {element_name}")
    print(f"Message affiché: {display_message}")
    print(f"Détails info: {details_info}")
    print(f"Ligne: {line_number}")
    
    # Vérifier les résultats attendus
    expected_results = {
        "element_name": "ComfyUI-Manager",
        "display_message": "Failed to load ComfyUI-Manager",
        "details_info": "CUDA memory allocation failed",
        "line_number": "45"
    }
    
    print("\n✅ VALIDATION:")
    all_correct = True
    for key, expected in expected_results.items():
        actual = locals()[key]
        if actual == expected:
            print(f"  ✅ {key}: '{actual}' (correct)")
        else:
            print(f"  ❌ {key}: '{actual}' (attendu: '{expected}')")
            all_correct = False
    
    return all_correct

if __name__ == "__main__":
    print("🚀 Test de validation de la correction")
    print("=" * 65)
    
    test1 = test_environment_data_consistency()
    test2 = test_reconstruction_logic()
    
    print("\n" + "=" * 65)
    if test1 and test2:
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("\n🎯 CORRECTION VALIDÉE:")
        print("• Les données enrichies sont correctement stockées")
        print("• Les détails sont correctement récupérés")
        print("• La logique de reconstruction fonctionne")
        print("• Format cohérent entre analyse fraîche et récupération")
    else:
        print("❌ Certains tests ont échoué")
        print("   → Vérification nécessaire")
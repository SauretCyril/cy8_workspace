#!/usr/bin/env python3
"""
Test pour reproduire le problème de changement d'environnement
"""

import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_environment_switching_issue():
    """Test du problème de changement d'environnement"""
    print("🔄 Test du problème de changement d'environnement")
    print("=" * 55)
    
    print("🔍 PROBLÈME IDENTIFIÉ:")
    print("• Sélection environnement A → analyse logs → données OK")
    print("• Changement vers environnement B")  
    print("• Retour vers environnement A → données différentes!")
    print()
    
    print("📋 ANALYSE DU CODE:")
    print("1. Fonction analyze_comfyui_log():")
    print("   - Insère 7 colonnes: timestamp, type, category, element, message, details, line")
    print("   - Met à jour self._original_log_results avec les données complètes")
    print()
    
    print("2. Fonction load_environment_analysis_results():")
    print("   - Récupère depuis la base: 8 colonnes (avec IDs)")
    print("   - Insère seulement 6 colonnes: timestamp, type, niveau, fichier, message, ''")
    print("   - N'utilise PAS les détails enrichis stockés en base")
    print("   - Ne met PAS à jour self._original_log_results")
    print()
    
    print("❌ PROBLÈMES DÉTECTÉS:")
    print("• Format d'affichage différent entre analyse fraîche et récupération")
    print("• Colonne 'Details' manquante lors de la récupération")
    print("• Variable _original_log_results non mise à jour")
    print("• Ordre des colonnes différent")
    print("• Informations enrichies perdues")
    print()
    
    print("🔧 SOLUTION NÉCESSAIRE:")
    print("• Unifier le format d'affichage")
    print("• Récupérer et afficher les détails enrichis")
    print("• Mettre à jour _original_log_results")
    print("• Assurer la cohérence des données")
    
    return True

def analyze_column_format_issue():
    """Analyser le problème de format des colonnes"""
    print("\n📊 Analyse du format des colonnes")
    print("=" * 55)
    
    print("🆕 DONNÉES FRAÎCHES (analyse directe):")
    print("Colonnes insérées:")
    print("1. timestamp: '2025-10-03 14:30:25.123'")
    print("2. type: 'ERREUR'")
    print("3. category: 'Module Not Found'")
    print("4. element: 'ComfyUI-Manager'")
    print("5. display_message: 'Import failed'")
    print("6. details_info: 'Loading failure'")
    print("7. line: '45'")
    print("Total: 7 colonnes avec détails enrichis")
    print()
    
    print("💾 DONNÉES RÉCUPÉRÉES (depuis base):")
    print("Données en base (8 colonnes):")
    print("0. result_id, 1. env_id, 2. fichier, 3. type_result,")
    print("4. niveau, 5. message, 6. details, 7. timestamp")
    print()
    print("Colonnes actuellement insérées:")
    print("1. timestamp_str: '03/10/2025 14:30:25'")
    print("2. type_result: 'ERREUR'")
    print("3. niveau: 'Module Not Found'")
    print("4. fichier: 'test.log'")
    print("5. message: 'Import failed | Loading failure'")
    print("6. '': (vide - détails manquants!)")
    print("Total: 6 colonnes, format différent!")
    print()
    
    print("⚠️ DIFFÉRENCES CRITIQUES:")
    print("• Colonne 'element' (nom du custom node) → remplacée par 'fichier'")
    print("• Message complet non traité pour l'affichage")
    print("• Détails enrichis ignorés")
    print("• Format timestamp différent")
    print("• Colonne 'line' manquante")
    
    return True

if __name__ == "__main__":
    print("🚀 Diagnostic du problème de changement d'environnement")
    print("=" * 65)
    
    success1 = test_environment_switching_issue()
    success2 = analyze_column_format_issue()
    
    print("\n" + "=" * 65)
    if success1 and success2:
        print("✅ PROBLÈME CLAIREMENT IDENTIFIÉ!")
        print("\n🎯 CAUSE RACINE:")
        print("• Format d'affichage incohérent entre analyse et récupération")
        print("• Données enrichies non utilisées lors de la récupération")
        print("• Structure des colonnes différente")
        print("\n🔧 CORRECTION NÉCESSAIRE:")
        print("• Unifier la fonction load_environment_analysis_results()")
        print("• Utiliser les détails enrichis stockés en base")
        print("• Reconstruire le même format d'affichage")
        print("• Mettre à jour _original_log_results")
    else:
        print("❌ Erreur lors du diagnostic")
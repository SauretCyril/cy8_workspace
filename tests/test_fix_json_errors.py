#!/usr/bin/env python3
"""
Script de migration et nettoyage des données legacy - Version directe
"""

import sys
import os
import json

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cy8_database_manager import cy8_database_manager

def fix_current_database():
    """Corriger la base de données actuelle"""
    print("🔧 Correction de la base de données actuelle")
    print("=" * 50)
    
    # Utiliser la base principale
    db_path = "G:\\tmp\\prompts_manager.db"
    print(f"📍 Base de données: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée")
        return False
    
    try:
        db_manager = cy8_database_manager(db_path)
        db_manager.init_database(mode="dev")
        
        # Récupérer tous les résultats d'analyse
        db_manager.cursor.execute("""
            SELECT id, environment_id, fichier, type, niveau, message, details, timestamp_analyse
            FROM resultats_analyses
            ORDER BY id
        """)
        
        results = db_manager.cursor.fetchall()
        print(f"📊 Total des résultats: {len(results)}")
        
        if len(results) == 0:
            print("ℹ️ Aucun résultat d'analyse dans cette base")
            return True
        
        # Analyser et corriger les détails
        fixed_count = 0
        error_count = 0
        
        for result in results:
            result_id, env_id, fichier, type_result, niveau, message, details, timestamp = result
            
            needs_fix = False
            
            # Vérifier si les détails sont problématiques
            if details is None or details == "" or details.strip() == "":
                needs_fix = True
            else:
                try:
                    json.loads(details)
                    # JSON valide, pas besoin de correction
                except json.JSONDecodeError:
                    needs_fix = True
            
            if needs_fix:
                # Construire des détails enrichis basiques
                enriched_details = {
                    "element": fichier if fichier else "Système",
                    "line": "N/A", 
                    "timestamp": timestamp,
                    "migrated": True,
                    "migration_date": "2025-10-04",
                    "original_details": details if details else ""
                }
                
                # Essayer d'extraire plus d'informations du message
                if message and " | " in message:
                    parts = message.split(" | ", 1)
                    if len(parts) > 1:
                        enriched_details["error_details"] = parts[1]
                
                # Rechercher des patterns dans le message
                if message:
                    import re
                    # Pattern pour les custom nodes
                    if "custom node" in message.lower():
                        match = re.search(r'custom node[:\s]*([^\s]+)', message, re.IGNORECASE)
                        if match:
                            enriched_details["element"] = match.group(1)
                    
                    # Pattern pour les numéros de ligne
                    line_match = re.search(r'line\s+(\d+)', message, re.IGNORECASE)
                    if line_match:
                        enriched_details["line"] = line_match.group(1)
                
                # Convertir en JSON
                new_details = json.dumps(enriched_details, ensure_ascii=False, indent=2)
                
                # Mettre à jour la base de données
                try:
                    db_manager.cursor.execute("""
                        UPDATE resultats_analyses 
                        SET details = ?
                        WHERE id = ?
                    """, (new_details, result_id))
                    
                    fixed_count += 1
                    print(f"✅ Résultat {result_id} corrigé")
                    
                except Exception as e:
                    error_count += 1
                    print(f"❌ Erreur correction résultat {result_id}: {e}")
        
        # Valider les changements
        db_manager.conn.commit()
        
        print(f"\n📋 RÉSUMÉ:")
        print(f"• Résultats traités: {len(results)}")
        print(f"• Résultats corrigés: {fixed_count}")
        print(f"• Erreurs: {error_count}")
        
        if fixed_count > 0:
            print(f"\n🎉 {fixed_count} résultats ont été migrés vers le nouveau format JSON !")
            print("✅ Les erreurs de parsing JSON devraient maintenant disparaître.")
        else:
            print("\n✅ Tous les résultats étaient déjà au bon format.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def test_corrected_data():
    """Tester les données corrigées"""
    print("\n🧪 Test des données corrigées")
    print("=" * 40)
    
    db_path = "G:\\tmp\\prompts_manager.db"
    
    try:
        db_manager = cy8_database_manager(db_path)
        db_manager.init_database(mode="dev")
        
        # Récupérer quelques résultats pour test
        db_manager.cursor.execute("""
            SELECT id, details
            FROM resultats_analyses
            LIMIT 5
        """)
        
        results = db_manager.cursor.fetchall()
        
        print(f"📋 Test sur {len(results)} résultats:")
        
        for result_id, details in results:
            if details:
                try:
                    parsed = json.loads(details)
                    print(f"✅ Résultat {result_id}: JSON valide")
                    print(f"   Element: {parsed.get('element', 'N/A')}")
                    print(f"   Line: {parsed.get('line', 'N/A')}")
                except json.JSONDecodeError as e:
                    print(f"❌ Résultat {result_id}: toujours invalide - {e}")
            else:
                print(f"⚠️ Résultat {result_id}: détails vides")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Correction rapide des erreurs JSON")
    print("=" * 50)
    
    success = fix_current_database()
    
    if success:
        test_corrected_data()
        
        print("\n" + "=" * 50)
        print("🎯 CORRECTION TERMINÉE")
        print("✅ Votre base de données a été mise à jour")
        print("✅ Les erreurs JSON ne devraient plus apparaître")
        print("✅ Vous pouvez maintenant changer d'environnement sans erreurs")
        print("\n💡 Conseil: Relancez l'application pour voir les améliorations")
    else:
        print("\n❌ La correction a échoué")
        print("💡 Vérifiez que l'application n'est pas ouverte en même temps")
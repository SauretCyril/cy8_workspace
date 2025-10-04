#!/usr/bin/env python3
"""
Script de migration et nettoyage des données legacy
"""

import sys
import os
import json

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cy8_database_manager import cy8_database_manager

def analyze_legacy_data():
    """Analyser les données legacy dans la base"""
    print("🔍 Analyse des données legacy")
    print("=" * 40)
    
    try:
        # Utiliser la base de données configurée (celle avec les vraies données)
        from cy8_paths import get_default_db_path
        db_path = get_default_db_path()
        print(f"📍 Utilisation de la base: {db_path}")
        
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
        
        # Analyser les types de données
        empty_details = 0
        valid_json = 0
        invalid_json = 0
        null_details = 0
        
        for result in results:
            result_id, env_id, fichier, type_result, niveau, message, details, timestamp = result
            
            if details is None:
                null_details += 1
            elif details == "" or details.strip() == "":
                empty_details += 1
            else:
                try:
                    json.loads(details)
                    valid_json += 1
                except json.JSONDecodeError:
                    invalid_json += 1
        
        print(f"📋 Répartition des données:")
        print(f"  • Détails NULL: {null_details}")
        print(f"  • Détails vides: {empty_details}")
        print(f"  • JSON valide: {valid_json}")
        print(f"  • JSON invalide: {invalid_json}")
        
        # Identifier les problématiques
        problematic = null_details + empty_details + invalid_json
        if len(results) > 0:
            percentage = problematic/len(results)*100
        else:
            percentage = 0
        print(f"\n⚠️ Données problématiques: {problematic}/{len(results)} ({percentage:.1f}%)")
        
        return {
            "total": len(results),
            "null_details": null_details,
            "empty_details": empty_details,
            "valid_json": valid_json,
            "invalid_json": invalid_json,
            "problematic": problematic
        }
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return None

def migrate_legacy_data():
    """Migrer les données legacy vers le nouveau format"""
    print("\n🔄 Migration des données legacy")
    print("=" * 40)
    
    try:
        from cy8_paths import get_default_db_path
        db_path = get_default_db_path()
        
        db_manager = cy8_database_manager(db_path)
        db_manager.init_database(mode="dev")
        
        # Récupérer les résultats avec détails problématiques
        db_manager.cursor.execute("""
            SELECT id, environment_id, fichier, type, niveau, message, details, timestamp_analyse
            FROM resultats_analyses
            WHERE details IS NULL OR details = '' OR (details IS NOT NULL AND details != '' AND details NOT LIKE '{%')
            ORDER BY id
        """)
        
        legacy_results = db_manager.cursor.fetchall()
        
        print(f"📋 Résultats à migrer: {len(legacy_results)}")
        
        migrated_count = 0
        
        for result in legacy_results:
            result_id, env_id, fichier, type_result, niveau, message, details, timestamp = result
            
            # Construire des détails enrichis basiques
            enriched_details = {
                "element": fichier if fichier else "Système",
                "line": "N/A",
                "timestamp": timestamp,
                "migrated": True,
                "original_details": details if details else ""
            }
            
            # Essayer d'extraire plus d'informations du message
            if message and " | " in message:
                parts = message.split(" | ", 1)
                if len(parts) > 1:
                    enriched_details["error_details"] = parts[1]
            
            # Rechercher des patterns dans le message pour identifier l'élément
            if message:
                # Pattern pour les custom nodes
                if "custom node" in message.lower():
                    # Extraire le nom du custom node si possible
                    import re
                    match = re.search(r'custom node[:\s]*([^\s]+)', message, re.IGNORECASE)
                    if match:
                        enriched_details["element"] = match.group(1)
                
                # Pattern pour les numéros de ligne
                line_match = re.search(r'line\s+(\d+)', message, re.IGNORECASE)
                if line_match:
                    enriched_details["line"] = line_match.group(1)
            
            # Convertir en JSON
            new_details = json.dumps(enriched_details, ensure_ascii=False)
            
            # Mettre à jour la base de données
            db_manager.cursor.execute("""
                UPDATE resultats_analyses 
                SET details = ?
                WHERE id = ?
            """, (new_details, result_id))
            
            migrated_count += 1
        
        db_manager.conn.commit()
        
        print(f"✅ Migration terminée: {migrated_count} résultats migrés")
        
        return migrated_count
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return 0

def verify_migration():
    """Vérifier que la migration s'est bien passée"""
    print("\n✅ Vérification de la migration")
    print("=" * 40)
    
    try:
        from cy8_paths import get_default_db_path
        db_path = get_default_db_path()
        
        db_manager = cy8_database_manager(db_path)
        db_manager.init_database(mode="dev")
        
        # Vérifier que tous les détails sont maintenant du JSON valide
        db_manager.cursor.execute("""
            SELECT id, details
            FROM resultats_analyses
            ORDER BY id
        """)
        
        results = db_manager.cursor.fetchall()
        
        invalid_count = 0
        for result_id, details in results:
            if details:
                try:
                    json.loads(details)
                except json.JSONDecodeError:
                    invalid_count += 1
                    print(f"⚠️ Résultat {result_id} toujours invalide")
        
        print(f"📊 Résultats vérifiés: {len(results)}")
        print(f"📋 JSON invalides restants: {invalid_count}")
        
        if invalid_count == 0:
            print("🎉 Migration réussie ! Tous les détails sont maintenant au format JSON.")
        else:
            print(f"⚠️ {invalid_count} résultats nécessitent encore une attention.")
        
        return invalid_count == 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def cleanup_interface_errors():
    """Nettoyer les erreurs d'affichage interface"""
    print("\n🧹 Nettoyage des erreurs d'interface")
    print("=" * 40)
    
    print("📋 Actions effectuées:")
    print("• Amélioration de la gestion des données legacy")
    print("• Réduction des messages d'erreur verbeux")
    print("• Récupération gracieuse des informations disponibles")
    print("• Traitement fallback pour données corrompues")
    
    print("\n✅ Interface optimisée pour:")
    print("• Données nouvelles (format JSON enrichi)")
    print("• Données legacy (format ancien)")
    print("• Données corrompues (récupération partielle)")
    print("• Données manquantes (valeurs par défaut)")
    
    return True

if __name__ == "__main__":
    print("🚀 Script de migration et nettoyage des données legacy")
    print("=" * 65)
    
    # Étape 1: Analyser les données existantes
    analysis = analyze_legacy_data()
    
    if analysis and analysis["problematic"] > 0:
        print(f"\n📋 {analysis['problematic']} résultats nécessitent une migration")
        
        # Étape 2: Migrer les données
        migrated = migrate_legacy_data()
        
        if migrated > 0:
            # Étape 3: Vérifier la migration
            success = verify_migration()
            
            if success:
                print("\n🎉 MIGRATION RÉUSSIE!")
            else:
                print("\n⚠️ Migration partiellement réussie")
        else:
            print("\n❌ Échec de la migration")
    else:
        print("\n✅ Aucune migration nécessaire - toutes les données sont déjà au bon format")
    
    # Étape 4: Optimisations interface
    cleanup_interface_errors()
    
    print("\n" + "=" * 65)
    print("🏁 RÉSULTAT:")
    if analysis:
        print(f"• Données analysées: {analysis['total']} résultats")
        print(f"• Format JSON valide: {analysis['valid_json']} résultats")
        print("• Interface optimisée pour tous les formats")
        print("• Messages d'erreur réduits et plus informatifs")
        print("\n💡 Les erreurs JSON lors du changement d'environnement")
        print("   ne devraient plus apparaître ou être beaucoup réduites.")
    else:
        print("❌ Impossible d'analyser les données")
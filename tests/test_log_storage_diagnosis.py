#!/usr/bin/env python3
"""
Test de diagnostic du stockage des résultats d'analyse en base de données
"""

import sys
import os
import tempfile

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_database_storage():
    """Test du stockage en base de données après analyse de log"""
    print("🔍 Diagnostic du stockage des résultats d'analyse")
    print("=" * 60)

    try:
        from cy8_database_manager import cy8_database_manager
        from cy8_log_analyzer import cy8_log_analyzer

        # Créer une base temporaire
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name

        print(f"📂 Base temporaire: {temp_db_path}")

        # Initialiser le gestionnaire de base
        db_manager = cy8_database_manager(temp_db_path)
        print("✅ Gestionnaire de base initialisé")

        # Utiliser un environnement par défaut (ils sont créés automatiquement)
        # Récupérer les environnements existants
        environments = db_manager.get_environments()
        if not environments:
            print("❌ Aucun environnement par défaut trouvé")
            return False

        env_id = environments[0][0]  # Premier environnement
        print(f"✅ Utilisation de l'environnement ID: {env_id}")

        # Créer un fichier log de test
        test_log_content = """2025-10-03 14:30:25.123 Import times for custom nodes:
2025-10-03 14:30:25.456 custom_nodes/ComfyUI-Manager: 1.2s
2025-10-03 14:30:26.789 custom_nodes/ComfyUI-AnimateDiff-Evolved: 2.5s
2025-10-03 14:30:27.012 ERROR: Failed to load custom_nodes/broken_node: ModuleNotFoundError: No module named 'missing_lib'
2025-10-03 14:30:27.345 WARNING: Deprecated function used in custom_nodes/old_node
2025-10-03 14:30:27.678 custom_nodes/failed_node (IMPORT FAILED): Permission denied
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as temp_log:
            temp_log.write(test_log_content)
            temp_log_path = temp_log.name

        print(f"📄 Log de test créé: {temp_log_path}")

        # Analyser le log
        analyzer = cy8_log_analyzer()
        result = analyzer.analyze_log_file(temp_log_path)

        if not result["success"]:
            print(f"❌ Échec de l'analyse: {result['error']}")
            return False

        entries = result["entries"]
        print(f"📊 {len(entries)} entrées analysées")

        # Afficher les entrées pour debug
        print("\n🔍 Entrées analysées:")
        for i, entry in enumerate(entries):
            print(f"  {i+1}. Type: {entry['type']}, Element: {entry['element']}, Message: {entry['message'][:50]}...")

        # Nettoyer les anciens résultats
        db_manager.clear_analysis_results(env_id)
        print("🧹 Anciens résultats nettoyés")

        # Stocker les résultats
        stored_count = 0
        errors_count = 0

        for entry in entries:
            try:
                # Construire les détails comme dans le code principal
                details_db = f"Element: {entry.get('element', '')}, Line: {entry.get('line', '')}, Timestamp: {entry.get('timestamp', '')}"

                success = db_manager.add_analysis_result(
                    environment_id=env_id,
                    fichier=os.path.basename(temp_log_path),
                    type_result=entry["type"],
                    niveau=entry["category"],
                    message=entry["message"],
                    details=details_db
                )

                if success:
                    stored_count += 1
                    print(f"  ✅ Stocké: {entry['type']} - {entry['element']}")
                else:
                    errors_count += 1
                    print(f"  ❌ Échec stockage: {entry['type']} - {entry['element']}")

            except Exception as e:
                errors_count += 1
                print(f"  ❌ Exception lors du stockage: {e}")

        print(f"\n📊 Résultat du stockage:")
        print(f"  • Stockés avec succès: {stored_count}/{len(entries)}")
        print(f"  • Erreurs: {errors_count}")

        # Vérifier la récupération
        print("\n🔍 Vérification de la récupération:")
        stored_results = db_manager.get_analysis_results(env_id)
        print(f"  • Résultats récupérés: {len(stored_results)}")

        if stored_results:
            print("  • Premiers résultats:")
            for result in stored_results[:3]:
                print(f"    - ID: {result[0]}, Type: {result[3]}, Message: {result[5][:30]}...")

        # Nettoyage
        os.unlink(temp_log_path)
        os.unlink(temp_db_path)

        # Résultat final
        success = stored_count == len(entries) and stored_count > 0
        if success:
            print(f"\n✅ Test réussi! {stored_count} résultats stockés et récupérés correctement")
        else:
            print(f"\n❌ Test échoué! Problème de stockage détecté")

        return success

    except Exception as e:
        print(f"❌ Erreur critique lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_current_storage_issue():
    """Test pour reproduire le problème de stockage actuel"""
    print("\n🔬 Test de reproduction du problème de stockage")
    print("=" * 60)

    try:
        # Simuler le processus exact de l'application
        print("📋 Simulation du processus d'analyse et stockage de l'application:")

        # Exemple d'entrée comme générée par le log analyzer amélioré
        sample_entry = {
            "type": "ERREUR",
            "category": "Module Not Found",
            "element": "ComfyUI-Manager",
            "message": "Import failed | Loading failure",
            "line": 45,
            "timestamp": "2025-10-03 14:30:25.123",
            "details": "Error in custom_nodes/ComfyUI-Manager/manager.py: ModuleNotFoundError"
        }

        print(f"🔍 Entrée d'exemple:")
        for key, value in sample_entry.items():
            print(f"  • {key}: {value}")

        # Simulation du traitement dans l'interface
        print("\n🔄 Traitement de l'interface:")

        # Extraction des détails pour l'affichage (comme dans le code actuel)
        details_info = ""
        if sample_entry["type"] == "ERREUR" and " | " in sample_entry["message"]:
            parts = sample_entry["message"].split(" | ", 1)
            if len(parts) > 1:
                details_info = parts[1]
                sample_entry["message"] = parts[0]  # Message principal

        print(f"  • Message principal: '{sample_entry['message']}'")
        print(f"  • Détails UI: '{details_info}'")

        # Construction des détails pour la base (format actuel)
        details_db = f"Element: {sample_entry.get('element', '')}, Line: {sample_entry.get('line', '')}, Timestamp: {sample_entry.get('timestamp', '')}"
        print(f"  • Détails DB: '{details_db}'")

        print("\n💡 Analyse du problème:")
        print("  • Le message est modifié pour l'affichage (séparation du ' | ')")
        print("  • Les détails riches sont perdus et remplacés par un format générique")
        print("  • Les informations contextuelles (CUDA, Memory, etc.) ne sont pas stockées")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de la simulation: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Diagnostic du stockage des résultats d'analyse")
    print("=" * 70)

    success1 = test_database_storage()
    success2 = test_current_storage_issue()

    print("\n" + "=" * 70)
    if success1 and success2:
        print("✅ DIAGNOSTIC TERMINÉ")
        print("\n🔧 PROBLÈMES IDENTIFIÉS:")
        print("1. Modification destructive du message pour l'affichage")
        print("2. Perte des informations contextuelles lors du stockage")
        print("3. Format des détails DB trop générique")
        print("\n💡 SOLUTIONS À IMPLÉMENTER:")
        print("• Stocker le message original ET les détails séparément")
        print("• Préserver les informations contextuelles dans les détails DB")
        print("• Améliorer le format des détails stockés")
    else:
        print("❌ Erreurs détectées lors du diagnostic")

#!/usr/bin/env python3
"""
Test simplifié pour identifier le problème de stockage des logs
"""

import sys
import os
import tempfile

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_actual_storage_process():
    """Test du processus de stockage réel comme dans l'application"""
    print("🔧 Test du processus de stockage actuel")
    print("=" * 50)

    try:
        from cy8_database_manager import cy8_database_manager

        # Créer une base temporaire
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name

        print(f"📂 Base temporaire: {temp_db_path}")

        # Initialiser le gestionnaire de base
        db_manager = cy8_database_manager(temp_db_path)
        print("✅ Database manager initialisé")

        # Utiliser un environnement par défaut
        env_id = "test_env_001"  # ID simple pour test

        # Simuler les entrées comme générées par l'analyseur amélioré
        test_entries = [
            {
                "type": "OK",
                "category": "Custom Node",
                "element": "ComfyUI-Manager",
                "message": "Chargé avec succès (1.2s)",
                "line": 10,
                "timestamp": "2025-10-03 14:30:25.123",
                "details": "custom_nodes/ComfyUI-Manager: 1.2s"
            },
            {
                "type": "ERREUR",
                "category": "Module Not Found",
                "element": "ComfyUI-VideoHelper",
                "message": "Import failed | Loading failure",
                "line": 45,
                "timestamp": "2025-10-03 14:30:26.456",
                "details": "Error in custom_nodes/ComfyUI-VideoHelper/video.py: ModuleNotFoundError"
            },
            {
                "type": "ATTENTION",
                "category": "Warning",
                "element": "Système",
                "message": "CUDA memory warning | Memory issue",
                "line": 78,
                "timestamp": "2025-10-03 14:30:27.789",
                "details": "CUDA out of memory warning detected"
            }
        ]

        print(f"🧪 Test avec {len(test_entries)} entrées")

        # Nettoyer d'abord
        db_manager.clear_analysis_results(env_id)
        print("🧹 Anciens résultats nettoyés")

        # Tester le stockage avec le code actuel de l'application
        stored_count = 0
        for entry in test_entries:
            print(f"\n📝 Traitement: {entry['type']} - {entry['element']}")

            # === SIMULATION DU CODE ACTUEL DE L'APPLICATION ===
            # Déterminer la couleur selon le type
            tag = entry["type"]

            # Stocker le résultat dans la base de données (CODE ACTUEL)
            try:
                success = db_manager.add_analysis_result(
                    environment_id=env_id,
                    fichier="test.log",  # Nom du fichier log
                    type_result=entry["type"],
                    niveau=entry["category"],
                    message=entry["message"],
                    details=f"Element: {entry.get('element', '')}, Line: {entry.get('line', '')}, Timestamp: {entry.get('timestamp', '')}"
                )
                if success:
                    stored_count += 1
                    print(f"  ✅ Stocké en DB")
                else:
                    print(f"  ❌ Échec stockage")
            except Exception as e:
                print(f"  ❌ Exception: {e}")

            # Traitement pour l'affichage (CODE ACTUEL MODIFIÉ)
            details_info = ""
            original_message = entry["message"]

            if entry["type"] == "OK" and "(" in entry["message"]:
                # Pour les custom nodes OK, extraire le temps
                import re
                time_match = re.search(r'\(([^)]+)\)', entry["message"])
                if time_match:
                    details_info = time_match.group(1)
            elif entry["type"] == "ERREUR" and " | " in entry["message"]:
                # Pour les erreurs, extraire les détails après le |
                parts = entry["message"].split(" | ", 1)
                if len(parts) > 1:
                    details_info = parts[1]
                    entry["message"] = parts[0]  # Garder seulement le message principal

            print(f"  📋 Message original: '{original_message}'")
            print(f"  📋 Message affiché: '{entry['message']}'")
            print(f"  📋 Détails UI: '{details_info}'")

        # Vérifier ce qui a été stocké
        print(f"\n📊 Résultat: {stored_count}/{len(test_entries)} entrées stockées")

        # Récupérer et afficher ce qui est en base
        stored_results = db_manager.get_analysis_results(env_id)
        print(f"\n🔍 Vérification en base: {len(stored_results)} résultats trouvés")

        for result in stored_results:
            print(f"  • Type: {result[3]}, Message: '{result[5]}', Détails: '{result[6]}'")

        # Nettoyage
        os.unlink(temp_db_path)

        print(f"\n💡 ANALYSE DU PROBLÈME:")
        if stored_count == len(test_entries):
            print("✅ Le stockage fonctionne techniquement")
            print("❓ Mais les détails stockés sont génériques...")

            print("\n🔍 PROBLÈMES IDENTIFIÉS:")
            print("1. Les détails riches (CUDA, Loading failure, etc.) sont perdus")
            print("2. Format des détails DB trop simple: 'Element: X, Line: Y, Timestamp: Z'")
            print("3. Les informations contextuelles ne sont pas préservées")
            print("4. Le message original complet n'est pas conservé")

            return True
        else:
            print("❌ Le stockage ne fonctionne pas correctement")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Diagnostic du problème de stockage des logs")
    print("=" * 60)

    success = test_actual_storage_process()

    print("\n" + "=" * 60)
    if success:
        print("✅ DIAGNOSTIC TERMINÉ - Problème identifié")
        print("\n🔧 SOLUTION À IMPLÉMENTER:")
        print("• Améliorer le format des détails stockés en base")
        print("• Préserver les informations contextuelles riches")
        print("• Stocker le message original ET le message traité")
        print("• Inclure les détails spécifiques (CUDA, Memory, Loading, etc.)")
    else:
        print("❌ Stockage défaillant - problème plus grave")

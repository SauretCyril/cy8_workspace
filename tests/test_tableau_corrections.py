#!/usr/bin/env python3
"""
Test de validation des corrections pour le tableau des résultats
"""

import sys
import os
import sqlite3
import json

def test_tableau_corrections():
    """Test des corrections du tableau des résultats d'analyse"""

    print("🔍 TEST CORRECTIONS TABLEAU RÉSULTATS")
    print("=" * 60)

    db_path = "G:\\tmp\\prompts_manager.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Récupérer les résultats d'analyse comme le ferait load_environment_analysis_results
        cursor.execute("""
            SELECT id, environment_id, fichier, type, niveau, message, details, timestamp_analyse
            FROM resultats_analyses
            WHERE environment_id = 'G11_05'
            ORDER BY timestamp_analyse DESC
            LIMIT 20
        """)

        results = cursor.fetchall()

        print(f"📊 Résultats récupérés: {len(results)} pour G11_05")
        print("")

        # Simuler le traitement de load_environment_analysis_results
        processed_results = []

        for result in results:
            (
                result_id,
                env_id,
                fichier,
                type_result,
                niveau,
                message,
                details,
                timestamp,
            ) = result

            print(f"🔍 **RÉSULTAT {result_id}:**")
            print(f"   📁 Fichier: {fichier}")
            print(f"   📂 Type: {type_result}")
            print(f"   📋 Niveau: {niveau}")
            print(f"   📝 Message: {message[:100]}...")
            print(f"   🔧 Détails: {details[:100] if details else 'None'}...")

            # Traitement comme dans le code corrigé
            display_message = message
            details_info = ""
            element_name = fichier  # Par défaut
            line_number = "N/A"

            # Extraire depuis les détails JSON
            if details and details.strip():
                try:
                    details_dict = json.loads(details)

                    if "element" in details_dict and details_dict["element"]:
                        element_name = details_dict["element"]
                        print(f"   🔌 Element depuis JSON: {element_name}")

                except json.JSONDecodeError:
                    # CORRECTION: Traiter le format legacy avec extraction d'Element
                    # Format: "Element: nom | Line: X | Timestamp: Y | ..."
                    if "Element:" in details:
                        import re
                        element_match = re.search(r'Element:\s*([^|]+)', details)
                        if element_match:
                            element_name = element_match.group(1).strip()
                            print(f"   🔌 Element depuis détails legacy: {element_name}")

                    if "Line:" in details:
                        import re
                        line_match = re.search(r'Line:\s*(\d+)', details)
                        if line_match:
                            line_number = line_match.group(1).strip()

                    print(f"   ⚠️ Format legacy traité - Element: {element_name}")

            print(f"   ✅ **ELEMENT FINAL: {element_name}**")

            processed_results.append({
                'id': result_id,
                'type': type_result,
                'niveau': niveau,
                'element_final': element_name,
                'message': message[:100],
                'fichier': fichier
            })
            print("")

        # Résumé des corrections
        print(f"📈 **RÉSUMÉ DES CORRECTIONS:**")

        comfyui_log_count = len([r for r in processed_results if r['element_final'] == 'comfyui.log'])
        custom_nodes_count = len([r for r in processed_results if r['element_final'] != 'comfyui.log'])

        print(f"• Total résultats: {len(processed_results)}")
        print(f"• Éléments = 'comfyui.log' (problématique): {comfyui_log_count}")
        print(f"• Éléments = custom nodes (correct): {custom_nodes_count}")

        print(f"\n🔌 **CUSTOM NODES IDENTIFIÉS:**")
        unique_elements = set([r['element_final'] for r in processed_results if r['element_final'] != 'comfyui.log'])
        for element in sorted(unique_elements):
            count = len([r for r in processed_results if r['element_final'] == element])
            print(f"• {element}: {count} occurrence(s)")

        # Vérification des améliorations
        print(f"\n🎯 **VALIDATION:**")
        if comfyui_log_count == 0:
            print("✅ SUCCÈS: Aucun élément 'comfyui.log' dans la colonne Custom Node/Élément")
        else:
            print(f"❌ PROBLÈME: {comfyui_log_count} éléments montrent encore 'comfyui.log'")

        if custom_nodes_count > 0:
            print(f"✅ SUCCÈS: {custom_nodes_count} custom nodes correctement identifiés")
        else:
            print("❌ PROBLÈME: Aucun custom node identifié")

        conn.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_tableau_corrections()

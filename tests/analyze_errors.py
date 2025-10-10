#!/usr/bin/env python3
"""
Recherche spécifique des erreurs dans G11_05
"""

import sys
import os
import sqlite3
import re

def analyze_errors():
    """Analyse spécifique des erreurs G11_05"""

    print("🔍 ANALYSE DES ERREURS G11_05")
    print("=" * 50)

    db_path = "G:\\tmp\\prompts_manager.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Chercher toutes les analyses qui ne sont PAS OK
        cursor.execute("""
            SELECT id, fichier, type, niveau, message, details
            FROM resultats_analyses
            WHERE environment_id = 'G11_05'
            AND (type != 'OK' OR message LIKE '%error%' OR message LIKE '%fail%'
                 OR message LIKE '%exception%' OR message LIKE '%traceback%')
            ORDER BY timestamp_analyse DESC
        """)

        errors = cursor.fetchall()
        print(f"📊 Erreurs trouvées: {len(errors)}")

        if not errors:
            print("ℹ️  Aucune erreur explicite. Cherchons les messages avec 'warning' ou problèmes...")

            cursor.execute("""
                SELECT id, fichier, type, niveau, message, details
                FROM resultats_analyses
                WHERE environment_id = 'G11_05'
                AND (message LIKE '%warning%' OR message LIKE '%problem%'
                     OR message LIKE '%issue%' OR message LIKE '%not found%'
                     OR message LIKE '%missing%')
                ORDER BY timestamp_analyse DESC
                LIMIT 10
            """)

            warnings = cursor.fetchall()
            print(f"⚠️  Avertissements/problèmes: {len(warnings)}")

            for warning in warnings:
                print(f"\n🟡 ID {warning[0]} - {warning[2]} ({warning[3]})")
                print(f"   📁 {warning[1]}")
                print(f"   📝 {warning[4][:200]}...")

        else:
            print(f"\n🔴 **ERREURS DÉTECTÉES:**")
            for error in errors:
                print(f"\n❌ ID {error[0]} - {error[2]} ({error[3]})")
                print(f"   📁 {error[1]}")
                print(f"   📝 {error[4]}")
                if error[5]:
                    print(f"   🔍 Détails: {error[5][:300]}...")

                # Essayer d'extraire des noms de custom nodes
                message = error[4]
                custom_node_patterns = [
                    r'custom_nodes[/\\]([^/\\]+)',
                    r'ComfyUI[/\\]custom_nodes[/\\]([^/\\]+)',
                    r'from\s+([a-zA-Z_][a-zA-Z0-9_-]*)\s+import',
                    r'module\s+[\'"]([^\'"/]+)[\'"]',
                    r'([a-zA-Z_][a-zA-Z0-9_-]*[-_]node)',
                    r'([a-zA-Z_][a-zA-Z0-9_-]*[-_]suite)',
                ]

                found_nodes = []
                for pattern in custom_node_patterns:
                    matches = re.finditer(pattern, message, re.IGNORECASE)
                    for match in matches:
                        node_name = match.group(1)
                        if len(node_name) > 2 and node_name not in found_nodes:
                            found_nodes.append(node_name)

                if found_nodes:
                    print(f"   🔌 Custom nodes détectés: {found_nodes}")

        # Statistiques générales
        cursor.execute("""
            SELECT type, COUNT(*)
            FROM resultats_analyses
            WHERE environment_id = 'G11_05'
            GROUP BY type
            ORDER BY COUNT(*) DESC
        """)

        stats = cursor.fetchall()
        print(f"\n📈 **STATISTIQUES PAR TYPE:**")
        for stat in stats:
            print(f"• {stat[0]}: {stat[1]} occurrence(s)")

        conn.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    analyze_errors()

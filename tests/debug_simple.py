#!/usr/bin/env python3
"""
Debug simple des données d'analyse sans charger l'application
"""

import sys
import os
import sqlite3

def debug_simple():
    """Debug simple direct avec SQLite"""

    print("🔍 DEBUG SIMPLE - ANALYSES G11_05")
    print("=" * 50)

    db_path = "G:\\tmp\\prompts_manager.db"
    print(f"📁 Base: {db_path}")

    if not os.path.exists(db_path):
        print("❌ Base non trouvée")
        return

    try:
        # Connexion directe SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Vérifier la structure de la table
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='resultats_analyses'")
        table_def = cursor.fetchone()
        if table_def:
            print(f"📋 Table structure: {table_def[0]}")

        # Récupérer les analyses pour G11_05
        cursor.execute("""
            SELECT id, environment_id, fichier, type, niveau, message, details, timestamp_analyse
            FROM resultats_analyses
            WHERE environment_id = 'G11_05'
            ORDER BY timestamp_analyse DESC
            LIMIT 20
        """)

        analyses = cursor.fetchall()
        print(f"\n📊 Analyses trouvées: {len(analyses)}")

        if not analyses:
            # Vérifier tous les environnements
            cursor.execute("SELECT DISTINCT environment_id FROM resultats_analyses")
            envs = cursor.fetchall()
            print(f"🆔 Environnements: {[e[0] for e in envs]}")
            return

        # Analyser quelques exemples
        print(f"\n📋 Exemples d'analyses:")
        for i, analysis in enumerate(analyses[:5]):
            print(f"\n{i+1}. ID: {analysis[0]}")
            print(f"   Type: {analysis[3]}")
            print(f"   Niveau: {analysis[4]}")
            print(f"   Message: {analysis[5][:150]}...")

        # Compter les erreurs
        error_count = 0
        custom_node_messages = []

        for analysis in analyses:
            message = analysis[5].lower()
            if 'error' in analysis[3].lower() or 'failed' in message:
                error_count += 1

            if 'custom' in message and 'node' in message:
                custom_node_messages.append(analysis[5])

        print(f"\n📊 **RÉSUMÉ:**")
        print(f"• Total analyses: {len(analyses)}")
        print(f"• Erreurs: {error_count}")
        print(f"• Custom nodes mentionnés: {len(custom_node_messages)}")

        if custom_node_messages:
            print(f"\n🔌 **MESSAGES CUSTOM NODES:**")
            for i, msg in enumerate(custom_node_messages[:3]):
                print(f"{i+1}. {msg[:200]}...")

        conn.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    debug_simple()

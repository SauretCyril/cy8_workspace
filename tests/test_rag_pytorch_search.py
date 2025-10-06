#!/usr/bin/env python3
"""
Test de recherche RAG pour PyTorch/CUDA
"""

import sys
import os
import sqlite3

def test_rag_search():
    """Test de recherche RAG pour les informations PyTorch/CUDA"""

    print("🔍 TEST RECHERCHE RAG - PYTORCH/CUDA")
    print("=" * 60)

    db_path = "G:\\tmp\\prompts_manager.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Rechercher spécifiquement les entrées PyTorch/CUDA
        cursor.execute("""
            SELECT id, environment_id, fichier, type, niveau, message, details
            FROM resultats_analyses
            WHERE environment_id = 'G11_05'
            AND (message LIKE '%pytorch%' OR message LIKE '%cuda%' OR message LIKE '%VRAM%' OR message LIKE '%torch%')
            ORDER BY timestamp_analyse DESC
        """)

        pytorch_results = cursor.fetchall()

        print(f"📊 Résultats PyTorch/CUDA trouvés: {len(pytorch_results)}")

        for result in pytorch_results:
            result_id, env_id, fichier, type_result, niveau, message, details = result
            print(f"\n🔍 **RÉSULTAT {result_id}:**")
            print(f"   📂 Type: {type_result}")
            print(f"   📋 Niveau: {niveau}")
            print(f"   📝 Message: {message}")
            print(f"   🔧 Détails: {details[:100] if details else 'None'}...")

        # Test des mots-clés de recherche
        test_queries = [
            "pytorch version",
            "cuda",
            "torch",
            "version pytorch",
            "pytorch",
            "VRAM",
            "gpu",
            "graphic",
            "modules pytorch cuda"
        ]

        print(f"\n🔍 **TEST RECHERCHE DANS MESSAGES:**")
        for query in test_queries:
            matches = []
            for result in pytorch_results:
                message = result[5].lower()
                if query.lower() in message:
                    matches.append(result[0])  # ID

            print(f"• '{query}': {len(matches)} correspondance(s) - IDs: {matches}")

        # Vérifier aussi si c'est dans le RAG
        print(f"\n📚 **INFORMATIONS POUR LE RAG:**")
        print("Les données suivantes devraient être indexées dans ChromaDB:")

        for result in pytorch_results:
            result_id, env_id, fichier, type_result, niveau, message, details = result

            # Simuler ce qui est envoyé au RAG
            rag_content = f"Type: {type_result} | Niveau: {niveau} | Message: {message}"
            if details:
                rag_content += f" | Détails: {details}"

            print(f"• ID {result_id}: {rag_content[:150]}...")

        conn.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_rag_search()

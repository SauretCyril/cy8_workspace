#!/usr/bin/env python3
"""
Examen direct de la base ChromaDB
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def examine_chromadb_direct():
    """Examiner directement la base ChromaDB"""
    print("🔍 Examen direct de ChromaDB")
    print("=" * 50)

    try:
        import chromadb
        from chromadb.config import Settings

        # Chemin vers la base vectorielle
        vector_db_path = "g:/G_WCS/cy8_workspace/data/analyses/vector_db"

        print(f"📁 Chemin base vectorielle: {vector_db_path}")

        if not os.path.exists(vector_db_path):
            print("❌ Répertoire vector_db non trouvé")
            return

        # Initialiser ChromaDB
        client = chromadb.PersistentClient(path=vector_db_path)

        # Lister les collections
        collections = client.list_collections()
        print(f"📊 Collections trouvées: {len(collections)}")

        for collection in collections:
            print(f"\n📋 Collection: {collection.name}")

            try:
                # Obtenir le nombre de documents
                count = collection.count()
                print(f"   📄 Documents: {count}")

                if count > 0:
                    # Récupérer quelques exemples
                    results = collection.get(
                        limit=3,
                        include=["metadatas", "documents", "ids"]
                    )

                    for i, (doc_id, doc, metadata) in enumerate(zip(
                        results['ids'],
                        results['documents'],
                        results['metadatas']
                    )):
                        print(f"\n   📄 Document {i+1}:")
                        print(f"      ID: {doc_id}")
                        print(f"      Timestamp: {metadata.get('timestamp', 'N/A')}")
                        print(f"      Type: {metadata.get('analysis_type', 'N/A')}")
                        print(f"      Environnement: {metadata.get('environment_id', 'N/A')}")
                        print(f"      Erreurs: {metadata.get('error_count', 0)}")
                        print(f"      Contenu (150 chars): {doc[:150]}...")

            except Exception as e:
                print(f"   ❌ Erreur lecture collection: {e}")

        if not collections:
            print("📭 Aucune collection trouvée - aucune analyse indexée")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def check_analysis_files():
    """Vérifier les fichiers d'analyses disponibles"""
    print("\n📁 Vérification des fichiers d'analyses")
    print("=" * 50)

    analyses_paths = [
        "g:/G_WCS/cy8_workspace/data/analyses",
        "g:/tmp/analyses",  # Possible autre emplacement
    ]

    for analyses_dir in analyses_paths:
        if os.path.exists(analyses_dir):
            print(f"\n📍 Répertoire: {analyses_dir}")

            # Parcourir récursivement
            analysis_files = []
            for root, dirs, files in os.walk(analyses_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in ['.json', '.txt', '.md']):
                        if any(keyword in file.lower() for keyword in ['analysis', 'analyse', 'log']):
                            filepath = os.path.join(root, file)
                            size = os.path.getsize(filepath)
                            analysis_files.append((filepath, size))

            print(f"   📄 Fichiers d'analyses: {len(analysis_files)}")
            for filepath, size in analysis_files[:5]:  # Premiers 5
                rel_path = os.path.relpath(filepath, analyses_dir)
                print(f"      - {rel_path} ({size} bytes)")

            if len(analysis_files) > 5:
                print(f"      ... et {len(analysis_files) - 5} autres")
        else:
            print(f"❌ Répertoire non trouvé: {analyses_dir}")

if __name__ == "__main__":
    examine_chromadb_direct()
    check_analysis_files()

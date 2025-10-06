#!/usr/bin/env python3
"""
Utilitaire pour examiner et gérer l'indexation RAG des analyses
"""

import sys
import os
import json
from datetime import datetime

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def examine_rag_index():
    """Examiner le contenu de l'index RAG"""
    print("🔍 Examen de l'index RAG")
    print("=" * 60)

    try:
        from cy8_rag_manager import RAGManager
        from cy8_database_manager import cy8_database_manager

        # Initialiser le système
        db_path = "G:/tmp/prompts_manager.db"  # Base principale
        db_manager = cy8_database_manager(db_path)

        # Utiliser l'environnement par défaut ou le dernier utilisé
        current_env = "G11_05"  # À ajuster selon votre environnement

        print(f"📍 Environnement: {current_env}")
        print(f"📁 Base de données: {db_path}")

        # Initialiser le RAG
        rag_manager = RAGManager(db_manager, current_env)

        if not rag_manager.is_available():
            print("❌ RAG non disponible")
            return

        print("✅ RAG initialisé avec succès")

        # Examiner la collection ChromaDB
        if rag_manager.collection:
            try:
                # Obtenir les statistiques de la collection
                count = rag_manager.collection.count()
                print(f"📊 Documents indexés: {count}")

                if count > 0:
                    # Récupérer quelques documents pour examen
                    results = rag_manager.collection.get(
                        limit=5,
                        include=["metadatas", "documents"]
                    )

                    print(f"\n📋 Échantillon des documents indexés:")
                    for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                        print(f"\n  📄 Document {i+1}:")
                        print(f"     Timestamp: {metadata.get('timestamp', 'N/A')}")
                        print(f"     Type: {metadata.get('analysis_type', 'N/A')}")
                        print(f"     Erreurs: {metadata.get('error_count', 0)}")
                        print(f"     Contenu (100 chars): {doc[:100]}...")

                else:
                    print("📭 Aucun document indexé")

            except Exception as e:
                print(f"❌ Erreur examen collection: {e}")

        # Examiner le répertoire d'analyses
        analyses_dir = db_manager.get_environment_analyses_directory(current_env)
        if analyses_dir and os.path.exists(analyses_dir):
            print(f"\n📁 Répertoire d'analyses: {analyses_dir}")

            # Lister les fichiers d'analyses
            analysis_files = []
            for root, dirs, files in os.walk(analyses_dir):
                for file in files:
                    if file.endswith(('.json', '.txt', '.md')):
                        filepath = os.path.join(root, file)
                        analysis_files.append(filepath)

            print(f"📄 Fichiers d'analyses trouvés: {len(analysis_files)}")
            for i, filepath in enumerate(analysis_files[:5]):  # Afficher les 5 premiers
                rel_path = os.path.relpath(filepath, analyses_dir)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"   {i+1}. {rel_path} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")

            if len(analysis_files) > 5:
                print(f"   ... et {len(analysis_files) - 5} autres")
        else:
            print(f"❌ Répertoire d'analyses non trouvé: {analyses_dir}")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def index_existing_analyses():
    """Indexer les analyses existantes non encore indexées"""
    print("\n🔄 Indexation des analyses existantes")
    print("=" * 60)

    try:
        from cy8_rag_manager import RAGManager
        from cy8_database_manager import cy8_database_manager

        # Initialiser le système
        db_path = "G:/tmp/prompts_manager.db"
        db_manager = cy8_database_manager(db_path)
        current_env = "G11_05"

        rag_manager = RAGManager(db_manager, current_env)

        if not rag_manager.is_available():
            print("❌ RAG non disponible pour l'indexation")
            return

        # Obtenir le répertoire d'analyses
        analyses_dir = db_manager.get_environment_analyses_directory(current_env)
        if not analyses_dir or not os.path.exists(analyses_dir):
            print(f"❌ Répertoire d'analyses non accessible: {analyses_dir}")
            return

        # Chercher les fichiers d'analyses
        analysis_files = []
        for root, dirs, files in os.walk(analyses_dir):
            for file in files:
                if file.endswith('.json') and 'analysis_' in file:
                    filepath = os.path.join(root, file)
                    analysis_files.append(filepath)

        print(f"📄 Fichiers d'analyses trouvés: {len(analysis_files)}")

        indexed_count = 0
        for filepath in analysis_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Créer une structure d'analyse simple
                analysis_data = {
                    "timestamp": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                    "type": "stored_analysis",
                    "filename": os.path.basename(filepath),
                    "full_analysis": content,
                    "environment_id": current_env,
                    "filepath": filepath
                }

                # Indexer
                success = rag_manager.index_analysis_result(analysis_data)
                if success:
                    indexed_count += 1
                    print(f"✅ Indexé: {os.path.basename(filepath)}")
                else:
                    print(f"❌ Échec: {os.path.basename(filepath)}")

            except Exception as e:
                print(f"❌ Erreur fichier {filepath}: {e}")

        print(f"\n🎉 Indexation terminée: {indexed_count}/{len(analysis_files)} fichiers indexés")

    except Exception as e:
        print(f"❌ Erreur indexation: {e}")

def main():
    """Fonction principale"""
    print("🧠 Utilitaire de gestion de l'index RAG")
    print("=" * 60)

    examine_rag_index()

    print("\n" + "="*60)

    # Proposer l'indexation si peu de documents
    response = input("\n❓ Voulez-vous indexer les analyses existantes ? (o/N): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        index_existing_analyses()

    print("\n" + "="*60)
    print("✅ Examen terminé")

if __name__ == "__main__":
    main()

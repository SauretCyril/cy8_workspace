#!/usr/bin/env python3
"""
Extension RAG avec gestion temporelle pour les analyses horodatées
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TemporalRAGManager:
    """Extension du RAG Manager avec gestion temporelle"""

    def __init__(self, rag_manager):
        self.rag_manager = rag_manager

    def search_with_temporal_priority(self, query: str, limit: int = 5,
                                    recent_weight: float = 1.5,
                                    max_age_days: Optional[int] = None) -> List[Dict]:
        """
        Recherche avec priorité temporelle

        Args:
            query: Requête de recherche
            limit: Nombre de résultats
            recent_weight: Coefficient de pondération pour les documents récents
            max_age_days: Âge maximum en jours (None = pas de limite)
        """
        try:
            if not self.rag_manager.collection or not self.rag_manager.embeddings_model:
                return []

            # Générer l'embedding de la requête
            query_embedding = self.rag_manager.embeddings_model.encode(query)

            # Rechercher plus de résultats pour filtrer ensuite
            search_limit = limit * 3  # Chercher plus pour pouvoir filtrer

            results = self.rag_manager.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=search_limit,
                include=["documents", "metadatas", "distances"]
            )

            if not results["documents"] or not results["documents"][0]:
                return []

            # Traiter et pondérer les résultats
            weighted_results = []
            now = datetime.now()

            for i in range(len(results["documents"][0])):
                metadata = results["metadatas"][0][i]
                document = results["documents"][0][i]
                distance = results["distances"][0][i]

                # Calculer l'âge du document
                timestamp_str = metadata.get('timestamp', '')
                doc_age_days = None

                if timestamp_str:
                    try:
                        # Gérer différents formats de timestamp
                        if isinstance(timestamp_str, (int, float)):
                            doc_date = datetime.fromtimestamp(timestamp_str)
                        else:
                            # Timestamp ISO string
                            doc_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                        doc_age_days = (now - doc_date).days

                    except Exception as e:
                        print(f"⚠️ Erreur parsing timestamp {timestamp_str}: {e}")

                # Filtrer par âge si spécifié
                if max_age_days is not None and doc_age_days is not None:
                    if doc_age_days > max_age_days:
                        continue  # Ignorer les documents trop anciens

                # Calculer le score avec pondération temporelle
                base_similarity = 1 - distance

                if doc_age_days is not None:
                    # Appliquer une pondération décroissante avec l'âge
                    age_factor = max(0.1, 1 / (1 + doc_age_days / 7))  # Décroissance sur 7 jours
                    temporal_bonus = recent_weight if doc_age_days <= 1 else 1.0
                    final_score = base_similarity * age_factor * temporal_bonus
                else:
                    # Pas de timestamp - score de base seulement
                    final_score = base_similarity * 0.5  # Pénaliser les docs sans timestamp

                weighted_results.append({
                    "content": document,
                    "metadata": metadata,
                    "similarity": base_similarity,
                    "temporal_score": final_score,
                    "age_days": doc_age_days,
                    "timestamp": timestamp_str
                })

            # Trier par score temporel décroissant
            weighted_results.sort(key=lambda x: x["temporal_score"], reverse=True)

            # Retourner les meilleurs résultats
            return weighted_results[:limit]

        except Exception as e:
            print(f"❌ Erreur recherche temporelle: {e}")
            return []

    def search_recent_only(self, query: str, max_age_hours: int = 24, limit: int = 5) -> List[Dict]:
        """Rechercher uniquement dans les analyses récentes"""
        return self.search_with_temporal_priority(
            query=query,
            limit=limit,
            recent_weight=2.0,
            max_age_days=max_age_hours // 24 if max_age_hours >= 24 else 1
        )

    def get_temporal_distribution(self) -> Dict:
        """Analyser la distribution temporelle des documents indexés"""
        try:
            if not self.rag_manager.collection:
                return {}

            results = self.rag_manager.collection.get(
                limit=1000,  # Analyser jusqu'à 1000 documents
                include=["metadatas"]
            )

            if not results or not results.get('metadatas'):
                return {}

            # Analyser les timestamps
            timestamps = []
            now = datetime.now()

            for metadata in results['metadatas']:
                timestamp_str = metadata.get('timestamp', '')
                if timestamp_str:
                    try:
                        if isinstance(timestamp_str, (int, float)):
                            doc_date = datetime.fromtimestamp(timestamp_str)
                        else:
                            doc_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        timestamps.append(doc_date)
                    except:
                        pass

            if not timestamps:
                return {"error": "Aucun timestamp valide trouvé"}

            # Calculer la distribution
            timestamps.sort()
            oldest = timestamps[0]
            newest = timestamps[-1]

            # Compter par périodes
            recent_24h = sum(1 for ts in timestamps if (now - ts).total_seconds() < 86400)
            recent_week = sum(1 for ts in timestamps if (now - ts).days <= 7)
            recent_month = sum(1 for ts in timestamps if (now - ts).days <= 30)

            return {
                "total_documents": len(results['metadatas']),
                "documents_with_timestamp": len(timestamps),
                "oldest_document": oldest.isoformat(),
                "newest_document": newest.isoformat(),
                "age_span_days": (newest - oldest).days,
                "recent_24h": recent_24h,
                "recent_week": recent_week,
                "recent_month": recent_month,
                "percentage_recent_24h": round(recent_24h / len(timestamps) * 100, 1),
                "percentage_recent_week": round(recent_week / len(timestamps) * 100, 1)
            }

        except Exception as e:
            return {"error": f"Erreur analyse temporelle: {e}"}

def test_temporal_rag():
    """Tester le RAG temporel"""
    print("🕒 TEST RAG TEMPOREL AMÉLIORÉ")
    print("=" * 50)

    try:
        from cy8_rag_manager import RAGManager
        from cy8_database_manager import cy8_database_manager

        # Initialiser le système
        db_path = "G:/tmp/prompts_manager.db"
        db_manager = cy8_database_manager(db_path)
        rag_manager = RAGManager(db_manager, "TEST_TEMPORAL")

        if not rag_manager.is_available():
            print("⚠️ RAG non disponible - test annulé")
            return False

        # Créer l'extension temporelle
        temporal_rag = TemporalRAGManager(rag_manager)

        print("1. 📊 Analyse de la distribution temporelle...")
        distribution = temporal_rag.get_temporal_distribution()

        if "error" not in distribution:
            print(f"   📄 Documents totaux: {distribution.get('total_documents', 0)}")
            print(f"   🕒 Documents avec timestamp: {distribution.get('documents_with_timestamp', 0)}")
            print(f"   📅 Période couverte: {distribution.get('age_span_days', 0)} jours")
            print(f"   🔥 Récents (24h): {distribution.get('recent_24h', 0)} ({distribution.get('percentage_recent_24h', 0)}%)")
            print(f"   📈 Récents (7j): {distribution.get('recent_week', 0)} ({distribution.get('percentage_recent_week', 0)}%)")
        else:
            print(f"   ❌ {distribution['error']}")

        print("\n2. 🔍 Test recherche temporelle vs normale...")
        query = "PyTorch CUDA erreur version"

        # Recherche normale
        normal_results = rag_manager.search_similar_issues(query, limit=3)
        print(f"   📋 Recherche normale: {len(normal_results)} résultats")

        # Recherche temporelle
        temporal_results = temporal_rag.search_with_temporal_priority(query, limit=3, recent_weight=2.0)
        print(f"   🕒 Recherche temporelle: {len(temporal_results)} résultats")

        # Comparer les résultats
        if temporal_results:
            print("   📊 Résultats avec pondération temporelle:")
            for i, result in enumerate(temporal_results):
                age = result.get('age_days', 'N/A')
                temporal_score = result.get('temporal_score', 0)
                similarity = result.get('similarity', 0)

                print(f"     • Rang {i+1}: Score temporel {temporal_score:.3f} (similarité {similarity:.3f}) - Âge: {age} jours")

        print("\n3. 🔥 Test recherche récente uniquement...")
        recent_only = temporal_rag.search_recent_only(query, max_age_hours=24, limit=3)
        print(f"   ⚡ Résultats récents (24h): {len(recent_only)}")

        for i, result in enumerate(recent_only):
            age = result.get('age_days', 'N/A')
            print(f"     • Document {i+1}: Âge {age} jours")

        print("\n✅ RAG TEMPOREL FONCTIONNEL !")
        return True

    except Exception as e:
        print(f"❌ Erreur test RAG temporel: {e}")
        return False

if __name__ == "__main__":
    print("🕒 RAG TEMPOREL - GESTION DES ANALYSES HORODATÉES")
    print("=" * 60)

    success = test_temporal_rag()

    print(f"\n{'✅ SUCCÈS' if success else '❌ ÉCHEC'} - RAG temporel")

    print("\n🎯 FONCTIONNALITÉS AJOUTÉES:")
    print("=" * 40)
    print("✅ search_with_temporal_priority():")
    print("   • Pondération par récence des documents")
    print("   • Filtrage par âge maximum")
    print("   • Bonus pour les analyses récentes")

    print("\n✅ search_recent_only():")
    print("   • Recherche uniquement dans les 24h")
    print("   • Idéal pour l'état actuel du serveur")

    print("\n✅ get_temporal_distribution():")
    print("   • Analyse de la répartition temporelle")
    print("   • Statistiques de fraîcheur des données")

    print("\n💡 UTILISATION RECOMMANDÉE:")
    print("   🔥 Questions sur l'état actuel → search_recent_only()")
    print("   📊 Questions générales → search_with_temporal_priority()")
    print("   📈 Évolution dans le temps → distribution temporelle")

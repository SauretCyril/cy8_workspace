"""
Gestionnaire RAG Hybride pour l'analyse et l'indexation des résultats d'analyse IA Mistral
Supporte deux modes : Rapide (templates) et Expert (RAG + Mistral AI)
Permet de surveiller et optimiser le serveur ComfyUI avec mémoire des erreurs et contraintes
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import hashlib
import time

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ ChromaDB non disponible. Installation: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ SentenceTransformers non disponible. Installation: pip install sentence-transformers")


class RAGManager:
    """Gestionnaire RAG pour l'analyse des logs ComfyUI et la mémoire des erreurs"""

    def __init__(self, db_manager, environment_id: str = None):
        """
        Initialiser le gestionnaire RAG

        Args:
            db_manager: Instance du gestionnaire de base de données
            environment_id: ID de l'environnement ComfyUI
        """
        self.db_manager = db_manager
        self.environment_id = environment_id
        self.logger = logging.getLogger(__name__)

        # Initialiser les composants
        self.chroma_client = None
        self.collection = None
        self.embeddings_model = None
        self.vector_db_path = None
        self.constraints_db_path = None

        # Initialiser les modèles et base vectorielle
        self._initialize_components()

    def _initialize_components(self):
        """Initialiser les composants RAG"""
        try:
            # Vérifier les dépendances
            if not CHROMADB_AVAILABLE:
                self.logger.error("ChromaDB non disponible")
                return False

            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                self.logger.error("SentenceTransformers non disponible")
                return False

            # Obtenir le répertoire d'analyses pour l'environnement
            if self.environment_id:
                analyses_dir = self.db_manager.get_environment_analyses_directory(self.environment_id)
            else:
                # Fallback vers un répertoire par défaut
                analyses_dir = os.path.join(os.getcwd(), "data", "analyses")

            # Créer le répertoire s'il n'existe pas
            os.makedirs(analyses_dir, exist_ok=True)

            # Chemins pour la base vectorielle et les contraintes
            self.vector_db_path = os.path.join(analyses_dir, "vector_db")
            self.constraints_db_path = os.path.join(analyses_dir, "constraints.db")

            # Initialiser ChromaDB (optionnel)
            self._initialize_chromadb()

            # Initialiser le modèle d'embeddings (optionnel)
            self._initialize_embeddings_model()

            # Initialiser la base de contraintes
            self._initialize_constraints_db()

            # Vérifier si au moins une fonctionnalité fonctionne
            if self.chroma_client is None and self.embeddings_model is None:
                self.logger.warning("⚠️ RAG initialisé en mode dégradé (ChromaDB et embeddings indisponibles)")
                print("⚠️ RAG en mode dégradé - fonctionnalités limitées")
            else:
                self.logger.info(f"✅ RAG initialisé pour l'environnement {self.environment_id}")
                print(f"✅ RAG fonctionnel pour {self.environment_id}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'initialisation RAG: {e}")
            print(f"❌ Erreur RAG: {e}")
            return False

    def _initialize_chromadb(self):
        """Initialiser ChromaDB avec gestion d'erreurs robuste"""
        try:
            if not CHROMADB_AVAILABLE:
                print("⚠️ ChromaDB non disponible")
                self.chroma_client = None
                self.collection = None
                return

            print(f"🔧 Initialisation ChromaDB: {self.vector_db_path}")

            # Créer le répertoire de la base vectorielle
            os.makedirs(self.vector_db_path, exist_ok=True)

            # Essayer d'initialiser ChromaDB avec configuration simple
            try:
                self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
                print("✅ ChromaDB PersistentClient initialisé")
            except Exception as e:
                print(f"⚠️ Erreur ChromaDB PersistentClient: {e}")
                # Désactiver ChromaDB en cas d'erreur
                self.chroma_client = None
                self.collection = None
                return

            # Créer ou récupérer la collection
            collection_name = f"comfyui_analyses_{self.environment_id or 'default'}"
            try:
                self.collection = self.chroma_client.get_collection(collection_name)
                print(f"📚 Collection existante récupérée: {collection_name}")
                self.logger.info(f"📚 Collection existante récupérée: {collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": f"Analyses ComfyUI pour environnement {self.environment_id}"}
                )
                print(f"📚 Nouvelle collection créée: {collection_name}")
                self.logger.info(f"📚 Nouvelle collection créée: {collection_name}")

        except Exception as e:
            self.logger.error(f"❌ Erreur ChromaDB: {e}")
            print(f"❌ Erreur ChromaDB globale: {e}")
            self.chroma_client = None
            self.collection = None

    def _initialize_embeddings_model(self):
        """Initialiser le modèle d'embeddings avec fallback"""
        try:
            # Essayer d'abord un modèle très léger
            model_names = [
                "sentence-transformers/all-MiniLM-L6-v2",  # Très léger et rapide
                "all-MiniLM-L6-v2",  # Même modèle, nom court
                "paraphrase-MiniLM-L3-v2"  # Encore plus léger
            ]

            for model_name in model_names:
                try:
                    print(f"🔍 Tentative de chargement: {model_name}")
                    self.embeddings_model = SentenceTransformer(model_name)
                    self.logger.info(f"🤖 Modèle d'embeddings chargé: {model_name}")
                    print(f"✅ Modèle chargé avec succès: {model_name}")
                    return
                except Exception as e:
                    print(f"⚠️ Échec {model_name}: {e}")
                    continue

            # Si tous les modèles échouent, désactiver les embeddings
            raise Exception("Aucun modèle d'embeddings disponible")

        except Exception as e:
            self.logger.warning(f"⚠️ Impossible de charger un modèle d'embeddings: {e}")
            print(f"⚠️ RAG fonctionnera en mode dégradé (sans embeddings)")
            self.embeddings_model = None

    def _initialize_constraints_db(self):
        """Initialiser la base de données des contraintes"""
        try:
            conn = sqlite3.connect(self.constraints_db_path)
            cursor = conn.cursor()

            # Table des contraintes système
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_constraints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    constraint_type TEXT NOT NULL,
                    constraint_value TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table de l'historique des erreurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    solution TEXT,
                    frequency INTEGER DEFAULT 1,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table de l'état du serveur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS server_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state_type TEXT NOT NULL,
                    state_value TEXT NOT NULL,
                    analysis_result TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()

            self.logger.info("🗃️ Base de contraintes initialisée")

        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation base contraintes: {e}")

    def add_constraint(self, constraint_type: str, constraint_value: str, description: str = ""):
        """Ajouter une contrainte système"""
        try:
            conn = sqlite3.connect(self.constraints_db_path)
            cursor = conn.cursor()

            # Vérifier si la contrainte existe déjà
            cursor.execute("""
                SELECT id FROM system_constraints
                WHERE constraint_type = ? AND constraint_value = ?
            """, (constraint_type, constraint_value))

            if cursor.fetchone():
                # Mettre à jour la contrainte existante
                cursor.execute("""
                    UPDATE system_constraints
                    SET description = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE constraint_type = ? AND constraint_value = ?
                """, (description, constraint_type, constraint_value))
            else:
                # Ajouter nouvelle contrainte
                cursor.execute("""
                    INSERT INTO system_constraints (constraint_type, constraint_value, description)
                    VALUES (?, ?, ?)
                """, (constraint_type, constraint_value, description))

            conn.commit()
            conn.close()

            self.logger.info(f"✅ Contrainte ajoutée: {constraint_type} = {constraint_value}")

        except Exception as e:
            self.logger.error(f"❌ Erreur ajout contrainte: {e}")

    def get_constraints(self) -> List[Dict]:
        """Récupérer toutes les contraintes système"""
        try:
            conn = sqlite3.connect(self.constraints_db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT constraint_type, constraint_value, description, created_at
                FROM system_constraints
                ORDER BY created_at DESC
            """)

            constraints = []
            for row in cursor.fetchall():
                constraints.append({
                    'type': row[0],
                    'value': row[1],
                    'description': row[2],
                    'created_at': row[3]
                })

            conn.close()
            return constraints

        except Exception as e:
            self.logger.error(f"❌ Erreur récupération contraintes: {e}")
            return []

    def index_analysis_result(self, analysis_result: Dict[str, Any]):
        """Indexer un résultat d'analyse dans la base vectorielle"""
        try:
            if not self.collection or not self.embeddings_model:
                self.logger.error("❌ RAG non initialisé correctement")
                return False

            # Préparer les données pour l'indexation
            content = self._prepare_content_for_indexing(analysis_result)
            if not content:
                return False

            # Générer l'embedding
            embedding = self.embeddings_model.encode(content)

            # Créer un ID unique pour le document
            doc_id = self._generate_document_id(analysis_result)

            # Métadonnées du document (s'assurer qu'aucune valeur n'est None)
            metadata = {
                "timestamp": analysis_result.get("timestamp", datetime.now().isoformat()),
                "environment_id": str(self.environment_id or "default"),
                "analysis_type": str(analysis_result.get("type", "general")),
                "has_errors": bool(len(analysis_result.get("errors", [])) > 0),
                "error_count": int(len(analysis_result.get("errors", []))),
                "success_count": int(len(analysis_result.get("successes", []))),
                "filename": str(analysis_result.get("filename", "")),
            }

            # Ajouter à la collection
            self.collection.add(
                embeddings=[embedding.tolist()],
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )

            # Enregistrer dans l'historique des erreurs
            self._update_error_history(analysis_result)

            # Mettre à jour l'état du serveur
            self._update_server_state(analysis_result)

            self.logger.info(f"✅ Résultat d'analyse indexé: {doc_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur indexation: {e}")
            return False

    def _prepare_content_for_indexing(self, analysis_result: Dict[str, Any]) -> str:
        """Préparer le contenu pour l'indexation"""
        try:
            content_parts = []

            # Ajouter le résumé
            if "summary" in analysis_result:
                content_parts.append(f"Résumé: {analysis_result['summary']}")

            # Ajouter les erreurs
            if "errors" in analysis_result:
                for error in analysis_result["errors"]:
                    if isinstance(error, dict):
                        error_text = error.get("message", str(error))
                        solution = error.get("solution", "")
                        content_parts.append(f"Erreur: {error_text}")
                        if solution:
                            content_parts.append(f"Solution: {solution}")
                    else:
                        content_parts.append(f"Erreur: {str(error)}")

            # Ajouter les succès
            if "successes" in analysis_result:
                for success in analysis_result["successes"]:
                    content_parts.append(f"Succès: {str(success)}")

            # Ajouter les recommandations
            if "recommendations" in analysis_result:
                for rec in analysis_result["recommendations"]:
                    content_parts.append(f"Recommandation: {str(rec)}")

            # Ajouter l'analyse complète si disponible
            if "full_analysis" in analysis_result:
                content_parts.append(f"Analyse: {analysis_result['full_analysis']}")

            return "\n".join(content_parts)

        except Exception as e:
            self.logger.error(f"❌ Erreur préparation contenu: {e}")
            return ""

    def _generate_document_id(self, analysis_result: Dict[str, Any]) -> str:
        """Générer un ID unique pour le document"""
        content = str(analysis_result)
        timestamp = analysis_result.get("timestamp", datetime.now().isoformat())
        unique_string = f"{timestamp}_{content}_{self.environment_id}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def _update_error_history(self, analysis_result: Dict[str, Any]):
        """Mettre à jour l'historique des erreurs"""
        try:
            if "errors" not in analysis_result:
                return

            conn = sqlite3.connect(self.constraints_db_path)
            cursor = conn.cursor()

            for error in analysis_result["errors"]:
                error_type = "unknown"
                error_message = str(error)
                solution = ""

                if isinstance(error, dict):
                    error_type = error.get("type", "unknown")
                    error_message = error.get("message", str(error))
                    solution = error.get("solution", "")

                # Vérifier si l'erreur existe déjà
                cursor.execute("""
                    SELECT id, frequency FROM error_history
                    WHERE error_type = ? AND error_message = ?
                """, (error_type, error_message))

                existing = cursor.fetchone()

                if existing:
                    # Mettre à jour la fréquence
                    cursor.execute("""
                        UPDATE error_history
                        SET frequency = frequency + 1, last_seen = CURRENT_TIMESTAMP, solution = ?
                        WHERE id = ?
                    """, (solution, existing[0]))
                else:
                    # Nouvelle erreur
                    cursor.execute("""
                        INSERT INTO error_history (error_type, error_message, solution)
                        VALUES (?, ?, ?)
                    """, (error_type, error_message, solution))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour historique: {e}")

    def _update_server_state(self, analysis_result: Dict[str, Any]):
        """Mettre à jour l'état du serveur"""
        try:
            conn = sqlite3.connect(self.constraints_db_path)
            cursor = conn.cursor()

            # Déterminer l'état du serveur
            error_count = len(analysis_result.get("errors", []))
            success_count = len(analysis_result.get("successes", []))

            if error_count == 0:
                state_type = "healthy"
                state_value = "Serveur en bon état"
            elif error_count > success_count:
                state_type = "problematic"
                state_value = f"{error_count} erreurs détectées"
            else:
                state_type = "warning"
                state_value = f"{error_count} erreurs, {success_count} succès"

            # Enregistrer l'état
            cursor.execute("""
                INSERT INTO server_state (state_type, state_value, analysis_result)
                VALUES (?, ?, ?)
            """, (state_type, state_value, json.dumps(analysis_result)))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour état serveur: {e}")

    def search_similar_issues(self, query: str, limit: int = 5) -> List[Dict]:
        """Rechercher des problèmes similaires dans la base vectorielle"""
        try:
            if not self.collection or not self.embeddings_model:
                return []

            # Générer l'embedding de la requête
            query_embedding = self.embeddings_model.encode(query)

            # Rechercher dans la collection
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )

            # Formater les résultats
            similar_issues = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    similar_issues.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1 - results["distances"][0][i],  # Convertir distance en similarité
                    })

            return similar_issues

        except Exception as e:
            self.logger.error(f"❌ Erreur recherche: {e}")
            return []

    def get_server_status_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé de l'état du serveur"""
        try:
            conn = sqlite3.connect(self.constraints_db_path)
            cursor = conn.cursor()

            # État actuel du serveur
            cursor.execute("""
                SELECT state_type, state_value, timestamp
                FROM server_state
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            current_state = cursor.fetchone()

            # Erreurs récurrentes
            cursor.execute("""
                SELECT error_type, error_message, frequency, solution
                FROM error_history
                WHERE frequency > 1
                ORDER BY frequency DESC
                LIMIT 5
            """)
            recurring_errors = cursor.fetchall()

            # Contraintes actives
            constraints = self.get_constraints()

            conn.close()

            return {
                "current_state": {
                    "type": current_state[0] if current_state else "unknown",
                    "value": current_state[1] if current_state else "État indéterminé",
                    "timestamp": current_state[2] if current_state else None
                },
                "recurring_errors": [
                    {
                        "type": row[0],
                        "message": row[1],
                        "frequency": row[2],
                        "solution": row[3]
                    } for row in recurring_errors
                ],
                "constraints": constraints,
                "environment_id": self.environment_id
            }

        except Exception as e:
            self.logger.error(f"❌ Erreur résumé état serveur: {e}")
            return {
                "current_state": {"type": "error", "value": "Erreur lors de la récupération"},
                "recurring_errors": [],
                "constraints": [],
                "environment_id": self.environment_id
            }

    def generate_chat_context(self, user_query: str = "") -> str:
        """Générer le contexte pour une conversation chat"""
        try:
            # Obtenir le résumé de l'état du serveur
            status = self.get_server_status_summary()

            # Rechercher des problèmes similaires si une requête est fournie
            similar_issues = []
            if user_query:
                similar_issues = self.search_similar_issues(user_query, limit=3)

            # Construire le contexte
            context_parts = [
                f"🖥️ **État du serveur ComfyUI (Environnement {self.environment_id})**",
                f"État actuel: {status['current_state']['value']}",
            ]

            # Ajouter les contraintes
            if status["constraints"]:
                context_parts.append("\n🚫 **Contraintes système actives:**")
                for constraint in status["constraints"][:3]:
                    context_parts.append(f"- {constraint['type']}: {constraint['value']}")
                    if constraint["description"]:
                        context_parts.append(f"  → {constraint['description']}")

            # Ajouter les erreurs récurrentes
            if status["recurring_errors"]:
                context_parts.append("\n⚠️ **Erreurs récurrentes:**")
                for error in status["recurring_errors"][:3]:
                    context_parts.append(f"- {error['message']} (x{error['frequency']})")
                    if error["solution"]:
                        context_parts.append(f"  → Solution: {error['solution']}")

            # Ajouter les problèmes similaires si recherche
            if similar_issues:
                context_parts.append(f"\n🔍 **Problèmes similaires trouvés pour '{user_query}':**")
                for issue in similar_issues:
                    similarity_pct = int(issue["similarity"] * 100)
                    context_parts.append(f"- ({similarity_pct}% similaire) {issue['content'][:200]}...")

            return "\n".join(context_parts)

        except Exception as e:
            self.logger.error(f"❌ Erreur génération contexte chat: {e}")
            return f"❌ Erreur lors de la génération du contexte: {e}"

    # === NOUVELLES MÉTHODES RAG HYBRIDE ===

    def query_with_mode(self, query: str, mode: str = "rapide", max_results: int = 5) -> Dict[str, Any]:
        """
        Interroger le RAG avec le mode spécifié

        Args:
            query: Question de l'utilisateur
            mode: "rapide" (templates) ou "expert" (RAG + Mistral AI)
            max_results: Nombre maximum de résultats

        Returns:
            Dict avec la réponse, le mode utilisé, et les métadonnées
        """
        start_time = time.time()

        try:
            if mode == "rapide":
                result = self._query_rapid_mode(query, max_results)
            elif mode == "expert":
                result = self._query_expert_mode(query, max_results)
            else:
                raise ValueError(f"Mode invalide: {mode}. Utilisez 'rapide' ou 'expert'")

            # Ajouter les métadonnées de performance
            result["metadata"] = {
                "mode": mode,
                "response_time": round(time.time() - start_time, 2),
                "timestamp": datetime.now().isoformat()
            }

            return result

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la requête {mode}: {e}")
            return {
                "success": False,
                "response": f"Erreur lors de la requête: {str(e)}",
                "sources": [],
                "metadata": {
                    "mode": mode,
                    "response_time": round(time.time() - start_time, 2),
                    "error": str(e)
                }
            }

    def _query_rapid_mode(self, query: str, max_results: int) -> Dict[str, Any]:
        """Mode rapide : Recherche vectorielle + Templates pré-programmés"""
        try:
            # Rechercher les documents similaires
            similar_docs = self.search_similar_issues(query, max_results)

            if not similar_docs:
                return {
                    "success": True,
                    "response": "❌ Aucune analyse similaire trouvée dans l'historique.\n\n"
                              "💡 Essayez le mode Expert pour une analyse plus approfondie, ou "
                              "analysez d'abord quelques logs pour enrichir la base de connaissances.",
                    "sources": [],
                    "mode": "rapide"
                }

            # Générer une réponse basée sur les templates
            response = self._generate_template_response(query, similar_docs)

            return {
                "success": True,
                "response": response,
                "sources": [doc.get("source", "Analyse ComfyUI") for doc in similar_docs],
                "mode": "rapide",
                "documents_found": len(similar_docs)
            }

        except Exception as e:
            self.logger.error(f"❌ Erreur mode rapide: {e}")
            raise e

    def _query_expert_mode(self, query: str, max_results: int) -> Dict[str, Any]:
        """Mode expert : Recherche vectorielle + Analyse Mistral AI"""
        try:
            # Rechercher les documents similaires
            similar_docs = self.search_similar_issues(query, max_results)

            if not similar_docs:
                return {
                    "success": True,
                    "response": "❌ Aucune analyse similaire trouvée dans l'historique.\n\n"
                              "📝 Pour enrichir la base de connaissances, analysez quelques logs ComfyUI "
                              "dans l'onglet Analyses. Le RAG Expert sera plus efficace avec plus de données.",
                    "sources": [],
                    "mode": "expert"
                }

            # Préparer le contexte pour Mistral AI
            context = self._prepare_context_for_mistral(similar_docs, query)

            # Appeler Mistral AI pour la synthèse
            mistral_response = self._call_mistral_for_analysis(query, context)

            if mistral_response["success"]:
                return {
                    "success": True,
                    "response": mistral_response["response"],
                    "sources": [doc.get("source", "Analyse ComfyUI") for doc in similar_docs],
                    "mode": "expert",
                    "documents_found": len(similar_docs),
                    "mistral_tokens": mistral_response.get("tokens_used", "N/A")
                }
            else:
                # Fallback vers le mode rapide en cas d'erreur Mistral
                self.logger.warning("Fallback vers mode rapide après erreur Mistral")
                return self._query_rapid_mode(query, max_results)

        except Exception as e:
            self.logger.error(f"❌ Erreur mode expert: {e}")
            # Fallback vers le mode rapide
            try:
                return self._query_rapid_mode(query, max_results)
            except:
                raise e

    def _generate_template_response(self, query: str, similar_docs: List[Dict]) -> str:
        """Générer une réponse basée sur des templates pré-programmés"""

        # Analyser les types d'erreurs trouvées
        error_types = set()
        solutions = []
        environments = set()

        for doc in similar_docs:
            doc_content = doc.get("content", {})

            # Extraire les types d'erreurs
            if "errors" in doc_content:
                for error in doc_content["errors"]:
                    if isinstance(error, dict):
                        error_types.add(error.get("type", "unknown"))
                        if "solution" in error:
                            solutions.append(error["solution"])

            # Extraire l'environnement
            if "environment_id" in doc_content:
                environments.add(doc_content["environment_id"])

        # Construire la réponse template
        response = "🔍 **Analyse Rapide RAG** - Résultats similaires trouvés\n\n"

        # Résumé des documents
        response += f"📊 **{len(similar_docs)} analyses similaires** trouvées dans l'historique\n"
        if environments:
            response += f"🌍 **Environnements concernés** : {', '.join(environments)}\n\n"

        # Types d'erreurs fréquents
        if error_types:
            response += "⚠️ **Types d'erreurs fréquents** :\n"
            for error_type in sorted(error_types):
                response += f"  • {error_type.replace('_', ' ').title()}\n"
            response += "\n"

        # Solutions recommandées
        if solutions:
            response += "💡 **Solutions recommandées** :\n"
            unique_solutions = list(set(solutions))[:3]  # Top 3 solutions uniques
            for i, solution in enumerate(unique_solutions, 1):
                response += f"  {i}. {solution}\n"
            response += "\n"

        # Conseils généraux selon le type de query
        query_lower = query.lower()
        if any(word in query_lower for word in ["cuda", "gpu", "memory", "vram"]):
            response += "🎯 **Conseils CUDA/GPU** :\n"
            response += "  • Vérifiez la version CUDA compatible avec PyTorch\n"
            response += "  • Surveillez l'utilisation VRAM (nvidia-smi)\n"
            response += "  • Redémarrez ComfyUI si problème persistant\n\n"

        elif any(word in query_lower for word in ["custom", "node", "missing"]):
            response += "🎯 **Conseils Custom Nodes** :\n"
            response += "  • Vérifiez l'installation des custom nodes\n"
            response += "  • Redémarrez ComfyUI après installation\n"
            response += "  • Consultez les logs de démarrage\n\n"

        elif any(word in query_lower for word in ["model", "checkpoint", "load"]):
            response += "🎯 **Conseils Modèles** :\n"
            response += "  • Vérifiez les chemins dans extra_model_paths.yaml\n"
            response += "  • Contrôlez la disponibilité des modèles\n"
            response += "  • Validez les permissions de fichiers\n\n"

        response += "💡 **Astuce** : Utilisez le mode **Expert** pour une analyse plus approfondie avec IA !"

        return response

    def _prepare_context_for_mistral(self, similar_docs: List[Dict], query: str) -> str:
        """Préparer le contexte pour l'analyse Mistral AI"""

        context = f"REQUÊTE UTILISATEUR: {query}\n\n"
        context += f"HISTORIQUE D'ANALYSES SIMILAIRES ({len(similar_docs)} documents):\n\n"

        for i, doc in enumerate(similar_docs, 1):
            context += f"--- ANALYSE {i} ---\n"

            doc_content = doc.get("content", {})

            # Métadonnées de base
            if "timestamp" in doc_content:
                context += f"Date: {doc_content['timestamp']}\n"
            if "environment_id" in doc_content:
                context += f"Environnement: {doc_content['environment_id']}\n"

            # Résumé
            if "summary" in doc_content:
                context += f"Résumé: {doc_content['summary']}\n"

            # Erreurs
            if "errors" in doc_content and doc_content["errors"]:
                context += "Erreurs trouvées:\n"
                for error in doc_content["errors"][:3]:  # Limiter à 3 erreurs par doc
                    if isinstance(error, dict):
                        context += f"  - Type: {error.get('type', 'N/A')}\n"
                        context += f"    Message: {error.get('message', 'N/A')}\n"
                        if "solution" in error:
                            context += f"    Solution: {error['solution']}\n"
                    else:
                        context += f"  - {error}\n"

            # Succès
            if "successes" in doc_content and doc_content["successes"]:
                context += f"Éléments fonctionnels: {', '.join(doc_content['successes'][:3])}\n"

            context += "\n"

        return context

    def _call_mistral_for_analysis(self, query: str, context: str) -> Dict[str, Any]:
        """Appeler Mistral AI pour analyser le contexte et répondre à la requête"""

        try:
            # Importer le module Mistral
            from cy8_mistral import get_mistral_answer

            # Préparer le rôle système pour Mistral
            system_role = """Tu es un expert technique ComfyUI spécialisé dans l'analyse des logs et la résolution de problèmes.

            Ton rôle est d'analyser l'historique d'erreurs similaires et de fournir une réponse experte, contextualisée et actionnable.

            INSTRUCTIONS:
            1. Analyse les documents d'historique fournis
            2. Identifie les patterns et corrélations
            3. Fournis une réponse structurée avec:
               - Diagnostic précis du problème
               - Solutions spécifiques et priorisées
               - Conseils préventifs
            4. Sois concis mais complet
            5. Utilise des emojis pour la lisibilité
            6. Référence les analyses similaires quand pertinent

            FORMAT DE RÉPONSE:
            🔍 **Diagnostic Expert**
            [Analyse du problème basée sur l'historique]

            ⚡ **Solutions Recommandées**
            1. [Solution prioritaire]
            2. [Solution alternative]

            🛡️ **Prévention**
            [Conseils pour éviter le problème]
            """

            # Construire la question complète
            full_question = f"""Basé sur l'historique d'analyses ComfyUI ci-dessous, réponds à cette requête utilisateur:

{query}

{context}

Fournis une analyse experte en te basant sur les patterns observés dans l'historique."""

            # Appeler Mistral
            print(f"🧠 Appel Mistral AI pour analyse experte...")
            start_time = time.time()

            mistral_result = get_mistral_answer(
                question=full_question,
                role=system_role,
                texte=""  # Le contexte est déjà dans la question
            )

            response_time = round(time.time() - start_time, 2)

            if mistral_result and len(mistral_result.strip()) > 50:
                # Ajouter un en-tête pour distinguer la réponse experte
                expert_response = f"🧠 **ANALYSE EXPERTE RAG + MISTRAL AI**\n"
                expert_response += f"⏱️ *Temps de traitement: {response_time}s*\n\n"
                expert_response += mistral_result
                expert_response += f"\n\n---\n📚 *Basé sur {context.count('--- ANALYSE')} analyses similaires de l'historique ComfyUI*"

                return {
                    "success": True,
                    "response": expert_response,
                    "tokens_used": len(full_question.split()) + len(mistral_result.split()),
                    "response_time": response_time
                }
            else:
                self.logger.warning("Réponse Mistral vide ou trop courte")
                return {"success": False, "error": "Réponse Mistral invalide"}

        except ImportError:
            self.logger.error("Module cy8_mistral non disponible")
            return {"success": False, "error": "Module Mistral non disponible"}

        except Exception as e:
            self.logger.error(f"Erreur lors de l'appel Mistral: {e}")
            return {"success": False, "error": str(e)}

    def get_mode_info(self) -> Dict[str, Dict[str, Any]]:
        """Retourner les informations sur les modes disponibles"""
        return {
            "rapide": {
                "name": "RAG Rapide ⚡",
                "description": "Recherche vectorielle + Templates pré-programmés",
                "speed": "< 1 seconde",
                "cost": "Gratuit",
                "accuracy": "Bonne pour problèmes connus",
                "best_for": ["Erreurs communes", "Diagnostics rapides", "Premiers secours"]
            },
            "expert": {
                "name": "RAG Expert 🧠",
                "description": "Recherche vectorielle + Analyse Mistral AI",
                "speed": "2-5 secondes",
                "cost": "Tokens Mistral",
                "accuracy": "Excellente avec contextualisation",
                "best_for": ["Problèmes complexes", "Analyse approfondie", "Solutions personnalisées"]
            }
        }

    def is_available(self) -> bool:
        """Vérifier si le RAG est disponible et fonctionnel"""
        return (
            CHROMADB_AVAILABLE and
            SENTENCE_TRANSFORMERS_AVAILABLE and
            self.collection is not None and
            self.embeddings_model is not None
        )


def main():
    """Test de la classe RAGManager"""
    print("🧪 Test de la classe RAGManager")

    # Simulation d'un db_manager
    class MockDBManager:
        def get_environment_analyses_directory(self, env_id):
            return f"H:/comfyui/{env_id}/analyses"

    # Test d'initialisation
    rag = RAGManager(MockDBManager(), "G11_01")

    if rag.is_available():
        print("✅ RAG initialisé avec succès")

        # Test d'ajout de contrainte
        rag.add_constraint("numpy_version", "1.x", "Ne peut pas utiliser numpy 2.x à cause du matériel")

        # Test d'indexation
        test_analysis = {
            "timestamp": datetime.now().isoformat(),
            "type": "log_analysis",
            "summary": "Analyse du log ComfyUI avec erreurs numpy",
            "errors": [
                {
                    "type": "dependency_conflict",
                    "message": "Conflit de version numpy 2.x vs 1.x",
                    "solution": "Downgrade vers numpy 1.24.x"
                }
            ],
            "successes": ["Chargement des custom nodes réussi"],
            "recommendations": ["Vérifier les versions de dépendances"]
        }

        rag.index_analysis_result(test_analysis)

        # Test de recherche
        results = rag.search_similar_issues("problème numpy version")
        print(f"🔍 Résultats de recherche: {len(results)}")

        # Test de résumé
        summary = rag.get_server_status_summary()
        print(f"📊 État serveur: {summary['current_state']['value']}")

    else:
        print("❌ RAG non disponible - vérifiez les dépendances")


class RAGManagerStats:
    """Extension pour les statistiques du RAG Manager"""

    def get_collection_stats(self):
        """Obtenir les statistiques de la collection ChromaDB"""
        try:
            if not self.collection:
                return {
                    'total_documents': 0,
                    'last_indexed': 'Jamais',
                    'collection_name': None,
                    'available': False
                }

            # Compter les documents
            count = self.collection.count()

            # Obtenir des métadonnées pour la dernière indexation
            last_indexed = 'Inconnu'
            if count > 0:
                try:
                    results = self.collection.get(
                        limit=1,
                        include=["metadatas"],
                        order_by=["timestamp"]  # Essayer de trier par timestamp si possible
                    )
                    if results and results.get('metadatas'):
                        last_timestamp = results['metadatas'][0].get('timestamp', 'Inconnu')
                        if last_timestamp != 'Inconnu':
                            try:
                                from datetime import datetime
                                if isinstance(last_timestamp, str):
                                    dt = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                                    last_indexed = dt.strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    last_indexed = str(last_timestamp)
                            except:
                                last_indexed = str(last_timestamp)
                except Exception:
                    # Si l'ordre n'est pas supporté, utiliser une recherche simple
                    results = self.collection.get(limit=5, include=["metadatas"])
                    if results and results.get('metadatas'):
                        # Prendre le timestamp le plus récent disponible
                        timestamps = []
                        for metadata in results['metadatas']:
                            ts = metadata.get('timestamp')
                            if ts:
                                timestamps.append(ts)
                        if timestamps:
                            last_indexed = max(timestamps)

            return {
                'total_documents': count,
                'last_indexed': last_indexed,
                'collection_name': getattr(self.collection, 'name', 'default'),
                'available': True,
                'environment_id': self.environment_id
            }

        except Exception as e:
            self.logger.error(f"Erreur statistiques collection: {e}")
            return {
                'total_documents': 0,
                'last_indexed': f'Erreur: {e}',
                'collection_name': None,
                'available': False
            }


# Ajouter la méthode à RAGManager
RAGManager.get_collection_stats = RAGManagerStats.get_collection_stats
if __name__ == "__main__":
    main()

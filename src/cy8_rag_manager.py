"""
Gestionnaire RAG pour l'analyse et l'indexation des résultats d'analyse IA Mistral
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
            
            # Initialiser ChromaDB
            self._initialize_chromadb()
            
            # Initialiser le modèle d'embeddings
            self._initialize_embeddings_model()
            
            # Initialiser la base de contraintes
            self._initialize_constraints_db()
            
            self.logger.info(f"✅ RAG initialisé pour l'environnement {self.environment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'initialisation RAG: {e}")
            return False
    
    def _initialize_chromadb(self):
        """Initialiser ChromaDB"""
        try:
            # Créer le répertoire de la base vectorielle
            os.makedirs(self.vector_db_path, exist_ok=True)
            
            # Initialiser ChromaDB avec persistance
            self.chroma_client = chromadb.PersistentClient(
                path=self.vector_db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Créer ou récupérer la collection
            collection_name = f"comfyui_analyses_{self.environment_id or 'default'}"
            try:
                self.collection = self.chroma_client.get_collection(collection_name)
                self.logger.info(f"📚 Collection existante récupérée: {collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": f"Analyses ComfyUI pour environnement {self.environment_id}"}
                )
                self.logger.info(f"📚 Nouvelle collection créée: {collection_name}")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None
    
    def _initialize_embeddings_model(self):
        """Initialiser le modèle d'embeddings"""
        try:
            # Utiliser un modèle français/multilingue optimisé
            model_name = "sentence-transformers/all-MiniLM-L6-v2"  # Léger et efficace
            self.embeddings_model = SentenceTransformer(model_name)
            self.logger.info(f"🤖 Modèle d'embeddings chargé: {model_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement modèle embeddings: {e}")
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
            
            # Métadonnées du document
            metadata = {
                "timestamp": analysis_result.get("timestamp", datetime.now().isoformat()),
                "environment_id": self.environment_id,
                "analysis_type": analysis_result.get("type", "general"),
                "has_errors": len(analysis_result.get("errors", [])) > 0,
                "error_count": len(analysis_result.get("errors", [])),
                "success_count": len(analysis_result.get("successes", [])),
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


if __name__ == "__main__":
    main()
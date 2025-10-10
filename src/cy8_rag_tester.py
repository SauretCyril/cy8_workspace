#!/usr/bin/env python3
"""
Système de test complet pour valider l'apprentissage du RAG
Vérifie que le RAG apprend des échanges et des nouveaux logs indexés
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import uuid


class RAGTester:
    """Testeur complet pour valider l'apprentissage du RAG"""

    def __init__(self, rag_manager, db_manager):
        self.rag_manager = rag_manager
        self.db_manager = db_manager
        self.test_results = []
        # NE PAS stocker environment_id - utiliser dynamiquement celui du rag_manager

    @property
    def environment_id(self):
        """Récupérer l'environment_id actuel du RAG Manager"""
        return self.rag_manager.environment_id if self.rag_manager else "default"

    def run_quick_test(self) -> Dict:
        """
        Lance un test rapide pour vérifier le fonctionnement de base

        Returns:
            Dict: Résultats du test rapide
        """
        print("⚡ Début du test rapide RAG...")
        start_time = time.time()

        try:
            # Tests de base uniquement
            indexing_result = self._test_new_data_indexing()
            performance_result = self._test_performance()

            # Vérifications simples
            indexing_works = indexing_result.get("indexing_successful", False)
            search_works = indexing_result.get("immediate_search_found", False)
            performance_ok = performance_result.get("avg_search_time", 10) < 2.0

            success = indexing_works and search_works and performance_ok

            duration = time.time() - start_time

            results = {
                "success": success,
                "indexing_works": indexing_works,
                "search_works": search_works,
                "performance_ok": performance_ok,
                "test_duration": round(duration, 2),
                "details": "Test rapide de fonctionnement de base du RAG",
                "timestamp": datetime.now().isoformat()
            }

            print(f"⚡ Test rapide terminé en {duration:.2f}s - {'✅ Succès' if success else '❌ Échec'}")
            return results

        except Exception as e:
            print(f"❌ Erreur dans le test rapide: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Lance une suite complète de tests RAG"""
        print("🧪 === SUITE DE TESTS RAG COMPLÈTE ===")
        print(f"📍 Environnement: {self.environment_id}")
        print(f"⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        results = {
            "environment_id": self.environment_id,
            "test_date": datetime.now().isoformat(),
            "tests": {}
        }

        # 1. Test de base - État initial
        results["tests"]["initial_state"] = self._test_initial_state()

        # 2. Test d'indexation de nouvelles données
        results["tests"]["new_data_indexing"] = self._test_new_data_indexing()

        # 3. Test d'apprentissage depuis échanges chat
        results["tests"]["chat_learning"] = self._test_chat_learning()

        # 4. Test de recherche temporelle
        results["tests"]["temporal_search"] = self._test_temporal_search()

        # 5. Test de mémorisation des erreurs
        results["tests"]["error_memory"] = self._test_error_memory()

        # 6. Test de cohérence environnement
        results["tests"]["environment_consistency"] = self._test_environment_consistency()

        # 7. Test de performance
        results["tests"]["performance"] = self._test_performance()

        # Résumé global
        results["summary"] = self._generate_summary(results["tests"])

        # Sauvegarde des résultats
        self._save_test_results(results)

        return results

    def _test_initial_state(self) -> Dict[str, Any]:
        """Test de l'état initial du RAG"""
        print("🔍 Test 1: État initial du RAG...")

        try:
            # Vérifier les composants RAG
            rag_available = self.rag_manager.is_available() if self.rag_manager else False

            # Compter les documents existants
            doc_count = 0
            if rag_available and hasattr(self.rag_manager, 'collection'):
                try:
                    doc_count = self.rag_manager.collection.count()
                except:
                    doc_count = 0

            # Vérifier l'environnement
            env_id = self.rag_manager.environment_id if self.rag_manager else None

            result = {
                "status": "success",
                "rag_available": rag_available,
                "document_count": doc_count,
                "environment_id": env_id,
                "timestamp": datetime.now().isoformat()
            }

            print(f"  ✅ RAG disponible: {rag_available}")
            print(f"  📊 Documents indexés: {doc_count}")
            print(f"  🏷️  Environnement: {env_id}")

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _test_new_data_indexing(self) -> Dict[str, Any]:
        """Test d'indexation de nouvelles données"""
        print("📥 Test 2: Indexation de nouvelles données...")

        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                return {"status": "skipped", "reason": "RAG non disponible"}

            # Créer des données de test
            test_data = {
                "test_id": str(uuid.uuid4())[:8],
                "environment_id": self.environment_id,
                "log_content": f"TEST LOG {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "errors_detected": ["Test Error: Simulation d'erreur pour validation RAG"],
                "success_rate": 100.0,
                "performance_metrics": {"test_metric": "ok"},
                "recommendations": ["Test: Vérifier que cette recommandation est mémorisée"],
                "analysis_summary": f"Analyse de test créée le {datetime.now()}"
            }

            # Indexer les données
            initial_count = self.rag_manager.collection.count()
            self.rag_manager.index_analysis_result(test_data)
            new_count = self.rag_manager.collection.count()

            # Vérifier que l'indexation a fonctionné
            indexed = new_count > initial_count

            # Tester la recherche immédiate
            search_results = self.rag_manager.search_similar_issues("Test Error simulation", limit=5)
            found_test_data = any("Test Error" in str(result) for result in search_results)

            result = {
                "status": "success",
                "test_data_id": test_data["test_id"],
                "documents_before": initial_count,
                "documents_after": new_count,
                "indexing_successful": indexed,
                "immediate_search_found": found_test_data,
                "timestamp": datetime.now().isoformat()
            }

            print(f"  📊 Documents avant: {initial_count}")
            print(f"  📊 Documents après: {new_count}")
            print(f"  ✅ Indexation: {'Réussie' if indexed else 'Échouée'}")
            print(f"  🔍 Recherche immédiate: {'Trouvée' if found_test_data else 'Non trouvée'}")

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _test_chat_learning(self) -> Dict[str, Any]:
        """Test d'apprentissage depuis les échanges chat"""
        print("💬 Test 3: Apprentissage depuis échanges chat...")

        try:
            if not self.rag_manager:
                return {"status": "skipped", "reason": "RAG non disponible"}

            # Simuler un échange chat avec information spécifique
            test_question = f"Comment résoudre l'erreur TEST_CHAT_{datetime.now().strftime('%H%M%S')} ?"
            test_answer = f"Solution TEST: Pour résoudre TEST_CHAT_{datetime.now().strftime('%H%M%S')}, il faut redémarrer ComfyUI et vérifier les dépendances."

            # Simuler l'ajout à l'historique (si la méthode existe)
            chat_learning_successful = False
            if hasattr(self.rag_manager, 'add_chat_interaction'):
                self.rag_manager.add_chat_interaction(test_question, test_answer)
                chat_learning_successful = True
            elif hasattr(self.rag_manager, 'index_chat_history'):
                # Méthode alternative
                chat_data = {
                    "question": test_question,
                    "answer": test_answer,
                    "timestamp": datetime.now().isoformat(),
                    "environment_id": self.environment_id
                }
                self.rag_manager.index_chat_history([chat_data])
                chat_learning_successful = True
            elif hasattr(self.rag_manager, 'index_analysis_result'):
                # Fallback: indexer comme analyse
                chat_data = {
                    "test_id": f"chat_test_{int(time.time())}",
                    "environment_id": self.environment_id,
                    "log_content": f"Chat Exchange: Q: {test_question} A: {test_answer}",
                    "analysis_summary": f"Chat learning test: {test_question}",
                    "chat_interaction": True
                }
                self.rag_manager.index_analysis_result(chat_data)
                chat_learning_successful = True

            # Tester si le RAG peut retrouver cette information
            search_test = self.rag_manager.search_similar_issues(test_question, limit=3)
            found_in_search = any("TEST_CHAT" in str(result) for result in search_test)

            result = {
                "status": "success",
                "test_question": test_question,
                "chat_indexing_method_available": chat_learning_successful,
                "found_in_subsequent_search": found_in_search,
                "search_results_count": len(search_test),
                "timestamp": datetime.now().isoformat()
            }

            print(f"  💬 Question test: {test_question[:50]}...")
            print(f"  📝 Méthode apprentissage chat: {'Disponible' if chat_learning_successful else 'Non implémentée'}")
            print(f"  🔍 Retrouvé en recherche: {'Oui' if found_in_search else 'Non'}")

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _test_temporal_search(self) -> Dict[str, Any]:
        """Test de la recherche temporelle"""
        print("🕒 Test 4: Recherche temporelle...")

        try:
            if not self.rag_manager:
                return {"status": "skipped", "reason": "RAG non disponible"}

            # Tester la recherche temporelle si disponible
            temporal_methods = []
            if hasattr(self.rag_manager, 'search_with_temporal_priority'):
                temporal_methods.append("search_with_temporal_priority")
            if hasattr(self.rag_manager, 'search_recent_only'):
                temporal_methods.append("search_recent_only")

            # Test basique de recherche
            basic_search = self.rag_manager.search_similar_issues("ComfyUI", limit=5)
            basic_count = len(basic_search)

            # Test temporal si disponible
            temporal_results = []
            if "search_with_temporal_priority" in temporal_methods:
                temporal_results = self.rag_manager.search_with_temporal_priority("ComfyUI", limit=5)

            result = {
                "status": "success",
                "temporal_methods_available": temporal_methods,
                "basic_search_results": basic_count,
                "temporal_search_results": len(temporal_results),
                "temporal_functionality": len(temporal_methods) > 0,
                "timestamp": datetime.now().isoformat()
            }

            print(f"  🔧 Méthodes temporelles: {temporal_methods}")
            print(f"  📊 Résultats recherche normale: {basic_count}")
            print(f"  ⏰ Résultats recherche temporelle: {len(temporal_results)}")

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _test_error_memory(self) -> Dict[str, Any]:
        """Test de mémorisation des erreurs"""
        print("🚨 Test 5: Mémorisation des erreurs...")

        try:
            # Rechercher des erreurs connues
            error_searches = [
                "CUDA out of memory",
                "Node not found",
                "Import error",
                "Module not found",
                "Connection refused"
            ]

            error_memory_results = {}
            total_results = 0

            for error_type in error_searches:
                if self.rag_manager and self.rag_manager.is_available():
                    results = self.rag_manager.search_similar_issues(error_type, limit=3)
                    error_memory_results[error_type] = len(results)
                    total_results += len(results)
                else:
                    error_memory_results[error_type] = 0

            # Vérifier s'il y a une base d'erreurs
            has_error_memory = total_results > 0
            most_documented_error = max(error_memory_results.items(), key=lambda x: x[1]) if error_memory_results else None

            result = {
                "status": "success",
                "error_searches_performed": len(error_searches),
                "total_error_results_found": total_results,
                "has_error_memory": has_error_memory,
                "error_breakdown": error_memory_results,
                "most_documented_error": most_documented_error,
                "timestamp": datetime.now().isoformat()
            }

            print(f"  🔍 Types d'erreurs testés: {len(error_searches)}")
            print(f"  📊 Total résultats trouvés: {total_results}")
            print(f"  🧠 Mémoire d'erreurs: {'Active' if has_error_memory else 'Limitée'}")
            if most_documented_error:
                print(f"  🥇 Erreur la plus documentée: {most_documented_error[0]} ({most_documented_error[1]} résultats)")

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _test_environment_consistency(self) -> Dict[str, Any]:
        """Test de cohérence environnement"""
        print("🏷️ Test 6: Cohérence environnement...")

        try:
            current_env = self.environment_id
            rag_env = self.rag_manager.environment_id if self.rag_manager else None

            # Vérifier la cohérence
            env_consistent = current_env == rag_env

            # Test de recherche spécifique à l'environnement
            env_specific_results = []
            if self.rag_manager and self.rag_manager.is_available():
                env_specific_results = self.rag_manager.search_similar_issues(
                    f"environnement {current_env}", limit=3
                )

            result = {
                "status": "success",
                "current_environment": current_env,
                "rag_environment": rag_env,
                "environment_consistent": env_consistent,
                "env_specific_results_count": len(env_specific_results),
                "timestamp": datetime.now().isoformat()
            }

            print(f"  🏷️ Environnement actuel: {current_env}")
            print(f"  🧠 Environnement RAG: {rag_env}")
            print(f"  ✅ Cohérence: {'Oui' if env_consistent else 'Non'}")
            print(f"  📊 Résultats spécifiques env: {len(env_specific_results)}")

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _test_performance(self) -> Dict[str, Any]:
        """Test de performance du RAG"""
        print("⚡ Test 7: Performance...")

        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                return {"status": "skipped", "reason": "RAG non disponible"}

            # Test de rapidité de recherche
            search_queries = [
                "ComfyUI error",
                "CUDA memory",
                "Node install",
                "Model load",
                "Python path"
            ]

            search_times = []
            total_results = 0

            for query in search_queries:
                start_time = time.time()
                results = self.rag_manager.search_similar_issues(query, limit=5)
                end_time = time.time()

                search_time = (end_time - start_time) * 1000  # en ms
                search_times.append(search_time)
                total_results += len(results)

            avg_search_time = sum(search_times) / len(search_times) if search_times else 0
            max_search_time = max(search_times) if search_times else 0
            min_search_time = min(search_times) if search_times else 0

            # Évaluation performance
            performance_rating = "excellent" if avg_search_time < 100 else "good" if avg_search_time < 500 else "slow"

            result = {
                "status": "success",
                "queries_tested": len(search_queries),
                "total_results_returned": total_results,
                "avg_search_time_ms": round(avg_search_time, 2),
                "max_search_time_ms": round(max_search_time, 2),
                "min_search_time_ms": round(min_search_time, 2),
                "performance_rating": performance_rating,
                "search_times_detail": [round(t, 2) for t in search_times],
                "timestamp": datetime.now().isoformat()
            }

            print(f"  🔍 Requêtes testées: {len(search_queries)}")
            print(f"  📊 Résultats totaux: {total_results}")
            print(f"  ⚡ Temps moyen: {avg_search_time:.1f}ms")
            print(f"  🏆 Performance: {performance_rating}")

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _generate_summary(self, tests: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résumé des tests"""
        print("📋 Génération du résumé...")

        total_tests = len(tests)
        successful_tests = sum(1 for test in tests.values() if test.get("status") == "success")
        error_tests = sum(1 for test in tests.values() if test.get("status") == "error")
        skipped_tests = sum(1 for test in tests.values() if test.get("status") == "skipped")

        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        # Évaluation globale
        if success_rate >= 90:
            overall_rating = "excellent"
        elif success_rate >= 70:
            overall_rating = "good"
        elif success_rate >= 50:
            overall_rating = "fair"
        else:
            overall_rating = "poor"

        # Recommandations
        recommendations = []

        if tests.get("initial_state", {}).get("document_count", 0) < 5:
            recommendations.append("📊 Analysez plus de logs pour enrichir la base de connaissances")

        if not tests.get("chat_learning", {}).get("chat_indexing_method_available", False):
            recommendations.append("💬 Implémentez l'apprentissage depuis les échanges chat")

        if not tests.get("temporal_search", {}).get("temporal_functionality", False):
            recommendations.append("🕒 Activez la recherche temporelle pour prioriser les informations récentes")

        if tests.get("performance", {}).get("performance_rating") == "slow":
            recommendations.append("⚡ Optimisez les performances de recherche RAG")

        if not tests.get("error_memory", {}).get("has_error_memory", False):
            recommendations.append("🚨 Enrichissez la base d'erreurs connues")

        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "error_tests": error_tests,
            "skipped_tests": skipped_tests,
            "success_rate_percent": round(success_rate, 1),
            "overall_rating": overall_rating,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }

        print(f"  📊 Tests réussis: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"  🏆 Évaluation globale: {overall_rating}")
        print(f"  💡 Recommandations: {len(recommendations)}")

        return summary

    def _save_test_results(self, results: Dict[str, Any]):
        """Sauvegarde les résultats de test"""
        try:
            # Créer le répertoire de test s'il n'existe pas
            test_dir = "data/rag_tests"
            os.makedirs(test_dir, exist_ok=True)

            # Nom de fichier avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_test_results_{self.environment_id}_{timestamp}.json"
            filepath = os.path.join(test_dir, filename)

            # Sauvegarder
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            print(f"💾 Résultats sauvegardés: {filepath}")

        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")

    def quick_learning_test(self, test_info: str) -> Dict[str, Any]:
        """Test rapide d'apprentissage avec une information spécifique"""
        print(f"🧪 Test rapide d'apprentissage: {test_info}")

        if not self.rag_manager or not self.rag_manager.is_available():
            return {"status": "error", "message": "RAG non disponible"}

        try:
            # Recherche AVANT l'ajout
            before_results = self.rag_manager.search_similar_issues(test_info, limit=3)
            before_count = len(before_results)

            # Ajouter l'information
            test_data = {
                "test_id": f"quick_test_{int(time.time())}",
                "environment_id": self.environment_id,
                "log_content": f"QUICK TEST: {test_info}",
                "analysis_summary": f"Test d'apprentissage rapide: {test_info}",
                "timestamp": datetime.now().isoformat()
            }

            self.rag_manager.index_analysis_result(test_data)

            # Recherche APRÈS l'ajout
            time.sleep(0.1)  # Petit délai pour l'indexation
            after_results = self.rag_manager.search_similar_issues(test_info, limit=3)
            after_count = len(after_results)

            learning_detected = after_count > before_count

            result = {
                "status": "success",
                "test_info": test_info,
                "results_before": before_count,
                "results_after": after_count,
                "learning_detected": learning_detected,
                "improvement": after_count - before_count,
                "timestamp": datetime.now().isoformat()
            }

            print(f"  📊 Avant: {before_count} résultats")
            print(f"  📊 Après: {after_count} résultats")
            print(f"  🧠 Apprentissage: {'✅ Détecté' if learning_detected else '❌ Non détecté'}")

            return result

        except Exception as e:
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    # Test autonome du module
    print("🧪 Test autonome du module RAGTester")
    print("Ce module doit être utilisé avec un RAG manager actif")

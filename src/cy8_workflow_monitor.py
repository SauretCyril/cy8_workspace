#!/usr/bin/env python3
"""
Gestionnaire de pile des workflows ComfyUI avec thread d'écoute
"""

import threading
import time
import queue
from dataclasses import dataclass
from typing import Dict, Optional, Callable
from enum import Enum


class WorkflowStatus(Enum):
    """Statuts possibles d'un workflow"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRIEVING_IMAGES = "retrieving_images"
    FINISHED = "finished"


@dataclass
class WorkflowTask:
    """Tâche de workflow dans la pile"""
    prompt_id: int  # ID du prompt dans notre base
    execution_id: str  # ID d'exécution interne
    comfyui_prompt_id: str  # ID retourné par ComfyUI
    status: WorkflowStatus
    prompt_name: str
    timestamp: float
    progress: int = 0
    error_message: Optional[str] = None
    images_count: int = 0
    comfyui_task_instance: Optional[object] = None  # Instance de comfyui_basic_task avec connexion WebSocket
    websocket_connected: bool = False  # Indicateur de connexion WebSocket
    last_progress_update: float = 0  # Timestamp de la dernière mise à jour de progression
    real_time_progress: int = 0  # Progression en temps réel depuis ComfyUI


class WorkflowQueue:
    """Pile de gestion des workflows"""

    def __init__(self):
        self.tasks: Dict[str, WorkflowTask] = {}
        self.lock = threading.Lock()

    def add_task(self, task: WorkflowTask):
        """Ajouter une tâche à la pile"""
        with self.lock:
            self.tasks[task.comfyui_prompt_id] = task
            print(f"📋 Ajout à la pile: {task.comfyui_prompt_id} -> {task.prompt_name}")

    def update_task_status(self, comfyui_prompt_id: str, status: WorkflowStatus,
                          progress: int = None, error_message: str = None):
        """Mettre à jour le statut d'une tâche"""
        with self.lock:
            if comfyui_prompt_id in self.tasks:
                task = self.tasks[comfyui_prompt_id]
                task.status = status
                if progress is not None:
                    task.progress = progress
                if error_message:
                    task.error_message = error_message
                print(f"🔄 Mise à jour pile: {comfyui_prompt_id} -> {status.value} ({progress}%)")
                return task
        return None

    def remove_task(self, comfyui_prompt_id: str) -> Optional[WorkflowTask]:
        """Supprimer une tâche de la pile"""
        with self.lock:
            task = self.tasks.pop(comfyui_prompt_id, None)
            if task:
                print(f"🗑️ Suppression de la pile: {comfyui_prompt_id} -> {task.prompt_name}")
            return task

    def get_task(self, comfyui_prompt_id: str) -> Optional[WorkflowTask]:
        """Récupérer une tâche de la pile"""
        with self.lock:
            return self.tasks.get(comfyui_prompt_id)

    def get_all_tasks(self) -> Dict[str, WorkflowTask]:
        """Récupérer toutes les tâches (copie thread-safe)"""
        with self.lock:
            return self.tasks.copy()

    def clear(self):
        """Vider la pile"""
        with self.lock:
            count = len(self.tasks)
            self.tasks.clear()
            print(f"🧹 Pile vidée: {count} tâches supprimées")


class WorkflowMonitor:
    """Thread d'écoute et de surveillance des workflows ComfyUI"""

    def __init__(self, workflow_queue: WorkflowQueue,
                 status_callback: Callable = None,
                 images_callback: Callable = None,
                 prompt_status_callback: Callable = None,
                 server_failure_callback: Callable = None,
                 root_widget=None,  # Ajout de la référence au widget root pour thread-safety
                 log_callback: Callable = None):  # Nouveau callback pour les logs
        self.workflow_queue = workflow_queue
        self.status_callback = status_callback
        self.images_callback = images_callback
        self.prompt_status_callback = prompt_status_callback  # Nouveau callback pour mettre à jour le statut des prompts
        self.server_failure_callback = server_failure_callback  # Callback pour gérer les pannes serveur
        self.root_widget = root_widget  # Référence au widget root pour root.after()
        self.log_callback = log_callback  # Callback pour envoyer les logs vers l'interface
        self.running = False
        self.thread = None
        self.check_interval = 3  # Vérifier toutes les 3 secondes

        # Gestion des pannes serveur
        self.server_error_count = 0
        self.max_server_errors = 3  # Arrêt après 3 erreurs consécutives
        self.last_server_check = 0
        self.server_check_interval = 10  # Vérification serveur toutes les 10s

        # Statut du monitoring pour visualisation
        self.monitor_status = "Arrêté"  # "Actif", "Arrêté", "Panne serveur"
        self.last_activity = time.time()
        self.workflows_processed = 0
        self.total_images_retrieved = 0

        # WebSocket pour surveillance en temps réel
        self.websocket_threads = {}  # Dict des threads WebSocket actifs par prompt_id

    def start(self):
        """Démarrer le thread de surveillance"""
        if not self.running:
            self.running = True
            self.monitor_status = "Actif"
            self.last_activity = time.time()
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print("🚀 Thread de surveillance des workflows démarré")

    def stop(self):
        """Arrêter le thread de surveillance"""
        if self.running:
            self.running = False
            self.monitor_status = "Arrêté"
            if self.thread:
                self.thread.join(timeout=5)
            print("⏹️ Thread de surveillance des workflows arrêté")

    def get_monitor_status(self) -> Dict:
        """Obtenir le statut du monitoring pour visualisation"""
        return {
            "status": self.monitor_status,
            "running": self.running,
            "last_activity": self.last_activity,
            "workflows_processed": self.workflows_processed,
            "total_images_retrieved": self.total_images_retrieved,
            "active_tasks": len(self.workflow_queue.get_all_tasks()),
            "server_error_count": self.server_error_count,
            "max_server_errors": self.max_server_errors
        }

    def _safe_callback(self, callback, *args, **kwargs):
        """Exécuter un callback de manière thread-safe"""
        if callback and self.root_widget:
            try:
                # Utiliser root.after pour exécuter dans le thread principal
                # Mais seulement si la mainloop est active
                self.root_widget.after(0, lambda: callback(*args, **kwargs))
            except RuntimeError as e:
                if "main thread is not in main loop" in str(e):
                    # Fallback: essayer d'exécuter directement en prenant le risque
                    print(f"⚠️ Mainloop non active, tentative d'exécution directe du callback")
                    try:
                        callback(*args, **kwargs)
                    except Exception as direct_error:
                        print(f"❌ Erreur callback direct: {direct_error}")
                else:
                    raise  # Re-raise si c'est une autre erreur RuntimeError
        elif callback:
            # Si pas de root_widget, essayer d'exécuter directement (risqué)
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"⚠️ Erreur callback direct: {e}")

    def _log_to_interface(self, message):
        """Envoyer un log vers l'interface utilisateur"""
        if self.log_callback:
            self._safe_callback(self.log_callback, message)
        # Toujours garder le print pour la console
        print(message)

    def _start_realtime_monitoring(self, task: WorkflowTask):
        """Démarrer la surveillance en temps réel d'un workflow via WebSocket"""
        def websocket_monitor():
            try:
                self._log_to_interface(f"🔌 Démarrage surveillance WebSocket pour {task.comfyui_prompt_id}")

                # Connecter au WebSocket
                from cy6_websocket_api_client import server_connect, listen_for_progress

                ws = server_connect()
                if not ws:
                    self._log_to_interface(f"❌ Impossible de connecter WebSocket pour {task.comfyui_prompt_id}")
                    return

                task.websocket_connected = True

                def on_progress(prompt_id, percent, node):
                    """Callback appelé lors des mises à jour de progression"""
                    elapsed_time = time.time() - task.timestamp
                    task.real_time_progress = percent
                    task.last_progress_update = time.time()

                    # Mettre à jour le statut avec progression en temps réel
                    status_msg = f"Génération en cours {percent}% (⏱️ {elapsed_time:.1f}s) - Node: {node}"

                    # Callback thread-safe vers l'interface
                    if self.status_callback:
                        self._safe_callback(self.status_callback, task.execution_id, status_msg, percent)

                    self._log_to_interface(f"🔄 Progression temps réel: {task.comfyui_prompt_id} - {percent}% (node: {node})")

                def on_status(prompt_id, status, message):
                    """Callback appelé lors des changements de statut"""
                    elapsed_time = time.time() - task.timestamp

                    if status == "completed":
                        # Workflow terminé, passer à la récupération d'images
                        self.workflow_queue.update_task_status(
                            task.comfyui_prompt_id,
                            WorkflowStatus.COMPLETED,
                            progress=95
                        )

                        status_msg = f"Terminé - Récupération des images (⏱️ {elapsed_time:.1f}s)"
                        if self.status_callback:
                            self._safe_callback(self.status_callback, task.execution_id, status_msg, 95)

                        self._log_to_interface(f"✅ Workflow {task.comfyui_prompt_id} terminé, récupération des images...")

                    elif status == "error":
                        # Erreur d'exécution
                        self.workflow_queue.update_task_status(
                            task.comfyui_prompt_id,
                            WorkflowStatus.FAILED,
                            error_message=message
                        )

                        error_msg = f"Erreur: {message} (⏱️ {elapsed_time:.1f}s)"
                        if self.status_callback:
                            self._safe_callback(self.status_callback, task.execution_id, error_msg, 0)

                        self._log_to_interface(f"❌ Erreur workflow {task.comfyui_prompt_id}: {message}")

                # Écouter les messages WebSocket
                listen_for_progress(ws, task.comfyui_prompt_id, on_progress, on_status)

                # Fermer la connexion
                ws.close()
                task.websocket_connected = False

                self._log_to_interface(f"🔌 Surveillance WebSocket terminée pour {task.comfyui_prompt_id}")

            except Exception as e:
                self._log_to_interface(f"❌ Erreur surveillance WebSocket {task.comfyui_prompt_id}: {e}")
                task.websocket_connected = False
                import traceback
                traceback.print_exc()        # Démarrer le thread de surveillance WebSocket
        thread = threading.Thread(target=websocket_monitor, daemon=True)
        thread.start()
        self.websocket_threads[task.comfyui_prompt_id] = thread

        print(f"🚀 Thread WebSocket démarré pour {task.comfyui_prompt_id}")

    def get_debug_info(self) -> Dict:
        """Obtenir des informations de debug détaillées"""
        tasks = self.workflow_queue.get_all_tasks()
        debug_info = {
            "monitor_status": self.monitor_status,
            "thread_running": self.running,
            "thread_alive": self.thread.is_alive() if self.thread else False,
            "tasks_count": len(tasks),
            "tasks_details": []
        }

        for prompt_id, task in tasks.items():
            elapsed = time.time() - task.timestamp
            debug_info["tasks_details"].append({
                "comfyui_prompt_id": prompt_id,
                "prompt_id": task.prompt_id,
                "status": task.status.value,
                "elapsed_seconds": round(elapsed, 1),
                "progress": task.progress,
                "error_message": task.error_message
            })

        return debug_info

    def _should_check_server(self) -> bool:
        """Vérifier s'il faut tester le serveur"""
        import time
        now = time.time()
        if now - self.last_server_check >= self.server_check_interval:
            self.last_server_check = now
            return True
        return False

    def _check_server_health(self) -> bool:
        """Vérifier si le serveur ComfyUI est accessible"""
        try:
            from cy6_websocket_api_client import get_queue_status

            status = get_queue_status()
            if status is None:
                self.server_error_count += 1
                print(f"⚠️ Serveur ComfyUI inaccessible ({self.server_error_count}/{self.max_server_errors})")

                if self.server_error_count >= self.max_server_errors:
                    print(f"🚨 PANNE SERVEUR DÉTECTÉE - Arrêt du monitoring")
                    self._handle_server_failure()
                    return False
            else:
                # Serveur accessible, reset compteur d'erreurs
                if self.server_error_count > 0:
                    print(f"✅ Serveur ComfyUI redevenu accessible")
                    self.server_error_count = 0

            return True

        except Exception as e:
            self.server_error_count += 1
            print(f"❌ Erreur vérification serveur ({self.server_error_count}/{self.max_server_errors}): {e}")

            if self.server_error_count >= self.max_server_errors:
                print(f"🚨 PANNE SERVEUR DÉTECTÉE - Arrêt du monitoring")
                self._handle_server_failure()
                return False

            return True

    def _handle_server_failure(self):
        """Gérer une panne serveur"""
        print("🛑 GESTION PANNE SERVEUR:")
        print("   📋 Marquage de tous les workflows en erreur")
        print("   🧹 Vidage de la pile de surveillance")

        self.monitor_status = "Panne serveur"

        # Marquer tous les workflows actifs comme en erreur
        tasks = self.workflow_queue.get_all_tasks()
        for comfyui_prompt_id, task in tasks.items():
            if task.status in [WorkflowStatus.QUEUED, WorkflowStatus.RUNNING, WorkflowStatus.COMPLETED]:
                self.workflow_queue.update_task_status(
                    comfyui_prompt_id,
                    WorkflowStatus.FAILED,
                    error_message="Panne serveur ComfyUI"
                )

                # Callback pour l'interface
                if self.status_callback:
                    self._safe_callback(self.status_callback, task.execution_id, "Panne serveur ComfyUI", 0)

                # Callback pour le statut du prompt
                if self.prompt_status_callback:
                    self._safe_callback(self.prompt_status_callback, task.prompt_id, "nok")

        # Vider la pile
        self.workflow_queue.clear()
        print("✅ Gestion de panne serveur terminée")

        # Notifier l'application principale
        if self.server_failure_callback:
            try:
                self._safe_callback(self.server_failure_callback)
                print("📞 Application principale notifiée de la panne serveur")
            except Exception as e:
                print(f"⚠️ Erreur notification panne serveur: {e}")

    def _monitor_loop(self):
        """Boucle principale de surveillance"""
        print("👁️ Démarrage de la boucle de surveillance des workflows")

        while self.running:
            try:
                # Mettre à jour l'activité
                self.last_activity = time.time()

                # Vérification périodique du serveur
                if self._should_check_server():
                    if not self._check_server_health():
                        print("🛑 Arrêt du monitoring suite à panne serveur")
                        break

                self._check_workflows()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ Erreur dans la boucle de surveillance: {e}")
                time.sleep(self.check_interval)

        print("👁️ Arrêt de la boucle de surveillance des workflows")
        self.running = False
        self.monitor_status = "Arrêté"

    def _check_workflows(self):
        """Vérifier tous les workflows en cours"""
        tasks = self.workflow_queue.get_all_tasks()

        if tasks:
            print(f"🔍 Vérification de {len(tasks)} tâches en cours...")

        for comfyui_prompt_id, task in tasks.items():
            try:
                elapsed_time = time.time() - task.timestamp
                print(f"📊 Tâche {comfyui_prompt_id}: {task.status.value} (⏱️ {elapsed_time:.1f}s)")

                if task.status in [WorkflowStatus.QUEUED, WorkflowStatus.RUNNING]:
                    # Démarrer la surveillance WebSocket en temps réel si pas encore fait
                    if not task.websocket_connected and comfyui_prompt_id not in self.websocket_threads:
                        self._start_realtime_monitoring(task)

                    self._check_workflow_status(task)
                elif task.status == WorkflowStatus.COMPLETED:
                    self._retrieve_images(task)
            except Exception as e:
                print(f"❌ Erreur vérification workflow {comfyui_prompt_id}: {e}")
                self.workflow_queue.update_task_status(
                    comfyui_prompt_id,
                    WorkflowStatus.FAILED,
                    error_message=str(e)
                )

    def _check_workflow_status(self, task: WorkflowTask):
        """Vérifier le statut d'un workflow spécifique"""
        try:
            elapsed_time = time.time() - task.timestamp
            print(f"🔍 Vérification statut {task.comfyui_prompt_id} (⏱️ {elapsed_time:.1f}s)")

            # Import des fonctions de vérification
            from cy6_websocket_api_client import workflow_is_running, is_prompt_in_queue, get_queue_status

            # D'abord, obtenir le statut complet de la queue pour debugging
            queue_status = get_queue_status()
            if queue_status:
                pending_count = len(queue_status.get("queue_pending", []))
                running_count = len(queue_status.get("queue_running", []))
                print(f"📋 Queue ComfyUI: {pending_count} en attente, {running_count} en cours")
            else:
                print("⚠️ Impossible d'obtenir le statut de la queue ComfyUI")
                return

            # Vérifier si le workflow est toujours en queue
            in_queue = is_prompt_in_queue(task.comfyui_prompt_id)
            print(f"🔄 Prompt {task.comfyui_prompt_id} en queue: {in_queue}")

            if not in_queue:
                # Le workflow n'est plus en queue, vérifier l'historique pour confirmer
                try:
                    from cy6_websocket_api_client import get_history
                    history = get_history(task.comfyui_prompt_id)
                    if history and task.comfyui_prompt_id in history:
                        print(f"✅ Workflow {task.comfyui_prompt_id} terminé (trouvé dans l'historique)")
                        self.workflow_queue.update_task_status(
                            task.comfyui_prompt_id,
                            WorkflowStatus.COMPLETED,
                            progress=95
                        )

                        # Callback de mise à jour du statut avec temps d'exécution
                        if self.status_callback:
                            status_msg = f"Terminé - Récupération des images (⏱️ {elapsed_time:.1f}s)"
                            self._safe_callback(self.status_callback, task.execution_id, status_msg, 95)
                    else:
                        print(f"⚠️ Workflow {task.comfyui_prompt_id} plus en queue mais pas dans l'historique")
                        # Attendre encore un peu avant de déclarer terminé
                        if elapsed_time > 30:  # Attendre au moins 30 secondes
                            print(f"🕐 Timeout de sécurité atteint, marquage comme terminé")
                            self.workflow_queue.update_task_status(
                                task.comfyui_prompt_id,
                                WorkflowStatus.COMPLETED,
                                progress=95
                            )
                except Exception as hist_error:
                    print(f"⚠️ Erreur vérification historique: {hist_error}")
                    # Fallback: marquer comme terminé s'il n'est plus en queue
                    self.workflow_queue.update_task_status(
                        task.comfyui_prompt_id,
                        WorkflowStatus.COMPLETED,
                        progress=95
                    )

            elif task.status == WorkflowStatus.QUEUED:
                # Toujours en queue, passer en running
                print(f"🔄 Workflow {task.comfyui_prompt_id} en cours d'exécution")
                self.workflow_queue.update_task_status(
                    task.comfyui_prompt_id,
                    WorkflowStatus.RUNNING,
                    progress=50
                )

                # Callback de mise à jour du statut avec temps d'exécution
                if self.status_callback:
                    status_msg = f"Génération en cours (⏱️ {elapsed_time:.1f}s)"
                    self._safe_callback(self.status_callback, task.execution_id, status_msg, 50)

            # Note: Pas de timeout - la surveillance continue tant que le serveur répond
            # Le workflow sera géré par le serveur ComfyUI jusqu'à completion

        except Exception as e:
            print(f"❌ Erreur vérification statut {task.comfyui_prompt_id}: {e}")
            import traceback
            traceback.print_exc()

    def _retrieve_images(self, task: WorkflowTask):
        """Récupérer les images d'un workflow terminé"""
        try:
            elapsed_time = time.time() - task.timestamp
            print(f"📸 Récupération des images pour {task.comfyui_prompt_id} (⏱️ {elapsed_time:.1f}s)")

            # Mettre à jour le statut
            self.workflow_queue.update_task_status(
                task.comfyui_prompt_id,
                WorkflowStatus.RETRIEVING_IMAGES,
                progress=98
            )

            # Callback de mise à jour du statut avec temps d'exécution
            if self.status_callback:
                status_msg = f"Récupération des images (⏱️ {elapsed_time:.1f}s)"
                self._safe_callback(self.status_callback, task.execution_id, status_msg, 98)

            # Vérifier d'abord si des images sont disponibles via l'historique
            try:
                from cy6_websocket_api_client import get_history
                history = get_history(task.comfyui_prompt_id)

                if not history or task.comfyui_prompt_id not in history:
                    print(f"⚠️ Aucun historique trouvé pour {task.comfyui_prompt_id}")
                    # Attendre un peu que l'historique soit disponible
                    time.sleep(2)
                    history = get_history(task.comfyui_prompt_id)

                if history and task.comfyui_prompt_id in history:
                    prompt_history = history[task.comfyui_prompt_id]
                    outputs = prompt_history.get("outputs", {})
                    print(f"📊 Historique trouvé avec {len(outputs)} nœuds de sortie")
                else:
                    print(f"❌ Impossible de récupérer l'historique pour {task.comfyui_prompt_id}")

            except Exception as hist_error:
                print(f"⚠️ Erreur vérification historique pour images: {hist_error}")

            # Récupérer les images avec ComfyUI
            # Utiliser l'instance stockée avec la connexion WebSocket si disponible
            if task.comfyui_task_instance and hasattr(task.comfyui_task_instance, 'ws') and task.comfyui_task_instance.ws:
                print(f"✅ Utilisation de l'instance ComfyUI avec connexion WebSocket existante")
                tsk1 = task.comfyui_task_instance
            else:
                print(f"⚠️ Création d'une nouvelle instance ComfyUI")
                from cy6_wkf001_Basic import comfyui_basic_task
                tsk1 = comfyui_basic_task()

                # Établir une connexion WebSocket obligatoire pour GetImages
                try:
                    from cy6_websocket_api_client import server_connect
                    tsk1.ws = server_connect()
                    print(f"✅ Connexion WebSocket établie pour récupération images")
                except Exception as ws_error:
                    print(f"❌ Impossible d'établir une connexion WebSocket: {ws_error}")
                    # Sans WebSocket, on ne peut pas récupérer les images
                    raise Exception(f"WebSocket requis pour GetImages: {ws_error}")

            print(f"🔍 Tentative de récupération des images avec GetImages({task.comfyui_prompt_id})")

            # Vérifier que l'instance a bien un WebSocket
            if not hasattr(tsk1, 'ws') or not tsk1.ws:
                raise Exception("Instance ComfyUI sans WebSocket valide")

            output_images = tsk1.GetImages(task.comfyui_prompt_id)

            # Debug des images récupérées
            if output_images:
                print(f"📊 Type d'images récupérées: {type(output_images)}")
                if isinstance(output_images, list):
                    print(f"📊 Nombre d'images dans la liste: {len(output_images)}")
                    for i, img in enumerate(output_images[:3]):  # Afficher seulement les 3 premières
                        print(f"📊 Image {i}: {type(img)} - {img if isinstance(img, str) else 'objet binaire'}")

            if output_images:
                task.images_count = len(output_images)
                self.total_images_retrieved += len(output_images)  # Statistiques
                print(f"✅ {len(output_images)} images récupérées pour {task.comfyui_prompt_id}")

                # Callback pour traiter les images
                if self.images_callback:
                    def safe_images_callback():
                        try:
                            images_added = self.images_callback(task.prompt_id, output_images)
                            print(f"💾 {images_added} images ajoutées à la base de données")
                        except Exception as img_callback_error:
                            print(f"❌ Erreur lors de l'ajout des images à la base: {img_callback_error}")
                            import traceback
                            traceback.print_exc()

                    self._safe_callback(safe_images_callback)

                # Statut final avec succès et temps d'exécution
                final_status = f"Terminé avec succès - {len(output_images)} images (⏱️ {elapsed_time:.1f}s)"

                # Callback de mise à jour du statut
                if self.status_callback:
                    self._safe_callback(self.status_callback, task.execution_id, final_status, 100)

                # Callback de mise à jour du statut du prompt
                if self.prompt_status_callback:
                    self._safe_callback(self.prompt_status_callback, task.prompt_id, "ok")

            else:
                print(f"⚠️ Aucune image récupérée pour {task.comfyui_prompt_id}")
                final_status = f"Terminé - Aucune image générée (⏱️ {elapsed_time:.1f}s)"

                # Callback de mise à jour du statut
                if self.status_callback:
                    self._safe_callback(self.status_callback, task.execution_id, final_status, 100)

                # Callback de mise à jour du statut du prompt
                if self.prompt_status_callback:
                    self._safe_callback(self.prompt_status_callback, task.prompt_id, "ok")

            # Incrémenter le compteur de workflows traités
            self.workflows_processed += 1

            # Marquer comme terminé et supprimer de la pile
            self.workflow_queue.update_task_status(
                task.comfyui_prompt_id,
                WorkflowStatus.FINISHED,
                progress=100
            )

            # Supprimer de la pile après un délai
            time.sleep(2)  # Laisser le temps à l'UI de se mettre à jour
            self.workflow_queue.remove_task(task.comfyui_prompt_id)

            print(f"🎉 Workflow {task.comfyui_prompt_id} traitement terminé (⏱️ {elapsed_time:.1f}s)")

        except Exception as e:
            elapsed_time = time.time() - task.timestamp
            print(f"❌ Erreur récupération images {task.comfyui_prompt_id}: {e}")
            import traceback
            traceback.print_exc()

            self.workflow_queue.update_task_status(
                task.comfyui_prompt_id,
                WorkflowStatus.FAILED,
                error_message=f"Erreur récupération images: {str(e)}"
            )

            # Callback de mise à jour du statut avec temps d'exécution
            if self.status_callback:
                error_msg = f"Erreur images: {str(e)} (⏱️ {elapsed_time:.1f}s)"
                self._safe_callback(self.status_callback, task.execution_id, error_msg, 0)

            # Callback de mise à jour du statut du prompt en cas d'erreur
            if self.prompt_status_callback:
                self._safe_callback(self.prompt_status_callback, task.prompt_id, "nok")

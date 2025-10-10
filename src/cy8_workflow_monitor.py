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
                 prompt_status_callback: Callable = None):
        self.workflow_queue = workflow_queue
        self.status_callback = status_callback
        self.images_callback = images_callback
        self.prompt_status_callback = prompt_status_callback  # Nouveau callback pour mettre à jour le statut des prompts
        self.running = False
        self.thread = None
        self.check_interval = 3  # Vérifier toutes les 3 secondes

    def start(self):
        """Démarrer le thread de surveillance"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print("🚀 Thread de surveillance des workflows démarré")

    def stop(self):
        """Arrêter le thread de surveillance"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            print("⏹️ Thread de surveillance des workflows arrêté")

    def _monitor_loop(self):
        """Boucle principale de surveillance"""
        print("👁️ Démarrage de la boucle de surveillance des workflows")

        while self.running:
            try:
                self._check_workflows()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ Erreur dans la boucle de surveillance: {e}")
                time.sleep(self.check_interval)

        print("👁️ Arrêt de la boucle de surveillance des workflows")

    def _check_workflows(self):
        """Vérifier tous les workflows en cours"""
        tasks = self.workflow_queue.get_all_tasks()

        for comfyui_prompt_id, task in tasks.items():
            try:
                if task.status in [WorkflowStatus.QUEUED, WorkflowStatus.RUNNING]:
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
            # Import des fonctions de vérification
            from cy6_websocket_api_client import workflow_is_running, is_prompt_in_queue

            # Vérifier si le workflow est toujours en queue
            in_queue = is_prompt_in_queue(task.comfyui_prompt_id)

            if not in_queue:
                # Le workflow n'est plus en queue, il est soit terminé soit en erreur
                print(f"✅ Workflow {task.comfyui_prompt_id} terminé (plus en queue)")
                self.workflow_queue.update_task_status(
                    task.comfyui_prompt_id,
                    WorkflowStatus.COMPLETED,
                    progress=95
                )

                # Callback de mise à jour du statut
                if self.status_callback:
                    self.status_callback(task.execution_id, "Terminé - Récupération des images", 95)

            elif task.status == WorkflowStatus.QUEUED:
                # Toujours en queue, passer en running
                print(f"🔄 Workflow {task.comfyui_prompt_id} en cours d'exécution")
                self.workflow_queue.update_task_status(
                    task.comfyui_prompt_id,
                    WorkflowStatus.RUNNING,
                    progress=50
                )

                # Callback de mise à jour du statut
                if self.status_callback:
                    self.status_callback(task.execution_id, "Génération en cours", 50)

            # Vérifier le timeout (10 minutes max)
            elapsed = time.time() - task.timestamp
            if elapsed > 600:  # 10 minutes
                print(f"⏱️ Timeout workflow {task.comfyui_prompt_id} ({elapsed:.1f}s)")
                self.workflow_queue.update_task_status(
                    task.comfyui_prompt_id,
                    WorkflowStatus.FAILED,
                    error_message="Timeout - Workflow trop long"
                )

                # Callback de mise à jour du statut
                if self.status_callback:
                    self.status_callback(task.execution_id, "Timeout - Workflow trop long", 0)

                # Callback de mise à jour du statut du prompt en cas de timeout
                if self.prompt_status_callback:
                    self.prompt_status_callback(task.prompt_id, "nok")

        except Exception as e:
            print(f"❌ Erreur vérification statut {task.comfyui_prompt_id}: {e}")

    def _retrieve_images(self, task: WorkflowTask):
        """Récupérer les images d'un workflow terminé"""
        try:
            print(f"📸 Récupération des images pour {task.comfyui_prompt_id}")

            # Mettre à jour le statut
            self.workflow_queue.update_task_status(
                task.comfyui_prompt_id,
                WorkflowStatus.RETRIEVING_IMAGES,
                progress=98
            )

            # Callback de mise à jour du statut
            if self.status_callback:
                self.status_callback(task.execution_id, "Récupération des images", 98)

            # Récupérer les images avec ComfyUI
            # Utiliser l'instance stockée avec la connexion WebSocket si disponible
            if task.comfyui_task_instance and hasattr(task.comfyui_task_instance, 'ws') and task.comfyui_task_instance.ws:
                print(f"✅ Utilisation de l'instance ComfyUI avec connexion WebSocket existante")
                tsk1 = task.comfyui_task_instance
            else:
                print(f"⚠️ Création d'une nouvelle instance ComfyUI (pas de WebSocket)")
                from cy6_wkf001_Basic import comfyui_basic_task
                tsk1 = comfyui_basic_task()
                # Essayer d'établir une connexion WebSocket
                try:
                    from cy6_websocket_api_client import server_connect
                    tsk1.ws = server_connect()
                    print(f"✅ Nouvelle connexion WebSocket établie")
                except Exception as ws_error:
                    print(f"⚠️ Impossible d'établir une connexion WebSocket: {ws_error}")
                    # Fallback vers l'API REST si besoin
                    tsk1.ws = None

            output_images = tsk1.GetImages(task.comfyui_prompt_id)

            if output_images:
                task.images_count = len(output_images)
                print(f"✅ {len(output_images)} images récupérées pour {task.comfyui_prompt_id}")

                # Callback pour traiter les images
                if self.images_callback:
                    images_added = self.images_callback(task.prompt_id, output_images)
                    print(f"💾 {images_added} images ajoutées à la base de données")

                # Statut final avec succès
                final_status = f"Terminé avec succès - {len(output_images)} images générées"

                # Callback de mise à jour du statut
                if self.status_callback:
                    self.status_callback(task.execution_id, final_status, 100)

                # Callback de mise à jour du statut du prompt
                if self.prompt_status_callback:
                    self.prompt_status_callback(task.prompt_id, "ok")

            else:
                print(f"⚠️ Aucune image récupérée pour {task.comfyui_prompt_id}")
                final_status = "Terminé - Aucune image générée"

                # Callback de mise à jour du statut
                if self.status_callback:
                    self.status_callback(task.execution_id, final_status, 100)

                # Callback de mise à jour du statut du prompt
                if self.prompt_status_callback:
                    self.prompt_status_callback(task.prompt_id, "ok")            # Marquer comme terminé et supprimer de la pile
            self.workflow_queue.update_task_status(
                task.comfyui_prompt_id,
                WorkflowStatus.FINISHED,
                progress=100
            )

            # Supprimer de la pile après un délai
            time.sleep(2)  # Laisser le temps à l'UI de se mettre à jour
            self.workflow_queue.remove_task(task.comfyui_prompt_id)

        except Exception as e:
            print(f"❌ Erreur récupération images {task.comfyui_prompt_id}: {e}")
            self.workflow_queue.update_task_status(
                task.comfyui_prompt_id,
                WorkflowStatus.FAILED,
                error_message=f"Erreur récupération images: {str(e)}"
            )

            # Callback de mise à jour du statut
            if self.status_callback:
                self.status_callback(task.execution_id, f"Erreur images: {str(e)}", 0)

            # Callback de mise à jour du statut du prompt en cas d'erreur
            if self.prompt_status_callback:
                self.prompt_status_callback(task.prompt_id, "nok")

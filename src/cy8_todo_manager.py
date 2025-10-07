#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire TODO/Focus intégré au RAG
Permet de maintenir une liste de tâches avec focus et historique
"""

import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import logging

class RAGTodoManager:
    """Gestionnaire de tâches TODO intégré au RAG"""
    
    def __init__(self, db_path: str, environment_id: str):
        self.db_path = db_path
        self.environment_id = environment_id
        self.logger = logging.getLogger(__name__)
        self.current_focus_id = None
        self.chat_history_backup = []
        
        # Initialiser la base de données
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialiser les tables TODO"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table des tâches TODO
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_todos (
                    id TEXT PRIMARY KEY,
                    environment_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 3,
                    context_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL
                )
            """)
            
            # Table de l'historique des focus
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_focus_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    environment_id TEXT NOT NULL,
                    todo_id TEXT,
                    chat_history_backup TEXT,
                    focus_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    focus_ended_at TIMESTAMP NULL,
                    FOREIGN KEY (todo_id) REFERENCES rag_todos (id) ON DELETE CASCADE
                )
            """)
            
            # Table des sessions de travail
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_work_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    environment_id TEXT NOT NULL,
                    todo_id TEXT,
                    session_notes TEXT,
                    duration_minutes INTEGER,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP NULL,
                    FOREIGN KEY (todo_id) REFERENCES rag_todos (id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.info("✅ Base TODO RAG initialisée")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation TODO: {e}")
    
    def add_todo(self, title: str, description: str = "", priority: int = 3, context_data: Dict = None) -> str:
        """Ajouter une nouvelle tâche TODO"""
        try:
            todo_id = str(uuid.uuid4())[:8]  # ID court
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO rag_todos (id, environment_id, title, description, priority, context_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                todo_id,
                self.environment_id,
                title,
                description,
                priority,
                json.dumps(context_data) if context_data else None
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"✅ TODO ajouté: {todo_id} - {title}")
            return todo_id
            
        except Exception as e:
            self.logger.error(f"❌ Erreur ajout TODO: {e}")
            return None
    
    def get_todos(self, status: str = None) -> List[Dict]:
        """Récupérer la liste des TODOs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if status:
                cursor.execute("""
                    SELECT id, title, description, status, priority, created_at, updated_at
                    FROM rag_todos
                    WHERE environment_id = ? AND status = ?
                    ORDER BY priority DESC, created_at ASC
                """, (self.environment_id, status))
            else:
                cursor.execute("""
                    SELECT id, title, description, status, priority, created_at, updated_at
                    FROM rag_todos
                    WHERE environment_id = ?
                    ORDER BY priority DESC, created_at ASC
                """, (self.environment_id,))
            
            todos = []
            for row in cursor.fetchall():
                todos.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'status': row[3],
                    'priority': row[4],
                    'created_at': row[5],
                    'updated_at': row[6]
                })
            
            conn.close()
            return todos
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération TODOs: {e}")
            return []
    
    def start_focus(self, todo_id: str, chat_history: List = None) -> bool:
        """Démarrer le mode focus sur une tâche"""
        try:
            # Vérifier que la tâche existe
            todo = self.get_todo_by_id(todo_id)
            if not todo:
                return False
            
            # Sauvegarder l'historique actuel
            if chat_history:
                self.chat_history_backup = chat_history.copy()
            
            # Enregistrer le début du focus
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO rag_focus_history (environment_id, todo_id, chat_history_backup)
                VALUES (?, ?, ?)
            """, (
                self.environment_id,
                todo_id,
                json.dumps(self.chat_history_backup) if self.chat_history_backup else None
            ))
            
            conn.commit()
            conn.close()
            
            self.current_focus_id = todo_id
            self.logger.info(f"🎯 Mode focus activé sur TODO: {todo_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage focus: {e}")
            return False
    
    def end_focus(self, session_notes: str = "") -> bool:
        """Terminer le mode focus"""
        try:
            if not self.current_focus_id:
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Mettre à jour l'historique du focus
            cursor.execute("""
                UPDATE rag_focus_history 
                SET focus_ended_at = CURRENT_TIMESTAMP
                WHERE environment_id = ? AND todo_id = ? AND focus_ended_at IS NULL
            """, (self.environment_id, self.current_focus_id))
            
            # Ajouter une session de travail si des notes sont fournies
            if session_notes:
                cursor.execute("""
                    INSERT INTO rag_work_sessions (environment_id, todo_id, session_notes, ended_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (self.environment_id, self.current_focus_id, session_notes))
            
            conn.commit()
            conn.close()
            
            focused_todo = self.current_focus_id
            self.current_focus_id = None
            
            self.logger.info(f"🏁 Mode focus terminé pour TODO: {focused_todo}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur fin focus: {e}")
            return False
    
    def get_current_focus(self) -> Optional[str]:
        """Obtenir l'ID de la tâche actuellement en focus"""
        return self.current_focus_id
    
    def get_todo_by_id(self, todo_id: str) -> Optional[Dict]:
        """Récupérer une tâche par son ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, description, status, priority, context_data, created_at, updated_at
                FROM rag_todos
                WHERE environment_id = ? AND id = ?
            """, (self.environment_id, todo_id))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                context_data = None
                if row[5]:
                    try:
                        context_data = json.loads(row[5])
                    except:
                        pass
                
                return {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'status': row[3],
                    'priority': row[4],
                    'context_data': context_data,
                    'created_at': row[6],
                    'updated_at': row[7]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération TODO {todo_id}: {e}")
            return None
    
    def update_todo_status(self, todo_id: str, status: str) -> bool:
        """Mettre à jour le statut d'une tâche"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            completed_at = "CURRENT_TIMESTAMP" if status == "completed" else "NULL"
            
            cursor.execute(f"""
                UPDATE rag_todos 
                SET status = ?, updated_at = CURRENT_TIMESTAMP, completed_at = {completed_at}
                WHERE environment_id = ? AND id = ?
            """, (status, self.environment_id, todo_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if success:
                self.logger.info(f"✅ TODO {todo_id} mis à jour: {status}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour TODO {todo_id}: {e}")
            return False
    
    def restore_chat_history(self) -> List:
        """Restaurer l'historique de chat sauvegardé"""
        try:
            if not self.current_focus_id:
                # Chercher le dernier focus
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT chat_history_backup FROM rag_focus_history
                    WHERE environment_id = ? AND chat_history_backup IS NOT NULL
                    ORDER BY focus_started_at DESC LIMIT 1
                """, (self.environment_id,))
                
                row = cursor.fetchone()
                conn.close()
                
                if row and row[0]:
                    try:
                        return json.loads(row[0])
                    except:
                        pass
            
            return self.chat_history_backup.copy() if self.chat_history_backup else []
            
        except Exception as e:
            self.logger.error(f"❌ Erreur restauration historique: {e}")
            return []
    
    def get_focus_context(self) -> str:
        """Obtenir le contexte du focus actuel"""
        if not self.current_focus_id:
            return "🔍 Aucun focus actif. Utilisez '/focus <id>' pour vous concentrer sur une tâche."
        
        todo = self.get_todo_by_id(self.current_focus_id)
        if not todo:
            return "❌ Tâche de focus introuvable."
        
        context = f"🎯 **MODE FOCUS ACTIF**\n\n"
        context += f"**ID:** {todo['id']}\n"
        context += f"**Tâche:** {todo['title']}\n"
        context += f"**Description:** {todo['description']}\n"
        context += f"**Priorité:** {todo['priority']}/5\n"
        context += f"**Statut:** {todo['status']}\n\n"
        context += f"💡 *Concentrez-vous uniquement sur cette tâche. Utilisez '/end-focus' pour terminer.*"
        
        return context
    
    def format_todos_list(self, todos: List[Dict]) -> str:
        """Formater la liste des TODOs pour affichage"""
        if not todos:
            return "📝 Aucune tâche TODO trouvée."
        
        output = "📋 **LISTE DES TÂCHES TODO**\n\n"
        
        # Grouper par statut
        pending = [t for t in todos if t['status'] == 'pending']
        in_progress = [t for t in todos if t['status'] == 'in_progress']
        completed = [t for t in todos if t['status'] == 'completed']
        
        def format_todo_item(todo):
            priority_icons = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🔵"}
            priority_icon = priority_icons.get(todo['priority'], "⚪")
            
            return f"  {priority_icon} **{todo['id']}** - {todo['title']}\n    {todo['description'][:50]}{'...' if len(todo['description']) > 50 else ''}\n"
        
        if pending:
            output += "⏳ **EN ATTENTE**\n"
            for todo in pending:
                output += format_todo_item(todo)
            output += "\n"
        
        if in_progress:
            output += "🚀 **EN COURS**\n"
            for todo in in_progress:
                output += format_todo_item(todo)
            output += "\n"
        
        if completed:
            output += "✅ **TERMINÉES**\n"
            for todo in completed[:3]:  # Limiter les terminées affichées
                output += format_todo_item(todo)
            if len(completed) > 3:
                output += f"    ... et {len(completed) - 3} autres tâches terminées\n"
            output += "\n"
        
        output += "💡 **Commandes:** `/focus <id>` - `/todo add <titre>` - `/todo done <id>` - `/todo list`"
        
        return output
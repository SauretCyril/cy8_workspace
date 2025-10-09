import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import json
import subprocess
from datetime import datetime
from PIL import Image, ImageTk
from typing import List, Dict, Optional

def center_window(window, width=None, height=None):
    """Centrer une fenêtre sur l'écran"""
    # Mettre à jour la fenêtre pour obtenir les bonnes dimensions
    window.update_idletasks()

    # Obtenir les dimensions de la fenêtre
    if width is None:
        width = window.winfo_reqwidth()
    if height is None:
        height = window.winfo_reqheight()

    # Obtenir les dimensions de l'écran
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculer la position pour centrer
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Appliquer la géométrie
    window.geometry(f"{width}x{height}+{x}+{y}")

# Import du gestionnaire RAG
try:
    from cy8_rag_manager import RAGManager
    from cy8_temporal_rag import TemporalRAGManager
    from cy8_rag_tester import RAGTester
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAGManager non disponible")

# Import du gestionnaire d'identifiants de popups
try:
    from cy8_popup_id_manager import popup_manager, get_popup_id, close_popup
except ImportError:
    # Fallback en cas d'absence du module
    def get_popup_id(title, popup_type="dialog"):
        return f"popup_{id(title)}", title
    def close_popup(popup_id):
        pass
    popup_manager = None

# Import conditionnel de safetensors (optionnel)
try:
    from safetensors.torch import safe_open

    SAFETENSORS_AVAILABLE = True
except ImportError:
    SAFETENSORS_AVAILABLE = False
    safe_open = None

from cy8_database_manager import cy8_database_manager
from cy8_popup_manager import cy8_popup_manager
from cy8_editable_tables import cy8_editable_tables
from cy8_user_preferences import cy8_user_preferences
from cy8_paths import normalize_path, ensure_dir, get_default_db_path, cy8_paths_manager
from cy6_wkf001_Basic import comfyui_basic_task
from cy8_log_analyzer import cy8_log_analyzer
from cy8_mistral import analyze_comfyui_error, save_error_solution, load_error_solution

# Nouveaux imports pour l'optimisation des images
from cy8_image_index_manager import ImageIndexManager
from cy8_fast_image_processor import get_image_processor


class cy8_prompts_manager:
    """Gestionnaire principal des prompts - Version cy8 refactorisée"""

    def __init__(self, root=None, db_path=None, mode="dev"):
        self.root = root or tk.Tk()

        # Gestionnaire des préférences utilisateur
        self.user_prefs = cy8_user_preferences()

        # Déterminer le chemin de la base de données
        if db_path is None:
            # Utiliser la dernière base utilisée ou le chemin par défaut
            last_db = self.user_prefs.get_last_database_path()
            if last_db and os.path.exists(last_db):
                self.db_path = normalize_path(last_db)
                print(f"Utilisation de la dernière base: {self.db_path}")
            else:
                self.db_path = get_default_db_path()
                print(f"Utilisation de la base par défaut: {self.db_path}")
        else:
            self.db_path = normalize_path(db_path)

        # Gestionnaires
        self.db_manager = cy8_database_manager(self.db_path)
        self.popup_manager = cy8_popup_manager(self.root, self.db_manager)
        self.table_manager = cy8_editable_tables(self.root, self.popup_manager)

        # Variables d'état
        self.selected_prompt_id = None
        self.execution_stack = []
        self.current_values_tree = None
        self.current_workflow_tree = None
        self.executions_tree = None  # Référence au TreeView des exécutions
        self.environments_tree = None  # Référence au TreeView des environnements
        self.filters_list = []  # Liste des filtres actifs

        # Variable pour l'environnement identifié
        self.current_environment_id = None

        # Gestionnaire RAG pour l'analyse intelligente (après définition de current_environment_id)
        self.rag_manager = None
        self.temporal_rag = None
        self.rag_tester = None
        if RAG_AVAILABLE:
            try:
                # Utiliser un environnement par défaut si aucun n'est défini
                default_env_id = self.current_environment_id or "default_workspace"

                self.rag_manager = RAGManager(self.db_manager, default_env_id)
                self.temporal_rag = TemporalRAGManager(self.rag_manager)
                self.rag_tester = RAGTester(self.rag_manager, self.db_manager)
                print("🧠 Gestionnaire RAG initialisé")
                print(f"🏷️ Environnement RAG: {default_env_id}")
                print("🕒 Extension RAG temporelle activée")
                print("🧪 Testeur RAG initialisé")
            except Exception as e:
                print(f"⚠️ Erreur initialisation RAG: {e}")
                self.rag_manager = None
                self.temporal_rag = None
                self.rag_tester = None

        # Gestionnaire d'index d'images optimisé
        self.image_index = ImageIndexManager()
        self.fast_processor = get_image_processor()
        print(
            f"🖼️ Processeur d'images: {self.fast_processor.get_performance_info()['backend']}"
        )

        # Connecter le callback de sauvegarde
        self.table_manager.set_save_callback(self.save_current_info)

        # Variables pour la gestion des répertoires d'images
        self.init_images_paths()

        # Configuration de l'interface
        self.setup_main_window()
        self.setup_ui()

        # Raccourcis clavier
        self.root.bind("<Control-s>", lambda e: self.save_current_info())

        # Initialisation
        self.db_manager.init_database(mode)
        self.load_prompts()
        self.update_database_stats()

        # NOUVEAU: Restaurer l'environnement sauvegardé
        self.restore_saved_environment()

        # Initialiser le tableau des environnements après la création de l'interface
        self.root.after(100, self.refresh_environments)

    def restore_saved_environment(self):
        """Restaurer l'environnement sauvegardé depuis les préférences"""
        try:
            saved_env_id = self.user_prefs.get_preference("current_environment_id")
            if saved_env_id:
                print(f"🔄 Restauration de l'environnement: {saved_env_id}")
                self.current_environment_id = saved_env_id

                # Synchroniser le RAG avec l'environnement restauré
                if hasattr(self, 'rag_manager') and self.rag_manager:
                    if self.rag_manager.environment_id != saved_env_id:
                        print(f"🔄 Synchronisation RAG: {self.rag_manager.environment_id} -> {saved_env_id}")
                        self.rag_manager.environment_id = saved_env_id
                        self.rag_manager._initialize_components()
                        print("✅ RAG synchronisé avec l'environnement restauré")

                print(f"✅ Environnement restauré: {saved_env_id}")

                # Mettre à jour le message de bienvenue pour indiquer l'environnement restauré
                self.update_chat_welcome_message(f"✅ Environnement restauré: {saved_env_id}")
            else:
                print("ℹ️  Aucun environnement sauvegardé")
                self.update_chat_welcome_message("⚠️ Aucun environnement sauvegardé - Identification requise")
        except Exception as e:
            print(f"⚠️ Erreur lors de la restauration de l'environnement: {e}")

    def update_chat_welcome_message(self, status_message):
        """Mettre à jour le message de bienvenue avec le statut de l'environnement"""
        try:
            if hasattr(self, 'chat_history'):
                # Différer l'update pour que l'interface soit complètement chargée
                self.root.after(500, lambda: self.add_chat_message("system", status_message))
        except Exception as e:
            print(f"⚠️ Erreur mise à jour chat: {e}")

    def add_startup_environment_message(self, env_id):
        """Ajouter un message de démarrage sur l'environnement restauré - DEPRECATED"""
        pass

    def add_no_environment_message(self):
        """Ajouter un message quand aucun environnement n'est sauvegardé - DEPRECATED"""
        pass

    def init_images_paths(self):
        """Initialiser le chemin du répertoire d'images depuis le fichier .env"""
        # Charger depuis la variable d'environnement ou utiliser la valeur par défaut ComfyUI
        default_comfyui_path = "E:/Comfyui_G11/ComfyUI/output"

        # IMAGES_COLLECTE depuis .env (ou valeur par défaut)
        images_path = os.getenv("IMAGES_COLLECTE") or default_comfyui_path

        # S'assurer que la variable d'environnement est définie
        os.environ["IMAGES_COLLECTE"] = images_path

    def setup_main_window(self):
        """Configuration de la fenêtre principale"""
        self.root.title("Gestionnaire de Prompts ComfyUI - Version cy8")

        # Restaurer la géométrie de la fenêtre ou utiliser par défaut
        saved_geometry = self.user_prefs.get_window_geometry()
        if saved_geometry:
            try:
                self.root.geometry(saved_geometry)
                print(f"Géométrie restaurée: {saved_geometry}")
            except:
                self.root.geometry("1400x900")
        else:
            self.root.geometry("1400x900")

        self.root.minsize(1200, 800)

        # Style professionnel
        style = ttk.Style()
        style.theme_use("clam")

        # Configuration des couleurs et styles
        style.configure("Title.TLabel", font=("TkDefaultFont", 12, "bold"))
        style.configure("Header.TFrame", relief="raised", borderwidth=1)

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Menu principal
        self.create_menu()

        # Ruban de boutons en haut
        self.setup_ribbon()

        # Layout principal avec panneau horizontal
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Panneau gauche - Tableau des prompts (0)
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Panneau droit - Détails (1)
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        # Configuration des panneaux
        self.setup_prompts_table(left_frame)  # 0) Tableau des prompts
        self.setup_details_panel(right_frame)  # 1) Panel détaillé

        # Barre de statut
        self.setup_status_bar()

    def create_menu(self):
        """Créer la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau prompt", command=self.new_prompt)
        file_menu.add_separator()

        # Sous-menu Base de données
        db_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Base de données", menu=db_menu)
        db_menu.add_command(label="Changer de base...", command=self.change_database)
        db_menu.add_command(
            label="Créer nouvelle base...", command=self.create_new_database
        )
        db_menu.add_separator()

        # Bases récentes
        self.recent_db_menu = tk.Menu(db_menu, tearoff=0)
        db_menu.add_cascade(label="Bases récentes", menu=self.recent_db_menu)
        self.update_recent_databases_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Importer JSON", command=self.import_json)
        file_menu.add_command(label="Exporter JSON", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)

        # Menu Édition
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        edit_menu.add_command(label="Hériter prompt", command=self.inherit_prompt)
        edit_menu.add_command(label="Supprimer", command=self.delete_prompt)

        # Menu Exécution
        exec_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exécution", menu=exec_menu)
        exec_menu.add_command(label="Exécuter prompt", command=self.execute_workflow)
        exec_menu.add_command(
            label="Analyser prompt", command=self.open_prompt_analysis
        )

        # Menu Maintenance RAG
        maintenance_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 Maintenance", menu=maintenance_menu)
        maintenance_menu.add_command(
            label="🗑️ Réinitialiser RAG complet",
            command=self.reset_rag_completely
        )
        maintenance_menu.add_command(
            label="🧹 Nettoyer environnements custom",
            command=self.clean_custom_environments
        )
        maintenance_menu.add_command(
            label="🔬 Test efficacité RAG",
            command=self.test_rag_efficiency
        )

    def setup_ribbon(self):
        """Configuration du ruban de boutons style Microsoft Office"""
        # Conteneur principal du ruban
        ribbon_frame = ttk.Frame(self.root)
        ribbon_frame.pack(fill="x", padx=5, pady=(5, 0))

        # Style pour le ruban
        style = ttk.Style()
        style.configure(
            "Ribbon.TFrame", relief="raised", borderwidth=2, background="#f0f0f0"
        )
        style.configure(
            "RibbonButton.TButton", padding=(5, 3), font=("TkDefaultFont", 9)
        )
        style.configure(
            "RibbonMain.TButton", padding=(8, 5), font=("TkDefaultFont", 9, "bold")
        )

        # Frame principal du ruban avec style
        main_ribbon = ttk.Frame(ribbon_frame, style="Ribbon.TFrame", padding="3")
        main_ribbon.pack(fill="x")

        # === GROUPE FICHIER ===
        file_group = ttk.LabelFrame(main_ribbon, text="Fichier", padding="5")
        file_group.pack(side="left", fill="y", padx=2)

        # Boutons du groupe Fichier (en colonne pour style ruban)
        file_buttons_frame = ttk.Frame(file_group)
        file_buttons_frame.pack()

        # Nouveau (bouton principal, plus grand)
        new_btn = ttk.Button(
            file_buttons_frame,
            text="✚ Nouveau",
            command=self.new_prompt,
            style="RibbonMain.TButton",
            width=16,
        )
        new_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=1)

        # Éditer et Hériter (côte à côte)
        ttk.Button(
            file_buttons_frame,
            text="✏️ Éditer",
            command=self.edit_prompt,
            style="RibbonButton.TButton",
            width=8,
        ).grid(row=1, column=0, padx=1, pady=1)
        ttk.Button(
            file_buttons_frame,
            text="📋 Hériter",
            command=self.inherit_prompt,
            style="RibbonButton.TButton",
            width=8,
        ).grid(row=1, column=1, padx=1, pady=1)

        # Supprimer (rouge)
        style.configure("Danger.TButton", foreground="red", padding=(5, 3))
        ttk.Button(
            file_buttons_frame,
            text="🗑️ Supprimer",
            command=self.delete_prompt,
            style="Danger.TButton",
            width=16,
        ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=1)

        # Séparateur vertical
        ttk.Separator(main_ribbon, orient="vertical").pack(
            side="left", fill="y", padx=5
        )

        # === GROUPE EXÉCUTION ===
        exec_group = ttk.LabelFrame(main_ribbon, text="Exécution", padding="5")
        exec_group.pack(side="left", fill="y", padx=2)

        exec_buttons_frame = ttk.Frame(exec_group)
        exec_buttons_frame.pack()

        # Exécuter (bouton principal)
        ttk.Button(
            exec_buttons_frame,
            text="▶️ Exécuter",
            command=self.execute_workflow,
            style="RibbonMain.TButton",
            width=16,
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=1)

        # Analyser
        ttk.Button(
            exec_buttons_frame,
            text="🔍 Analyser",
            command=self.open_prompt_analysis,
            style="RibbonButton.TButton",
            width=16,
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=1)

        # Séparateur vertical
        ttk.Separator(main_ribbon, orient="vertical").pack(
            side="left", fill="y", padx=5
        )

        # === GROUPE AFFICHAGE ===
        view_group = ttk.LabelFrame(main_ribbon, text="Affichage", padding="5")
        view_group.pack(side="left", fill="y", padx=2)

        view_buttons_frame = ttk.Frame(view_group)
        view_buttons_frame.pack()

        # Actualiser
        ttk.Button(
            view_buttons_frame,
            text="🔄 Actualiser",
            command=self.refresh_prompts_display,
            style="RibbonButton.TButton",
            width=16,
        ).grid(row=0, column=0, sticky="ew", pady=1)

        # Filtres (raccourci)
        ttk.Button(
            view_buttons_frame,
            text="🔽 Filtres",
            command=self.toggle_filters_tab,
            style="RibbonButton.TButton",
            width=16,
        ).grid(row=1, column=0, sticky="ew", pady=1)

        # Séparateur vertical
        ttk.Separator(main_ribbon, orient="vertical").pack(
            side="left", fill="y", padx=5
        )

        # === GROUPE BASE DE DONNÉES ===
        db_group = ttk.LabelFrame(main_ribbon, text="Base de données", padding="5")
        db_group.pack(side="left", fill="y", padx=2)

        db_buttons_frame = ttk.Frame(db_group)
        db_buttons_frame.pack()

        # Changer de base
        ttk.Button(
            db_buttons_frame,
            text="📂 Changer",
            command=self.change_database,
            style="RibbonButton.TButton",
            width=12,
        ).grid(row=0, column=0, padx=1, pady=1)

        # Créer base
        ttk.Button(
            db_buttons_frame,
            text="➕ Créer",
            command=self.create_new_database,
            style="RibbonButton.TButton",
            width=12,
        ).grid(row=0, column=1, padx=1, pady=1)

        # Espace flexible pour pousser les éléments à droite
        spacer_frame = ttk.Frame(main_ribbon)
        spacer_frame.pack(side="left", fill="x", expand=True)

        # === GROUPE AIDE (à droite) ===
        help_group = ttk.LabelFrame(main_ribbon, text="Aide", padding="5")
        help_group.pack(side="right", fill="y", padx=2)

        help_buttons_frame = ttk.Frame(help_group)
        help_buttons_frame.pack()

        # About/Info
        ttk.Button(
            help_buttons_frame,
            text="❓ À propos",
            command=self.show_about,
            style="RibbonButton.TButton",
            width=14,
        ).grid(row=0, column=0, pady=1)

    def toggle_filters_tab(self):
        """Basculer vers l'onglet filtres"""
        try:
            # Rechercher le notebook dans l'interface et activer l'onglet filtres
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.PanedWindow):
                    for pane in widget.panes():
                        pane_widget = widget.nametowidget(pane)
                        for child in pane_widget.winfo_children():
                            if isinstance(
                                child, ttk.LabelFrame
                            ) and "Détails" in child.cget("text"):
                                for notebook_child in child.winfo_children():
                                    if isinstance(notebook_child, ttk.Notebook):
                                        notebook_child.select(
                                            4
                                        )  # Onglet filtres (index 4)
                                        return
        except Exception as e:
            print(f"Erreur lors du basculement vers les filtres: {e}")

    def show_about(self):
        """Afficher les informations À propos"""
        messagebox.showinfo(
            "À propos",
            "Gestionnaire de Prompts ComfyUI\n"
            "Version cy8\n\n"
            "Application de gestion de prompts et workflows\n"
            "pour ComfyUI avec interface moderne.\n\n"
            "© 2025 - Développé avec Python & Tkinter",
        )

    def setup_prompts_table(self, parent):
        """
        0) Configuration du tableau des prompts
        Colonnes: ID, Name, Status, Model, Comment, Parent, Env
        """
        table_frame = ttk.LabelFrame(parent, text="Liste des Prompts", padding="5")
        table_frame.pack(fill="both", expand=True)

        # Treeview pour les prompts
        columns = ("id", "name", "status", "model", "comment", "parent", "id_env")
        self.prompts_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=15
        )

        # Configuration des colonnes
        self.prompts_tree.heading("id", text="ID")
        self.prompts_tree.heading("name", text="Nom")
        self.prompts_tree.heading("status", text="Statut")
        self.prompts_tree.heading("model", text="Modèle")
        self.prompts_tree.heading("comment", text="Commentaire")
        self.prompts_tree.heading("parent", text="Parent")
        self.prompts_tree.heading("id_env", text="Env")

        self.prompts_tree.column("id", width=50)
        self.prompts_tree.column("name", width=200)
        self.prompts_tree.column("status", width=80)
        self.prompts_tree.column("model", width=150)
        self.prompts_tree.column("comment", width=200)
        self.prompts_tree.column("parent", width=60)
        self.prompts_tree.column("id_env", width=100)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.prompts_tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.prompts_tree.xview
        )
        self.prompts_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Placement
        self.prompts_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Événements
        self.prompts_tree.bind("<<TreeviewSelect>>", self.on_prompt_select)
        self.prompts_tree.bind("<Double-1>", self.on_prompt_double_click)

    def setup_details_panel(self, parent):
        """
        1) Configuration du panel détaillé
        Fonction initiale: load_prompt_details
        """
        details_frame = ttk.LabelFrame(parent, text="Détails du Prompt", padding="5")
        details_frame.pack(fill="both", expand=True)

        # Notebook pour organiser les onglets
        notebook = ttk.Notebook(details_frame)
        notebook.pack(fill="both", expand=True)

        # 1.1) Onglet Prompt Values
        values_tab = ttk.Frame(notebook)
        notebook.add(values_tab, text="Prompt Values")

        self.values_frame, self.values_tree = (
            self.table_manager.create_prompt_values_table(
                values_tab, self.on_data_change
            )
        )
        self.values_frame.pack(fill="both", expand=True)
        self.current_values_tree = self.values_tree
        self.table_manager._current_values_tree = self.values_tree

        # 1.2) Onglet Workflow
        workflow_tab = ttk.Frame(notebook)
        notebook.add(workflow_tab, text="Workflow")

        self.workflow_frame, self.workflow_tree = (
            self.table_manager.create_workflow_table(workflow_tab, self.on_data_change)
        )
        self.workflow_frame.pack(fill="both", expand=True)
        self.current_workflow_tree = self.workflow_tree
        self.table_manager._current_workflow_tree = self.workflow_tree

        # Onglet Informations générales
        info_tab = ttk.Frame(notebook)
        notebook.add(info_tab, text="Informations")

        self.setup_info_tab(info_tab)

        # Onglet ComfyUI - Environnement et Extra Paths
        comfyui_tab = ttk.Frame(notebook)
        notebook.add(comfyui_tab, text="ComfyUI")

        self.setup_comfyui_tab(comfyui_tab)

        # Onglet Log - Analyse des logs ComfyUI
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="📊 Log")

        self.setup_log_tab(log_tab)

        # Onglet Data - Gestion de la base de données
        data_tab = ttk.Frame(notebook)
        notebook.add(data_tab, text="Data")

        self.setup_data_tab(data_tab)

        # Onglet Exécutions - Suivi des workflows
        executions_tab = ttk.Frame(notebook)
        notebook.add(executions_tab, text="Exécutions")

        self.setup_executions_tab(executions_tab)

        # Onglet Images - Explorateur d'images générées
        images_tab = ttk.Frame(notebook)
        notebook.add(images_tab, text="Images")

        self.setup_images_tab(images_tab)

        # Onglet Filtres - Système de filtres avancés
        filters_tab = ttk.Frame(notebook)
        notebook.add(filters_tab, text="Filtres")

        self.setup_filters_tab(filters_tab)

        # Onglet Chat RAG - Assistant IA pour ComfyUI
        chat_tab = ttk.Frame(notebook)
        notebook.add(chat_tab, text="💬 Chat")

        self.setup_chat_tab(chat_tab)

        # Onglet Terminal - Terminal intégré avec indexation RAG
        self.terminal_tab = ttk.Frame(notebook)
        notebook.add(self.terminal_tab, text="⚡ Terminal")

        self.setup_terminal_tab(self.terminal_tab)

    def setup_filters_tab(self, parent):
        """Configurer l'onglet des filtres avancés"""

        # Frame principal avec scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header du tableau des filtres
        header_frame = ttk.LabelFrame(scrollable_frame, text="Filtres actifs")
        header_frame.pack(fill="x", padx=5, pady=5)

        # Colonnes: [✓] | Type de filtre | Critère | Valeur
        ttk.Label(header_frame, text="Actif", font=("Arial", 9, "bold")).grid(
            row=0, column=0, padx=5, pady=2
        )
        ttk.Label(header_frame, text="Type de filtre", font=("Arial", 9, "bold")).grid(
            row=0, column=1, padx=5, pady=2
        )
        ttk.Label(header_frame, text="Critère", font=("Arial", 9, "bold")).grid(
            row=0, column=2, padx=5, pady=2
        )
        ttk.Label(header_frame, text="Valeur", font=("Arial", 9, "bold")).grid(
            row=0, column=3, padx=5, pady=2
        )
        ttk.Label(header_frame, text="Actions", font=("Arial", 9, "bold")).grid(
            row=0, column=4, padx=5, pady=2
        )

        # Initialiser la liste des filtres
        self.filters_list = []
        self.filters_frame = scrollable_frame

        # Ajouter les filtres par défaut
        self.add_default_filters()

        # Boutons d'action
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill="x", padx=5, pady=10)

        ttk.Button(
            action_frame, text="+ Ajouter filtre", command=self.add_new_filter
        ).pack(side="left", padx=5)
        ttk.Button(
            action_frame, text="Appliquer filtres", command=self.apply_filters
        ).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Réinitialiser", command=self.reset_filters).pack(
            side="left", padx=5
        )

        # Statistiques des filtres
        stats_frame = ttk.LabelFrame(scrollable_frame, text="Statistiques")
        stats_frame.pack(fill="x", padx=5, pady=5)

        self.stats_label = ttk.Label(stats_frame, text="Aucun filtre appliqué")
        self.stats_label.pack(padx=5, pady=5)

        # Pack du canvas et scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_chat_tab(self, parent):
        """Configurer l'onglet Chat RAG pour l'assistance ComfyUI"""

        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header avec informations sur l'environnement
        header_frame = ttk.LabelFrame(main_frame, text="🧠 Assistant RAG ComfyUI", padding="10")
        header_frame.pack(fill="x", pady=(0, 10))

        # === INDICATEURS RAG ===
        # Frame pour les indicateurs RAG
        self.rag_status_frame = ttk.Frame(header_frame)
        self.rag_status_frame.pack(fill="x", pady=(0, 10))

        # Ligne 1: Statut global et environnement
        status_row1 = ttk.Frame(self.rag_status_frame)
        status_row1.pack(fill="x", pady=(0, 5))

        ttk.Label(status_row1, text="Statut:", font=("TkDefaultFont", 9, "bold")).pack(side="left")
        self.rag_status_indicator = ttk.Label(status_row1, text="🔴", font=("TkDefaultFont", 12))
        self.rag_status_indicator.pack(side="left", padx=(5, 15))

        ttk.Label(status_row1, text="Environnement:", font=("TkDefaultFont", 9, "bold")).pack(side="left")
        self.rag_env_label = ttk.Label(status_row1, text="Aucun", foreground="gray")
        self.rag_env_label.pack(side="left", padx=(5, 0))

        # Ligne 2: Nombre de documents et actions
        status_row2 = ttk.Frame(self.rag_status_frame)
        status_row2.pack(fill="x")

        ttk.Label(status_row2, text="Documents indexés:", font=("TkDefaultFont", 9, "bold")).pack(side="left")
        self.rag_docs_count_label = ttk.Label(status_row2, text="0", foreground="blue", font=("TkDefaultFont", 9, "bold"))
        self.rag_docs_count_label.pack(side="left", padx=(5, 15))

        # Bouton pour scanner manuellement
        ttk.Button(
            status_row2,
            text="🔍 Scanner analyses",
            command=self.manual_rag_scan,
            width=15
        ).pack(side="left", padx=(0, 10))

        # Séparateur
        ttk.Separator(header_frame, orient="horizontal").pack(fill="x", pady=(10, 5))

        # === SÉLECTEUR DE MODE RAG ===
        mode_frame = ttk.Frame(header_frame)
        mode_frame.pack(fill="x", pady=(5, 10))

        ttk.Label(mode_frame, text="Mode RAG:", font=("TkDefaultFont", 9, "bold")).pack(side="left")

        # Variable pour le mode sélectionné
        self.rag_mode_var = tk.StringVar(value="rapide")

        # Boutons radio pour les modes
        mode_buttons_frame = ttk.Frame(mode_frame)
        mode_buttons_frame.pack(side="left", padx=(10, 0))

        self.rapid_mode_radio = ttk.Radiobutton(
            mode_buttons_frame,
            text="⚡ Rapide (Templates)",
            variable=self.rag_mode_var,
            value="rapide",
            command=self.on_rag_mode_changed
        )
        self.rapid_mode_radio.pack(side="left", padx=(0, 15))

        self.expert_mode_radio = ttk.Radiobutton(
            mode_buttons_frame,
            text="🧠 Expert (RAG + Mistral AI)",
            variable=self.rag_mode_var,
            value="expert",
            command=self.on_rag_mode_changed
        )
        self.expert_mode_radio.pack(side="left")

        # Indicateur de coût/performance
        self.mode_info_label = ttk.Label(
            mode_frame,
            text="< 1s - Gratuit",
            font=("TkDefaultFont", 8),
            foreground="green"
        )
        self.mode_info_label.pack(side="right")

        # Bouton info sur les modes
        ttk.Button(
            mode_frame,
            text="ℹ️",
            command=self.show_rag_modes_info,
            width=3
        ).pack(side="right", padx=(5, 10))

        # Informations de statut (existant)
        self.chat_status_frame = ttk.Frame(header_frame)
        self.chat_status_frame.pack(fill="x", pady=(0, 5))

        self.chat_status_label = ttk.Label(
            self.chat_status_frame,
            text="🔄 Initialisation du RAG...",
            font=("TkDefaultFont", 9)
        )
        self.chat_status_label.pack(side="left")

        # Bouton de rafraîchissement du contexte
        ttk.Button(
            self.chat_status_frame,
            text="🔄 Actualiser contexte",
            command=self.refresh_chat_context,
            width=20
        ).pack(side="right", padx=(5, 0))

        # Boutons de test RAG
        test_buttons_frame = ttk.Frame(self.chat_status_frame)
        test_buttons_frame.pack(side="right", padx=(5, 5))

        ttk.Button(
            test_buttons_frame,
            text="🧪 Test RAG",
            command=self.run_rag_test_suite,
            width=12
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            test_buttons_frame,
            text="⚡ Test rapide",
            command=self.run_quick_rag_test,
            width=12
        ).pack(side="left")

        # Zone de conversation
        conversation_frame = ttk.LabelFrame(main_frame, text="💬 Conversation", padding="5")
        conversation_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Text widget pour l'historique de conversation avec scrollbar
        chat_scroll_frame = ttk.Frame(conversation_frame)
        chat_scroll_frame.pack(fill="both", expand=True)

        self.chat_history = tk.Text(
            chat_scroll_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20,
            font=("Consolas", 10),
            bg="#f8f9fa",
            fg="#212529"
        )

        chat_scrollbar = ttk.Scrollbar(chat_scroll_frame, orient="vertical", command=self.chat_history.yview)
        self.chat_history.configure(yscrollcommand=chat_scrollbar.set)

        self.chat_history.pack(side="left", fill="both", expand=True)
        chat_scrollbar.pack(side="right", fill="y")

        # Configuration des tags pour le formatage
        self.chat_history.tag_configure("user", foreground="#0066cc", font=("Consolas", 10, "bold"))
        self.chat_history.tag_configure("assistant", foreground="#006600")
        self.chat_history.tag_configure("system", foreground="#666666", font=("Consolas", 9, "italic"))
        self.chat_history.tag_configure("error", foreground="#cc0000")
        self.chat_history.tag_configure("timestamp", foreground="#999999", font=("Consolas", 8))

        # Message de bienvenue au démarrage
        self.chat_history.config(state=tk.NORMAL)
        welcome_msg = (
            "🚀 **CHAT RAG DÉMARRÉ**\n\n"
            "✅ Interface chat opérationnelle\n"
            "🔍 En attente de l'identification de l'environnement ComfyUI...\n\n"
            "💡 Pour activer le RAG, allez dans l'onglet ComfyUI → 'Identifier l'environnement'"
        )
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_history.insert(tk.END, f"[{timestamp}] 🔧 Système: {welcome_msg}\n\n", "system")
        self.chat_history.config(state=tk.DISABLED)

        # Zone de saisie
        input_frame = ttk.LabelFrame(main_frame, text="✍️ Votre message", padding="5")
        input_frame.pack(fill="x")

        # Frame pour l'entrée et les boutons
        input_controls_frame = ttk.Frame(input_frame)
        input_controls_frame.pack(fill="x")

        # Zone de texte pour la saisie
        self.chat_input = tk.Text(
            input_controls_frame,
            height=3,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.chat_input.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Frame pour les boutons
        buttons_frame = ttk.Frame(input_controls_frame)
        buttons_frame.pack(side="right", fill="y")

        # Bouton d'envoi
        self.send_button = ttk.Button(
            buttons_frame,
            text="📤 Envoyer",
            command=self.send_chat_message,
            width=12
        )
        self.send_button.pack(pady=(0, 5))

        # Bouton d'effacement
        ttk.Button(
            buttons_frame,
            text="🗑️ Effacer",
            command=self.clear_chat_input,
            width=12
        ).pack()

        # Bind Enter pour envoyer (Ctrl+Enter pour nouvelle ligne)
        self.chat_input.bind("<Return>", self.on_enter_pressed)
        self.chat_input.bind("<Control-Return>", lambda e: self.chat_input.insert(tk.INSERT, "\n"))

        # Frame d'actions rapides
        quick_actions_frame = ttk.LabelFrame(main_frame, text="⚡ Actions rapides", padding="5")
        quick_actions_frame.pack(fill="x", pady=(5, 0))

        quick_buttons_frame = ttk.Frame(quick_actions_frame)
        quick_buttons_frame.pack()

        # Boutons d'actions rapides
        ttk.Button(
            quick_buttons_frame,
            text="📊 État du serveur",
            command=lambda: self.send_quick_message("Quel est l'état actuel du serveur ComfyUI ?"),
            width=18
        ).grid(row=0, column=0, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="⚠️ Erreurs récurrentes",
            command=lambda: self.send_quick_message("Quelles sont les erreurs les plus fréquentes ?"),
            width=18
        ).grid(row=0, column=1, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="🎯 Optimisations",
            command=lambda: self.send_quick_message("Quelles optimisations recommandes-tu ?"),
            width=18
        ).grid(row=0, column=2, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="🔧 Contraintes",
            command=lambda: self.send_quick_message("Rappelle-moi mes contraintes système."),
            width=18
        ).grid(row=1, column=0, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="📝 Ajouter contrainte",
            command=self.add_system_constraint,
            width=18
        ).grid(row=1, column=1, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="🔍 Rechercher erreur",
            command=self.search_error_history,
            width=18
        ).grid(row=1, column=2, padx=2, pady=2)

        # Ligne 3: Gestion RAG
        ttk.Button(
            quick_buttons_frame,
            text="🧠 Examiner RAG",
            command=self.examine_rag_index,
            width=18
        ).grid(row=2, column=0, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="🔄 Ré-indexer",
            command=self.reindex_rag_analyses,
            width=18
        ).grid(row=2, column=1, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="📊 Stats RAG",
            command=self.show_rag_statistics,
            width=18
        ).grid(row=2, column=2, padx=2, pady=2)

        # Ligne 4: Fonctions RAG temporelles
        ttk.Button(
            quick_buttons_frame,
            text="🔥 État actuel",
            command=self.show_current_server_state,
            width=18
        ).grid(row=3, column=0, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="🕒 Analyse temporelle",
            command=self.show_temporal_analysis,
            width=18
        ).grid(row=3, column=1, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="📈 Évolution",
            command=self.show_temporal_evolution,
            width=18
        ).grid(row=3, column=2, padx=2, pady=2)

        # Ligne 5: Réinitialisation et maintenance
        ttk.Button(
            quick_buttons_frame,
            text="🗑️ RAG Reset",
            command=self.reset_rag_completely,
            width=18
        ).grid(row=4, column=0, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="🧹 Nettoyer Custom",
            command=self.clean_custom_environments,
            width=18
        ).grid(row=4, column=1, padx=2, pady=2)

        ttk.Button(
            quick_buttons_frame,
            text="🔬 Test Efficacité",
            command=self.test_rag_efficiency,
            width=18
        ).grid(row=4, column=2, padx=2, pady=2)

        # Initialiser la conversation avec le message de bienvenue
        self.root.after(1000, self.initialize_chat_welcome)

    def setup_terminal_tab(self, parent):
        """Configurer l'onglet Terminal intégré avec indexation RAG"""

        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header avec informations et contrôles
        header_frame = ttk.LabelFrame(main_frame, text="⚡ Terminal intégré avec indexation RAG", padding="10")
        header_frame.pack(fill="x", pady=(0, 10))

        # === CONTRÔLES TERMINAL ===
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        # Ligne 1: Répertoire de travail et boutons de navigation
        work_dir_frame = ttk.Frame(controls_frame)
        work_dir_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(work_dir_frame, text="Répertoire:", font=("TkDefaultFont", 9, "bold")).pack(side="left")

        # Variable pour le répertoire de travail
        self.terminal_cwd_var = tk.StringVar(value=os.getcwd())
        self.terminal_cwd = os.getcwd()  # String version pour les opérations

        # Entry pour afficher/modifier le répertoire
        self.cwd_entry = ttk.Entry(work_dir_frame, textvariable=self.terminal_cwd_var, width=60)
        self.cwd_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))

        # Boutons de navigation
        ttk.Button(
            work_dir_frame,
            text="📁 Parcourir",
            command=self.browse_terminal_directory,
            width=12
        ).pack(side="right", padx=(5, 0))

        # Ligne 2: Statut et options
        status_frame = ttk.Frame(controls_frame)
        status_frame.pack(fill="x")

        ttk.Label(status_frame, text="Statut:", font=("TkDefaultFont", 9, "bold")).pack(side="left")
        self.terminal_status_label = ttk.Label(status_frame, text="Prêt", foreground="green")
        self.terminal_status_label.pack(side="left", padx=(5, 15))

        # Options d'indexation RAG
        ttk.Label(status_frame, text="Indexation RAG:", font=("TkDefaultFont", 9, "bold")).pack(side="left")
        self.terminal_rag_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            status_frame,
            text="Auto",
            variable=self.terminal_rag_enabled,
            command=lambda: self.toggle_rag_indexing()
        ).pack(side="left", padx=(5, 15))

        # Boutons de contrôle
        ttk.Button(
            status_frame,
            text="🗑️ Effacer",
            command=self.clear_terminal_output,
            width=10
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            status_frame,
            text="💾 Sauver session",
            command=self.save_terminal_session,
            width=15
        ).pack(side="right", padx=(5, 5))

        # === ZONE D'AFFICHAGE TERMINAL ===
        terminal_frame = ttk.LabelFrame(main_frame, text="🖥️ Sortie Terminal", padding="5")
        terminal_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Terminal avec scrollbar
        terminal_scroll_frame = ttk.Frame(terminal_frame)
        terminal_scroll_frame.pack(fill="both", expand=True)

        self.terminal_output = tk.Text(
            terminal_scroll_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=25,
            font=("Consolas", 10),
            bg="#1e1e1e",  # Fond sombre comme un terminal
            fg="#ffffff",  # Texte blanc
            insertbackground="#ffffff"  # Curseur blanc
        )

        terminal_scrollbar = ttk.Scrollbar(terminal_scroll_frame, orient="vertical", command=self.terminal_output.yview)
        self.terminal_output.configure(yscrollcommand=terminal_scrollbar.set)

        self.terminal_output.pack(side="left", fill="both", expand=True)
        terminal_scrollbar.pack(side="right", fill="y")

        # Configuration des tags pour le formatage
        self.terminal_output.tag_configure("command", foreground="#87CEEB")  # Bleu clair pour les commandes
        self.terminal_output.tag_configure("output", foreground="#ffffff")   # Blanc pour la sortie
        self.terminal_output.tag_configure("error", foreground="#ff6b6b")    # Rouge pour les erreurs
        self.terminal_output.tag_configure("success", foreground="#51cf66")  # Vert pour les succès
        self.terminal_output.tag_configure("info", foreground="#74c0fc")     # Bleu info au lieu de jaune
        self.terminal_output.tag_configure("warning", foreground="#ffa726")  # Orange pour warnings
        self.terminal_output.tag_configure("timestamp", foreground="#868e96", font=("Consolas", 8))
        self.terminal_output.tag_configure("prompt", foreground="#40c057", font=("Consolas", 10, "bold"))  # Vert clair pour prompt

        # === ZONE DE SAISIE COMMANDE ===
        input_frame = ttk.LabelFrame(main_frame, text="✍️ Saisie commande", padding="5")
        input_frame.pack(fill="x")

        # Frame pour l'entrée et les boutons
        input_controls_frame = ttk.Frame(input_frame)
        input_controls_frame.pack(fill="x")

        # Prompt du terminal
        self.terminal_prompt_label = ttk.Label(
            input_controls_frame,
            text=f"{os.path.basename(self.terminal_cwd)}> ",
            font=("Consolas", 10, "bold"),
            foreground="#40c057"
        )
        self.terminal_prompt_label.pack(side="left")

        # Zone de saisie de commande
        self.terminal_input = tk.Entry(
            input_controls_frame,
            font=("Consolas", 10),
            bg="#2e2e2e",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.terminal_input.pack(side="left", fill="x", expand=True, padx=(5, 5))

        # Boutons d'action
        button_frame = ttk.Frame(input_controls_frame)
        button_frame.pack(side="right")

        # Bouton d'exécution
        self.execute_button = ttk.Button(
            button_frame,
            text="▶️ Exécuter",
            command=self.execute_terminal_command,
            width=12
        )
        self.execute_button.pack(side="left", padx=(0, 5))

        # Bouton d'interruption
        self.interrupt_button = ttk.Button(
            button_frame,
            text="⏹️ Interrompre",
            command=self.interrupt_terminal_command,
            width=12,
            state="disabled"
        )
        self.interrupt_button.pack(side="left")

        # Bind Enter pour exécuter la commande
        self.terminal_input.bind("<Return>", self.on_terminal_key_press)
        self.terminal_input.bind("<Up>", self.on_terminal_key_press)
        self.terminal_input.bind("<Down>", self.on_terminal_key_press)

        # Historique des commandes
        self.terminal_command_history = []
        self.terminal_history = self.terminal_command_history  # Alias pour compatibilité
        self.terminal_history_index = -1

        # Session actuelle
        self.current_terminal_session = {
            "commands": [],
            "start_time": time.time(),
            "working_directory": self.terminal_cwd
        }

        # Processus en cours
        self.current_process = None

        # Initialiser le terminal avec un message de bienvenue
        self.root.after(500, self.initialize_terminal_welcome)

    def setup_info_tab(self, parent):
        """Configuration de l'onglet informations générales"""
        info_frame = ttk.Frame(parent, padding="10")
        info_frame.pack(fill="both", expand=True)

        # Variables
        self.name_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.comment_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.file_var = tk.StringVar()
        self.id_env_var = tk.StringVar()

        # Interface
        row = 0

        ttk.Label(info_frame, text="Nom:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(info_frame, textvariable=self.name_var, width=50).grid(
            row=row, column=1, sticky="ew", padx=10
        )
        row += 1

        ttk.Label(info_frame, text="URL:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(info_frame, textvariable=self.url_var, width=50).grid(
            row=row, column=1, sticky="ew", padx=10
        )
        row += 1

        ttk.Label(info_frame, text="Modèle:").grid(
            row=row, column=0, sticky="w", pady=5
        )
        ttk.Entry(info_frame, textvariable=self.model_var, width=50).grid(
            row=row, column=1, sticky="ew", padx=10
        )
        row += 1

        ttk.Label(info_frame, text="Statut:").grid(
            row=row, column=0, sticky="w", pady=5
        )
        status_combo = ttk.Combobox(
            info_frame,
            textvariable=self.status_var,
            values=self.db_manager.status_options,
            state="readonly",
            width=15,
        )
        status_combo.grid(row=row, column=1, sticky="w", padx=10)
        row += 1

        ttk.Label(info_frame, text="Commentaire:").grid(
            row=row, column=0, sticky="w", pady=5
        )
        ttk.Entry(info_frame, textvariable=self.comment_var, width=50).grid(
            row=row, column=1, sticky="ew", padx=10
        )
        row += 1

        ttk.Label(info_frame, text="ID Environnement:").grid(
            row=row, column=0, sticky="w", pady=5
        )
        ttk.Entry(info_frame, textvariable=self.id_env_var, width=50).grid(
            row=row, column=1, sticky="ew", padx=10
        )
        row += 1

        ttk.Label(info_frame, text="Fichier exporté:").grid(
            row=row, column=0, sticky="w", pady=5
        )
        file_frame = ttk.Frame(info_frame)
        file_frame.grid(row=row, column=1, sticky="ew", padx=10)
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=40, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True)
        file_button = ttk.Button(file_frame, text="📂", width=3, command=lambda: self.copy_path_to_clipboard(self.file_var.get()))
        file_button.pack(side="left", padx=(5, 0))
        row += 1

        info_frame.grid_columnconfigure(1, weight=1)

        # Bouton de sauvegarde
        ttk.Button(
            info_frame,
            text="Sauvegarder les informations",
            command=self.save_current_info,
        ).grid(row=row, column=0, columnspan=2, pady=20)

    def setup_comfyui_tab(self, parent):
        """Configuration de l'onglet ComfyUI - Interface complète"""
        # Frame principal avec scrolling
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        comfyui_frame = ttk.Frame(scrollable_frame, padding="10")
        comfyui_frame.pack(fill="both", expand=True)

        # Titre principal
        ttk.Label(
            comfyui_frame,
            text="🚀 ComfyUI - Gestion & Environnement",
            font=("TkDefaultFont", 14, "bold"),
        ).pack(pady=(0, 10))

        # === SECTION 1: ENVIRONNEMENT COMFYUI (MISE EN AVANT) ===
        env_main_frame = ttk.LabelFrame(
            comfyui_frame, text="🌍 Environnement ComfyUI - Extra Paths", padding="10"
        )
        env_main_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Ligne d'information rapide
        env_info_line = ttk.Frame(env_main_frame)
        env_info_line.pack(fill="x", pady=(0, 10))

        # Serveur et statut en une ligne compacte
        server_info = os.getenv("COMFYUI_SERVER", "127.0.0.1:8188")
        ttk.Label(
            env_info_line, text="🖥️ Serveur:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left")
        ttk.Label(env_info_line, text=server_info, font=("Consolas", 8)).pack(
            side="left", padx=(5, 20)
        )

        ttk.Label(env_info_line, text="🆔 ID:", font=("TkDefaultFont", 9, "bold")).pack(
            side="left"
        )
        self.env_config_id_label = ttk.Label(
            env_info_line, text="Non identifié", foreground="gray", font=("Consolas", 8)
        )
        self.env_config_id_label.pack(side="left", padx=(5, 20))

        ttk.Label(
            env_info_line, text="📁 Racine:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left")
        self.env_root_label = ttk.Label(
            env_info_line, text="Non détecté", foreground="gray", font=("Consolas", 8)
        )
        self.env_root_label.pack(side="left", padx=(5, 0))

        # Boutons d'action principaux
        buttons_frame = ttk.Frame(env_main_frame)
        buttons_frame.pack(fill="x", pady=(0, 10))

        # Bouton principal d'identification
        identify_btn = ttk.Button(
            buttons_frame,
            text="� Identifier l'environnement",
            command=self.identify_comfyui_environment,
            style="Accent.TButton",
        )
        identify_btn.pack(side="left", padx=(0, 10))

        # Bouton test connexion plus discret
        self.test_connection_btn = ttk.Button(
            buttons_frame, text="🔗 Test", command=self.test_comfyui_connection, width=8
        )
        self.test_connection_btn.pack(side="left", padx=(0, 10))

        # Bouton actualiser
        ttk.Button(
            buttons_frame, text="🔄 Actualiser", command=self.refresh_env_data, width=12
        ).pack(side="left", padx=(0, 10))

        # Indicateur de statut compact
        self.status_icon_label = ttk.Label(
            buttons_frame, text="⚪", font=("TkDefaultFont", 12)
        )
        self.status_icon_label.pack(side="left", padx=(10, 5))

        self.status_text_label = ttk.Label(
            buttons_frame, text="Prêt", font=("TkDefaultFont", 8), foreground="gray"
        )
        self.status_text_label.pack(side="left")

        # Outils de recherche et filtrage
        search_frame = ttk.Frame(env_main_frame)
        search_frame.pack(fill="x", pady=(10, 5))

        ttk.Label(
            search_frame, text="🔍 Rechercher:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left", padx=(0, 5))
        self.env_search_var = tk.StringVar()
        self.env_search_var.trace("w", self.filter_env_paths)
        search_entry = ttk.Entry(
            search_frame, textvariable=self.env_search_var, width=25
        )
        search_entry.pack(side="left", padx=(0, 15))

        ttk.Label(search_frame, text="🏷️ Type:", font=("TkDefaultFont", 9, "bold")).pack(
            side="left", padx=(0, 5)
        )
        self.env_type_filter = ttk.Combobox(
            search_frame,
            values=[
                "Tous",
                "checkpoints",
                "loras",
                "embeddings",
                "vae",
                "custom_nodes",
                "controlnet",
            ],
            state="readonly",
            width=15,
        )
        self.env_type_filter.set("Tous")
        self.env_type_filter.bind("<<ComboboxSelected>>", self.filter_env_paths)
        self.env_type_filter.pack(side="left", padx=(0, 15))

        ttk.Button(
            search_frame,
            text="📋 Copier chemin",
            command=self.copy_selected_path,
            width=15,
        ).pack(side="left")

        # TABLEAU DES EXTRA PATHS (PRINCIPAL ET VISIBLE)
        env_tree_frame = ttk.Frame(env_main_frame)
        env_tree_frame.pack(fill="both", expand=True, pady=(5, 0))

        # Frame pour la scrollbar horizontale (en bas)
        env_h_scroll_frame = ttk.Frame(env_tree_frame)
        env_h_scroll_frame.pack(side="bottom", fill="x")

        # Frame pour le contenu principal (treeview + scrollbar verticale)
        env_main_content_frame = ttk.Frame(env_tree_frame)
        env_main_content_frame.pack(side="top", fill="both", expand=True)

        # Colonnes: Clé, Type, Chemin, Section
        env_columns = ("key", "type", "path", "section")
        self.env_tree = ttk.Treeview(
            env_main_content_frame, columns=env_columns, show="headings", height=12
        )

        # Configuration des colonnes avec largeurs adaptives
        self.env_tree.heading("key", text="Clé")
        self.env_tree.heading("type", text="Type")
        self.env_tree.heading("path", text="Chemin")
        self.env_tree.heading("section", text="Section")

        # Largeurs optimisées et flexibles
        self.env_tree.column("key", width=120, minwidth=80, anchor="w")
        self.env_tree.column("type", width=140, minwidth=100, anchor="w")
        self.env_tree.column("path", width=500, minwidth=300, anchor="w")
        self.env_tree.column("section", width=100, minwidth=80, anchor="w")

        # Scrollbars pour le treeview des paths
        env_tree_v_scrollbar = ttk.Scrollbar(
            env_main_content_frame, orient="vertical", command=self.env_tree.yview
        )
        env_tree_h_scrollbar = ttk.Scrollbar(
            env_h_scroll_frame, orient="horizontal", command=self.env_tree.xview
        )
        self.env_tree.configure(
            yscrollcommand=env_tree_v_scrollbar.set,
            xscrollcommand=env_tree_h_scrollbar.set,
        )

        # Placement optimisé avec pack
        self.env_tree.pack(side="left", fill="both", expand=True)
        env_tree_v_scrollbar.pack(side="right", fill="y")
        env_tree_h_scrollbar.pack(side="bottom", fill="x")

        # Configuration des couleurs pour les différents types
        self.env_tree.tag_configure("checkpoints", background="#e8f5e8")
        self.env_tree.tag_configure("loras", background="#e8f0ff")
        self.env_tree.tag_configure("embeddings", background="#fff8e8")
        self.env_tree.tag_configure("custom_nodes", background="#f0e8ff")
        self.env_tree.tag_configure("vae", background="#ffe8f0")

        # === SECTION 2: OUTILS COMPLEMENTAIRES (COLLAPSIBLE) ===
        tools_frame = ttk.LabelFrame(
            comfyui_frame, text="🔧 Outils complémentaires", padding="10"
        )
        tools_frame.pack(fill="x", pady=(10, 0))

        # Frame pour les détails techniques (masqué par défaut)
        self.details_frame = ttk.LabelFrame(
            tools_frame, text="Détails techniques", padding="5"
        )
        # Note: On n'utilise pas pack() ici, le frame sera affiché uniquement après un test

        # Zone de texte pour les détails (avec scrollbar) - plus compacte
        details_text_frame = ttk.Frame(self.details_frame)
        details_text_frame.pack(fill="both", expand=True)

        self.details_text = tk.Text(
            details_text_frame,
            height=6,  # Réduit de 10 à 6
            wrap="word",
            state="disabled",
            font=("Consolas", 8),  # Police plus petite
        )
        details_scrollbar = ttk.Scrollbar(
            details_text_frame, orient="vertical", command=self.details_text.yview
        )
        self.details_text.configure(yscrollcommand=details_scrollbar.set)

        self.details_text.pack(side="left", fill="both", expand=True)
        details_scrollbar.pack(side="right", fill="y")

        # Variables pour compatibilité avec le code existant
        self.comfyui_config_id = tk.StringVar(value="")
        self.config_id_entry = None  # Plus utilisé dans la nouvelle interface
        self.config_info_label = (
            self.status_text_label
        )  # Redirection vers le nouveau label de statut

        # Chargement initial des données environnement
        self.refresh_env_data()

        # === SECTION PYTHON EMBEDDED ===
        python_frame = ttk.LabelFrame(
            comfyui_frame, text="🐍 Environnement Python ComfyUI", padding="10"
        )
        python_frame.pack(fill="x", pady=(10, 0))

        # Ligne de statut Python
        python_status_frame = ttk.Frame(python_frame)
        python_status_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            python_status_frame, text="Statut:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left")

        self.python_status_label = ttk.Label(
            python_status_frame, text="⏳ Non détecté", foreground="gray"
        )
        self.python_status_label.pack(side="left", padx=(5, 0))

        # Bouton de détection manuelle (optionnel)
        ttk.Button(
            python_status_frame,
            text="🔍 Détecter manuellement",
            command=self.detect_python_manually,
            width=20
        ).pack(side="right")

        # Ligne préfixe de commande
        prefix_frame = ttk.Frame(python_frame)
        prefix_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            prefix_frame, text="Préfixe:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left")

        self.python_prefix_entry = ttk.Entry(
            prefix_frame, state="readonly", font=("Consolas", 8)
        )
        self.python_prefix_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))

        # Ligne d'exécution de commandes
        command_frame = ttk.Frame(python_frame)
        command_frame.pack(fill="x")

        ttk.Label(
            command_frame, text="Commande:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left")

        self.python_command_entry = ttk.Entry(
            command_frame, font=("Consolas", 8), width=30
        )
        self.python_command_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))

        self.execute_python_btn = ttk.Button(
            command_frame,
            text="▶️ Exécuter",
            command=self.execute_python_command,
            state="disabled"
        )
        self.execute_python_btn.pack(side="right")

    def setup_log_tab(self, parent):
        """Configuration de l'onglet d'analyse des logs ComfyUI"""
        # Créer un Canvas avec barre de défilement pour tout l'onglet
        canvas = tk.Canvas(parent)
        canvas.pack(side="left", fill="both", expand=True)

        # Barre de défilement verticale pour l'onglet complet
        main_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        main_scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=main_scrollbar.set)

        # Frame principal avec padding qui sera scrollable
        log_frame = ttk.Frame(canvas, padding="15")
        canvas_window = canvas.create_window((0, 0), window=log_frame, anchor="nw")

        # Configurer le défilement
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def configure_canvas_width(event):
            # Ajuster la largeur du frame au canvas
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)

        log_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)

        # Rendre la molette de la souris fonctionnelle
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Titre principal
        title_frame = ttk.Frame(log_frame)
        title_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(
            title_frame,
            text="📊 Analyse des Logs ComfyUI",
            font=("TkDefaultFont", 14, "bold"),
        ).pack(side="left")

        # Informations rapides sur le côté
        info_label = ttk.Label(
            title_frame,
            text="Analysez les logs ComfyUI pour détecter les erreurs et problèmes",
            font=("TkDefaultFont", 9),
            foreground="gray",
        )
        info_label.pack(side="right")

        # === SECTION 1: CONFIGURATION DU FICHIER LOG ===
        config_frame = ttk.LabelFrame(
            log_frame, text="📁 Configuration du fichier log", padding="10"
        )
        config_frame.pack(fill="x", pady=(0, 15))

        # Ligne de sélection du fichier
        file_selection_frame = ttk.Frame(config_frame)
        file_selection_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            file_selection_frame, text="Fichier log:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left", padx=(0, 10))

        # Zone de texte pour le chemin avec valeur par défaut
        # Récupérer depuis les préférences ou utiliser la valeur par défaut
        saved_log_path = self.user_prefs.get_preference("comfyui_log_path")
        if not saved_log_path:
            saved_log_path = os.getenv(
                "COMFYUI_FILE_LOG", "E:/Comfyui_G11/ComfyUI/user/comfyui.log"
            )
        self.comfyui_log_path = tk.StringVar(value=saved_log_path)
        log_path_entry = ttk.Entry(
            file_selection_frame,
            textvariable=self.comfyui_log_path,
            font=("Consolas", 9),
        )
        log_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Bouton parcourir
        browse_log_btn = ttk.Button(
            file_selection_frame,
            text="📂 Parcourir...",
            command=self.browse_log_file,
            width=15,
        )
        browse_log_btn.pack(side="right")

        # Informations sur le fichier
        file_info_frame = ttk.Frame(config_frame)
        file_info_frame.pack(fill="x")

        self.log_file_info_label = ttk.Label(
            file_info_frame,
            text="💡 Sélectionnez un fichier log ComfyUI pour commencer l'analyse",
            font=("TkDefaultFont", 8),
            foreground="gray",
        )
        self.log_file_info_label.pack(anchor="w")

        # === SECTION 2: ACTIONS D'ANALYSE ===
        actions_frame = ttk.LabelFrame(
            log_frame, text="🔍 Actions d'analyse", padding="10"
        )
        actions_frame.pack(fill="x", pady=(0, 15))

        # Boutons d'action
        buttons_frame = ttk.Frame(actions_frame)
        buttons_frame.pack(fill="x", pady=(0, 10))

        # Bouton analyser principal
        self.analyze_log_btn = ttk.Button(
            buttons_frame,
            text="🔍 Analyser le log",
            command=self.analyze_comfyui_log,
            style="Accent.TButton",
            width=20,
        )
        self.analyze_log_btn.pack(side="left", padx=(0, 15))

        # Bouton analyse IA du log complet
        self.ai_analyze_btn = ttk.Button(
            buttons_frame,
            text="🤖 Analyse IA complète",
            command=self.analyze_complete_log_global,
            width=20,
        )
        self.ai_analyze_btn.pack(side="left", padx=(0, 15))

        # Bouton actualiser
        refresh_log_btn = ttk.Button(
            buttons_frame,
            text="🔄 Actualiser",
            command=self.refresh_log_analysis,
            width=15,
        )
        refresh_log_btn.pack(side="left", padx=(0, 15))

        # Bouton exporter
        export_log_btn = ttk.Button(
            buttons_frame,
            text="📤 Exporter",
            command=self.export_log_analysis,
            width=15,
        )
        export_log_btn.pack(side="left")

        # Indicateur de statut
        status_frame = ttk.Frame(actions_frame)
        status_frame.pack(fill="x")

        ttk.Label(status_frame, text="Statut:", font=("TkDefaultFont", 9, "bold")).pack(
            side="left", padx=(0, 10)
        )

        self.log_status_label = ttk.Label(
            status_frame,
            text="Aucune analyse effectuée",
            font=("TkDefaultFont", 9),
            foreground="gray",
        )
        self.log_status_label.pack(side="left")

        # === SECTION 3: ENVIRONNEMENTS ===
        environments_frame = ttk.LabelFrame(
            log_frame, text="🌍 Environnements ComfyUI", padding="10"
        )
        environments_frame.pack(fill="x", pady=(0, 15))

        # Tableau des environnements
        env_table_frame = ttk.Frame(environments_frame)
        env_table_frame.pack(fill="x", pady=(0, 10))

        # Créer le Treeview pour les environnements
        env_columns = ("id", "name", "path", "last_analysis", "status")
        self.environments_tree = ttk.Treeview(
            env_table_frame, columns=env_columns, show="headings", height=6
        )

        # Configuration des colonnes des environnements
        self.environments_tree.heading("id", text="ID")
        self.environments_tree.heading("name", text="Nom")
        self.environments_tree.heading("path", text="Chemin")
        self.environments_tree.heading("last_analysis", text="Dernière analyse")
        self.environments_tree.heading("status", text="Statut")

        # Largeurs des colonnes
        self.environments_tree.column("id", width=80, minwidth=60)
        self.environments_tree.column("name", width=120, minwidth=100)
        self.environments_tree.column("path", width=300, minwidth=200)
        self.environments_tree.column("last_analysis", width=150, minwidth=120)
        self.environments_tree.column("status", width=100, minwidth=80)

        # Scrollbars pour le tableau des environnements
        env_v_scrollbar = ttk.Scrollbar(
            env_table_frame, orient="vertical", command=self.environments_tree.yview
        )
        env_h_scrollbar = ttk.Scrollbar(
            env_table_frame, orient="horizontal", command=self.environments_tree.xview
        )

        self.environments_tree.configure(
            yscrollcommand=env_v_scrollbar.set, xscrollcommand=env_h_scrollbar.set
        )

        # Grid layout pour le tableau des environnements
        env_table_frame.grid_rowconfigure(0, weight=1)
        env_table_frame.grid_columnconfigure(0, weight=1)

        self.environments_tree.grid(row=0, column=0, sticky="nsew")
        env_v_scrollbar.grid(row=0, column=1, sticky="ns")
        env_h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Binding pour la sélection d'un environnement
        self.environments_tree.bind("<<TreeviewSelect>>", self.on_environment_select)
        # Binding pour double-clic = ouvrir popup des actions
        self.environments_tree.bind("<Double-1>", self.on_environment_double_click)

        # Boutons d'actions pour les environnements
        env_actions_frame = ttk.Frame(environments_frame)
        env_actions_frame.pack(fill="x")

        ttk.Button(
            env_actions_frame,
            text="🔄 Actualiser environnements",
            command=self.refresh_environments,
            width=25,
        ).pack(side="left", padx=(0, 10))

        # Boutons CRUD pour les environnements
        ttk.Button(
            env_actions_frame,
            text="➕ Ajouter",
            command=self.add_environment,
            width=15,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            env_actions_frame,
            text="✏️ Modifier",
            command=self.edit_environment,
            width=15,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            env_actions_frame,
            text="🗑️ Supprimer",
            command=self.delete_environment,
            width=15,
        ).pack(side="left", padx=(0, 10))

        # === SECTION 4: RESULTATS D'ANALYSE ===
        results_main_frame = ttk.LabelFrame(
            log_frame, text="📋 Résultats de l'analyse", padding="10"
        )
        results_main_frame.pack(fill="both", expand=True)

        # Barre d'outils pour les résultats
        results_toolbar = ttk.Frame(results_main_frame)
        results_toolbar.pack(fill="x", pady=(0, 10))

        # Filtres pour les résultats
        ttk.Label(
            results_toolbar, text="Filtrer:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left", padx=(0, 10))

        self.log_filter_var = tk.StringVar(value="Tous")
        log_filter_combo = ttk.Combobox(
            results_toolbar,
            textvariable=self.log_filter_var,
            values=["Tous", "ERREUR", "ATTENTION", "OK", "INFO"],
            state="readonly",
            width=15,
        )
        log_filter_combo.pack(side="left", padx=(0, 15))
        log_filter_combo.bind("<<ComboboxSelected>>", self.filter_log_results)

        # Recherche dans les résultats
        ttk.Label(
            results_toolbar, text="Rechercher:", font=("TkDefaultFont", 9, "bold")
        ).pack(side="left", padx=(0, 5))

        self.log_search_var = tk.StringVar()
        self.log_search_var.trace("w", self.search_log_results)
        log_search_entry = ttk.Entry(
            results_toolbar, textvariable=self.log_search_var, width=25
        )
        log_search_entry.pack(side="left", padx=(0, 15))

        # Compteur de résultats
        self.log_results_count_label = ttk.Label(
            results_toolbar,
            text="0 résultats",
            font=("TkDefaultFont", 8),
            foreground="gray",
        )
        self.log_results_count_label.pack(side="right")

        # Tableau des résultats
        results_frame = ttk.Frame(results_main_frame)
        results_frame.pack(fill="both", expand=True)

        # Frame pour la scrollbar horizontale (en bas)
        h_scroll_frame = ttk.Frame(results_frame)
        h_scroll_frame.pack(side="bottom", fill="x")

        # Frame pour le contenu principal (treeview + scrollbar verticale)
        main_content_frame = ttk.Frame(results_frame)
        main_content_frame.pack(side="top", fill="both", expand=True)

        # Créer le Treeview pour afficher les résultats avec plus de colonnes
        columns = ("timestamp", "type", "category", "element", "message", "details", "line")
        self.log_results_tree = ttk.Treeview(
            main_content_frame, columns=columns, show="headings", height=15
        )

        # Configuration des colonnes avec plus de détails
        self.log_results_tree.heading("timestamp", text="Timestamp")
        self.log_results_tree.heading("type", text="État")
        self.log_results_tree.heading("category", text="Catégorie")
        self.log_results_tree.heading("element", text="Custom Node/Élément")
        self.log_results_tree.heading("message", text="Message Principal")
        self.log_results_tree.heading("details", text="Détails/Temps")
        self.log_results_tree.heading("line", text="Ligne")

        # Largeurs optimisées pour plus d'informations
        self.log_results_tree.column("timestamp", width=140, minwidth=120)
        self.log_results_tree.column("type", width=80, minwidth=60)
        self.log_results_tree.column("category", width=110, minwidth=90)
        self.log_results_tree.column("element", width=160, minwidth=120)
        self.log_results_tree.column("message", width=300, minwidth=250)
        self.log_results_tree.column("details", width=150, minwidth=100)
        self.log_results_tree.column("line", width=60, minwidth=50)

        # Scrollbars
        tree_v_scrollbar = ttk.Scrollbar(
            main_content_frame, orient="vertical", command=self.log_results_tree.yview
        )
        tree_h_scrollbar = ttk.Scrollbar(
            h_scroll_frame, orient="horizontal", command=self.log_results_tree.xview
        )
        self.log_results_tree.configure(
            yscrollcommand=tree_v_scrollbar.set, xscrollcommand=tree_h_scrollbar.set
        )

        # Placement
        self.log_results_tree.pack(side="left", fill="both", expand=True)
        tree_v_scrollbar.pack(side="right", fill="y")
        tree_h_scrollbar.pack(side="bottom", fill="x")

        # Configuration des couleurs selon le type d'entrée
        self.log_results_tree.tag_configure(
            "OK", background="#d4edda", foreground="#155724"
        )
        self.log_results_tree.tag_configure(
            "ERREUR", background="#f8d7da", foreground="#721c24"
        )
        self.log_results_tree.tag_configure(
            "ATTENTION", background="#fff3cd", foreground="#856404"
        )
        self.log_results_tree.tag_configure(
            "INFO", background="#d1ecf1", foreground="#0c5460"
        )

        # Bind pour double-clic (détails)
        self.log_results_tree.bind("<Double-1>", self.show_log_detail)

        # Initialiser l'analyseur de logs
        self.log_analyzer = cy8_log_analyzer()

        # Vérifier si le fichier log par défaut existe
        self.check_log_file_status()

        # Initialiser l'état des boutons d'analyse (désactivés au démarrage)
        self.update_analysis_buttons_state()

    def setup_data_tab(self, parent):
        """Configuration de l'onglet gestion des données"""
        data_frame = ttk.Frame(parent, padding="10")
        data_frame.pack(fill="both", expand=True)

        # Titre
        ttk.Label(
            data_frame,
            text="Gestion de la Base de Données",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(pady=(0, 20))

        # Localisation actuelle de la base
        location_frame = ttk.LabelFrame(
            data_frame, text="Base de données actuelle", padding="10"
        )
        location_frame.pack(fill="x", pady=(0, 20))

        # Affichage du chemin
        ttk.Label(location_frame, text="Chemin:").grid(
            row=0, column=0, sticky="w", pady=5
        )

        self.db_path_var = tk.StringVar(value=self.db_path)
        db_path_entry = ttk.Entry(
            location_frame, textvariable=self.db_path_var, state="readonly", width=60
        )
        db_path_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        location_frame.grid_columnconfigure(1, weight=1)

        # Boutons d'action
        actions_frame = ttk.LabelFrame(data_frame, text="Actions", padding="10")
        actions_frame.pack(fill="x", pady=(0, 20))

        # Bouton changer de base
        ttk.Button(
            actions_frame, text="Changer de base...", command=self.change_database
        ).pack(side="left", padx=(0, 10))

        # Bouton créer nouvelle base
        ttk.Button(
            actions_frame,
            text="Créer nouvelle base...",
            command=self.create_new_database,
        ).pack(side="left")

        # Bases récentes avec mise en page améliorée
        recent_frame = ttk.LabelFrame(data_frame, text="Bases récentes", padding="10")
        recent_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Frame principal avec grille pour la liste et les boutons
        recent_main_frame = ttk.Frame(recent_frame)
        recent_main_frame.pack(fill="both", expand=True)
        recent_main_frame.grid_columnconfigure(0, weight=1)
        recent_main_frame.grid_rowconfigure(0, weight=1)

        # Frame pour la liste avec scrollbar
        list_frame = ttk.Frame(recent_main_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        # Liste des bases récentes
        self.recent_listbox = tk.Listbox(list_frame, height=8)
        recent_scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.recent_listbox.yview
        )
        self.recent_listbox.configure(yscrollcommand=recent_scroll.set)

        self.recent_listbox.grid(row=0, column=0, sticky="nsew")
        recent_scroll.grid(row=0, column=1, sticky="ns")

        # Frame pour les boutons (vertical à droite)
        buttons_frame = ttk.Frame(recent_main_frame)
        buttons_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))

        # Boutons empilés verticalement
        ttk.Button(
            buttons_frame,
            text="Ouvrir\nsélectionnée",
            command=self.open_selected_recent,
            width=12,
        ).pack(pady=(0, 5))

        ttk.Button(
            buttons_frame, text="Actualiser", command=self.refresh_recent_list, width=12
        ).pack(pady=(0, 5))

        ttk.Button(
            buttons_frame,
            text="Effacer\nliste",
            command=self.clear_recent_databases,
            width=12,
        ).pack(pady=(0, 5))

        # Séparateur
        ttk.Separator(buttons_frame, orient="horizontal").pack(fill="x", pady=10)

        # Bouton pour retirer une base sélectionnée
        ttk.Button(
            buttons_frame,
            text="Retirer\nsélectionnée",
            command=self.remove_selected_recent,
            width=12,
        ).pack(pady=(5, 0))

        # Affichage du répertoire d'images
        images_frame = ttk.LabelFrame(
            data_frame, text="Répertoire des images générées", padding="10"
        )
        images_frame.pack(fill="x", pady=(0, 20))

        # Répertoire principal des images (IMAGES_COLLECTE) - LECTURE SEULE
        ttk.Label(
            images_frame,
            text="IMAGES_COLLECTE (défini dans .env):",
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        images_main_frame = ttk.Frame(images_frame)
        images_main_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        images_main_frame.grid_columnconfigure(0, weight=1)

        # Variable pour afficher le chemin des images (lecture seule)
        self.images_path_var = tk.StringVar()
        current_images_path = (
            os.getenv("IMAGES_COLLECTE") or "E:/Comfyui_G11/ComfyUI/output"
        )
        self.images_path_var.set(current_images_path)

        # Champ en lecture seule avec style différent pour indiquer qu'il n'est pas modifiable
        images_entry = ttk.Entry(
            images_main_frame,
            textvariable=self.images_path_var,
            state="readonly",
            width=70,
            font=("Consolas", 9),
        )
        images_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Seul bouton : ouvrir l'explorateur
        ttk.Button(
            images_main_frame,
            text="🗂️ Ouvrir l'explorateur",
            command=self.open_images_in_explorer,
            width=18,
        ).grid(row=0, column=1)

        # Note explicative
        note_label = ttk.Label(
            images_frame,
            text="� Ce répertoire est configuré dans le fichier .env et ne peut pas être modifié depuis l'interface.",
            font=("TkDefaultFont", 8),
            foreground="gray",
        )
        note_label.grid(row=2, column=0, sticky="w", pady=(10, 0))

        images_frame.grid_columnconfigure(0, weight=1)

        # Statistiques
        stats_frame = ttk.LabelFrame(data_frame, text="Statistiques", padding="10")
        stats_frame.pack(fill="x")

        self.stats_text = tk.StringVar()
        ttk.Label(stats_frame, textvariable=self.stats_text).pack(anchor="w")

        # Mettre à jour les données
        self.update_database_stats()
        self.refresh_recent_list()

    def setup_executions_tab(self, parent):
        """Configuration de l'onglet suivi des exécutions"""
        exec_frame = ttk.Frame(parent, padding="10")
        exec_frame.pack(fill="both", expand=True)

        # Titre
        ttk.Label(
            exec_frame,
            text="Suivi des Exécutions de Workflows",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(pady=(0, 20))

        # Frame pour les contrôles
        controls_frame = ttk.Frame(exec_frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        # Bouton pour effacer l'historique
        ttk.Button(
            controls_frame,
            text="Effacer l'historique",
            command=self.clear_execution_history,
        ).pack(side="right")

        # Frame conteneur pour le TreeView et ses scrollbars
        tree_frame = ttk.Frame(exec_frame)
        tree_frame.pack(fill="both", expand=True, pady=(0, 5))

        # TreeView pour afficher les exécutions
        columns = ("id", "prompt", "status", "progress", "timestamp")
        self.executions_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=10
        )

        # Configuration des colonnes
        self.executions_tree.heading("id", text="ID Exécution")
        self.executions_tree.heading("prompt", text="Nom du Prompt")
        self.executions_tree.heading("status", text="Statut")
        self.executions_tree.heading("progress", text="Progression")
        self.executions_tree.heading("timestamp", text="Démarré à")

        # Largeurs des colonnes
        self.executions_tree.column("id", width=100)
        self.executions_tree.column("prompt", width=200)
        self.executions_tree.column("status", width=200)
        self.executions_tree.column("progress", width=100)
        self.executions_tree.column("timestamp", width=150)

        # Scrollbars pour le TreeView
        exec_v_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.executions_tree.yview
        )
        exec_h_scrollbar = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.executions_tree.xview
        )
        self.executions_tree.configure(
            yscrollcommand=exec_v_scrollbar.set, xscrollcommand=exec_h_scrollbar.set
        )

        # Pack du TreeView avec scrollbars
        self.executions_tree.grid(row=0, column=0, sticky="nsew")
        exec_v_scrollbar.grid(row=0, column=1, sticky="ns")
        exec_h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configuration des poids pour le redimensionnement
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Frame pour les détails de l'exécution sélectionnée
        details_frame = ttk.LabelFrame(
            exec_frame, text="Détails de l'exécution", padding="10"
        )
        details_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Text widget pour les détails avec scrollbar
        details_text_frame = ttk.Frame(details_frame)
        details_text_frame.pack(fill="both", expand=True)

        self.execution_details = tk.Text(
            details_text_frame, height=12, wrap="word", state="disabled"
        )
        details_scrollbar = ttk.Scrollbar(
            details_text_frame, orient="vertical", command=self.execution_details.yview
        )
        self.execution_details.configure(yscrollcommand=details_scrollbar.set)

        self.execution_details.pack(side="left", fill="both", expand=True)
        details_scrollbar.pack(side="right", fill="y")

        # Bind pour la sélection
        self.executions_tree.bind("<<TreeviewSelect>>", self.on_execution_select)

    def setup_images_tab(self, parent):
        """Configuration de l'onglet explorateur d'images avec sous-onglets"""
        # Créer un notebook pour les sous-onglets
        images_notebook = ttk.Notebook(parent)
        images_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Sous-onglet 1: Images du prompt sélectionné
        prompt_images_frame = ttk.Frame(images_notebook)
        images_notebook.add(prompt_images_frame, text="📋 Images du prompt")

        # Sous-onglet 2: Galerie complète
        gallery_frame = ttk.Frame(images_notebook)
        images_notebook.add(gallery_frame, text="🖼️ Galerie complète")

        # Configuration du sous-onglet "Images du prompt"
        self.setup_prompt_images_tab(prompt_images_frame)

        # Configuration du sous-onglet "Galerie complète"
        self.setup_gallery_tab(gallery_frame)

        # Bind pour charger la galerie seulement quand l'onglet est sélectionné
        images_notebook.bind("<<NotebookTabChanged>>", self.on_gallery_tab_selected)
        self.images_notebook = images_notebook

    def setup_prompt_images_tab(self, parent):
        """Configuration du sous-onglet images du prompt sélectionné"""
        images_frame = ttk.Frame(parent, padding="10")
        images_frame.pack(fill="both", expand=True)

        # Titre
        ttk.Label(
            images_frame,
            text="Images générées par le prompt sélectionné",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(pady=(0, 10))

        # Frame pour les boutons d'action
        controls_frame = ttk.Frame(images_frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        # Bouton pour ajouter des images
        ttk.Button(
            controls_frame,
            text="Ajouter des images",
            command=self.add_images_to_prompt,
        ).pack(side="left", padx=(0, 5))

        # Bouton pour actualiser la liste
        ttk.Button(
            controls_frame,
            text="Actualiser",
            command=self.refresh_images_list,
        ).pack(side="left", padx=(0, 5))

        # Bouton pour ouvrir le dossier d'images
        ttk.Button(
            controls_frame,
            text="Ouvrir dossier images",
            command=self.open_images_folder,
        ).pack(side="left", padx=(0, 5))

        # Frame principal avec deux parties
        main_frame = ttk.Frame(images_frame)
        main_frame.pack(fill="both", expand=True)

        # Frame gauche pour la liste des images
        left_frame = ttk.LabelFrame(main_frame, text="Liste des images", padding="5")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # TreeView pour la liste des images
        columns = ("filename", "path", "date")
        self.images_tree = ttk.Treeview(
            left_frame, columns=columns, show="headings", height=15
        )

        # Configuration des colonnes
        self.images_tree.heading("filename", text="Nom du fichier")
        self.images_tree.heading("path", text="Chemin")
        self.images_tree.heading("date", text="Date de création")

        # Largeurs des colonnes
        self.images_tree.column("filename", width=200)
        self.images_tree.column("path", width=300)
        self.images_tree.column("date", width=150)

        # Scrollbars pour la liste
        images_v_scrollbar = ttk.Scrollbar(
            left_frame, orient="vertical", command=self.images_tree.yview
        )
        images_h_scrollbar = ttk.Scrollbar(
            left_frame, orient="horizontal", command=self.images_tree.xview
        )
        self.images_tree.configure(
            yscrollcommand=images_v_scrollbar.set, xscrollcommand=images_h_scrollbar.set
        )

        # Pack du TreeView avec scrollbars
        self.images_tree.pack(side="left", fill="both", expand=True)
        images_v_scrollbar.pack(side="right", fill="y")

        # Frame droit pour la prévisualisation
        right_frame = ttk.LabelFrame(main_frame, text="Prévisualisation", padding="5")
        right_frame.pack(side="right", fill="y", padx=(5, 0))
        right_frame.configure(width=350)  # Largeur fixe pour la prévisualisation

        # Label pour l'image de prévisualisation
        self.preview_label = ttk.Label(
            right_frame, text="Sélectionnez une image\npour la prévisualiser"
        )
        self.preview_label.pack(pady=10)

        # Boutons pour actions sur l'image sélectionnée
        preview_buttons_frame = ttk.Frame(right_frame)
        preview_buttons_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            preview_buttons_frame,
            text="Agrandir",
            command=self.enlarge_selected_image,
        ).pack(fill="x", pady=(0, 5))

        ttk.Button(
            preview_buttons_frame,
            text="Ouvrir avec...",
            command=self.open_selected_image,
        ).pack(fill="x", pady=(0, 5))

        ttk.Button(
            preview_buttons_frame,
            text="Supprimer de la liste",
            command=self.remove_selected_image,
        ).pack(fill="x", pady=(0, 5))

        # Bind pour la sélection d'image
        self.images_tree.bind("<<TreeviewSelect>>", self.on_image_select)

        # Variable pour stocker l'image courante
        self.current_preview_image = None

    def setup_gallery_tab(self, parent):
        """Configuration du sous-onglet galerie complète"""
        gallery_frame = ttk.Frame(parent, padding="10")
        gallery_frame.pack(fill="both", expand=True)

        # Titre et contrôles
        header_frame = ttk.Frame(gallery_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header_frame,
            text="Galerie complète - Toutes les images du répertoire IMAGES_COLLECTE",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(side="left")

        # Boutons de contrôle
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side="right")

        ttk.Button(
            controls_frame,
            text="🔄 Actualiser",
            command=self.refresh_gallery_with_scan,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            controls_frame,
            text="⚡ Recharger index",
            command=self.force_refresh_gallery,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            controls_frame,
            text="📊 Statistiques",
            command=self.show_gallery_stats,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            controls_frame,
            text="📁 Ouvrir dossier",
            command=self.open_images_folder,
        ).pack(side="left")

        # Barre de boutons contextuels (cachée par défaut)
        self.gallery_context_frame = ttk.Frame(gallery_frame)
        self.gallery_context_frame.pack(fill="x", pady=(0, 10))

        # Label pour l'image sélectionnée
        self.gallery_selected_label = ttk.Label(
            self.gallery_context_frame,
            text="",
            font=("TkDefaultFont", 10, "bold"),
            foreground="blue",
        )
        self.gallery_selected_label.pack(side="left")

        # Boutons contextuels
        context_buttons_frame = ttk.Frame(self.gallery_context_frame)
        context_buttons_frame.pack(side="right")

        ttk.Button(
            context_buttons_frame,
            text="🗑️ Marquer supprimée",
            command=self.mark_gallery_image_deleted,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            context_buttons_frame,
            text="♻️ Restaurer",
            command=self.restore_gallery_image,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            context_buttons_frame,
            text="🗑️ Supprimer définitivement",
            command=self.delete_selected_gallery_image,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            context_buttons_frame,
            text="📁 Ouvrir avec...",
            command=self.open_selected_gallery_image,
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            context_buttons_frame,
            text="📋 Copier chemin",
            command=self.copy_selected_gallery_path,
        ).pack(side="left")

        # Cacher la barre par défaut
        self.gallery_context_frame.pack_forget()

        # Frame pour la grille d'images avec scrollbar
        gallery_container = ttk.Frame(gallery_frame)
        gallery_container.pack(fill="both", expand=True)

        # Canvas pour permettre le scroll
        self.gallery_canvas = tk.Canvas(gallery_container, bg="white")
        gallery_scrollbar = ttk.Scrollbar(
            gallery_container, orient="vertical", command=self.gallery_canvas.yview
        )
        self.gallery_scrollable_frame = ttk.Frame(self.gallery_canvas)

        # Configuration du scroll
        self.gallery_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.gallery_canvas.configure(
                scrollregion=self.gallery_canvas.bbox("all")
            ),
        )

        self.gallery_canvas.create_window(
            (0, 0), window=self.gallery_scrollable_frame, anchor="nw"
        )
        self.gallery_canvas.configure(yscrollcommand=gallery_scrollbar.set)

        # Pack du canvas et scrollbar
        self.gallery_canvas.pack(side="left", fill="both", expand=True)
        gallery_scrollbar.pack(side="right", fill="y")

        # Bind scroll de la souris
        self.gallery_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.gallery_canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            ),
        )

        # Variables pour la galerie
        self.gallery_images = []
        self.gallery_thumbnails = {}
        self.gallery_loaded = False
        self.selected_gallery_image = None
        self.selected_gallery_button = None

        # Message d'information pour charger la galerie
        info_label = ttk.Label(
            self.gallery_scrollable_frame,
            text="🖼️ Cliquez sur 'Actualiser' pour charger la galerie d'images",
            font=("TkDefaultFont", 10),
            foreground="blue",
        )
        info_label.grid(row=0, column=0, columnspan=5, pady=20)

        # NE PAS charger la galerie au démarrage pour éviter les erreurs
        # self.refresh_gallery() - sera appelé plus tard

    def refresh_gallery(self):
        """Actualiser la galerie complète (rapide - utilise l'index)"""
        try:
            # Réinitialiser la sélection
            self.selected_gallery_image = None
            self.selected_gallery_button = None
            self.gallery_context_frame.pack_forget()

            # Vider les anciennes images
            for widget in self.gallery_scrollable_frame.winfo_children():
                widget.destroy()

            self.gallery_images.clear()
            self.gallery_thumbnails.clear()

            # Obtenir le répertoire IMAGES_COLLECTE
            images_dir = os.getenv("IMAGES_COLLECTE")
            if not images_dir or not os.path.exists(images_dir):
                error_label = ttk.Label(
                    self.gallery_scrollable_frame,
                    text="❌ Répertoire IMAGES_COLLECTE non trouvé ou invalide",
                    foreground="red",
                )
                error_label.grid(row=0, column=0, columnspan=5, pady=20)
                return

            # Utiliser l'index optimisé au lieu du scan de fichiers
            print("🔄 Chargement depuis l'index...")
            indexed_images = self.image_index.get_images(
                images_dir, include_deleted=True
            )

            if not indexed_images:
                info_label = ttk.Label(
                    self.gallery_scrollable_frame,
                    text="📁 Aucune image dans l'index. Cliquez sur 'Actualiser' pour scanner.",
                    foreground="orange",
                )
                info_label.grid(row=0, column=0, columnspan=5, pady=20)
                return

            # Créer la grille optimisée depuis l'index
            self.create_gallery_grid_from_index(indexed_images)

            # Mettre à jour le statut
            active_count = sum(1 for img in indexed_images if not img["is_deleted"])
            deleted_count = sum(1 for img in indexed_images if img["is_deleted"])

            status_text = f"Galerie: {active_count} images"
            if deleted_count > 0:
                status_text += f" ({deleted_count} supprimées)"

            self.update_status(status_text)

        except Exception as e:
            print(f"❌ Erreur lors du rafraîchissement de la galerie: {e}")
            error_label = ttk.Label(
                self.gallery_scrollable_frame,
                text=f"❌ Erreur: {str(e)}",
                foreground="red",
            )
            error_label.grid(row=0, column=0, columnspan=5, pady=20)

    def refresh_gallery_with_scan(self):
        """Actualiser la galerie avec scan des fichiers (plus lent mais complet)"""
        try:
            images_dir = os.getenv("IMAGES_COLLECTE")
            if not images_dir or not os.path.exists(images_dir):
                messagebox.showerror("Erreur", "Répertoire IMAGES_COLLECTE non trouvé")
                return

            # Afficher un message de progression
            progress_label = ttk.Label(
                self.gallery_scrollable_frame,
                text="⏳ Scan en cours... Veuillez patienter",
                foreground="blue",
            )
            progress_label.grid(row=0, column=0, columnspan=5, pady=20)
            self.root.update()

            # Scanner et indexer les fichiers
            stats = self.image_index.scan_directory(images_dir)

            # Afficher les résultats du scan
            if "error" in stats:
                messagebox.showerror("Erreur", f"Erreur lors du scan: {stats['error']}")
            else:
                info_msg = f"Scan terminé:\n"
                info_msg += f"• {stats['total_files']} fichiers traités\n"
                info_msg += f"• {stats['new_files']} nouveaux\n"
                info_msg += f"• {stats['updated_files']} mis à jour\n"
                info_msg += f"• {stats['deleted_files']} supprimés\n"
                info_msg += f"• Temps: {stats['scan_time']:.2f}s"

                messagebox.showinfo("Scan terminé", info_msg)

            # Actualiser l'affichage
            self.refresh_gallery()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du scan: {str(e)}")

    def force_refresh_gallery(self):
        """Forcer la régénération complète de l'index"""
        try:
            images_dir = os.getenv("IMAGES_COLLECTE")
            if not images_dir or not os.path.exists(images_dir):
                messagebox.showerror("Erreur", "Répertoire IMAGES_COLLECTE non trouvé")
                return

            result = messagebox.askyesno(
                "Confirmation",
                "Régénérer complètement l'index ?\n\n"
                "Cela peut prendre du temps selon le nombre d'images.",
                icon="question",
            )

            if result:
                # Vider le cache
                self.image_index.clear_cache()

                # Forcer le scan complet
                progress_label = ttk.Label(
                    self.gallery_scrollable_frame,
                    text="⚡ Régénération de l'index... Veuillez patienter",
                    foreground="blue",
                )
                progress_label.grid(row=0, column=0, columnspan=5, pady=20)
                self.root.update()

                stats = self.image_index.scan_directory(images_dir, force_refresh=True)

                info_msg = f"Index régénéré:\n"
                info_msg += f"• {stats['total_files']} fichiers traités\n"
                info_msg += f"• Temps: {stats['scan_time']:.2f}s"

                messagebox.showinfo("Régénération terminée", info_msg)

                # Actualiser l'affichage
                self.refresh_gallery()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la régénération: {str(e)}")

    def create_gallery_grid_from_index(self, indexed_images):
        """Créer la grille d'images optimisée depuis l'index"""
        try:
            row = 0
            col = 0

            for i, image_data in enumerate(indexed_images):
                try:
                    file_path = image_data["file_path"]
                    is_deleted = image_data["is_deleted"]

                    # Créer le frame pour chaque image
                    image_frame = ttk.Frame(self.gallery_scrollable_frame, padding="5")
                    image_frame.grid(row=row, column=col, padx=5, pady=5, sticky="w")

                    # Obtenir la miniature depuis l'index (beaucoup plus rapide)
                    photo = self.image_index.get_thumbnail(file_path)

                    if photo is None:
                        # Créer une miniature par défaut si problème
                        photo = self._create_default_thumbnail(is_deleted)

                    # Stocker la référence
                    self.gallery_thumbnails[file_path] = photo

                    # Créer le bouton image cliquable
                    image_button = tk.Button(
                        image_frame,
                        image=photo,
                        border=2,
                        relief="raised",
                        bg="white" if not is_deleted else "#f0f0f0",
                    )
                    image_button.pack()

                    # Modifier les couleurs si image supprimée
                    if is_deleted:
                        image_button.configure(bg="#ffe6e6", activebackground="#ffcccc")

                    # Bindings pour sélection et agrandissement
                    image_button.bind(
                        "<Button-1>",
                        lambda e, path=file_path, btn=image_button: self.select_gallery_image(
                            path, btn
                        ),
                    )
                    image_button.bind(
                        "<Double-Button-1>",
                        lambda e, path=file_path: self.enlarge_gallery_image(path),
                    )

                    # Ajouter le nom du fichier avec indicateur de statut
                    filename = image_data["file_name"]
                    if len(filename) > 20:
                        filename = filename[:17] + "..."

                    if is_deleted:
                        filename = f"🗑️ {filename}"

                    ttk.Label(
                        image_frame,
                        text=filename,
                        font=("TkDefaultFont", 8),
                        justify="center",
                        foreground="gray" if is_deleted else "black",
                    ).pack(pady=(2, 0))

                    # Passer à la colonne suivante
                    col += 1
                    if col >= 5:  # 5 colonnes
                        col = 0
                        row += 1

                except Exception as e:
                    print(
                        f"Erreur lors du traitement de l'image {image_data.get('file_path', 'unknown')}: {e}"
                    )
                    continue

        except Exception as e:
            print(f"Erreur lors de la création de la grille depuis l'index: {e}")

    def _create_default_thumbnail(self, is_deleted=False):
        """Créer une miniature par défaut"""
        try:
            if is_deleted:
                return self.image_index._create_trash_icon()
            else:
                # Image par défaut pour erreur de chargement
                img = Image.new("RGB", (150, 150), (200, 200, 200))
                from PIL import ImageDraw

                draw = ImageDraw.Draw(img)
                draw.text((50, 70), "❌\nErreur", fill=(100, 100, 100))
                return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def create_gallery_grid(self, image_files):
        """Créer la grille d'images 5 colonnes"""
        try:
            row = 0
            col = 0
            thumbnail_size = (150, 150)

            for i, image_path in enumerate(image_files):
                try:
                    # Créer le frame pour chaque image
                    image_frame = ttk.Frame(self.gallery_scrollable_frame, padding="5")
                    image_frame.grid(row=row, column=col, padx=5, pady=5, sticky="w")

                    # Créer la miniature
                    image = Image.open(image_path)
                    image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)

                    # Stocker la référence
                    self.gallery_thumbnails[image_path] = photo

                    # Créer le bouton image cliquable
                    image_button = tk.Button(
                        image_frame, image=photo, border=2, relief="raised", bg="white"
                    )
                    image_button.pack()

                    # Bindings pour sélection et agrandissement
                    image_button.bind(
                        "<Button-1>",
                        lambda e, path=image_path, btn=image_button: self.select_gallery_image(
                            path, btn
                        ),
                    )
                    image_button.bind(
                        "<Double-Button-1>",
                        lambda e, path=image_path: self.enlarge_gallery_image(path),
                    )

                    # Ajouter le nom du fichier
                    filename = os.path.basename(image_path)
                    if len(filename) > 20:
                        filename = filename[:17] + "..."

                    ttk.Label(
                        image_frame,
                        text=filename,
                        font=("TkDefaultFont", 8),
                        justify="center",
                    ).pack(pady=(2, 0))

                    # Passer à la colonne suivante
                    col += 1
                    if col >= 5:  # 5 colonnes
                        col = 0
                        row += 1

                except Exception as e:
                    print(f"Erreur lors du traitement de l'image {image_path}: {e}")
                    continue

        except Exception as e:
            print(f"Erreur lors de la création de la grille: {e}")

    def enlarge_gallery_image(self, image_path):
        """Agrandir une image de la galerie dans une nouvelle fenêtre"""
        try:
            # Créer une nouvelle fenêtre
            enlarge_window = tk.Toplevel(self.root)
            enlarge_window.title(f"Image: {os.path.basename(image_path)}")
            enlarge_window.geometry("800x600")

            # Centrer la fenêtre
            enlarge_window.transient(self.root)
            enlarge_window.grab_set()
            center_window(enlarge_window, 800, 600)

            # Frame principal avec scrollbars
            main_frame = ttk.Frame(enlarge_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Canvas pour l'image avec scrollbars
            canvas = tk.Canvas(main_frame, bg="white")
            v_scrollbar = ttk.Scrollbar(
                main_frame, orient="vertical", command=canvas.yview
            )
            h_scrollbar = ttk.Scrollbar(
                main_frame, orient="horizontal", command=canvas.xview
            )

            # Frame pour l'image
            image_frame = ttk.Frame(canvas)

            # Charger et afficher l'image
            image = Image.open(image_path)

            # Redimensionner si trop grande (max 1200x800)
            max_size = (1200, 800)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image)

            image_label = ttk.Label(image_frame, image=photo)
            image_label.image = photo  # Garder une référence
            image_label.pack()

            # Configuration du canvas
            canvas.create_window((0, 0), window=image_frame, anchor="nw")
            canvas.configure(
                yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
            )

            # Pack des éléments
            canvas.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")

            # Frame pour les boutons
            buttons_frame = ttk.Frame(enlarge_window)
            buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

            # Boutons d'action
            ttk.Button(
                buttons_frame,
                text="📁 Ouvrir avec...",
                command=lambda: self.open_image_with_default(image_path),
            ).pack(side="left", padx=(0, 5))

            ttk.Button(
                buttons_frame,
                text="📋 Copier chemin",
                command=lambda: self.copy_path_to_clipboard(image_path),
            ).pack(side="left", padx=(0, 5))

            ttk.Button(
                buttons_frame, text="❌ Fermer", command=enlarge_window.destroy
            ).pack(side="right")

            # Informations sur l'image
            info_text = f"Fichier: {os.path.basename(image_path)}\n"
            info_text += f"Taille: {image.size[0]}x{image.size[1]} pixels\n"
            try:
                file_size = os.path.getsize(image_path) / 1024  # KB
                info_text += f"Poids: {file_size:.1f} KB"
            except:
                pass

            ttk.Label(buttons_frame, text=info_text, font=("TkDefaultFont", 8)).pack(
                side="left", padx=20
            )

            # Mise à jour de la region de scroll
            image_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'image:\n{str(e)}")

    def open_image_with_default(self, image_path):
        """Ouvrir une image avec l'application par défaut"""
        try:
            if os.name == "nt":  # Windows
                os.startfile(image_path)
            else:  # Linux/Mac
                subprocess.run(["xdg-open", image_path])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'image:\n{str(e)}")

    def select_gallery_image(self, image_path, button):
        """Sélectionner une image dans la galerie"""
        try:
            # Désélectionner l'image précédente
            if self.selected_gallery_button:
                self.selected_gallery_button.configure(
                    relief="raised",
                    bg="white",
                    highlightbackground="white",
                    highlightcolor="white",
                    highlightthickness=0,
                )

            # Sélectionner la nouvelle image
            self.selected_gallery_image = image_path
            self.selected_gallery_button = button

            # Mettre en évidence l'image sélectionnée
            button.configure(
                relief="solid",
                bg="#e6f3ff",
                highlightbackground="#0078d4",
                highlightcolor="#0078d4",
                highlightthickness=3,
            )

            # Afficher la barre de boutons contextuels
            filename = os.path.basename(image_path)
            if len(filename) > 50:
                filename = filename[:47] + "..."
            self.gallery_selected_label.config(text=f"📸 Sélectionnée: {filename}")
            self.gallery_context_frame.pack(
                fill="x",
                pady=(0, 10),
                after=self.gallery_context_frame.master.winfo_children()[0],
            )

        except Exception as e:
            print(f"Erreur lors de la sélection d'image: {e}")

    def delete_selected_gallery_image(self):
        """Supprimer l'image sélectionnée dans la galerie"""
        if not self.selected_gallery_image:
            messagebox.showwarning("Attention", "Aucune image sélectionnée")
            return

        try:
            filename = os.path.basename(self.selected_gallery_image)
            result = messagebox.askyesno(
                "Confirmer la suppression",
                f"Êtes-vous sûr de vouloir supprimer définitivement l'image ?\n\n{filename}\n\n⚠️ Cette action est irréversible !",
                icon="warning",
            )

            if result:
                # Supprimer le fichier
                os.remove(self.selected_gallery_image)

                # Masquer la barre contextuelle
                self.gallery_context_frame.pack_forget()

                # Actualiser la galerie
                self.refresh_gallery()

                # Réinitialiser la sélection
                self.selected_gallery_image = None
                self.selected_gallery_button = None

                messagebox.showinfo(
                    "Succès", f"L'image '{filename}' a été supprimée avec succès."
                )

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Impossible de supprimer l'image:\n{str(e)}"
            )

    def open_selected_gallery_image(self):
        """Ouvrir l'image sélectionnée avec l'application par défaut"""
        if not self.selected_gallery_image:
            messagebox.showwarning("Attention", "Aucune image sélectionnée")
            return
        self.open_image_with_default(self.selected_gallery_image)

    def copy_selected_gallery_path(self):
        """Copier le chemin de l'image sélectionnée vers le presse-papier"""
        if not self.selected_gallery_image:
            messagebox.showwarning("Attention", "Aucune image sélectionnée")
            return
        self.copy_path_to_clipboard(self.selected_gallery_image)

    def mark_gallery_image_deleted(self):
        """Marquer une image comme supprimée (soft delete)"""
        if not self.selected_gallery_image:
            messagebox.showwarning("Attention", "Aucune image sélectionnée")
            return

        try:
            filename = os.path.basename(self.selected_gallery_image)
            result = messagebox.askyesno(
                "Marquer comme supprimée",
                f"Marquer l'image comme supprimée ?\n\n{filename}\n\n"
                "L'image sera cachée mais le fichier restera sur le disque.",
                icon="question",
            )

            if result:
                # Marquer comme supprimée dans l'index
                self.image_index.mark_deleted(self.selected_gallery_image)

                # Actualiser l'affichage
                self.refresh_gallery()

                messagebox.showinfo(
                    "Succès", f"L'image '{filename}' a été marquée comme supprimée."
                )

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de marquer l'image: {str(e)}")

    def restore_gallery_image(self):
        """Restaurer une image marquée comme supprimée"""
        if not self.selected_gallery_image:
            messagebox.showwarning("Attention", "Aucune image sélectionnée")
            return

        try:
            filename = os.path.basename(self.selected_gallery_image)

            # Vérifier si l'image est marquée comme supprimée
            images = self.image_index.get_images(
                os.path.dirname(self.selected_gallery_image), include_deleted=True
            )

            selected_image = next(
                (
                    img
                    for img in images
                    if img["file_path"] == self.selected_gallery_image
                ),
                None,
            )

            if not selected_image or not selected_image["is_deleted"]:
                messagebox.showinfo(
                    "Information", "Cette image n'est pas marquée comme supprimée."
                )
                return

            result = messagebox.askyesno(
                "Restaurer l'image",
                f"Restaurer l'image ?\n\n{filename}\n\n"
                "L'image redeviendra visible dans la galerie.",
                icon="question",
            )

            if result:
                # Restaurer dans l'index
                self.image_index.restore_deleted(self.selected_gallery_image)

                # Actualiser l'affichage
                self.refresh_gallery()

                messagebox.showinfo("Succès", f"L'image '{filename}' a été restaurée.")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de restaurer l'image: {str(e)}")

    def show_gallery_stats(self):
        """Afficher les statistiques de la galerie"""
        try:
            stats = self.image_index.get_stats()
            perf_info = self.fast_processor.get_performance_info()

            stats_text = "📊 STATISTIQUES DE LA GALERIE\n"
            stats_text += "=" * 40 + "\n\n"

            stats_text += f"📸 Images totales: {stats.get('total_images', 0)}\n"
            stats_text += f"✅ Images actives: {stats.get('active_images', 0)}\n"
            stats_text += f"🗑️ Images supprimées: {stats.get('deleted_images', 0)}\n"
            stats_text += f"💾 Taille totale: {stats.get('total_size_mb', 0)} MB\n"
            stats_text += (
                f"🧠 Cache mémoire: {stats.get('cache_size', 0)} miniatures\n\n"
            )

            stats_text += "⚡ PERFORMANCE\n"
            stats_text += "-" * 20 + "\n"
            stats_text += f"Backend: {perf_info['backend']}\n"
            stats_text += f"Vitesse: {perf_info['estimated_speed']}\n"

            if perf_info["recommended_action"] != "Aucune":
                stats_text += f"Recommandation: {perf_info['recommended_action']}\n"

            # Afficher dans une fenêtre popup
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Statistiques de la galerie")
            stats_window.geometry("500x400")
            stats_window.transient(self.root)
            stats_window.grab_set()

            # Centrer la fenêtre
            center_window(stats_window, 500, 400)

            # Zone de texte avec scrollbar
            text_frame = ttk.Frame(stats_window)
            text_frame.pack(fill="both", expand=True, padx=10, pady=10)

            text_widget = tk.Text(text_frame, wrap="word", font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(
                text_frame, orient="vertical", command=text_widget.yview
            )
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            text_widget.insert("1.0", stats_text)
            text_widget.configure(state="disabled")

            # Boutons d'action
            buttons_frame = ttk.Frame(stats_window)
            buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

            ttk.Button(
                buttons_frame,
                text="🧹 Vider le cache",
                command=lambda: self._clear_cache_and_refresh(stats_window),
            ).pack(side="left", padx=(0, 5))

            ttk.Button(
                buttons_frame, text="❌ Fermer", command=stats_window.destroy
            ).pack(side="right")

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Impossible d'afficher les statistiques: {str(e)}"
            )

    def _clear_cache_and_refresh(self, parent_window):
        """Vider le cache et actualiser"""
        try:
            self.image_index.clear_cache()
            messagebox.showinfo("Cache vidé", "Le cache mémoire a été vidé.")
            parent_window.destroy()
            self.refresh_gallery()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de vider le cache: {str(e)}")

    def on_gallery_tab_selected(self, event):
        """Callback appelé quand un sous-onglet des images est sélectionné"""
        try:
            # Ne rien faire si la galerie n'est pas encore configurée
            if not hasattr(self, "gallery_scrollable_frame"):
                return

            notebook = event.widget
            selected_tab_id = notebook.select()
            tab_text = notebook.tab(selected_tab_id, "text")

            # Afficher un message informatif mais ne pas charger automatiquement
            if "Galerie complète" in tab_text and not self.gallery_loaded:
                print(
                    "🖼️ Onglet galerie sélectionné - Cliquez sur 'Actualiser' pour charger"
                )
                # Ne pas charger automatiquement pour laisser l'utilisateur choisir
                # self.refresh_gallery()
                # self.gallery_loaded = True
        except Exception as e:
            print(f"Erreur lors du changement d'onglet: {e}")

    def copy_path_to_clipboard(self, path):
        """Copier le chemin vers le presse-papier"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            self.update_status(f"Chemin copié: {os.path.basename(path)}")
        except Exception as e:
            print(f"Erreur copie presse-papier: {e}")

    def setup_status_bar(self):
        """Configuration de la barre de statut"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill="x", side="bottom")

        self.status_text = tk.StringVar()
        self.status_text.set("Prêt")
        ttk.Label(self.status_bar, textvariable=self.status_text).pack(
            side="left", padx=5
        )

        # Indicateur d'exécution
        self.execution_text = tk.StringVar()
        self.execution_text.set("")
        ttk.Label(self.status_bar, textvariable=self.execution_text).pack(
            side="right", padx=5
        )

    def load_prompts(self):
        """Charger tous les prompts dans le tableau"""
        # Effacer le tableau
        for item in self.prompts_tree.get_children():
            self.prompts_tree.delete(item)

        try:
            prompts = self.db_manager.get_all_prompts()
            for prompt_id, name, parent, model, workflow, status, comment, id_env in prompts:
                self.prompts_tree.insert(
                    "",
                    "end",
                    iid=str(prompt_id),
                    values=(prompt_id, name, status, model, comment, parent or "", id_env or ""),
                )

            self.update_status(f"{len(prompts)} prompts chargés")
            # Mettre à jour les statistiques après chargement
            if hasattr(self, "stats_text"):
                self.update_database_stats()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les prompts: {e}")

    def on_prompt_select(self, event):
        """Gestionnaire de sélection de prompt"""
        selection = self.prompts_tree.selection()
        if selection:
            self.selected_prompt_id = int(selection[0])
            self.load_prompt_details(self.selected_prompt_id)

    def on_prompt_double_click(self, event):
        """Gestionnaire de double-clic sur un prompt"""
        if self.selected_prompt_id:
            self.edit_prompt()

    def load_prompt_details(self, prompt_id):
        """
        Charger les détails d'un prompt - Fonction initiale: load_prompt_details
        1) Panel détaillé
        """
        try:
            data = self.db_manager.get_prompt_by_id(prompt_id)
            if data:
                name, prompt_values, workflow, url, parent, model, comment, status, file, id_env = (
                    data
                )

                # Mettre à jour les informations générales
                self.name_var.set(name or "")
                self.url_var.set(url or "")
                self.comment_var.set(comment or "")
                self.model_var.set(model or "")
                self.status_var.set(status or "new")

                # Nouveaux champs
                if hasattr(self, "file_var"):
                    self.file_var.set(file or "")
                if hasattr(self, "id_env_var"):
                    self.id_env_var.set(id_env or "")

                # 1.1) Charger les prompt_values dans le tableau
                self.table_manager.load_prompt_values_data(
                    self.values_tree, prompt_values or "{}"
                )

                # 1.2) Charger le workflow dans le tableau
                self.table_manager.load_workflow_data(
                    self.workflow_tree, workflow or "{}"
                )

                self.update_status(f"Prompt '{name}' chargé")

                # Mettre à jour les détails dans l'onglet Détails
                if hasattr(self, "id_label"):
                    self.id_label.config(text=str(prompt_id))
                if hasattr(self, "name_label"):
                    self.name_label.config(text=name or "")
                if hasattr(self, "model_label"):
                    self.model_label.config(text=model or "")
                if hasattr(self, "status_label"):
                    self.status_label.config(text=status or "")
                if hasattr(self, "parent_label"):
                    self.parent_label.config(text=parent or "")

                # Actualiser la liste des images pour ce prompt
                self.refresh_images_list()

            # Le commentaire est maintenant géré par self.comment_var dans l'onglet Info
            # Plus besoin de manipuler directement un widget Text

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les détails: {e}")

    def on_data_change(self):
        """Callback appelé quand les données sont modifiées"""
        self.update_status("Données modifiées - Pensez à sauvegarder")

    def save_current_info(self):
        """Sauvegarder les informations du prompt actuel"""
        if not self.selected_prompt_id:
            messagebox.showwarning("Attention", "Aucun prompt sélectionné.")
            return

        try:
            name = self.name_var.get().strip()
            url = self.url_var.get().strip()
            comment = self.comment_var.get().strip()
            model = self.model_var.get().strip()
            status = self.status_var.get()
            file = self.file_var.get().strip() if hasattr(self, "file_var") else None
            id_env = self.id_env_var.get().strip() if hasattr(self, "id_env_var") else None

            if not name:
                messagebox.showerror("Erreur", "Le nom est obligatoire.")
                return

            # Récupérer les données JSON des tableaux
            prompt_values_json = self.table_manager.get_prompt_values_json()
            workflow_json = self.table_manager.get_workflow_json()

            # Auto-dériver le modèle si vide
            if not model:
                model = self.db_manager.derive_model_from_workflow(workflow_json)

            # Sauvegarder
            self.db_manager.update_prompt(
                self.selected_prompt_id,
                name,
                prompt_values_json,
                workflow_json,
                url,
                model,
                comment,
                status,
                file,
                id_env,
            )

            # Mettre à jour l'affichage
            self.prompts_tree.item(
                str(self.selected_prompt_id),
                values=(
                    self.selected_prompt_id,
                    name,
                    status,
                    model,
                    comment,
                    self.prompts_tree.item(str(self.selected_prompt_id), "values")[5],
                    id_env or "",
                ),
            )

            self.update_status("Prompt sauvegardé avec succès")
            messagebox.showinfo("Succès", "Prompt sauvegardé avec succès.")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")

    def new_prompt(self):
        """0.5) Créer un nouveau prompt"""

        def on_save():
            old_has_filters = self.has_active_filters()
            self.refresh_prompts_display()

            # Si des filtres étaient actifs, informer l'utilisateur
            if old_has_filters:
                messagebox.showinfo(
                    "Information",
                    "Nouveau prompt créé avec succès !\n\n"
                    "Il se peut que le nouveau prompt ne soit pas visible "
                    "avec les filtres actuels. Vous pouvez modifier les filtres "
                    "ou les réinitialiser pour le voir.",
                )

        self.popup_manager.prompt_form("new", None, on_save)

    def edit_prompt(self):
        """0.2) Éditer un prompt de façon brute"""
        if not self.selected_prompt_id:
            messagebox.showwarning("Attention", "Sélectionnez un prompt à éditer.")
            return

        def on_save():
            self.refresh_prompts_display()
            self.load_prompt_details(self.selected_prompt_id)

        self.popup_manager.prompt_form("edit", self.selected_prompt_id, on_save)

    def inherit_prompt(self):
        """
        0.4) Hériter d'un prompt - Fonction initiale: inherit_prompt
        Dupliquer le prompt et renseigner le parent et modifier le nom
        """
        if not self.selected_prompt_id:
            messagebox.showwarning("Attention", "Sélectionnez un prompt à hériter.")
            return

        try:
            # Récupérer les données du prompt parent
            data = self.db_manager.get_prompt_by_id(self.selected_prompt_id)
            if not data:
                messagebox.showerror(
                    "Erreur", "Impossible de récupérer les données du prompt."
                )
                return

            name, prompt_values, workflow, url, parent, model, comment, status, file, id_env = data

            # Utiliser le même nom que le prompt parent
            new_name = name

            # Créer le nouveau prompt avec parent
            new_id = self.db_manager.create_prompt(
                new_name,
                prompt_values,
                workflow,
                url,
                model,
                "new",
                f"Hérité de: {name}",
                parent=self.selected_prompt_id,
                file=None,  # Pas de fichier exporté pour l'héritage
                id_env=id_env,  # Garder le même environnement
            )

            # Recharger et sélectionner le nouveau prompt (en respectant les filtres)
            self.refresh_prompts_display()

            # Sélectionner le nouveau prompt seulement s'il est visible
            prompt_visible = False
            try:
                self.prompts_tree.selection_set(str(new_id))
                self.prompts_tree.focus(str(new_id))
                prompt_visible = True
            except tk.TclError:
                # Le prompt n'est pas visible à cause des filtres
                prompt_visible = False

            # Informer l'utilisateur
            if prompt_visible:
                self.update_status(f"Prompt hérité créé: {new_name}")
                messagebox.showinfo(
                    "Succès", f"Prompt hérité créé avec succès: {new_name}"
                )
            else:
                self.update_status(f"Prompt hérité créé: {new_name} (filtré)")
                result = messagebox.askyesnocancel(
                    "Prompt créé mais non visible",
                    f"Prompt hérité créé avec succès: {new_name}\n\n"
                    "Le nouveau prompt n'est pas visible avec les filtres actuels.\n\n"
                    "Voulez-vous réinitialiser les filtres pour le voir ?\n"
                    "• Oui: Réinitialiser les filtres\n"
                    "• Non: Garder les filtres actuels\n"
                    "• Annuler: Aller à l'onglet Filtres",
                )

                if result is True:  # Oui - Réinitialiser
                    self.reset_filters()
                    # Essayer de sélectionner le prompt maintenant
                    try:
                        self.prompts_tree.selection_set(str(new_id))
                        self.prompts_tree.focus(str(new_id))
                    except:
                        pass
                elif result is None:  # Annuler - Aller aux filtres
                    # Aller à l'onglet filtres si le notebook existe
                    try:
                        # Trouver le notebook et activer l'onglet filtres
                        for widget in self.root.winfo_children():
                            if isinstance(widget, ttk.PanedWindow):
                                for pane in widget.panes():
                                    pane_widget = widget.nametowidget(pane)
                                    for child in pane_widget.winfo_children():
                                        if isinstance(
                                            child, ttk.LabelFrame
                                        ) and "Détails" in child.cget("text"):
                                            for (
                                                notebook_child
                                            ) in child.winfo_children():
                                                if isinstance(
                                                    notebook_child, ttk.Notebook
                                                ):
                                                    # Activer l'onglet filtres (index 4)
                                                    notebook_child.select(4)
                                                    return
                    except:
                        pass

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'héritage: {e}")

    def delete_prompt(self):
        """0.3) Supprimer un prompt"""
        if not self.selected_prompt_id:
            messagebox.showwarning("Attention", "Sélectionnez un prompt à supprimer.")
            return

        # Récupérer le nom pour confirmation
        item = str(self.selected_prompt_id)
        values = self.prompts_tree.item(item, "values")
        name = values[1] if len(values) > 1 else "Inconnu"

        if messagebox.askyesno(
            "Confirmer", f"Supprimer définitivement le prompt '{name}' ?"
        ):
            try:
                self.db_manager.delete_prompt(self.selected_prompt_id)
                self.prompts_tree.delete(item)

                # Réinitialiser la sélection
                self.selected_prompt_id = None
                self.clear_details()

                self.update_status(f"Prompt '{name}' supprimé")

            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")

    def execute_workflow(self):
        """
        0.6) Exécuter le workflow - Fonction initiale: execute_workflow
        """
        if not self.selected_prompt_id:
            messagebox.showwarning("Attention", "Sélectionnez un prompt à exécuter.")
            return

        # Vérifier qu'un environnement ComfyUI est identifié
        current_env_id = self.comfyui_config_id.get().strip()
        if not current_env_id:
            error_msg = (
                "❌ ERREUR - Environnement ComfyUI non identifié !\n\n"
                "Vous devez d'abord identifier l'environnement ComfyUI avant d'exécuter un workflow.\n\n"
                "📋 Actions requises :\n"
                "1. Aller dans l'onglet 'ComfyUI'\n"
                "2. Cliquer sur '🔍 Identifier l'environnement'\n"
                "3. Vérifier que l'ID de configuration est affiché\n"
                "4. Revenir dans cet onglet pour exécuter le workflow\n\n"
                "⚠️ Cette vérification garantit la traçabilité des images générées."
            )

            messagebox.showerror("Environnement non identifié", error_msg)

            # Mettre à jour le statut
            self.update_status("❌ Échec - Environnement non identifié")
            return

        # L'environnement est identifié, stocker l'ID pour l'utiliser lors de la sauvegarde des images
        self.current_execution_environment_id = current_env_id
        print(f"🌍 Exécution du workflow dans l'environnement : {current_env_id}")

        # Simulation d'exécution (à adapter selon l'implémentation originale)
        try:
            # Récupérer les données
            data = self.db_manager.get_prompt_by_id(self.selected_prompt_id)
            if not data:
                messagebox.showerror(
                    "Erreur", "Impossible de récupérer les données du prompt."
                )
                return

            name, prompt_values, workflow, url, parent, model, comment, status, file, id_env = data

            # Ajouter à la pile d'exécution
            execution_id = f"exec_{int(time.time())}"
            self.add_to_execution_stack(execution_id, "Initialisation", name, 10)

            # Créer un thread pour l'exécution
            thread = threading.Thread(
                target=self._execute_workflow_task,
                args=(self.selected_prompt_id, execution_id),
            )
            thread.daemon = True
            thread.start()

            self.update_status(f"Exécution démarrée pour: {name}")

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Erreur lors du démarrage de l'exécution: {e}"
            )

    def _execute_workflow_task(self, prompt_id, execution_id):
        """Tâche d'exécution du workflow (en thread séparé)"""
        import time  # Import au début de la fonction pour éviter les problèmes de scope

        try:
            # Récupérer les données du prompt
            data = self.db_manager.get_prompt_by_id(prompt_id)
            if not data:
                self.update_execution_stack_status(
                    execution_id, "Erreur: Prompt introuvable", 0
                )
                self.root.after(
                    0,
                    lambda: self.update_prompt_status_after_execution(prompt_id, "nok"),
                )
                return

            name, prompt_values_json, workflow_json, url, parent, model, comment, status, file, id_env = data

            # Mettre à jour le statut
            self.update_execution_stack_status(
                execution_id, f"Préparation des données", 25
            )

            # Créer le répertoire data/Workflows s'il n'existe pas
            os.makedirs("data/Workflows", exist_ok=True)

            # Générer des noms de fichiers uniques dans data/Workflows
            timestamp = int(time.time())
            workflow_file_path = f"data/Workflows/{name}_workflow_{timestamp}.json"
            prompt_values_file_path = f"data/Workflows/{name}_values_{timestamp}.json"

            # Écrire les fichiers directement dans data/Workflows
            with open(workflow_file_path, "w", encoding="utf-8") as wf_file:
                wf_file.write(workflow_json)

            with open(prompt_values_file_path, "w", encoding="utf-8") as pv_file:
                pv_file.write(prompt_values_json)

            # Mettre à jour le statut
            self.update_execution_stack_status(execution_id, f"Connexion à ComfyUI", 50)

            # Vérifier les fichiers générés
            print(f"DEBUG: Workflow file: {workflow_file_path}")
            print(f"DEBUG: Values file: {prompt_values_file_path}")

            # Vérifier le contenu JSON
            try:
                import json

                with open(workflow_file_path, "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
                    print(f"DEBUG: Workflow JSON valide, {len(workflow_data)} nodes")

                with open(prompt_values_file_path, "r", encoding="utf-8") as f:
                    values_data = json.load(f)
                    print(f"DEBUG: Values JSON valide, {len(values_data)} entrées")
            except json.JSONDecodeError as e:
                self.update_execution_stack_status(execution_id, f"Erreur JSON: {e}", 0)
                return
            except Exception as e:
                self.update_execution_stack_status(
                    execution_id, f"Erreur fichiers: {e}", 0
                )
                return

            # Exécuter le workflow avec ComfyUI
            try:
                from cy6_websocket_api_client import (
                    workflow_is_running,
                    is_prompt_in_queue,
                )

                tsk1 = comfyui_basic_task()

                # Étape 1: Ajout à la queue (50% -> 60%)
                self.update_execution_stack_status(
                    execution_id, "Ajout à la queue ComfyUI", 60
                )
                comfyui_prompt_id = tsk1.addToQueue(
                    workflow_file_path, prompt_values_file_path
                )
                print(f"DEBUG: ComfyUI prompt ID: {comfyui_prompt_id}")

                # Étape 2: Workflow en queue (60% -> 75%)
                self.update_execution_stack_status(
                    execution_id, f"En queue (ID: {comfyui_prompt_id})", 75
                )

                # Étape 3: Génération en cours avec vérification progressive
                max_wait_time = 600  # 10 minutes max
                start_time = time.time()
                progress_step = 75
                check_count = 0

                while True:
                    elapsed_time = time.time() - start_time
                    check_count += 1

                    if elapsed_time > max_wait_time:
                        self.update_execution_stack_status(
                            execution_id, "Timeout - Workflow trop long", 0
                        )
                        print(
                            f"DEBUG: Timeout après {elapsed_time:.1f}s pour prompt {comfyui_prompt_id}"
                        )
                        return

                    # Mise à jour progressive du statut (75% -> 95%)
                    if elapsed_time > 5:  # Après 5 secondes, on augmente le progrès
                        progress_increment = min(
                            20, int(elapsed_time / 10) * 5
                        )  # 5% toutes les 10 secondes
                        progress_step = min(95, 75 + progress_increment)
                        self.update_execution_stack_status(
                            execution_id,
                            f"Génération en cours ({int(elapsed_time)}s)",
                            progress_step,
                        )

                    # Vérifier si le workflow est toujours en cours
                    workflow_finished = False
                    websocket_says_finished = False
                    queue_says_running = False

                    # Méthode 1: Vérification WebSocket
                    try:
                        if hasattr(tsk1, "ws") and tsk1.ws:
                            is_running = workflow_is_running(tsk1.ws, comfyui_prompt_id)
                            print(
                                f"DEBUG: Check {check_count}: workflow_is_running = {is_running}"
                            )
                            if not is_running:
                                websocket_says_finished = True
                        else:
                            print("DEBUG: Pas de connexion WebSocket active")
                    except Exception as ws_error:
                        print(f"DEBUG: Erreur WebSocket check: {ws_error}")

                    # Méthode 2: Vérification via API HTTP de la queue
                    try:
                        queue_says_running = is_prompt_in_queue(comfyui_prompt_id)
                        print(
                            f"DEBUG: Check {check_count}: is_prompt_in_queue = {queue_says_running}"
                        )
                    except Exception as queue_error:
                        print(f"DEBUG: Erreur queue check: {queue_error}")

                    # Décision basée sur les deux méthodes
                    if websocket_says_finished and not queue_says_running:
                        print(
                            f"DEBUG: Workflow terminé après {elapsed_time:.1f}s (WebSocket ET Queue confirment)"
                        )
                        workflow_finished = True
                    elif not queue_says_running and elapsed_time > 10:
                        # Si la queue ne contient plus le prompt et que ça fait plus de 10s, c'est probablement fini
                        print(
                            f"DEBUG: Workflow probablement terminé après {elapsed_time:.1f}s (Plus dans la queue)"
                        )
                        workflow_finished = True
                    elif elapsed_time > max_wait_time:
                        print(f"DEBUG: Timeout général après {elapsed_time:.1f}s")
                        workflow_finished = True

                    if workflow_finished:
                        break

                    time.sleep(3)  # Vérifier toutes les 3 secondes

                # Étape 4: Récupération des images (95% -> 100%)
                self.update_execution_stack_status(
                    execution_id, "Récupération des images", 95
                )

            except Exception as comfy_error:
                print(f"DEBUG: Erreur ComfyUI: {comfy_error}")
                self.update_execution_stack_status(
                    execution_id, f"Erreur ComfyUI: {str(comfy_error)}", 0
                )
                return

            # Récupérer les images générées
            try:
                output_images = tsk1.GetImages(comfyui_prompt_id)
            except Exception as img_error:
                print(f"DEBUG: Erreur récupération images: {img_error}")
                self.update_execution_stack_status(
                    execution_id, f"Erreur images: {str(img_error)}", 0
                )
                return

            if output_images:
                # Ajouter les images à la base de données
                images_added = self.add_output_images_to_database(
                    prompt_id, output_images
                )

                self.update_execution_stack_status(
                    execution_id,
                    f"Terminé avec succès - {len(output_images)} images générées ({images_added} ajoutées)",
                    100,
                )

                # Actualiser la liste d'images si c'est le prompt actuellement sélectionné
                if self.selected_prompt_id == prompt_id:
                    self.root.after(0, self.refresh_images_list)

                self.root.after(
                    0,
                    lambda: self.update_prompt_status_after_execution(prompt_id, "ok"),
                )
            else:
                self.update_execution_stack_status(
                    execution_id, "Terminé - Aucune image générée", 100
                )
                self.root.after(
                    0,
                    lambda: self.update_prompt_status_after_execution(prompt_id, "ok"),
                )

        except Exception as e:
            error_msg = f"Erreur ComfyUI: {str(e)}"
            self.update_execution_stack_status(execution_id, error_msg, 0)
            self.root.after(
                0, lambda: self.update_prompt_status_after_execution(prompt_id, "nok")
            )
            print(f"Erreur dans _execute_workflow_task: {e}")

        finally:
            # Nettoyer l'ID d'environnement d'exécution
            if hasattr(self, "current_execution_environment_id"):
                delattr(self, "current_execution_environment_id")
                print("🧹 Environment ID d'exécution nettoyé")

    def update_prompt_status_after_execution(self, prompt_id, status):
        """Mettre à jour le statut du prompt après exécution"""
        try:
            # Récupérer les données actuelles
            data = self.db_manager.get_prompt_by_id(prompt_id)
            if data:
                name, prompt_values, workflow, url, parent, model, comment, _, file, id_env = data

                # Mettre à jour avec le nouveau statut
                self.db_manager.update_prompt(
                    prompt_id,
                    name,
                    prompt_values,
                    workflow,
                    url,
                    model,
                    comment,
                    status,
                )

                # Mettre à jour l'affichage
                if str(prompt_id) in [
                    self.prompts_tree.item(item, "values")[0]
                    for item in self.prompts_tree.get_children()
                ]:
                    for item in self.prompts_tree.get_children():
                        if self.prompts_tree.item(item, "values")[0] == str(prompt_id):
                            values = list(self.prompts_tree.item(item, "values"))
                            values[2] = status  # Colonne statut
                            self.prompts_tree.item(item, values=values)
                            break

                # Si c'est le prompt sélectionné, mettre à jour aussi les détails
                if self.selected_prompt_id == prompt_id:
                    self.status_var.set(status)

        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut: {e}")

    def open_prompt_analysis(self):
        """
        0.7) Analyser le prompt - Fonction initiale: open_prompt_analysis
        POPUP-ID: CY8-POPUP-009
        """
        if not self.selected_prompt_id:
            messagebox.showwarning("Attention", "Sélectionnez un prompt à analyser.")
            return

        # CY8-POPUP-009: Popup d'analyse
        popup = tk.Toplevel(self.root)
        popup.title("CY8-POPUP-009 | Analyse du Prompt")
        popup.transient(self.root)
        popup.grab_set()

        self.popup_manager.center_window(popup, 600, 400)

        main_frame = ttk.Frame(popup, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Identifiant popup en haut
        ttk.Label(
            main_frame,
            text="CY8-POPUP-009",
            font=("TkDefaultFont", 8, "bold"),
            foreground="blue",
        ).pack(anchor="e", pady=(0, 5))

        ttk.Label(main_frame, text="Analyse du Prompt", style="Title.TLabel").pack(
            pady=10
        )

        # Zone d'analyse
        analysis_text = tk.Text(main_frame, wrap="word", font=("Consolas", 10))
        analysis_text.pack(fill="both", expand=True, pady=10)

        # Effectuer l'analyse
        try:
            data = self.db_manager.get_prompt_by_id(self.selected_prompt_id)
            if data:
                name, prompt_values, workflow, url, parent, model, comment, status, file, id_env = (
                    data
                )

                analysis = f"""ANALYSE DU PROMPT: {name}
{'='*50}

INFORMATIONS GÉNÉRALES:
- ID: {self.selected_prompt_id}
- Nom: {name}
- Statut: {status}
- Modèle: {model or 'Non défini'}
- URL: {url or 'Non définie'}
- Commentaire: {comment or 'Aucun'}
- Environnement: {id_env or 'Non défini'}
- Fichier exporté: {file or 'Non exporté'}

PROMPT VALUES:
{'-'*20}
"""

                # Analyser les prompt values
                try:
                    pv_data = json.loads(prompt_values) if prompt_values else {}
                    analysis += f"Nombre d'éléments: {len(pv_data)}\\n"
                    for key, value in pv_data.items():
                        if isinstance(value, dict):
                            analysis += f"- {key}: {value.get('type', 'N/A')} -> {str(value.get('value', ''))[:50]}...\\n"
                        else:
                            analysis += f"- {key}: {str(value)[:50]}...\\n"
                except:
                    analysis += "Erreur lors de l'analyse des prompt values\\n"

                analysis += f"""
WORKFLOW:
{'-'*20}
"""

                # Analyser le workflow
                try:
                    wf_data = json.loads(workflow) if workflow else {}
                    analysis += f"Nombre de nœuds: {len(wf_data)}\\n"
                    for node_id, node_data in wf_data.items():
                        if isinstance(node_data, dict):
                            class_type = node_data.get("class_type", "N/A")
                            title = node_data.get("_meta", {}).get("title", "N/A")
                            analysis += f"- Nœud {node_id}: {class_type} ({title})\\n"
                except:
                    analysis += "Erreur lors de l'analyse du workflow\\n"

                analysis_text.insert("1.0", analysis)

        except Exception as e:
            analysis_text.insert("1.0", f"Erreur lors de l'analyse: {e}")

        analysis_text.config(state="disabled")

        ttk.Button(main_frame, text="Fermer", command=popup.destroy).pack(pady=10)

    def add_to_execution_stack(self, execution_id, message, prompt_name="", progress=0):
        """Ajouter une exécution à la pile"""
        execution_item = {
            "id": execution_id,
            "message": message,
            "prompt_name": prompt_name,
            "progress": progress,
            "timestamp": time.time(),
            "formatted_time": time.strftime("%H:%M:%S", time.localtime()),
            "details": [],
        }
        self.execution_stack.append(execution_item)
        self.update_execution_display()
        self.update_executions_tree()

    def update_execution_stack_status(self, execution_id, message, progress=None):
        """Mettre à jour le statut d'une exécution"""
        for item in self.execution_stack:
            if item["id"] == execution_id:
                item["message"] = message
                if progress is not None:
                    item["progress"] = progress
                # Ajouter aux détails
                detail_entry = f"[{time.strftime('%H:%M:%S')}] {message}"
                item["details"].append(detail_entry)
                break
        self.update_execution_display()
        self.update_executions_tree()

    def update_execution_display(self):
        """Mettre à jour l'affichage des exécutions dans la barre de statut"""
        if self.execution_stack:
            last_execution = self.execution_stack[-1]
            progress_str = (
                f" ({last_execution['progress']}%)"
                if last_execution["progress"] > 0
                else ""
            )
            display_text = f"{last_execution['prompt_name']}: {last_execution['message']}{progress_str}"
            self.execution_text.set(display_text)
        else:
            self.execution_text.set("")

    def update_executions_tree(self):
        """Mettre à jour le TreeView des exécutions"""
        if not self.executions_tree:
            return

        # Effacer le contenu actuel
        for item in self.executions_tree.get_children():
            self.executions_tree.delete(item)

        # Ajouter les exécutions (les plus récentes en premier)
        for execution in reversed(self.execution_stack):
            progress_display = (
                f"{execution['progress']}%" if execution["progress"] > 0 else "-"
            )

            self.executions_tree.insert(
                "",
                "end",
                values=(
                    execution["id"],
                    execution["prompt_name"],
                    execution["message"],
                    progress_display,
                    execution["formatted_time"],
                ),
            )

    def clear_execution_history(self):
        """Effacer l'historique des exécutions"""
        self.execution_stack.clear()
        self.update_executions_tree()
        self.update_execution_display()
        # Effacer les détails
        if hasattr(self, "execution_details"):
            self.execution_details.config(state="normal")
            self.execution_details.delete("1.0", "end")
            self.execution_details.config(state="disabled")

    def on_execution_select(self, event):
        """Gérer la sélection d'une exécution dans le TreeView"""
        if not self.executions_tree or not hasattr(self, "execution_details"):
            return

        selection = self.executions_tree.selection()
        if not selection:
            return

        # Récupérer l'item sélectionné
        item = self.executions_tree.item(selection[0])
        execution_id = item["values"][0]

        # Trouver l'exécution correspondante
        execution = None
        for exec_item in self.execution_stack:
            if exec_item["id"] == execution_id:
                execution = exec_item
                break

        if execution:
            # Afficher les détails
            self.execution_details.config(state="normal")
            self.execution_details.delete("1.0", "end")

            details_text = f"ID: {execution['id']}\n"
            details_text += f"Prompt: {execution['prompt_name']}\n"
            details_text += f"Démarré: {execution['formatted_time']}\n"
            details_text += f"Progression: {execution['progress']}%\n"
            details_text += f"Statut actuel: {execution['message']}\n\n"

            if execution["details"]:
                details_text += "Historique:\n"
                for detail in execution["details"]:
                    details_text += f"{detail}\n"

            self.execution_details.insert("1.0", details_text)
            self.execution_details.config(state="disabled")

    # Méthodes pour la gestion des images

    def refresh_images_list(self):
        """Actualiser la liste des images pour le prompt sélectionné"""
        if not hasattr(self, "images_tree") or not self.images_tree:
            return

        # Effacer la liste actuelle
        for item in self.images_tree.get_children():
            self.images_tree.delete(item)

        # Récupérer le prompt sélectionné
        selection = self.prompts_tree.selection()
        if not selection:
            return

        prompt_id = int(selection[0])

        # Récupérer les images de la base de données
        images = self.db_manager.get_prompt_images(prompt_id)

        for image_data in images:
            # Adapter selon le nouveau format avec environment_id
            if len(image_data) >= 4:
                image_id, image_path, environment_id, created_at = image_data
            else:
                # Compatibilité avec l'ancien format
                image_id, image_path, created_at = image_data[:3]
                environment_id = "N/A"

            if os.path.exists(image_path):
                filename = os.path.basename(image_path)
                # Afficher l'environnement s'il existe
                env_display = (
                    environment_id[:12] + "..."
                    if environment_id and len(environment_id) > 15
                    else (environment_id or "N/A")
                )
                self.images_tree.insert(
                    "", "end", values=(filename, image_path, env_display, created_at)
                )

    def on_image_select(self, event):
        """Gérer la sélection d'une image pour la prévisualisation"""
        if not hasattr(self, "images_tree") or not self.images_tree:
            return

        selection = self.images_tree.selection()
        if not selection:
            self.preview_label.configure(
                image="", text="Sélectionnez une image\npour la prévisualiser"
            )
            return

        # Récupérer le chemin de l'image
        item = self.images_tree.item(selection[0])
        image_path = item["values"][1]

        try:
            # Charger et redimensionner l'image pour la prévisualisation
            image = Image.open(image_path)

            # Calculer la taille de prévisualisation (max 300x300)
            preview_size = 300
            image.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)

            # Convertir pour tkinter
            photo = ImageTk.PhotoImage(image)

            # Afficher la prévisualisation
            self.preview_label.configure(image=photo, text="")
            self.current_preview_image = photo  # Garder une référence

        except Exception as e:
            self.preview_label.configure(
                image="", text=f"Erreur lors du chargement:\n{str(e)}"
            )
            self.current_preview_image = None

    def add_images_to_prompt(self):
        """Ajouter des images au prompt sélectionné"""
        # Récupérer le prompt sélectionné
        selection = self.prompts_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Aucune sélection", "Veuillez sélectionner un prompt"
            )
            return

        prompt_id = int(selection[0])

        # Ouvrir le dialogue de sélection de fichiers
        filetypes = [
            ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("Tous les fichiers", "*.*"),
        ]

        filenames = filedialog.askopenfilenames(
            title="Sélectionner des images", filetypes=filetypes
        )

        if filenames:
            success_count = 0
            # Récupérer l'environment_id actuel (peut être null pour les ajouts manuels)
            environment_id = (
                self.comfyui_config_id.get().strip()
                if hasattr(self, "comfyui_config_id")
                else None
            )

            for filename in filenames:
                if self.db_manager.add_prompt_image(
                    prompt_id, filename, environment_id
                ):
                    success_count += 1

            messagebox.showinfo(
                "Images ajoutées",
                f"{success_count} image(s) ajoutée(s) sur {len(filenames)} sélectionnée(s)",
            )

            # Actualiser la liste
            self.refresh_images_list()

    def enlarge_selected_image(self):
        """Agrandir l'image sélectionnée dans une nouvelle fenêtre"""
        selection = self.images_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Aucune sélection", "Veuillez sélectionner une image"
            )
            return

        item = self.images_tree.item(selection[0])
        image_path = item["values"][1]

        try:
            # Créer une nouvelle fenêtre
            image_window = tk.Toplevel(self.root)
            image_window.title(f"Image - {os.path.basename(image_path)}")

            # Charger l'image complète
            image = Image.open(image_path)

            # Calculer la taille pour l'affichage (max 800x600)
            max_width, max_height = 800, 600
            image_ratio = image.width / image.height

            if image.width > max_width or image.height > max_height:
                if image_ratio > max_width / max_height:
                    new_width = max_width
                    new_height = int(max_width / image_ratio)
                else:
                    new_height = max_height
                    new_width = int(max_height * image_ratio)

                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convertir pour tkinter
            photo = ImageTk.PhotoImage(image)

            # Afficher l'image
            image_label = ttk.Label(image_window, image=photo)
            image_label.pack(padx=10, pady=10)

            # Garder une référence à l'image
            image_label.image = photo

            # Centrer la fenêtre
            image_window.geometry(f"{image.width + 20}x{image.height + 20}")
            image_window.resizable(True, True)
            center_window(image_window, image.width + 20, image.height + 20)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'image:\n{str(e)}")

    def open_selected_image(self):
        """Ouvrir l'image sélectionnée avec l'application par défaut"""
        selection = self.images_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Aucune sélection", "Veuillez sélectionner une image"
            )
            return

        item = self.images_tree.item(selection[0])
        image_path = item["values"][1]

        try:
            # Ouvrir avec l'application par défaut du système
            if os.name == "nt":  # Windows
                os.startfile(image_path)
            elif os.name == "posix":  # macOS et Linux
                subprocess.call(
                    [
                        "open" if os.uname().sysname == "Darwin" else "xdg-open",
                        image_path,
                    ]
                )

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'image:\n{str(e)}")

    def remove_selected_image(self):
        """Supprimer l'image sélectionnée de la liste (pas du disque)"""
        selection = self.images_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Aucune sélection", "Veuillez sélectionner une image"
            )
            return

        item = self.images_tree.item(selection[0])
        image_path = item["values"][1]

        response = messagebox.askyesno(
            "Confirmer la suppression",
            f"Voulez-vous supprimer cette image de la liste ?\n\n{os.path.basename(image_path)}\n\n"
            "Note: L'image ne sera pas supprimée du disque.",
        )

        if response:
            # Récupérer le prompt sélectionné
            prompt_selection = self.prompts_tree.selection()
            if prompt_selection:
                prompt_id = int(prompt_selection[0])

                # Trouver l'ID de l'image dans la base
                images = self.db_manager.get_prompt_images(prompt_id)
                for image_id, db_image_path, created_at in images:
                    if db_image_path == image_path:
                        if self.db_manager.delete_prompt_image(image_id):
                            messagebox.showinfo(
                                "Suppression", "Image supprimée de la liste"
                            )
                            self.refresh_images_list()
                        else:
                            messagebox.showerror(
                                "Erreur", "Impossible de supprimer l'image"
                            )
                        break

    def open_images_folder(self):
        """Ouvrir le dossier d'images par défaut"""
        from tkinter import filedialog

        try:
            images_path = os.getenv("IMAGES_COLLECTE")
            if not images_path:
                # Utiliser le chemin par défaut ComfyUI
                images_path = "E:/Comfyui_G11/ComfyUI/output"

            if os.path.exists(images_path):
                if os.name == "nt":  # Windows
                    os.startfile(images_path)
                elif os.name == "posix":  # macOS et Linux
                    subprocess.call(
                        [
                            "open" if os.uname().sysname == "Darwin" else "xdg-open",
                            images_path,
                        ]
                    )
            else:
                # Proposer de choisir un nouveau dossier
                result = messagebox.askyesno(
                    "Dossier introuvable",
                    f"Le dossier d'images n'existe pas:\n{images_path}\n\n"
                    f"Voulez-vous choisir un autre dossier d'images ?",
                    icon='warning'
                )

                if result:
                    # Ouvrir le sélecteur de dossier
                    new_path = filedialog.askdirectory(
                        title="Sélectionner le dossier d'images",
                        initialdir=os.path.expanduser("~")
                    )

                    if new_path:
                        # Ouvrir le nouveau dossier
                        if os.name == "nt":  # Windows
                            os.startfile(new_path)
                        elif os.name == "posix":  # macOS et Linux
                            subprocess.call(
                                [
                                    "open" if os.uname().sysname == "Darwin" else "xdg-open",
                                    new_path,
                                ]
                            )

                        # Proposer de sauvegarder ce chemin
                        save_result = messagebox.askyesno(
                            "Sauvegarder le chemin",
                            f"Voulez-vous définir ce dossier comme dossier d'images par défaut ?\n\n"
                            f"Dossier: {new_path}\n\n"
                            f"(Ceci créera/modifiera la variable d'environnement IMAGES_COLLECTE)",
                            icon='question'
                        )

                        if save_result:
                            # Sauvegarder dans le fichier .env s'il existe
                            try:
                                env_file = os.path.join(os.getcwd(), ".env")
                                env_content = ""

                                # Lire le contenu existant si le fichier existe
                                if os.path.exists(env_file):
                                    with open(env_file, "r", encoding="utf-8") as f:
                                        lines = f.readlines()
                                        # Remplacer ou ajouter IMAGES_COLLECTE
                                        found = False
                                        for i, line in enumerate(lines):
                                            if line.startswith("IMAGES_COLLECTE="):
                                                lines[i] = f"IMAGES_COLLECTE={new_path}\n"
                                                found = True
                                        if not found:
                                            lines.append(f"IMAGES_COLLECTE={new_path}\n")
                                        env_content = "".join(lines)
                                else:
                                    env_content = f"IMAGES_COLLECTE={new_path}\n"

                                # Écrire le fichier .env
                                with open(env_file, "w", encoding="utf-8") as f:
                                    f.write(env_content)

                                # Mettre à jour la variable d'environnement pour cette session
                                os.environ["IMAGES_COLLECTE"] = new_path

                                messagebox.showinfo(
                                    "Succès",
                                    f"Le dossier d'images par défaut a été défini sur:\n{new_path}\n\n"
                                    f"Sauvegardé dans: {env_file}"
                                )
                            except Exception as save_error:
                                messagebox.showwarning(
                                    "Avertissement",
                                    f"Le dossier a été ouvert mais n'a pas pu être sauvegardé:\n{str(save_error)}"
                                )

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Impossible d'ouvrir le dossier d'images:\n{str(e)}"
            )

    def add_output_images_to_database(self, prompt_id, output_images):
        """Ajouter automatiquement les images de sortie à la base de données avec environment_id"""
        if not output_images:
            return 0

        images_added = 0

        # Récupérer l'ID de l'environnement d'exécution
        environment_id = getattr(self, "current_execution_environment_id", None)
        if not environment_id:
            # Essayer de récupérer depuis l'interface
            environment_id = (
                self.comfyui_config_id.get().strip()
                if hasattr(self, "comfyui_config_id")
                else None
            )

        print(f"🔗 Ajout d'images avec environment_id: {environment_id}")

        try:
            for image_info in output_images:
                # output_images contient normalement des dictionnaires avec 'filename', 'path', etc.
                # Adapter selon la structure exacte retournée par GetImages()

                if isinstance(image_info, dict):
                    # Si c'est un dictionnaire avec des informations sur l'image
                    image_path = image_info.get("path") or image_info.get("filename")
                elif isinstance(image_info, str):
                    # Si c'est directement le chemin vers l'image
                    image_path = image_info
                else:
                    print(
                        f"DEBUG: Format d'image non reconnu: {type(image_info)} - {image_info}"
                    )
                    continue

                # Vérifier que le fichier existe
                if image_path and os.path.exists(image_path):
                    # Ajouter à la base de données avec l'environment_id
                    if self.db_manager.add_prompt_image(
                        prompt_id, image_path, environment_id
                    ):
                        images_added += 1
                        print(
                            f"DEBUG: Image ajoutée à la BDD avec env {environment_id}: {image_path}"
                        )
                    else:
                        print(f"DEBUG: Échec ajout image en BDD: {image_path}")
                else:
                    print(f"DEBUG: Image introuvable: {image_path}")

        except Exception as e:
            print(f"DEBUG: Erreur lors de l'ajout des images à la BDD: {e}")

        return images_added

    def clear_details(self):
        """Effacer les détails affichés"""
        self.name_var.set("")
        self.url_var.set("")
        self.comment_var.set("")
        self.model_var.set("")
        self.status_var.set("")

        # Effacer les tableaux
        for item in self.values_tree.get_children():
            self.values_tree.delete(item)
        for item in self.workflow_tree.get_children():
            self.workflow_tree.delete(item)

        self.table_manager.values_data.clear()
        self.table_manager.workflow_data.clear()

    def update_status(self, message):
        """Mettre à jour la barre de statut"""
        try:
            if hasattr(self, "status_text") and self.status_text:
                self.status_text.set(message)
                self.root.update_idletasks()
            else:
                # Fallback: juste imprimer le message
                print(f"Status: {message}")
        except Exception as e:
            print(f"Erreur update_status: {e}")
            print(f"Message était: {message}")

    def update_database_stats(self):
        """Mettre à jour les statistiques de la base de données"""
        try:
            prompts = self.db_manager.get_all_prompts()
            total_prompts = len(prompts)

            # Statistiques par statut
            status_counts = {}
            for _, _, _, _, _, status, _, _ in prompts:
                status_counts[status] = status_counts.get(status, 0) + 1

            stats_text = f"Total prompts: {total_prompts}"
            if status_counts:
                stats_text += "\n" + " | ".join(
                    [f"{status}: {count}" for status, count in status_counts.items()]
                )

            self.stats_text.set(stats_text)
        except Exception as e:
            self.stats_text.set(f"Erreur lors du calcul des statistiques: {e}")

    def change_database(self):
        """Changer de base de données existante"""
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="Sélectionner une base de données",
            filetypes=[("SQLite Database", "*.db"), ("All files", "*.*")],
            initialdir=cy8_paths_manager.get_directory_from_path(self.db_path),
        )

        if file_path:
            self.switch_to_database(normalize_path(file_path))

    def create_new_database(self):
        """Créer une nouvelle base de données
        POPUP-ID: CY8-POPUP-010
        """
        # CY8-POPUP-010: Popup création nouvelle base
        popup = tk.Toplevel(self.root)
        popup.title("CY8-POPUP-010 | Créer nouvelle base de données")
        popup.transient(self.root)
        popup.grab_set()

        self.popup_manager.center_window(popup, 500, 300)

        main_frame = ttk.Frame(popup, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Identifiant popup en haut
        ttk.Label(
            main_frame,
            text="CY8-POPUP-010",
            font=("TkDefaultFont", 8, "bold"),
            foreground="blue",
        ).pack(anchor="e", pady=(0, 10))

        # Titre
        ttk.Label(
            main_frame,
            text="Créer une nouvelle base de données",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(pady=(0, 20))

        # Nom de la base
        ttk.Label(main_frame, text="Nom de la base:").pack(anchor="w", pady=(0, 5))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=50)
        name_entry.pack(fill="x", pady=(0, 15))
        name_entry.focus_set()

        # Chemin de destination
        ttk.Label(main_frame, text="Répertoire de destination:").pack(
            anchor="w", pady=(0, 5)
        )

        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill="x", pady=(0, 20))

        path_var = tk.StringVar(
            value=cy8_paths_manager.get_directory_from_path(self.db_path)
        )
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=40)
        path_entry.pack(side="left", fill="x", expand=True)

        def browse_directory():
            from tkinter import filedialog

            directory = filedialog.askdirectory(
                title="Sélectionner le répertoire", initialdir=path_var.get()
            )
            if directory:
                path_var.set(directory)

        ttk.Button(path_frame, text="Parcourir...", command=browse_directory).pack(
            side="right", padx=(5, 0)
        )

        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)

        def create_database():
            name = name_var.get().strip()
            path = path_var.get().strip()

            if not name:
                messagebox.showerror("Erreur", "Le nom de la base est obligatoire.")
                return

            if not path or not os.path.isdir(path):
                messagebox.showerror("Erreur", "Le chemin spécifié n'est pas valide.")
                return

            # Construire le chemin complet
            if not name.endswith(".db"):
                name += ".db"

            # Nettoyer le nom de fichier et construire le chemin
            clean_name = cy8_paths_manager.sanitize_filename(name)
            full_path = normalize_path(cy8_paths_manager.join_path(path, clean_name))

            if os.path.exists(full_path):
                if not messagebox.askyesno(
                    "Confirmer", f"Le fichier {full_path} existe déjà. L'écraser ?"
                ):
                    return

            try:
                # S'assurer que le répertoire existe
                ensure_dir(full_path)

                # Créer et basculer vers la nouvelle base
                self.switch_to_database(full_path, create_new=True)
                popup.destroy()
                messagebox.showinfo(
                    "Succès", f"Base de données créée avec succès: {full_path}"
                )
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la création: {e}")

        def cancel():
            popup.destroy()

        ttk.Button(button_frame, text="Créer", command=create_database).pack(
            side="right", padx=(5, 0)
        )
        ttk.Button(button_frame, text="Annuler", command=cancel).pack(side="right")

    def switch_to_database(self, new_db_path, create_new=False):
        """Basculer vers une nouvelle base de données"""
        try:
            # Normaliser le chemin
            normalized_path = normalize_path(new_db_path)

            # Fermer l'ancienne connexion
            if hasattr(self, "db_manager") and self.db_manager:
                self.db_manager.close()

            # Créer le nouveau gestionnaire de base
            self.db_path = normalized_path
            self.db_manager = cy8_database_manager(normalized_path)

            # Initialiser la base (créer les tables si nécessaire)
            if create_new:
                self.db_manager.init_database(
                    "init"
                )  # Mode init pour créer avec prompt par défaut
            else:
                self.db_manager.init_database("dev")  # Mode dev pour ouvrir existante

            # Recréer tous les gestionnaires avec le nouveau db_manager
            self.popup_manager = cy8_popup_manager(self.root, self.db_manager)
            self.table_manager = cy8_editable_tables(self.root, self.popup_manager)

            # Reconnector le callback de sauvegarde
            self.table_manager.set_save_callback(self.save_current_info)

            # Reconnecter les références vers les arbres dans table_manager
            if hasattr(self, "values_tree"):
                self.table_manager._current_values_tree = self.values_tree
            if hasattr(self, "workflow_tree"):
                self.table_manager._current_workflow_tree = self.workflow_tree

            # Sauvegarder la nouvelle base dans les cookies
            self.user_prefs.set_last_database_path(normalized_path)
            print(f"Base sauvegardée dans les cookies: {normalized_path}")

            # Mettre à jour l'affichage
            self.db_path_var.set(normalized_path)
            self.clear_details()
            self.load_prompts()
            self.update_database_stats()

            # Mettre à jour les menus et listes
            if hasattr(self, "recent_db_menu"):
                self.update_recent_databases_menu()
            if hasattr(self, "recent_listbox"):
                self.refresh_recent_list()

            self.update_status(
                f"Base de données changée: {cy8_paths_manager.get_filename_from_path(normalized_path)}"
            )

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Impossible de changer de base de données: {e}"
            )

    def import_json(self):
        """Importer des données JSON - Crée un prompt depuis un fichier workflow"""
        try:
            # Dialogue de sélection de fichier
            file_path = filedialog.askopenfilename(
                title="Sélectionner un fichier workflow JSON",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
                defaultextension=".json",
            )

            if not file_path:
                return  # Utilisateur a annulé

            # Lire le contenu du fichier
            with open(file_path, "r", encoding="utf-8") as f:
                workflow_content = json.load(f)

            # Extraire le nom du fichier (sans extension)
            import os

            prompt_name = os.path.splitext(os.path.basename(file_path))[0]

            # Vérifier si un prompt avec ce nom existe déjà
            if self.db_manager.prompt_name_exists(prompt_name):
                response = messagebox.askyesno(
                    "Nom existant",
                    f"Un prompt nommé '{prompt_name}' existe déjà.\nVoulez-vous utiliser un nom différent ?",
                )
                if response:
                    # Ajouter un suffixe numérique
                    counter = 1
                    original_name = prompt_name
                    while self.db_manager.prompt_name_exists(prompt_name):
                        prompt_name = f"{original_name}_{counter}"
                        counter += 1
                else:
                    return  # Utilisateur a annulé

            # Valeurs par défaut pour prompt_values
            default_values = {
                "1": {
                    "id": "6",
                    "type": "prompt",
                    "value": "beautiful scenery nature glass bottle landscape, purple galaxy bottle",
                },
                "2": {"id": "7", "type": "prompt", "value": "text, watermark"},
                "3": {"id": "3", "type": "seed", "value": 1234567},
                "4": {"id": "9", "type": "SaveImage", "filename_prefix": "basic"},
            }

            # Dériver le modèle depuis le workflow
            model = self.db_manager.derive_model_from_workflow(workflow_content)

            # Créer le nouveau prompt
            prompt_id = self.db_manager.create_prompt(
                name=prompt_name,
                prompt_values=json.dumps(default_values, ensure_ascii=False),
                workflow=json.dumps(workflow_content, ensure_ascii=False),
                url="",
                model=model,
                status="new",
                comment=f"Importé depuis {os.path.basename(file_path)}",
                parent=None,
            )

            # Rafraîchir l'affichage
            self.load_prompts()

            # Sélectionner le nouveau prompt dans la liste (si possible)
            try:
                if hasattr(self, "prompts_tree") and self.prompts_tree:
                    for item in self.prompts_tree.get_children():
                        values = self.prompts_tree.item(item)["values"]
                        if values and int(values[0]) == prompt_id:  # ID du prompt
                            self.prompts_tree.selection_set(item)
                            self.prompts_tree.focus(item)
                            self.prompts_tree.see(item)
                            self.on_prompt_select(None)  # Charger les détails
                            break
            except Exception as e:
                print(f"Erreur lors de la sélection du prompt: {e}")
                # Ce n'est pas critique, on continue sans sélectionner

            messagebox.showinfo(
                "Import réussi",
                f"Workflow importé avec succès !\n\nNom du prompt : {prompt_name}\nModèle détecté : {model or 'Aucun'}\nFichier : {os.path.basename(file_path)}",
            )

        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Erreur JSON",
                f"Le fichier sélectionné n'est pas un JSON valide :\n{str(e)}",
            )
        except FileNotFoundError:
            messagebox.showerror(
                "Fichier introuvable",
                "Le fichier sélectionné n'existe pas ou n'est pas accessible.",
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur d'import",
                f"Une erreur est survenue lors de l'import :\n{str(e)}",
            )
            print(f"Erreur lors de l'import JSON: {e}")  # Pour le debug

    def export_json(self):
        """Exporter le workflow du prompt sélectionné"""
        if not self.selected_prompt_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un prompt à exporter.")
            return

        try:
            # Récupérer les données du prompt
            data = self.db_manager.get_prompt_by_id(self.selected_prompt_id)
            if not data:
                messagebox.showerror("Erreur", "Impossible de récupérer les données du prompt.")
                return

            name, prompt_values, workflow, url, parent, model, comment, status, file, id_env = data

            if not workflow or not prompt_values:
                messagebox.showerror("Erreur", "Le prompt ne contient pas de workflow ou de valeurs à exporter.")
                return

            # Créer les fichiers temporaires
            import tempfile
            temp_dir = tempfile.gettempdir()

            tmp_values_file = os.path.join(temp_dir, "tmp_values.json")
            tmp_workflow_file = os.path.join(temp_dir, "tmp_workflow.json")

            # Écrire les fichiers temporaires
            with open(tmp_values_file, "w", encoding="utf-8") as f:
                f.write(prompt_values)

            with open(tmp_workflow_file, "w", encoding="utf-8") as f:
                f.write(workflow)

            # Importer la fonction update_workflow
            from cy6_websocket_api_client import update_workflow

            # Mettre à jour le workflow avec les valeurs
            self.update_status("Fusion du workflow avec les valeurs...")
            updated_workflow, updated_values = update_workflow(tmp_values_file, tmp_workflow_file)

            # Nettoyer les fichiers temporaires
            try:
                os.remove(tmp_values_file)
                os.remove(tmp_workflow_file)
            except:
                pass

            # Demander où sauvegarder le fichier
            filename = filedialog.asksaveasfilename(
                title="Exporter le workflow",
                defaultextension=".json",
                initialfile=f"{name}_workflow.json",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )

            if not filename:
                self.update_status("Export annulé")
                return

            # Sauvegarder le workflow mis à jour
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(updated_workflow, f, indent=2, ensure_ascii=False)

            # Mettre à jour le champ file dans la base de données
            self.file_var.set(filename)
            self.db_manager.update_prompt(
                self.selected_prompt_id,
                name,
                json.dumps(updated_values, ensure_ascii=False),
                json.dumps(updated_workflow, ensure_ascii=False),
                url,
                model,
                comment,
                status,
                filename,
                id_env,
            )

            self.update_status(f"Workflow exporté vers: {filename}")
            messagebox.showinfo("Succès", f"Workflow exporté avec succès !\n\nFichier: {filename}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
            import traceback
            traceback.print_exc()
            self.update_status("Erreur lors de l'export")

    def update_recent_databases_menu(self):
        """Mettre à jour le menu des bases récentes"""
        # Effacer le menu
        self.recent_db_menu.delete(0, "end")

        recent_dbs = self.user_prefs.get_recent_databases()

        if not recent_dbs:
            self.recent_db_menu.add_command(
                label="(Aucune base récente)", state="disabled"
            )
        else:
            for db_path in recent_dbs:
                db_name = os.path.basename(db_path)
                # Limiter la longueur du nom affiché
                display_name = db_name if len(db_name) <= 30 else db_name[:27] + "..."

                self.recent_db_menu.add_command(
                    label=f"{display_name} ({os.path.dirname(db_path)})",
                    command=lambda path=db_path: self.open_recent_database(path),
                )

            # Séparateur et option pour effacer
            self.recent_db_menu.add_separator()
            self.recent_db_menu.add_command(
                label="Effacer la liste", command=self.clear_recent_databases
            )

    def open_recent_database(self, db_path):
        """Ouvrir une base de données récente"""
        if os.path.exists(db_path):
            self.switch_to_database(db_path)
        else:
            if messagebox.askyesno(
                "Base introuvable",
                f"La base {db_path} n'existe plus.\nLa retirer de la liste ?",
            ):
                self.user_prefs.remove_recent_database(db_path)
                self.update_recent_databases_menu()

    def clear_recent_databases(self):
        """Effacer la liste des bases récentes"""
        if messagebox.askyesno("Confirmer", "Effacer la liste des bases récentes ?"):
            self.user_prefs.clear_recent_databases()
            self.update_recent_databases_menu()
            if hasattr(self, "recent_listbox"):
                self.refresh_recent_list()

    def refresh_recent_list(self):
        """Actualiser la liste des bases récentes dans l'onglet Data"""
        if hasattr(self, "recent_listbox"):
            # Effacer la liste
            self.recent_listbox.delete(0, tk.END)

            # Ajouter les bases récentes
            recent_dbs = self.user_prefs.get_recent_databases()
            for db_path in recent_dbs:
                # Marquer la base actuelle en comparant les chemins normalisés
                is_current = cy8_paths_manager.compare_paths(db_path, self.db_path)
                marker = " (ACTUELLE)" if is_current else ""
                display_text = f"{cy8_paths_manager.get_filename_from_path(db_path)} - {db_path}{marker}"
                self.recent_listbox.insert(tk.END, display_text)

    def open_selected_recent(self):
        """Ouvrir la base sélectionnée dans la liste des récentes"""
        if hasattr(self, "recent_listbox"):
            selection = self.recent_listbox.curselection()
            if selection:
                index = selection[0]
                recent_dbs = self.user_prefs.get_recent_databases()
                if index < len(recent_dbs):
                    db_path = recent_dbs[index]
                    if os.path.exists(db_path):
                        # Comparer les chemins normalisés
                        if not cy8_paths_manager.compare_paths(db_path, self.db_path):
                            self.switch_to_database(db_path)
                        else:
                            messagebox.showinfo(
                                "Information", "Cette base est déjà ouverte."
                            )
                    else:
                        if messagebox.askyesno(
                            "Base introuvable",
                            f"La base {db_path} n'existe plus.\nLa retirer de la liste ?",
                        ):
                            self.user_prefs.remove_recent_database(db_path)
                            self.refresh_recent_list()
                            self.update_recent_databases_menu()
            else:
                messagebox.showwarning(
                    "Sélection", "Sélectionnez une base dans la liste."
                )

    def remove_selected_recent(self):
        """Retirer la base sélectionnée de la liste des récentes"""
        if hasattr(self, "recent_listbox"):
            selection = self.recent_listbox.curselection()
            if selection:
                index = selection[0]
                recent_dbs = self.user_prefs.get_recent_databases()
                if index < len(recent_dbs):
                    db_path = recent_dbs[index]
                    db_name = cy8_paths_manager.get_filename_from_path(db_path)

                    if messagebox.askyesno(
                        "Confirmer",
                        f"Retirer '{db_name}' de la liste des bases récentes ?",
                    ):
                        self.user_prefs.remove_recent_database(db_path)
                        self.refresh_recent_list()
                        self.update_recent_databases_menu()
                        messagebox.showinfo(
                            "Succès", f"'{db_name}' retiré de la liste."
                        )
            else:
                messagebox.showwarning(
                    "Sélection", "Sélectionnez une base à retirer de la liste."
                )

    def run(self):
        """Démarrer l'application"""
        self.root.mainloop()

    def on_closing(self):
        """Gestionnaire de fermeture"""
        try:
            # Sauvegarder la géométrie de la fenêtre
            geometry = self.root.geometry()
            self.user_prefs.set_window_geometry(geometry)
            print(f"Géométrie sauvegardée: {geometry}")

            # Sauvegarder la base actuelle
            if hasattr(self, "db_path") and self.db_path:
                self.user_prefs.set_last_database_path(self.db_path)

            # Fermer la base de données
            if hasattr(self, "db_manager") and self.db_manager:
                self.db_manager.close()
        except Exception as e:
            print(f"Erreur lors de la fermeture: {e}")

        self.root.destroy()

    def add_default_filters(self):
        """Ajouter les filtres par défaut"""

        # Filtre 1: Exécutions en cours
        self.add_filter_row(
            filter_type="Statut d'exécution",
            criteria="En cours d'exécution",
            value="",
            active=False,
            filter_id="execution_running",
        )

        # Filtre 2: Modèle spécifique
        self.add_filter_row(
            filter_type="Modèle",
            criteria="Égal à",
            value="",
            active=False,
            filter_id="model_equals",
        )

        # Filtre 3: Fils du prompt sélectionné
        self.add_filter_row(
            filter_type="Hiérarchie",
            criteria="Fils du prompt sélectionné",
            value="",
            active=False,
            filter_id="children_selected",
        )

        # Filtre 4: Nom du prompt
        self.add_filter_row(
            filter_type="Nom",
            criteria="Contient",
            value="",
            active=False,
            filter_id="name_contains",
        )

    def add_filter_row(
        self, filter_type="", criteria="", value="", active=False, filter_id=None
    ):
        """Ajouter une ligne de filtre"""

        # Frame pour cette ligne de filtre
        filter_frame = ttk.Frame(self.filters_frame)
        filter_frame.pack(fill="x", padx=5, pady=2)

        # Checkbox pour activer/désactiver
        active_var = tk.BooleanVar(value=active)
        active_check = ttk.Checkbutton(
            filter_frame, variable=active_var, command=self.on_filter_changed
        )
        active_check.grid(row=0, column=0, padx=5, pady=2)

        # Type de filtre (ComboBox)
        filter_types = ["Statut d'exécution", "Modèle", "Hiérarchie", "Nom", "Statut", "Environnement"]
        type_var = tk.StringVar(value=filter_type)
        type_combo = ttk.Combobox(
            filter_frame, textvariable=type_var, values=filter_types, width=15
        )
        type_combo.grid(row=0, column=1, padx=5, pady=2)
        type_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.on_filter_type_changed(filter_id, type_var.get()),
        )

        # Critère (dépend du type)
        criteria_var = tk.StringVar(value=criteria)
        criteria_combo = ttk.Combobox(filter_frame, textvariable=criteria_var, width=20)
        criteria_combo.grid(row=0, column=2, padx=5, pady=2)

        # Valeur (Entry ou ComboBox selon le type)
        value_var = tk.StringVar(value=value)
        value_widget = ttk.Entry(filter_frame, textvariable=value_var, width=20)
        value_widget.grid(row=0, column=3, padx=5, pady=2)
        value_widget.bind("<KeyRelease>", lambda e: self.on_filter_changed())

        # Bouton supprimer
        delete_btn = ttk.Button(
            filter_frame,
            text="✕",
            width=3,
            command=lambda: self.remove_filter_row(filter_id),
        )
        delete_btn.grid(row=0, column=4, padx=5, pady=2)

        # Stocker les références
        filter_data = {
            "id": filter_id or f"filter_{len(self.filters_list)}",
            "frame": filter_frame,
            "active_var": active_var,
            "type_var": type_var,
            "criteria_var": criteria_var,
            "value_var": value_var,
            "criteria_combo": criteria_combo,
            "value_widget": value_widget,
        }

        self.filters_list.append(filter_data)

        # Configurer les critères selon le type
        self.update_criteria_options(filter_data)

    def on_filter_type_changed(self, filter_id, new_type):
        """Quand le type de filtre change, mettre à jour les critères"""
        filter_data = next((f for f in self.filters_list if f["id"] == filter_id), None)
        if filter_data:
            self.update_criteria_options(filter_data)
            self.on_filter_changed()

    def update_criteria_options(self, filter_data):
        """Mettre à jour les options de critères selon le type de filtre"""

        filter_type = filter_data["type_var"].get()
        criteria_combo = filter_data["criteria_combo"]

        if filter_type == "Statut d'exécution":
            criteria_combo["values"] = [
                "En cours d'exécution",
                "Terminé",
                "En erreur",
                "En attente",
            ]
            filter_data["criteria_var"].set("En cours d'exécution")

        elif filter_type == "Modèle":
            criteria_combo["values"] = [
                "Égal à",
                "Contient",
                "Commence par",
                "Finit par",
            ]
            filter_data["criteria_var"].set("Égal à")

        elif filter_type == "Hiérarchie":
            criteria_combo["values"] = [
                "Fils du prompt sélectionné",
                "Parent du prompt sélectionné",
                "Racine (sans parent)",
                "Avec enfants",
            ]
            filter_data["criteria_var"].set("Fils du prompt sélectionné")

        elif filter_type == "Nom":
            criteria_combo["values"] = [
                "Contient",
                "Égal à",
                "Commence par",
                "Finit par",
            ]
            filter_data["criteria_var"].set("Contient")

        elif filter_type == "Statut":
            criteria_combo["values"] = ["Égal à", "Différent de"]
            filter_data["criteria_var"].set("Égal à")

        elif filter_type == "Environnement":
            criteria_combo["values"] = [
                "Égal à",
                "Contient",
                "Vide",
                "Non vide",
            ]
            filter_data["criteria_var"].set("Égal à")

    def add_new_filter(self):
        """Ajouter un nouveau filtre vide"""
        self.add_filter_row()

    def remove_filter_row(self, filter_id):
        """Supprimer une ligne de filtre"""
        filter_data = next((f for f in self.filters_list if f["id"] == filter_id), None)
        if filter_data:
            filter_data["frame"].destroy()
            self.filters_list.remove(filter_data)
            self.on_filter_changed()

    def on_filter_changed(self):
        """Appelé quand un filtre change"""
        # Pour l'instant, ne pas appliquer automatiquement
        pass

    def apply_filters(self):
        """Appliquer tous les filtres actifs à la liste des prompts"""

        if not hasattr(self, "db_manager") or not self.db_manager:
            return

        # Récupérer tous les prompts de base (utiliser get_all_prompts pour cohérence)
        try:
            all_prompts = self.db_manager.get_all_prompts()
        except Exception as e:
            print(f"Erreur lors de la récupération des prompts: {e}")
            return

        filtered_prompts = all_prompts.copy()
        active_filters_count = 0

        # Appliquer chaque filtre actif
        for filter_data in self.filters_list:
            if not filter_data["active_var"].get():
                continue

            active_filters_count += 1
            filter_type = filter_data["type_var"].get()
            criteria = filter_data["criteria_var"].get()
            value = filter_data["value_var"].get()

            filtered_prompts = self.apply_single_filter(
                filtered_prompts, filter_type, criteria, value
            )

        # Si aucun filtre actif, utiliser la méthode standard
        if active_filters_count == 0:
            self.load_prompts()
            self.stats_label.config(text="Aucun filtre appliqué")
            return

        # Mettre à jour l'affichage avec les prompts filtrés
        self.update_prompts_display(filtered_prompts)

        # Mettre à jour les statistiques
        total_prompts = len(all_prompts)
        filtered_count = len(filtered_prompts)
        stats_text = f"{active_filters_count} filtre(s) actif(s) - {filtered_count}/{total_prompts} prompts affichés"
        self.stats_label.config(text=stats_text)

    def apply_single_filter(self, prompts, filter_type, criteria, value):
        """Appliquer un filtre spécifique à la liste de prompts"""

        result = []

        for prompt in prompts:
            # prompt est un tuple: (id, name, parent, model, workflow, status, comment, id_env) - format get_all_prompts
            prompt_id, name, parent, model, workflow, status, comment, id_env = prompt

            include_prompt = False

            if filter_type == "Statut d'exécution":
                # Vérifier si le prompt est en cours d'exécution
                is_executing = any(
                    exec_item["prompt_name"] == name
                    and exec_item["message"] in ["En cours", "Génération"]
                    for exec_item in self.execution_stack
                )

                if criteria == "En cours d'exécution":
                    include_prompt = is_executing
                elif criteria == "Terminé":
                    include_prompt = not is_executing

            elif filter_type == "Modèle":
                if criteria == "Égal à":
                    include_prompt = (model or "").lower() == value.lower()
                elif criteria == "Contient":
                    include_prompt = value.lower() in (model or "").lower()
                elif criteria == "Commence par":
                    include_prompt = (model or "").lower().startswith(value.lower())
                elif criteria == "Finit par":
                    include_prompt = (model or "").lower().endswith(value.lower())

            elif filter_type == "Hiérarchie":
                if criteria == "Fils du prompt sélectionné":
                    selected_item = self.prompts_tree.selection()
                    if selected_item:
                        selected_id = self.prompts_tree.item(selected_item[0])[
                            "values"
                        ][0]
                        include_prompt = parent == selected_id
                    else:
                        include_prompt = False
                elif criteria == "Racine (sans parent)":
                    include_prompt = parent is None or parent == ""

            elif filter_type == "Nom":
                if criteria == "Contient":
                    include_prompt = value.lower() in (name or "").lower()
                elif criteria == "Égal à":
                    include_prompt = (name or "").lower() == value.lower()
                elif criteria == "Commence par":
                    include_prompt = (name or "").lower().startswith(value.lower())
                elif criteria == "Finit par":
                    include_prompt = (name or "").lower().endswith(value.lower())

            elif filter_type == "Statut":
                if criteria == "Égal à":
                    include_prompt = (status or "").lower() == value.lower()
                elif criteria == "Différent de":
                    include_prompt = (status or "").lower() != value.lower()

            elif filter_type == "Environnement":
                if criteria == "Égal à":
                    include_prompt = (id_env or "").lower() == value.lower()
                elif criteria == "Contient":
                    include_prompt = value.lower() in (id_env or "").lower()
                elif criteria == "Vide":
                    include_prompt = not id_env or id_env.strip() == ""
                elif criteria == "Non vide":
                    include_prompt = id_env and id_env.strip() != ""

            if include_prompt:
                result.append(prompt)

        return result

    def update_prompts_display(self, filtered_prompts):
        """Mettre à jour l'affichage du TreeView avec les prompts filtrés"""

        # Sauvegarder la sélection actuelle
        selected_items = self.prompts_tree.selection()
        selected_ids = []
        for item in selected_items:
            try:
                selected_ids.append(int(item))  # l'iid est l'ID du prompt
            except:
                pass

        # Vider le TreeView
        for item in self.prompts_tree.get_children():
            self.prompts_tree.delete(item)

        # Ajouter les prompts filtrés
        for prompt in filtered_prompts:
            prompt_id, name, parent, model, workflow, status, comment, id_env = prompt

            # Format des valeurs pour l'affichage (même format que load_prompts)
            display_values = (
                prompt_id,
                name or "",
                status or "new",
                model or "",
                comment or "",
                parent or "",
                id_env or "",
            )

            # Insérer avec iid pour pouvoir identifier l'élément
            item = self.prompts_tree.insert(
                "", "end", iid=str(prompt_id), values=display_values
            )

            # Restaurer la sélection si c'était sélectionné avant
            if prompt_id in selected_ids:
                self.prompts_tree.selection_add(str(prompt_id))
                self.selected_prompt_id = prompt_id
                # Recharger les détails du prompt sélectionné
                self.load_prompt_details(prompt_id)

    def reset_filters(self):
        """Réinitialiser tous les filtres"""

        for filter_data in self.filters_list:
            filter_data["active_var"].set(False)
            filter_data["value_var"].set("")

        # Recharger tous les prompts (pas de filtre)
        self.load_prompts()

        # Mettre à jour les statistiques
        self.stats_label.config(text="Aucun filtre appliqué")

    def refresh_prompts_display(self):
        """Rafraîchir l'affichage des prompts en respectant les filtres actifs"""

        # Vérifier s'il y a des filtres actifs
        if not hasattr(self, "filters_list"):
            # Pas de système de filtres initialisé, utiliser la méthode standard
            self.load_prompts()
            return

        # Compter les filtres actifs
        active_filters_count = 0
        for filter_data in self.filters_list:
            if filter_data["active_var"].get():
                active_filters_count += 1
                break  # On a trouvé au moins un filtre actif

        if active_filters_count == 0:
            # Aucun filtre actif, utiliser la méthode standard
            self.load_prompts()
            if hasattr(self, "stats_label"):
                self.stats_label.config(text="Aucun filtre appliqué")
        else:
            # Des filtres sont actifs, les réappliquer
            self.apply_filters()

    def has_active_filters(self):
        """Vérifier s'il y a des filtres actifs"""
        if not hasattr(self, "filters_list"):
            return False

        for filter_data in self.filters_list:
            if filter_data["active_var"].get():
                return True
        return False

    # === Méthode d'accès au répertoire d'images ===

    def open_images_in_explorer(self):
        """Ouvrir le répertoire principal des images dans l'explorateur"""
        try:
            import subprocess
            import platform

            path = self.images_path_var.get()

            if not os.path.exists(path):
                response = messagebox.askyesno(
                    "Répertoire inexistant",
                    f"Le répertoire n'existe pas:\n{path}\n\nVoulez-vous le créer?",
                )
                if response:
                    os.makedirs(path, exist_ok=True)
                else:
                    return

            # Ouvrir selon l'OS
            system = platform.system()
            if system == "Windows":
                subprocess.run(["explorer", path])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])

            self.update_status(f"Ouverture du répertoire: {os.path.basename(path)}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'explorateur: {e}")

    def test_comfyui_connection(self):
        """Tester la connexion avec ComfyUI et mettre à jour les indicateurs visuels"""
        # Désactiver le bouton pendant le test
        self.test_connection_btn.config(state="disabled", text="🔄 Test en cours...")

        # Indicateur de test en cours
        self.status_icon_label.config(text="🟡", foreground="orange")
        self.status_text_label.config(
            text="Test de connexion en cours...", foreground="orange"
        )

        # Forcer la mise à jour de l'interface
        self.root.update_idletasks()

        try:
            # Importer et tester la connexion ComfyUI
            from cy6_websocket_api_client import workflow_is_running

            # Récupérer les informations du serveur
            server_info = os.getenv("COMFYUI_SERVER", "127.0.0.1:8188")

            # Tenter la connexion
            import requests
            import json

            # Test de connexion HTTP basique
            url = f"http://{server_info}/system_stats"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                # Connexion réussie
                self.status_icon_label.config(text="✅", foreground="green")
                self.status_text_label.config(
                    text="Connexion ComfyUI réussie", foreground="green"
                )

                # Récupérer les détails
                stats = response.json()
                details = f"✅ CONNEXION RÉUSSIE\n\n"
                details += f"Serveur: {server_info}\n"
                details += f"Status: {response.status_code} OK\n"
                details += f"Système:\n"

                if "system" in stats:
                    for key, value in stats["system"].items():
                        details += f"  • {key}: {value}\n"

                # Test WebSocket (optionnel)
                try:
                    is_running = workflow_is_running()
                    details += f"\nWebSocket: {'✅ Connecté' if is_running is not None else '⚠️ Non testé'}\n"
                except Exception as ws_error:
                    details += f"\nWebSocket: ❌ Erreur ({str(ws_error)})\n"

                self.update_status("Connexion ComfyUI : OK")

            else:
                # Erreur HTTP
                raise Exception(f"HTTP {response.status_code}")

        except requests.exceptions.ConnectionError:
            # Serveur non accessible
            self.status_icon_label.config(text="❌", foreground="red")
            self.status_text_label.config(
                text="ComfyUI non accessible", foreground="red"
            )

            details = f"❌ CONNEXION ÉCHOUÉE\n\n"
            details += f"Serveur: {server_info}\n"
            details += f"Erreur: Serveur non accessible\n\n"
            details += f"Vérifications à effectuer:\n"
            details += f"  • ComfyUI est-il démarré ?\n"
            details += f"  • Le serveur écoute-t-il sur {server_info} ?\n"
            details += f"  • Y a-t-il un firewall qui bloque ?\n"

            self.update_status("Connexion ComfyUI : ÉCHEC")

        except requests.exceptions.Timeout:
            # Timeout
            self.status_icon_label.config(text="⏱️", foreground="orange")
            self.status_text_label.config(text="ComfyUI : Timeout", foreground="orange")

            details = f"⏱️ TIMEOUT\n\n"
            details += f"Serveur: {server_info}\n"
            details += f"Erreur: Timeout (>5s)\n\n"
            details += f"Le serveur ComfyUI est peut-être surchargé.\n"

            self.update_status("Connexion ComfyUI : TIMEOUT")

        except Exception as e:
            # Autres erreurs
            self.status_icon_label.config(text="❌", foreground="red")
            self.status_text_label.config(text=f"Erreur: {str(e)}", foreground="red")

            details = f"❌ ERREUR\n\n"
            details += f"Serveur: {server_info}\n"
            details += f"Erreur: {str(e)}\n\n"
            details += f"Détails techniques:\n{str(e)}\n"

            self.update_status(f"Connexion ComfyUI : ERREUR")

        finally:
            # Remettre le bouton en état normal
            self.test_connection_btn.config(
                state="normal", text="🔗 Tester la connexion"
            )

            # Afficher les détails techniques
            self.details_text.config(state="normal")
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, details)
            self.details_text.config(state="disabled")

            # Afficher le frame des détails s'il n'est pas déjà visible
            if not self.details_frame.winfo_viewable():
                self.details_frame.pack(fill="both", expand=True, pady=(20, 0))

    def get_model_metadata(model_path: str) -> dict:
        """
        Lit les métadonnées d'un fichier .safetensors et les retourne sous forme de dictionnaire.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Fichier introuvable : {model_path}")

        if not SAFETENSORS_AVAILABLE:
            raise RuntimeError(
                "safetensors n'est pas disponible. Installez torch et safetensors pour cette fonctionnalité."
            )

        try:
            with safe_open(model_path, framework="pt") as f:
                metadata = f.metadata()
            return metadata
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la lecture du modèle : {str(e)}")

    def identify_comfyui_environment(self):
        """Identifier l'environnement ComfyUI - UNIQUEMENT via le custom node ExtraPathReader"""
        import logging
        import time

        # Configuration du logging pour cette fonction
        logger = logging.getLogger(__name__)

        print("\n" + "=" * 60)
        print("🚀 DÉBUT - Identification de l'environnement ComfyUI")
        print("=" * 60)
        logger.info("Début de l'identification de l'environnement ComfyUI")

        # Identification UNIQUEMENT via le custom node
        try:
            self._identify_with_custom_node()
            return  # Succès avec custom node
        except Exception as custom_node_error:
            print(f"❌ Identification via custom node échouée: {custom_node_error}")
            logger.error(f"Identification via custom node échouée: {custom_node_error}")

            # Pas de fallback - l'identification échoue si le custom node ne fonctionne pas
            raise custom_node_error

    def _identify_with_custom_node(self):
        """Identifier l'environnement avec le custom node ExtraPathReader"""
        import logging
        import time

        logger = logging.getLogger(__name__)

        try:
            # Importer notre classe de custom node caller
            print("📦 Import de ComfyUICustomNodeCaller...")
            logger.info("Import de ComfyUICustomNodeCaller")
            from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

            # Mettre à jour le statut
            print("🔍 Mise à jour du statut de l'interface...")
            logger.info("Mise à jour du statut de l'interface")
            self.config_info_label.config(
                text="🔍 Connexion à ComfyUI et récupération des extra paths...",
                foreground="blue",
            )
            self.root.update()

            # Utiliser le custom node caller pour appeler ExtraPathReader
            print("🔧 Initialisation du ComfyUICustomNodeCaller...")
            logger.info("Initialisation du ComfyUICustomNodeCaller")

            with ComfyUICustomNodeCaller() as caller:
                print("✅ ComfyUICustomNodeCaller initialisé avec succès")
                logger.info("ComfyUICustomNodeCaller initialisé avec succès")

                # Vérifier que ComfyUI est accessible
                print("📡 Vérification du statut du serveur ComfyUI...")
                logger.info("Vérification du statut du serveur ComfyUI")
                status = caller.get_server_status()

                print(f"📊 Statut du serveur: {status['status']}")
                logger.info(f"Statut du serveur ComfyUI: {status}")

                if status["status"] != "online":
                    error_msg = f"ComfyUI n'est pas accessible: {status.get('error', 'Serveur offline')}"
                    print(f"❌ {error_msg}")
                    logger.error(error_msg)
                    raise Exception(error_msg)

                print("🟢 Serveur ComfyUI accessible et en ligne")
                logger.info("Serveur ComfyUI accessible et en ligne")

                # Test direct d'ExtraPathReader avec diagnostic
                print("🚀 Test diagnostic d'ExtraPathReader...")
                logger.info("Test diagnostic d'ExtraPathReader")

                start_time = time.time()

                # Essayer d'abord la méthode de test direct
                diagnostic_result = caller.test_extra_path_reader_direct()

                if diagnostic_result.get("error", True):
                    print("❌ Test direct échoué, tentative avec méthode standard...")
                    try:
                        result = caller.call_custom_node(
                            node_type="ExtraPathReader", inputs={}
                        )
                    except Exception as e:
                        print(f"❌ Méthode standard également échouée: {e}")
                        print("🔍 Diagnostic détaillé:")
                        print(
                            f"   - Workflow utilisé: {diagnostic_result.get('workflow_used', 'N/A')}"
                        )
                        print(
                            f"   - Statut HTTP: {diagnostic_result.get('status_code', 'N/A')}"
                        )
                        print(
                            f"   - Erreur: {diagnostic_result.get('exception', 'N/A')}"
                        )
                        raise e
                else:
                    result = diagnostic_result["result"]
                    print("✅ Test direct réussi !")

                end_time = time.time()

                print(
                    f"✅ Custom node appelé avec succès en {end_time - start_time:.2f}s"
                )
                print(f"📋 Résultat: {result}")
                logger.info(
                    f"Custom node ExtraPathReader appelé avec succès en {end_time - start_time:.2f}s: {result}"
                )

                # Récupérer la réponse (normalement contient un prompt_id)
                if "prompt_id" in result:
                    prompt_id = result["prompt_id"]
                    print(f"🆔 Prompt ID reçu: {prompt_id}")
                    logger.info(f"Prompt ID reçu: {prompt_id}")

                    # Attendre un peu que le workflow s'exécute
                    print("⏳ Attente de l'exécution du workflow (2s)...")
                    logger.info("Attente de l'exécution du workflow")
                    time.sleep(2)

                    # Mise à jour de l'interface
                    self.config_info_label.config(
                        text="⏳ Récupération des données du custom node...",
                        foreground="orange",
                    )
                    self.root.update()

                    # Récupération des données directement depuis le résultat du custom node
                    print("📂 Récupération des données du custom node...")
                    logger.info("Début de récupération des données du custom node")

                    # Le custom node doit retourner les données dans le résultat directement
                    # Nous devons récupérer la sortie du custom node via l'API ComfyUI
                    try:
                        extra_paths_data = caller.get_custom_node_output(prompt_id, "1")
                        if extra_paths_data and isinstance(extra_paths_data, str):
                            # Le custom node retourne un JSON string, le parser
                            import json
                            extra_paths_data = json.loads(extra_paths_data)
                            print("✅ Données du custom node récupérées et parsées")
                        else:
                            raise Exception("Données du custom node non valides ou vides")
                    except Exception as e:
                        print(f"❌ Impossible de récupérer les données du custom node: {e}")
                        raise Exception(f"Custom node non fonctionnel: {e}")

                    if extra_paths_data:
                        print("✅ Extra paths récupérés avec succès")
                        print(
                            f"📊 Données récupérées: {list(extra_paths_data.keys()) if isinstance(extra_paths_data, dict) else type(extra_paths_data)}"
                        )
                        logger.info(f"Extra paths récupérés: {extra_paths_data}")

                        # Stocker les extra paths dans le gestionnaire de chemins
                        print("💾 Stockage des extra paths dans cy8_paths_manager...")
                        from cy8_paths import set_extra_paths

                        set_extra_paths(extra_paths_data)
                        logger.info("Extra paths stockés dans cy8_paths_manager")

                        # Mettre à jour les informations de l'onglet Env si il existe
                        if hasattr(self, "env_config_id_label") and hasattr(
                            self, "env_root_label"
                        ):
                            comfyui_root = extra_paths_data.get(
                                "comfyui_root", "Non détecté"
                            )
                            self.env_root_label.config(
                                text=comfyui_root, foreground="green"
                            )
                            print(f"📍 Racine ComfyUI mise à jour: {comfyui_root}")

                        # Actualiser immédiatement l'affichage des extra paths
                        print(
                            "🔄 Actualisation immédiate du tableau des extra paths..."
                        )
                        self.refresh_env_data()
                        logger.info("Tableau des extra paths actualisé après stockage")
                    else:
                        print("❌ Aucune donnée extra paths récupérée")
                        logger.warning("Aucune donnée extra paths récupérée")

                    if extra_paths_data:
                        # Le custom node retourne maintenant un objet avec comfyui_root, config_path et extra_paths
                        print("🔍 Extraction de l'ID de configuration...")
                        logger.info("Début de l'extraction de l'ID de configuration")

                        config_id = self._extract_config_id_from_extra_paths(
                            extra_paths_data
                        )

                        if config_id:
                            print(f"🎯 ID de configuration extrait: {config_id}")
                            logger.info(
                                f"ID de configuration extrait avec succès: {config_id}"
                            )

                            # Mettre à jour l'ID de configuration
                            print("✏️ Mise à jour de l'ID de configuration...")
                            self.comfyui_config_id.set(config_id)

                            # L'environnement sera défini via set_current_environment() plus bas
                            print(f"🌍 Préparation de la mise à jour de l'environnement: {config_id}")
                            logger.info(f"Configuration ID détecté: {config_id}")

                            # Mettre à jour le champ si il existe (compatibilité ancienne interface)
                            if self.config_id_entry and hasattr(
                                self.config_id_entry, "config"
                            ):
                                self.config_id_entry.config(state="normal")
                                self.config_id_entry.config(state="readonly")

                            self.config_info_label.config(
                                text=f"✅ Environnement identifié: {config_id}",
                                foreground="green",
                            )

                            print("✅ Interface mise à jour avec succès")
                            logger.info(
                                "Interface mise à jour avec l'ID de configuration"
                            )

                            # Mettre à jour l'onglet Env si il existe
                            if hasattr(self, "env_config_id_label"):
                                self.env_config_id_label.config(
                                    text=config_id, foreground="green"
                                )
                                print(
                                    f"🆔 ID de configuration mis à jour dans l'onglet Env: {config_id}"
                                )

                            messagebox.showinfo(
                                "Environnement identifié",
                                f"ID de configuration ComfyUI détecté:\n\n🆔 {config_id}\n\nSource: Extra paths ComfyUI",
                            )

                            # Définir l'environnement actuel pour l'onglet Log
                            self.set_current_environment(config_id)

                            # NOUVEAU: Ajouter un message dans le chat pour informer l'utilisateur
                            if hasattr(self, 'add_chat_message'):
                                self.add_chat_message(
                                    "system",
                                    f"✅ **ENVIRONNEMENT IDENTIFIÉ AVEC SUCCÈS**\n\n"
                                    f"🆔 **ID:** {config_id}\n"
                                    f"🧠 **RAG:** Synchronisé automatiquement\n"
                                    f"💾 **Sauvegarde:** Environnement persisté\n\n"
                                    f"Le système RAG est maintenant opérationnel pour cet environnement !"
                                )

                            # *** NOUVEAU: Détecter automatiquement le Python embedded ***
                            print("🐍 Détection automatique du Python embedded...")
                            logger.info("Début de la détection automatique du Python embedded")

                            try:
                                python_path = caller.get_python_path_from_comfyui()
                                if python_path:
                                    print(f"✅ Python path détecté: {python_path}")
                                    logger.info(f"Python path détecté: {python_path}")

                                    # Stocker le chemin Python détecté
                                    self.detected_python_path = python_path

                                    # Mettre à jour l'interface Python si elle existe
                                    if hasattr(self, 'python_status_label'):
                                        self.python_status_label.config(
                                            text=f"✅ Python embedded: {python_path.split('/')[-1] if '/' in python_path else python_path}",
                                            foreground="green"
                                        )

                                    # Mettre à jour le préfixe de commande si l'interface existe
                                    if hasattr(self, 'python_prefix_entry'):
                                        self.python_prefix_entry.config(state="normal")
                                        self.python_prefix_entry.delete(0, tk.END)
                                        self.python_prefix_entry.insert(0, f'"{python_path}" -m ')
                                        self.python_prefix_entry.config(state="readonly")

                                        # Activer le bouton d'exécution
                                        if hasattr(self, 'execute_python_btn'):
                                            self.execute_python_btn.config(state="normal")

                                    print(f"🎯 Python embedded configuré automatiquement")
                                else:
                                    print("⚠️ Aucun Python path détecté par le custom node")
                                    logger.warning("Aucun Python path détecté par le custom node")

                            except Exception as python_error:
                                print(f"⚠️ Erreur détection Python embedded: {python_error}")
                                logger.warning(f"Erreur détection Python embedded: {python_error}")
                                # Ne pas faire échouer l'identification pour une erreur Python

                            # *** NOUVEAU: Scanner et indexer automatiquement les analyses existantes ***
                            print("🧠 Scan automatique du référentiel RAG...")
                            logger.info("Début du scan automatique du référentiel RAG")

                            try:
                                self.scan_and_index_existing_analyses(config_id, logger)
                            except Exception as rag_error:
                                print(f"⚠️ Erreur scan RAG: {rag_error}")
                                logger.warning(f"Erreur scan RAG: {rag_error}")
                                # Ne pas faire échouer l'identification pour une erreur RAG

                            # *** NOUVEAU: Envoyer le contexte complet de l'environnement au RAG ***
                            print("🧠 Envoi du contexte environnement au RAG...")
                            logger.info("Début de l'envoi du contexte environnement au RAG")

                            try:
                                self.send_environment_context_to_rag(
                                    environment_id=config_id,
                                    extra_paths_data=extra_paths_data,
                                    server_status=status
                                )
                                print("✅ Contexte environnement envoyé au RAG avec succès")
                                logger.info("Contexte environnement envoyé au RAG avec succès")
                            except Exception as context_error:
                                print(f"⚠️ Erreur envoi contexte RAG: {context_error}")
                                logger.warning(f"Erreur envoi contexte RAG: {context_error}")
                                # Ne pas faire échouer l'identification pour une erreur de contexte

                            print("🎉 SUCCÈS - Identification terminée avec succès")
                            logger.info(
                                "Identification de l'environnement terminée avec succès"
                            )
                        else:
                            error_msg = (
                                "Aucun ID de configuration trouvé dans les extra paths"
                            )
                            print(f"❌ {error_msg}")
                            logger.error(error_msg)
                            raise Exception(error_msg)
                    else:
                        error_msg = (
                            "Impossible de récupérer les extra paths depuis ComfyUI"
                        )
                        print(f"❌ {error_msg}")
                        logger.error(error_msg)
                        raise Exception(error_msg)
                else:
                    error_msg = "Échec de l'exécution du custom node ExtraPathReader - Pas de prompt_id"
                    print(f"❌ {error_msg}")
                    logger.error(f"Résultat reçu sans prompt_id: {result}")
                    raise Exception(error_msg)

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ ERREUR lors de l'identification: {error_msg}")
            logger.error(
                f"Erreur lors de l'identification de l'environnement: {error_msg}"
            )

            # Afficher les détails de l'erreur pour le debugging
            import traceback

            traceback_str = traceback.format_exc()
            print(f"📋 Traceback complet:\n{traceback_str}")
            logger.error(f"Traceback: {traceback_str}")

            self.config_info_label.config(
                text=f"❌ Erreur: {str(e)[:50]}...", foreground="red"
            )
            messagebox.showerror(
                "Erreur d'identification",
                f"Impossible d'identifier l'environnement ComfyUI:\n\n{str(e)}\n\n"
                "Vérifiez que:\n"
                "• ComfyUI est démarré sur 127.0.0.1:8188\n"
                "• Le custom node ExtraPathReader est installé\n"
                "• Les extra paths sont configurés",
            )

        finally:
            print("🏁 FIN - Identification de l'environnement ComfyUI")
            print("=" * 60 + "\n")
            logger.info("Fin de l'identification de l'environnement ComfyUI")

    def refresh_env_data(self):
        """Actualiser les données de l'onglet environnement"""
        try:
            # Importer le gestionnaire de chemins
            from cy8_paths import cy8_paths_manager, get_all_extra_paths

            # Récupérer tous les extra paths stockés
            all_paths = get_all_extra_paths()

            # Vider le treeview
            for item in self.env_tree.get_children():
                self.env_tree.delete(item)

            if not all_paths:
                # Aucun chemin disponible
                self.env_tree.insert(
                    "",
                    "end",
                    values=("Aucun", "N/A", "Aucun extra path configuré", "N/A"),
                )
                self.env_config_id_label.config(text="Non identifié", foreground="gray")
                self.env_root_label.config(text="Non détecté", foreground="gray")
                return

            # Remplir le treeview avec les données
            for key, path_info in all_paths.items():
                self.env_tree.insert(
                    "",
                    "end",
                    values=(
                        key,
                        path_info.get("type", "N/A"),
                        path_info.get("path", "N/A"),
                        path_info.get("section", "N/A"),
                    ),
                )

            # Mettre à jour les informations générales si disponibles
            # (Ces informations seraient mises à jour lors de l'identification)

        except Exception as e:
            print(f"Erreur lors de l'actualisation des données environnement: {e}")
            # Afficher l'erreur dans le treeview
            for item in self.env_tree.get_children():
                self.env_tree.delete(item)
            self.env_tree.insert(
                "", "end", values=("Erreur", "N/A", f"Erreur: {str(e)}", "N/A")
            )

    def filter_env_paths(self, *args):
        """Filtrer les chemins affichés selon les critères de recherche"""
        try:
            from cy8_paths import get_all_extra_paths

            search_term = self.env_search_var.get().lower()
            type_filter = self.env_type_filter.get()

            # Vider le treeview
            for item in self.env_tree.get_children():
                self.env_tree.delete(item)

            # Récupérer tous les paths
            all_paths = get_all_extra_paths()

            if not all_paths:
                self.env_tree.insert(
                    "",
                    "end",
                    values=("Aucun", "N/A", "Aucun extra path configuré", "N/A"),
                )
                return

            # Filtrer et afficher
            for key, path_info in all_paths.items():
                path_type = path_info.get("type", "")
                path_value = path_info.get("path", "")

                # Appliquer le filtre de recherche
                if (
                    search_term
                    and search_term not in key.lower()
                    and search_term not in path_value.lower()
                ):
                    continue

                # Appliquer le filtre de type
                if type_filter != "Tous" and path_type != type_filter:
                    continue

                # Ajouter l'item filtré
                self.env_tree.insert(
                    "",
                    "end",
                    values=(
                        key,
                        path_type,
                        path_value,
                        path_info.get("section", "N/A"),
                    ),
                )

        except Exception as e:
            print(f"Erreur lors du filtrage: {e}")

    def copy_selected_path(self):
        """Copier le chemin sélectionné dans le presse-papiers"""
        try:
            selection = self.env_tree.selection()
            if not selection:
                messagebox.showwarning(
                    "Attention", "Veuillez sélectionner un chemin à copier."
                )
                return

            # Récupérer le chemin de l'item sélectionné
            item = self.env_tree.item(selection[0])
            path = item["values"][2]  # Colonne "path"

            # Copier dans le presse-papiers
            self.root.clipboard_clear()
            self.root.clipboard_append(path)

            messagebox.showinfo(
                "Copié", f"Chemin copié dans le presse-papiers:\n{path}"
            )

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier le chemin:\n{str(e)}")

    def _extract_config_id_from_extra_paths(self, extra_paths_data):
        """Extraire l'ID de configuration depuis les extra paths"""
        if not extra_paths_data or not isinstance(extra_paths_data, dict):
            return None

        import re

        # Extraire les informations du custom node
        comfyui_root = extra_paths_data.get("comfyui_root", "")
        extra_paths_config = extra_paths_data.get("extra_paths", {})

        # D'abord, chercher dans les chemins custom_nodes (priorité la plus haute)
        custom_nodes_config_id = None
        other_config_id = None

        for key, paths in extra_paths_config.items():
            if isinstance(paths, dict):
                # Parcourir tous les chemins dans cette section
                for path_key, path_value in paths.items():
                    if isinstance(path_value, str):
                        # Priorité aux chemins custom_nodes
                        if "custom_nodes" in path_value.lower():
                            # Pattern: H:/comfyui/G11_04/custom_nodes -> G11_04
                            pattern = r".*[/\\]comfyui[/\\]([^/\\]+)[/\\]custom_nodes"
                            match = re.search(pattern, path_value, re.IGNORECASE)
                            if match:
                                candidate_id = match.group(1)
                                if candidate_id.lower() not in [
                                    "models",
                                    "checkpoints",
                                    "loras",
                                    "embeddings",
                                    "vae",
                                ]:
                                    custom_nodes_config_id = candidate_id
                                    break

                        # Autres patterns pour fallback
                        patterns = [
                            r".*[/\\]comfyui[/\\]([^/\\]+)[/\\]",  # H:/comfyui/ID/...
                            r".*[/\\]([^/\\]+)[/\\]ComfyUI[/\\]",  # H:/ID/ComfyUI/...
                            r".*[/\\]comfyui[/\\]([^/\\]+)$",  # H:/comfyui/ID (fin de chemin)
                        ]

                        for pattern in patterns:
                            match = re.search(pattern, path_value, re.IGNORECASE)
                            if match:
                                candidate_id = match.group(1)
                                # Exclure certains noms génériques
                                if candidate_id.lower() not in [
                                    "models",
                                    "checkpoints",
                                    "loras",
                                    "embeddings",
                                    "vae",
                                    "custom_nodes",
                                ]:
                                    if not other_config_id:  # Prendre le premier trouvé
                                        other_config_id = candidate_id

                # Si on a trouvé un ID via custom_nodes, le retourner immédiatement
                if custom_nodes_config_id:
                    break

            elif isinstance(paths, str):
                # Traiter le cas où la valeur est directement une chaîne
                if "custom_nodes" in paths.lower():
                    pattern = r".*[/\\]comfyui[/\\]([^/\\]+)[/\\]custom_nodes"
                    match = re.search(pattern, paths, re.IGNORECASE)
                    if match:
                        candidate_id = match.group(1)
                        if candidate_id.lower() not in [
                            "models",
                            "checkpoints",
                            "loras",
                            "embeddings",
                            "vae",
                        ]:
                            custom_nodes_config_id = candidate_id
                            break

        # Priorité 1: ID trouvé via custom_nodes
        if custom_nodes_config_id:
            return custom_nodes_config_id

        # Priorité 2: Autres IDs trouvés
        if other_config_id:
            return other_config_id

        # Priorité 3: Essayer d'extraire l'ID depuis la racine ComfyUI détectée
        if comfyui_root:
            # Pattern: E:\Comfyui_G11\ComfyUI -> G11
            # Pattern: H:\comfyui\G11_04\ComfyUI -> G11_04
            patterns = [
                r".*[/\\]Comfyui_([^/\\]+)[/\\]ComfyUI",  # E:\Comfyui_G11\ComfyUI -> G11
                r".*[/\\]comfyui[/\\]([^/\\]+)[/\\]ComfyUI",  # H:\comfyui\G11_04\ComfyUI -> G11_04
                r".*[/\\]([^/\\]+)_ComfyUI[/\\]ComfyUI",  # X:\G11_ComfyUI\ComfyUI -> G11
            ]

            for pattern in patterns:
                match = re.search(pattern, comfyui_root, re.IGNORECASE)
                if match:
                    candidate_id = match.group(1)
                    return candidate_id

        # Priorité 4: ID par défaut basé sur le base_path si disponible
        if "comfyui" in extra_paths_config and isinstance(
            extra_paths_config["comfyui"], dict
        ):
            base_path = extra_paths_config["comfyui"].get("base_path", "")
            if base_path:
                pattern = r".*[/\\]([^/\\]+)[/\\]ComfyUI"
                match = re.search(pattern, base_path, re.IGNORECASE)
                if match:
                    return match.group(1)

        return None

    def browse_log_file(self):
        """Ouvrir un dialogue pour sélectionner le fichier de log ComfyUI"""
        from tkinter import filedialog

        initial_dir = (
            os.path.dirname(self.comfyui_log_path.get())
            if self.comfyui_log_path.get()
            else "."
        )

        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier de log ComfyUI",
            initialdir=initial_dir,
            filetypes=[
                ("Fichiers log", "*.log"),
                ("Fichiers texte", "*.txt"),
                ("Tous les fichiers", "*.*"),
            ],
        )

        if filename:
            self.comfyui_log_path.set(filename)
            # Sauvegarder automatiquement le chemin dans les préférences
            self.user_prefs.set_preference("comfyui_log_path", filename)
            print(f"Chemin du log sauvegardé: {filename}")

    def analyze_comfyui_log(self):
        """Analyser le fichier de log ComfyUI"""
        # Vérifier qu'un environnement est identifié
        if not self.current_environment_id:
            messagebox.showwarning(
                "Environnement requis",
                "Vous devez d'abord identifier l'environnement ComfyUI avant d'analyser le log.\n\n"
                "Allez dans l'onglet ComfyUI et cliquez sur '🔍 Identifier l'environnement'."
            )
            return

        log_path = self.comfyui_log_path.get().strip()

        if not log_path:
            messagebox.showwarning(
                "Attention", "Veuillez spécifier un fichier de log à analyser."
            )
            return

        if not os.path.exists(log_path):
            messagebox.showerror(
                "Erreur", f"Le fichier de log n'existe pas :\n{log_path}"
            )
            return

        # Désactiver le bouton pendant l'analyse
        self.analyze_log_btn.config(state="disabled", text="⏳ Analyse en cours...")
        self.log_status_label.config(text="Analyse en cours...", foreground="blue")

        # Vider le tableau des résultats précédents
        for item in self.log_results_tree.get_children():
            self.log_results_tree.delete(item)

        # Mettre à jour l'affichage
        self.root.update()

        try:
            # Analyser le fichier de log
            result = self.log_analyzer.analyze_log_file(log_path)

            if not result["success"]:
                messagebox.showerror("Erreur d'analyse", result["error"])
                self.log_status_label.config(
                    text="Erreur lors de l'analyse", foreground="red"
                )
                return

            # Stocker les résultats pour le filtrage
            entries = result["entries"]
            self._original_log_results = entries

            # Vider le tableau avant d'afficher les nouveaux résultats
            for item in self.log_results_tree.get_children():
                self.log_results_tree.delete(item)

            # Nettoyer les anciens résultats d'analyse pour cet environnement
            self.db_manager.clear_analysis_results(self.current_environment_id)

            # Stocker et afficher les résultats dans le tableau
            stored_count = 0
            for entry in entries:
                # Déterminer la couleur selon le type
                tag = entry["type"]

                # Préparer les informations pour l'affichage et le stockage
                original_message = entry["message"]
                display_message = original_message
                details_info = ""

                # Extraire des informations supplémentaires selon le type pour l'affichage
                if entry["type"] == "OK" and "(" in entry["message"]:
                    # Pour les custom nodes OK, extraire le temps
                    import re
                    time_match = re.search(r'\(([^)]+)\)', entry["message"])
                    if time_match:
                        details_info = time_match.group(1)
                        display_message = entry["message"].split(" (")[0]  # Message sans le temps
                elif entry["type"] == "ERREUR" and " | " in entry["message"]:
                    # Pour les erreurs, extraire les détails après le |
                    parts = entry["message"].split(" | ", 1)
                    if len(parts) > 1:
                        display_message = parts[0]  # Message principal
                        details_info = parts[1]     # Détails pour l'UI
                elif entry["type"] == "ATTENTION" and " | " in entry["message"]:
                    # Pour les warnings, traiter de même
                    parts = entry["message"].split(" | ", 1)
                    if len(parts) > 1:
                        display_message = parts[0]
                        details_info = parts[1]

                # Construire des détails enrichis pour la base de données
                details_db = self._build_rich_details_for_db(entry, original_message)

                # Stocker le résultat dans la base de données avec informations enrichies
                try:
                    success = self.db_manager.add_analysis_result(
                        environment_id=self.current_environment_id,
                        fichier=os.path.basename(log_path),  # Nom du fichier log
                        type_result=entry["type"],
                        niveau=entry["category"],
                        message=original_message,  # Stocker le message original complet
                        details=details_db  # Détails enrichis
                    )
                    if success:
                        stored_count += 1
                except Exception as e:
                    print(f"Erreur lors du stockage du résultat: {e}")

                # Insérer dans le tableau avec les informations traitées pour l'affichage
                item = self.log_results_tree.insert(
                    "",
                    "end",
                    values=(
                        entry.get("timestamp", "N/A"),
                        entry["type"],
                        entry["category"],
                        entry["element"],
                        display_message,  # Message traité pour l'affichage
                        details_info,     # Détails pour l'affichage (temps, type d'erreur, etc.)
                        entry["line"],
                    ),
                    tags=(tag,),
                )            # Mettre à jour le compteur de résultats
            if hasattr(self, "log_results_count_label"):
                self.log_results_count_label.config(text=f"{len(entries)} résultats")

            # Afficher un message de confirmation du stockage
            print(f"💾 Stockage en base: {stored_count}/{len(entries)} résultats sauvegardés pour l'environnement {self.current_environment_id}")

            # Mettre à jour l'ID de configuration s'il est trouvé dans le log
            detected_config_id = result.get("config_id")
            current_config_id = self.comfyui_config_id.get().strip()

            if detected_config_id and not current_config_id:
                # Si un ID est détecté et qu'il n'y en a pas déjà un saisi
                self.comfyui_config_id.set(detected_config_id)
                self.config_info_label.config(
                    text=f"✅ ID détecté automatiquement lors de l'analyse : {detected_config_id}",
                    foreground="green",
                )
            elif detected_config_id and current_config_id != detected_config_id:
                # Si un ID différent est détecté
                self.config_info_label.config(
                    text=f"ℹ️ ID détecté dans le log : {detected_config_id} (vous pouvez le remplacer)",
                    foreground="blue",
                )
            elif not detected_config_id and not current_config_id:
                # Aucun ID détecté ni saisi
                self.config_info_label.config(
                    text="💡 Aucun ID détecté dans le log. Saisissez-le manuellement si nécessaire.",
                    foreground="gray",
                )

            # Utiliser l'ID saisi ou détecté pour l'affichage
            display_config_id = current_config_id or detected_config_id

            # Mettre à jour le statut
            summary = result["summary"]
            status_text = f"Analyse terminée - {len(entries)} éléments trouvés (OK: {summary['custom_nodes_ok'] + summary['info_messages']}, Erreurs: {summary['custom_nodes_failed'] + summary['errors']}, Warnings: {summary['warnings']})"
            self.log_status_label.config(text=status_text, foreground="green")

            # Afficher un résumé dans une popup avec l'ID de configuration
            summary_text = self.log_analyzer.get_summary_text()
            config_info = (
                f"\n🆔 ID Configuration: {display_config_id}"
                if display_config_id
                else "\n🆔 ID Configuration: Non spécifié"
            )

            # Ajouter l'information de stockage
            storage_info = f"\n💾 {stored_count} résultats stockés en base de données"

            if entries:
                messagebox.showinfo(
                    "Analyse terminée",
                    f"Analyse du log ComfyUI terminée avec succès !{config_info}{storage_info}\n\n{summary_text}",
                )
            else:
                messagebox.showinfo(
                    "Analyse terminée",
                    f"Aucun élément significatif trouvé dans le log.{config_info}",
                )

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Erreur lors de l'analyse du log :\n{str(e)}"
            )
            self.log_status_label.config(
                text="Erreur lors de l'analyse", foreground="red"
            )

        finally:
            # Réactiver le bouton
            self.analyze_log_btn.config(state="normal", text="🔍 Analyser le log")

    def check_log_file_status(self):
        """Vérifier le statut du fichier log et mettre à jour l'interface"""
        log_path = self.comfyui_log_path.get()
        if os.path.exists(log_path):
            try:
                # Obtenir les informations du fichier
                stat = os.stat(log_path)
                size_mb = stat.st_size / (1024 * 1024)
                mtime = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)
                )

                # Construire le texte d'information avec taille et environnement
                info_text = f"✅ Fichier trouvé ({size_mb:.1f} MB, modifié le {mtime})\n"

                # Ajouter l'information d'environnement
                if self.current_environment_id:
                    info_text += f"🌍 Environnement: {self.current_environment_id}"
                else:
                    info_text += "⚠️ Environnement: Non identifié (requis pour l'analyse)"

                # Couleur selon le statut de l'environnement
                color = "green" if self.current_environment_id else "orange"
                self.log_file_info_label.config(text=info_text, foreground=color)

                # Activer/désactiver les boutons d'analyse selon l'environnement
                self.update_analysis_buttons_state()

            except Exception as e:
                self.log_file_info_label.config(
                    text=f"⚠️ Erreur lecture fichier: {e}", foreground="orange"
                )
                self.update_analysis_buttons_state()
        else:
            self.log_file_info_label.config(
                text="❌ Fichier log non trouvé", foreground="red"
            )
            self.update_analysis_buttons_state()

    def update_analysis_buttons_state(self):
        """Mettre à jour l'état des boutons d'analyse selon l'environnement identifié"""
        # Vérifier si un environnement est identifié et si le fichier log existe
        can_analyze = (
            self.current_environment_id is not None
            and os.path.exists(self.comfyui_log_path.get())
        )

        # Mettre à jour les boutons d'analyse
        if hasattr(self, 'analyze_log_btn'):
            if can_analyze:
                self.analyze_log_btn.config(
                    state="normal",
                    text="🔍 Analyser le log"
                )
            else:
                self.analyze_log_btn.config(
                    state="disabled",
                    text="🔍 Analyser le log (identification requise)"
                )

        if hasattr(self, 'ai_analyze_btn'):
            if can_analyze:
                self.ai_analyze_btn.config(
                    state="normal",
                    text="🤖 Analyse IA complète"
                )
            else:
                self.ai_analyze_btn.config(
                    state="disabled",
                    text="🤖 Analyse IA complète (identification requise)"
                )

    def set_current_environment(self, environment_id):
        """Définir l'environnement actuellement identifié"""
        print(f"🔧 DEBUG: set_current_environment appelé avec: {environment_id}")
        self.current_environment_id = environment_id
        print(f"🌍 Environnement identifié: {environment_id}")
        print(f"🔍 Vérification: self.current_environment_id = {self.current_environment_id}")

        # NOUVEAU: Sauvegarder l'environnement dans les préférences
        if hasattr(self, 'user_prefs') and self.user_prefs:
            self.user_prefs.set_preference("current_environment_id", environment_id)
            print(f"💾 Environnement sauvegardé: {environment_id}")

        # NOUVEAU: Synchroniser le gestionnaire RAG avec le nouvel environnement
        if hasattr(self, 'rag_manager') and self.rag_manager:
            if self.rag_manager.environment_id != environment_id:
                print(f"🔄 Synchronisation RAG: {self.rag_manager.environment_id} -> {environment_id}")
                self.rag_manager.environment_id = environment_id
                # Réinitialiser les composants RAG avec le nouvel environnement
                self.rag_manager._initialize_components()
                print("✅ RAG synchronisé avec le nouvel environnement")

                # Synchroniser le RAG Tester (il utilise maintenant dynamiquement l'environment_id)
                if hasattr(self, 'rag_tester') and self.rag_tester:
                    print(f"🧪 RAG Tester synchronisé: {self.rag_tester.environment_id}")

                # Synchroniser le Temporal RAG
                if hasattr(self, 'temporal_rag') and self.temporal_rag:
                    print("🕒 Temporal RAG synchronisé")

        # Mettre à jour l'affichage des informations du log
        self.check_log_file_status()

        # Mettre à jour la base de données si nécessaire
        if environment_id:
            self.db_manager.update_environment_analysis(environment_id)

    def refresh_log_analysis(self):
        """Actualiser l'analyse des logs"""
        # Vérifier le statut du fichier
        self.check_log_file_status()

        # Relancer l'analyse si des résultats existent déjà
        if len(self.log_results_tree.get_children()) > 0:
            self.analyze_comfyui_log()

    def export_log_analysis(self):
        """Exporter les résultats de l'analyse vers un fichier"""
        if len(self.log_results_tree.get_children()) == 0:
            messagebox.showwarning(
                "Aucun résultat", "Aucun résultat d'analyse à exporter."
            )
            return

        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            title="Exporter l'analyse des logs",
            defaultextension=".csv",
            filetypes=[
                ("Fichiers CSV", "*.csv"),
                ("Fichiers texte", "*.txt"),
                ("Tous les fichiers", "*.*"),
            ],
        )

        if filename:
            try:
                import csv

                with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    # En-têtes
                    writer.writerow(
                        ["État", "Catégorie", "Élément", "Message", "Ligne"]
                    )

                    # Données
                    for item in self.log_results_tree.get_children():
                        values = self.log_results_tree.item(item)["values"]
                        writer.writerow(values)

                messagebox.showinfo(
                    "Export réussi", f"Analyse exportée vers:\n{filename}"
                )
            except Exception as e:
                messagebox.showerror("Erreur d'export", f"Impossible d'exporter: {e}")

    def refresh_environments(self):
        """Actualiser le tableau des environnements"""
        try:
            print("🔄 DEBUG refresh_environments: Début de l'actualisation...")

            # Effacer le tableau
            for item in self.environments_tree.get_children():
                self.environments_tree.delete(item)

            # Récupérer les environnements depuis la base
            print("   📥 Appel de db_manager.get_all_environments()...")
            environments = self.db_manager.get_all_environments()
            print(f"   📊 {len(environments)} environnements récupérés")

            for idx, env in enumerate(environments):
                print(f"   🔍 Traitement environnement #{idx + 1}: {env}")

                (
                    env_id,
                    name,
                    path,
                    description,
                    last_analysis,
                    created_at,
                    updated_at,
                ) = env

                # Formater la date de dernière analyse
                if last_analysis:
                    from datetime import datetime

                    try:
                        analysis_date = datetime.fromisoformat(
                            last_analysis.replace("Z", "+00:00")
                        )
                        last_analysis_str = analysis_date.strftime("%d/%m/%Y %H:%M")
                    except:
                        last_analysis_str = last_analysis
                else:
                    last_analysis_str = "Jamais"

                # Déterminer le statut de l'environnement
                status = "🟢 Actif" if os.path.exists(path) else "🔴 Indisponible"

                # Ajouter l'environnement au tableau
                values = (env_id, name, path, last_analysis_str, status)
                print(f"      ➕ Insertion: {values}")
                self.environments_tree.insert("", "end", values=values)

            print(f"✅ Tableau des environnements actualisé : {len(environments)} environnements")

        except Exception as e:
            print(f"❌ Erreur lors de l'actualisation des environnements : {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erreur", f"Impossible d'actualiser les environnements :\n{e}"
            )

    def on_environment_select(self, event):
        """Gérer la sélection d'un environnement"""
        selection = self.environments_tree.selection()
        if not selection:
            return

        # Récupérer l'ID de l'environnement sélectionné
        item = selection[0]
        values = self.environments_tree.item(item)["values"]
        environment_id = values[0]

        print(f"Environnement sélectionné : {environment_id}")

        # CORRECTION: Mettre à jour l'environnement actuel
        self.current_environment_id = environment_id

        # Charger les résultats d'analyse pour cet environnement
        self.load_environment_analysis_results(environment_id)

    def on_environment_double_click(self, event):
        """Gérer le double-clic sur un environnement pour ouvrir la popup des actions"""
        selection = self.environments_tree.selection()
        if not selection:
            return

        # Récupérer l'ID de l'environnement sélectionné
        item = selection[0]
        values = self.environments_tree.item(item)["values"]
        environment_id = values[0]
        environment_name = values[1] if len(values) > 1 else environment_id

        self.open_env_actions_popup(environment_id, environment_name)

    def open_env_actions_popup(self, environment_id, environment_name):
        """Ouvrir la popup de gestion des actions pour un environnement"""
        import tkinter as tk
        from tkinter import ttk, messagebox
        import json
        import os

        # Créer la popup
        popup = tk.Toplevel(self.root)
        popup.title(f"Actions pour l'environnement {environment_name}")
        popup.geometry("800x600")
        popup.transient(self.root)
        popup.grab_set()

        # Centrer la popup
        center_window(popup, 800, 600)

        # Frame principal
        main_frame = ttk.Frame(popup, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Titre
        title_label = ttk.Label(
            main_frame,
            text=f"🔧 Actions pour {environment_name}",
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Frame pour le tableau des actions
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Tableau des actions
        columns = ("id", "desc", "cmd")
        actions_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Définir les colonnes
        actions_tree.heading("id", text="ID")
        actions_tree.heading("desc", text="Descriptif court")
        actions_tree.heading("cmd", text="Action (commande)")

        actions_tree.column("id", width=50, minwidth=40)
        actions_tree.column("desc", width=200, minwidth=150)
        actions_tree.column("cmd", width=400, minwidth=200)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=actions_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=actions_tree.xview)
        actions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack tree et scrollbars
        actions_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Fonction pour rafraîchir le tableau
        def refresh_actions():
            for item in actions_tree.get_children():
                actions_tree.delete(item)

            actions = self.db_manager.get_env_actions(environment_id)
            for action in actions:
                actions_tree.insert("", "end", values=(
                    action["id"],
                    action["short_desc"],
                    action["action_cmd"] or ""
                ))

        # Charger les actions initiales
        refresh_actions()

        # Frame pour les boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(0, 10))

        # Boutons CRUD
        ttk.Button(
            buttons_frame,
            text="➕ Ajouter",
            command=lambda: self.add_env_action_dialog(environment_id, refresh_actions)
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            buttons_frame,
            text="✏️ Modifier",
            command=lambda: self.edit_env_action_dialog(actions_tree, refresh_actions)
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            buttons_frame,
            text="🗑️ Supprimer",
            command=lambda: self.delete_env_action_dialog(actions_tree, refresh_actions)
        ).pack(side="left", padx=(0, 5))

        # Espace
        ttk.Frame(buttons_frame).pack(side="left", expand=True)

        # Bouton sauvegarde JSON
        ttk.Button(
            buttons_frame,
            text="💾 Sauvegarder JSON",
            command=lambda: self.save_env_actions_json(environment_id, environment_name)
        ).pack(side="right")

        # Bouton fermer
        ttk.Button(
            main_frame,
            text="Fermer",
            command=popup.destroy
        ).pack(pady=(10, 0))

    def add_env_action_dialog(self, environment_id, refresh_callback):
        """Dialogue pour ajouter une nouvelle action"""
        import tkinter as tk
        from tkinter import ttk, messagebox

        # Créer le dialogue
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter une action")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Centrer le dialogue
        center_window(dialog, 500, 300)

        # Frame principal
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill="both", expand=True)

        # Descriptif court
        ttk.Label(main_frame, text="Descriptif court:").pack(anchor="w")
        desc_entry = ttk.Entry(main_frame, width=60)
        desc_entry.pack(fill="x", pady=(5, 10))

        # Action/commande
        ttk.Label(main_frame, text="Action (commande):").pack(anchor="w")
        action_text = tk.Text(main_frame, height=8, width=60)
        action_text.pack(fill="both", expand=True, pady=(5, 10))

        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        def save_action():
            desc = desc_entry.get().strip()
            cmd = action_text.get("1.0", "end-1c").strip()

            if not desc:
                messagebox.showerror("Erreur", "Le descriptif est obligatoire")
                return

            action_id = self.db_manager.add_env_action(environment_id, desc, cmd)
            if action_id:
                messagebox.showinfo("Succès", "Action ajoutée avec succès")
                refresh_callback()
                dialog.destroy()
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout de l'action")

        ttk.Button(button_frame, text="Sauvegarder", command=save_action).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Annuler", command=dialog.destroy).pack(side="right")

        # Focus sur le champ descriptif
        desc_entry.focus()

    def edit_env_action_dialog(self, actions_tree, refresh_callback):
        """Dialogue pour modifier une action existante"""
        import tkinter as tk
        from tkinter import ttk, messagebox

        # Vérifier qu'une action est sélectionnée
        selection = actions_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une action à modifier")
            return

        # Récupérer les valeurs de l'action sélectionnée
        item = selection[0]
        values = actions_tree.item(item)["values"]
        action_id = values[0]
        current_desc = values[1]
        current_cmd = values[2]

        # Créer le dialogue
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier l'action")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Centrer le dialogue
        center_window(dialog, 500, 300)

        # Frame principal
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill="both", expand=True)

        # Descriptif court
        ttk.Label(main_frame, text="Descriptif court:").pack(anchor="w")
        desc_entry = ttk.Entry(main_frame, width=60)
        desc_entry.pack(fill="x", pady=(5, 10))
        desc_entry.insert(0, current_desc)

        # Action/commande
        ttk.Label(main_frame, text="Action (commande):").pack(anchor="w")
        action_text = tk.Text(main_frame, height=8, width=60)
        action_text.pack(fill="both", expand=True, pady=(5, 10))
        action_text.insert("1.0", current_cmd)

        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        def save_changes():
            desc = desc_entry.get().strip()
            cmd = action_text.get("1.0", "end-1c").strip()

            if not desc:
                messagebox.showerror("Erreur", "Le descriptif est obligatoire")
                return

            success = self.db_manager.update_env_action(action_id, desc, cmd)
            if success:
                messagebox.showinfo("Succès", "Action modifiée avec succès")
                refresh_callback()
                dialog.destroy()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la modification de l'action")

        ttk.Button(button_frame, text="Sauvegarder", command=save_changes).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Annuler", command=dialog.destroy).pack(side="right")

        # Focus sur le champ descriptif
        desc_entry.focus()

    def delete_env_action_dialog(self, actions_tree, refresh_callback):
        """Dialogue pour supprimer une action"""
        from tkinter import messagebox

        # Vérifier qu'une action est sélectionnée
        selection = actions_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une action à supprimer")
            return

        # Récupérer les valeurs de l'action sélectionnée
        item = selection[0]
        values = actions_tree.item(item)["values"]
        action_id = values[0]
        desc = values[1]

        # Demander confirmation
        result = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer l'action:\n\n'{desc}' ?"
        )

        if result:
            success = self.db_manager.delete_env_action(action_id)
            if success:
                messagebox.showinfo("Succès", "Action supprimée avec succès")
                refresh_callback()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression de l'action")

    def save_env_actions_json(self, environment_id, environment_name):
        """Sauvegarder les actions en JSON dans le répertoire analyses"""
        import json
        import os
        from tkinter import messagebox

        try:
            # Récupérer toutes les actions
            actions = self.db_manager.get_env_actions(environment_id)

            # Récupérer le répertoire d'analyses
            analyses_dir = self.db_manager.get_environment_analyses_directory(environment_id)

            if not analyses_dir:
                messagebox.showerror("Erreur", "Impossible de déterminer le répertoire d'analyses")
                return

            # Créer le répertoire s'il n'existe pas
            os.makedirs(analyses_dir, exist_ok=True)

            # Chemin du fichier JSON
            json_path = os.path.join(analyses_dir, "actions.json")

            # Préparer les données à sauvegarder
            export_data = {
                "environment_id": environment_id,
                "environment_name": environment_name,
                "export_date": datetime.now().isoformat(),
                "actions": actions
            }

            # Sauvegarder le fichier JSON
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo(
                "Sauvegarde réussie",
                f"Actions sauvegardées dans:\n{json_path}\n\n{len(actions)} action(s) exportée(s)"
            )

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")

    # === MÉTHODES CRUD POUR LES ENVIRONNEMENTS ===

    def add_environment(self):
        """Ajouter un nouvel environnement ComfyUI"""
        dialog = EnvironmentDialog(self.root, "Ajouter un environnement")
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            # dialog.result est maintenant un dictionnaire
            print(f"🔍 DEBUG add_environment: dialog.result = {dialog.result}")
            print(f"   Type: {type(dialog.result)}")

            env_id = dialog.result.get("id")
            name = dialog.result.get("name")
            path = dialog.result.get("path")

            print(f"   Extrait: env_id='{env_id}', name='{name}', path='{path}'")

            try:
                # Vérifier que l'ID n'existe pas déjà
                existing_envs = self.db_manager.get_all_environments()
                existing_ids = [env[0] for env in existing_envs]

                if env_id in existing_ids:
                    messagebox.showerror(
                        "Erreur",
                        f"L'ID '{env_id}' existe déjà. Veuillez choisir un ID unique."
                    )
                    return

                # Ajouter l'environnement à la base de données
                print(f"📥 Appel de db_manager.add_environment('{env_id}', '{name}', '{path}')")
                result = self.db_manager.add_environment(env_id, name, path)
                print(f"   Résultat: {result}")

                # Actualiser le tableau
                print("🔄 Actualisation du tableau...")
                self.refresh_environments()

                messagebox.showinfo(
                    "Succès",
                    f"Environnement '{name}' ajouté avec succès !"
                )

            except Exception as e:
                print(f"❌ Exception dans add_environment: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror(
                    "Erreur",
                    f"Impossible d'ajouter l'environnement : {e}"
                )

    def edit_environment(self):
        """Modifier l'environnement sélectionné"""
        selection = self.environments_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Aucune sélection",
                "Veuillez sélectionner un environnement à modifier."
            )
            return

        # Récupérer les données de l'environnement sélectionné
        item = selection[0]
        values = self.environments_tree.item(item)["values"]
        env_id, name, path = values[0], values[1], values[2]

        # Ouvrir le dialogue de modification
        dialog = EnvironmentDialog(
            self.root,
            "Modifier l'environnement",
            current_data=(env_id, name, path)
        )
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            # dialog.result est maintenant un dictionnaire
            print(f"🔍 DEBUG edit_environment: dialog.result = {dialog.result}")

            new_env_id = dialog.result.get("id")
            new_name = dialog.result.get("name")
            new_path = dialog.result.get("path")

            print(f"   Ancien: env_id='{env_id}', name='{name}', path='{path}'")
            print(f"   Nouveau: env_id='{new_env_id}', name='{new_name}', path='{new_path}'")

            try:
                # Si l'ID a changé, vérifier qu'il n'existe pas déjà
                if new_env_id != env_id:
                    existing_envs = self.db_manager.get_all_environments()
                    existing_ids = [env[0] for env in existing_envs if env[0] != env_id]

                    if new_env_id in existing_ids:
                        messagebox.showerror(
                            "Erreur",
                            f"L'ID '{new_env_id}' existe déjà. Veuillez choisir un ID unique."
                        )
                        return

                # Mettre à jour l'environnement
                print(f"📝 Appel de db_manager.update_environment('{env_id}', '{new_env_id}', '{new_name}', '{new_path}')")
                result = self.db_manager.update_environment(env_id, new_env_id, new_name, new_path)
                print(f"   Résultat: {result}")

                # Actualiser le tableau
                print("🔄 Actualisation du tableau...")
                self.refresh_environments()

                messagebox.showinfo(
                    "Succès",
                    f"Environnement '{new_name}' modifié avec succès !"
                )

            except Exception as e:
                print(f"❌ Exception dans edit_environment: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror(
                    "Erreur",
                    f"Impossible de modifier l'environnement : {e}"
                )

    def delete_environment(self):
        """Supprimer l'environnement sélectionné"""
        selection = self.environments_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Aucune sélection",
                "Veuillez sélectionner un environnement à supprimer."
            )
            return

        # Récupérer les données de l'environnement sélectionné
        item = selection[0]
        values = self.environments_tree.item(item)["values"]
        env_id, name = values[0], values[1]

        # Confirmation de suppression
        response = messagebox.askyesno(
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer l'environnement '{name}' (ID: {env_id}) ?\n\n"
            "Cette action supprimera également toutes les analyses associées et ne peut pas être annulée.",
            icon="warning"
        )

        if response:
            try:
                # Supprimer l'environnement de la base de données
                self.db_manager.delete_environment(env_id)

                # Actualiser le tableau
                self.refresh_environments()

                # Si c'était l'environnement actuel, le réinitialiser
                if self.current_environment_id == env_id:
                    self.current_environment_id = None

                messagebox.showinfo(
                    "Succès",
                    f"Environnement '{name}' supprimé avec succès !"
                )

            except Exception as e:
                messagebox.showerror(
                    "Erreur",
                    f"Impossible de supprimer l'environnement : {e}"
                )

    def load_environment_analysis_results(self, environment_id):
        """Charger les résultats d'analyse pour un environnement spécifique"""
        try:
            # Effacer le tableau des résultats
            for item in self.log_results_tree.get_children():
                self.log_results_tree.delete(item)

            # Récupérer les résultats d'analyse depuis la base
            results = self.db_manager.get_analysis_results(environment_id)

            if not results:
                self.log_results_count_label.config(text="0 résultat")
                print(f"Aucun résultat d'analyse trouvé pour {environment_id}")
                # Réinitialiser _original_log_results
                self._original_log_results = []
                return

            # Reconstruire les données au format _original_log_results pour la cohérence
            reconstructed_entries = []

            for result in results:
                (
                    result_id,
                    env_id,
                    fichier,
                    type_result,
                    niveau,
                    message,
                    details,
                    timestamp,
                ) = result

                # Formater le timestamp
                try:
                    from datetime import datetime

                    analysis_time = datetime.fromisoformat(
                        timestamp.replace("Z", "+00:00")
                    )
                    timestamp_str = analysis_time.strftime("%d/%m/%Y %H:%M:%S")
                except:
                    timestamp_str = timestamp

                # Traiter le message pour l'affichage (comme dans l'analyse fraîche)
                display_message = message
                details_info = ""
                element_name = fichier  # Par défaut, utiliser le nom du fichier
                line_number = "N/A"

                # Extraire les informations des détails enrichis si disponibles
                if details and details.strip():  # Vérifier que details n'est pas vide
                    try:
                        import json
                        details_dict = json.loads(details)

                        # Extraire le nom de l'élément (custom node)
                        if "element" in details_dict and details_dict["element"]:
                            element_name = details_dict["element"]

                        # Extraire le numéro de ligne
                        if "line" in details_dict and details_dict["line"]:
                            line_number = str(details_dict["line"])

                        # Traiter le message pour extraire les détails d'affichage
                        if type_result == "OK" and "time" in details_dict:
                            details_info = details_dict["time"]
                            if " (" in message:
                                display_message = message.split(" (")[0]
                        elif type_result in ["ERREUR", "ATTENTION"] and " | " in message:
                            parts = message.split(" | ", 1)
                            if len(parts) > 1:
                                display_message = parts[0]
                                details_info = parts[1]
                        elif "error_details" in details_dict and details_dict["error_details"]:
                            details_info = details_dict["error_details"]

                    except (json.JSONDecodeError, Exception) as e:
                        # CORRECTION: Traiter le format legacy avec extraction d'Element
                        # Format: "Element: nom | Line: X | Timestamp: Y | ..."
                        if "Element:" in details:
                            import re
                            element_match = re.search(r'Element:\s*([^|]+)', details)
                            if element_match:
                                element_name = element_match.group(1).strip()

                        if "Line:" in details:
                            import re
                            line_match = re.search(r'Line:\s*(\d+)', details)
                            if line_match:
                                line_number = line_match.group(1).strip()

                        # Essayer d'extraire quelques informations du message direct pour l'affichage
                        if " | " in message:
                            parts = message.split(" | ", 1)
                            if len(parts) > 1:
                                display_message = parts[0]
                                details_info = parts[1]

                        # Debug uniquement si les détails ne sont pas vides
                        if details and details.strip():
                            print(f"⚠️ Format legacy traité pour résultat {result_id} - Element: {element_name}")
                else:
                    # Pas de détails JSON, essayer de traiter le message directement
                    if " | " in message:
                        parts = message.split(" | ", 1)
                        if len(parts) > 1:
                            display_message = parts[0]
                            details_info = parts[1]



                # Reconstruire l'entrée au format _original_log_results
                entry = {
                    "timestamp": timestamp_str,
                    "type": type_result,
                    "category": niveau or "",
                    "element": element_name,
                    "message": message,
                    "line": line_number,
                    "file": fichier
                }
                reconstructed_entries.append(entry)

                # Ajouter le résultat au tableau avec le même format que l'analyse fraîche
                self.log_results_tree.insert(
                    "",
                    "end",
                    values=(
                        timestamp_str,
                        type_result,
                        niveau or "",
                        element_name,
                        display_message,
                        details_info,
                        line_number,
                    ),
                    tags=(type_result,),
                )

            # Mettre à jour _original_log_results pour la cohérence avec le filtrage
            self._original_log_results = reconstructed_entries

            # Mettre à jour le compteur
            count = len(results)
            self.log_results_count_label.config(
                text=f"{count} résultat{'s' if count > 1 else ''}"
            )

            print(
                f"✅ Résultats d'analyse chargés pour {environment_id} : {count} résultats avec format enrichi"
            )

        except Exception as e:
            print(f"❌ Erreur lors du chargement des résultats : {e}")
            # En cas d'erreur, réinitialiser _original_log_results
            self._original_log_results = []

    def filter_log_results(self, event=None):
        """Filtrer les résultats selon le type sélectionné"""
        filter_type = self.log_filter_var.get()
        search_term = self.log_search_var.get().lower()

        # Masquer tous les éléments d'abord
        for item in self.log_results_tree.get_children():
            self.log_results_tree.delete(item)

        # Réinsérer les éléments filtrés
        if hasattr(self, "_original_log_results"):
            visible_count = 0
            for entry in self._original_log_results:
                # Filtre par type
                if filter_type != "Tous" and entry["type"] != filter_type:
                    continue

                # Filtre par recherche
                if (
                    search_term
                    and search_term not in entry["message"].lower()
                    and search_term not in entry["element"].lower()
                ):
                    continue

                # Ajouter l'élément
                item = self.log_results_tree.insert(
                    "",
                    "end",
                    values=(
                        entry.get("timestamp", "N/A"),
                        entry["type"],
                        entry["category"],
                        entry["element"],
                        entry["message"],
                        entry["line"],
                    ),
                    tags=(entry["type"],),
                )
                visible_count += 1

            # Mettre à jour le compteur
            self.log_results_count_label.config(text=f"{visible_count} résultats")

    def search_log_results(self, *args):
        """Rechercher dans les résultats"""
        self.filter_log_results()

    def show_log_detail(self, event):
        """Afficher les détails d'une entrée de log (double-clic) sans analyse AI automatique"""
        selection = self.log_results_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.log_results_tree.item(item)["values"]

        if (
            len(values) >= 7
        ):  # Maintenant on a timestamp, type, category, element, message, details, line
            timestamp, type_val, category, element, message, details, line = values

            # Créer une fenêtre de détails simple
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Détails - {type_val} - {element}")
            detail_window.geometry("800x600")
            detail_window.transient(self.root)
            detail_window.grab_set()

            # Contenu de la fenêtre
            main_frame = ttk.Frame(detail_window, padding="10")
            main_frame.pack(fill="both", expand=True)

            # === SECTION 1: INFORMATIONS DÉTAILLÉES ===
            info_frame = ttk.LabelFrame(
                main_frame, text="📋 Informations détaillées", padding="10"
            )
            info_frame.pack(fill="x", pady=(0, 10))

            # Grille d'informations avec plus de détails
            row = 0
            ttk.Label(
                info_frame, text="Timestamp:", font=("TkDefaultFont", 9, "bold")
            ).grid(row=row, column=0, sticky="w", padx=(0, 10))
            ttk.Label(info_frame, text=timestamp).grid(row=row, column=1, sticky="w")
            row += 1

            ttk.Label(info_frame, text="État:", font=("TkDefaultFont", 9, "bold")).grid(
                row=row, column=0, sticky="w", padx=(0, 10)
            )
            status_label = ttk.Label(info_frame, text=type_val)
            status_label.grid(row=row, column=1, sticky="w")
            # Colorer selon le type
            if type_val == "ERREUR":
                status_label.configure(foreground="red")
            elif type_val == "ATTENTION":
                status_label.configure(foreground="orange")
            elif type_val == "OK":
                status_label.configure(foreground="green")
            row += 1

            ttk.Label(
                info_frame, text="Catégorie:", font=("TkDefaultFont", 9, "bold")
            ).grid(row=row, column=0, sticky="w", padx=(0, 10))
            ttk.Label(info_frame, text=category).grid(row=row, column=1, sticky="w")
            row += 1

            ttk.Label(
                info_frame, text="Élément/Node:", font=("TkDefaultFont", 9, "bold")
            ).grid(row=row, column=0, sticky="w", padx=(0, 10))
            element_label = ttk.Label(info_frame, text=element, font=("TkDefaultFont", 9, "bold"))
            element_label.grid(row=row, column=1, sticky="w")
            if element != "Système" and element != "Unknown":
                element_label.configure(foreground="blue")
            row += 1

            ttk.Label(
                info_frame, text="Ligne dans log:", font=("TkDefaultFont", 9, "bold")
            ).grid(row=row, column=0, sticky="w", padx=(0, 10))
            ttk.Label(info_frame, text=f"Ligne {line}").grid(row=row, column=1, sticky="w")

            # === SECTION 2: MESSAGE DÉTAILLÉ ===
            error_frame = ttk.LabelFrame(
                main_frame, text="📝 Message et détails", padding="10"
            )
            error_frame.pack(fill="both", expand=True, pady=(0, 10))

            # Créer un Text widget avec scrollbar pour le message
            text_frame = ttk.Frame(error_frame)
            text_frame.pack(fill="both", expand=True)

            message_text = tk.Text(
                text_frame,
                wrap="word",
                font=("Consolas", 9),
                height=8,
                background="#f8f9fa"
            )
            message_scrollbar = ttk.Scrollbar(
                text_frame, orient="vertical", command=message_text.yview
            )
            message_text.configure(yscrollcommand=message_scrollbar.set)

            # Insérer le message complet avec formatage
            detailed_message = f"MESSAGE:\n{message}\n\n"

            # Essayer de récupérer plus de détails depuis l'entrée originale
            if hasattr(self, '_original_log_results'):
                for entry in self._original_log_results:
                    if (entry.get("line") == int(line) and
                        entry.get("message") == message.split(" | ")[0]):
                        if "details" in entry:
                            detailed_message += f"CONTEXTE COMPLET:\n{entry['details']}\n\n"
                        break

            message_text.insert("1.0", detailed_message)
            message_text.config(state="disabled")

            message_text.pack(side="left", fill="both", expand=True)
            message_scrollbar.pack(side="right", fill="y")

            # === SECTION 3: ACTIONS DISPONIBLES ===
            buttons_frame = ttk.LabelFrame(
                main_frame, text="🔧 Actions disponibles", padding="10"
            )
            buttons_frame.pack(fill="x", pady=(0, 10))

            # Information sur l'analyse
            info_label = ttk.Label(
                buttons_frame,
                text="ℹ️ Pour une analyse complète avec l'IA, utilisez le bouton d'analyse ci-dessous.",
                font=("TkDefaultFont", 8),
                foreground="gray"
            )
            info_label.pack(anchor="w", pady=(0, 5))

            # Boutons d'action
            action_buttons_frame = ttk.Frame(buttons_frame)
            action_buttons_frame.pack(fill="x")

            ttk.Button(
                action_buttons_frame,
                text="🤖 Analyser avec l'IA (optionnel)",
                command=lambda: self.analyze_complete_log_with_ai(
                    timestamp, None, None, detail_window
                ),
            ).pack(side="left", padx=(0, 10))

            ttk.Button(
                action_buttons_frame,
                text="📋 Copier les détails",
                command=lambda: self._copy_log_details_to_clipboard(
                    timestamp, type_val, category, element, message, line
                ),
            ).pack(side="left", padx=(0, 10))

            ttk.Button(
                action_buttons_frame, text="✖️ Fermer", command=detail_window.destroy
            ).pack(side="right")

    def _copy_log_details_to_clipboard(self, timestamp, type_val, category, element, message, line):
        """Copier les détails du log dans le presse-papier"""
        details_text = f"""DÉTAILS DU LOG COMFYUI
========================
Timestamp: {timestamp}
État: {type_val}
Catégorie: {category}
Élément/Node: {element}
Ligne: {line}
Message: {message}
========================
"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(details_text)
            messagebox.showinfo("Copié", "Les détails ont été copiés dans le presse-papier.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier dans le presse-papier: {e}")

    def _build_rich_details_for_db(self, entry, original_message):
        """Construire des détails enrichis pour le stockage en base de données"""
        details_parts = []

        # Informations de base
        details_parts.append(f"Element: {entry.get('element', 'N/A')}")
        details_parts.append(f"Line: {entry.get('line', 'N/A')}")
        details_parts.append(f"Timestamp: {entry.get('timestamp', 'N/A')}")

        # Ajouter le message original complet s'il est différent du message affiché
        if " | " in original_message:
            parts = original_message.split(" | ", 1)
            if len(parts) > 1:
                details_parts.append(f"Context: {parts[1]}")

        # Ajouter les détails spécifiques selon le type
        if entry["type"] == "ERREUR":
            details_parts.append(f"Error_Type: {entry.get('category', 'Unknown')}")

        # Ajouter les détails bruts s'ils existent
        if "details" in entry and entry["details"]:
            details_parts.append(f"Full_Line: {entry['details']}")

        return " | ".join(details_parts)

    def open_solutions_folder(self):
        """Ouvrir le dossier des solutions"""
        try:
            # Utiliser le répertoire spécifique à l'environnement s'il y en a un de sélectionné
            if self.current_environment_id:
                solutions_dir = self.db_manager.get_environment_analyses_directory(self.current_environment_id)
                print(f"📁 Ouverture du répertoire d'analyses pour l'environnement {self.current_environment_id}: {solutions_dir}")
            else:
                # Si aucun environnement sélectionné, utiliser un répertoire par défaut
                solutions_dir = self.user_prefs.get_error_solutions_directory()
                # Créer le dossier s'il n'existe pas
                os.makedirs(solutions_dir, exist_ok=True)
                print(f"📁 Ouverture du répertoire par défaut: {solutions_dir}")

            # Ouvrir le dossier
            if os.name == "nt":  # Windows
                os.startfile(solutions_dir)
            elif os.name == "posix":  # Linux/Mac
                subprocess.run(["xdg-open", solutions_dir])
            else:
                messagebox.showinfo("Info", f"Dossier des solutions :\n{solutions_dir}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier :\n{e}")

    def analyze_complete_log_global(self):
        """Analyse complète du log avec Mistral AI (bouton global)"""
        # Vérifier qu'un environnement est identifié
        if not self.current_environment_id:
            messagebox.showwarning(
                "Environnement requis",
                "Vous devez d'abord identifier l'environnement ComfyUI avant d'analyser le log.\n\n"
                "Allez dans l'onglet ComfyUI et cliquez sur '🔍 Identifier l'environnement'."
            )
            return

        log_path = self.comfyui_log_path.get().strip()

        if not log_path or not os.path.exists(log_path):
            messagebox.showerror(
                "Erreur", "Veuillez d'abord sélectionner un fichier log valide."
            )
            return

        # Créer identifiant unique pour cette popup
        popup_id, formatted_title = get_popup_id("Analyse complète du log ComfyUI - Mistral AI", "analysis")

        # Créer une fenêtre de popup pour l'analyse globale
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title(formatted_title)
        analysis_window.geometry("1000x800")
        analysis_window.transient(self.root)
        analysis_window.grab_set()
        center_window(analysis_window, 1000, 800)

        # Gérer la fermeture avec désregistrement
        def on_close():
            close_popup(popup_id)
            analysis_window.destroy()

        analysis_window.protocol("WM_DELETE_WINDOW", on_close)

        # Contenu de la fenêtre
        main_frame = ttk.Frame(analysis_window, padding="15")
        main_frame.pack(fill="both", expand=True)

        # === TITRE ET INFORMATIONS ===
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            title_frame,
            text="🤖 Analyse complète du log ComfyUI avec Mistral AI",
            font=("TkDefaultFont", 14, "bold"),
        ).pack(side="left")

        # Informations sur le log
        info_frame = ttk.LabelFrame(
            main_frame, text="📋 Informations du log", padding="10"
        )
        info_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(info_frame, text="Fichier:", font=("TkDefaultFont", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Label(info_frame, text=log_path, font=("Consolas", 9)).grid(
            row=0, column=1, sticky="w"
        )

        try:
            file_size = os.path.getsize(log_path) / 1024  # KB
            ttk.Label(
                info_frame, text="Taille:", font=("TkDefaultFont", 9, "bold")
            ).grid(row=1, column=0, sticky="w", padx=(0, 10))
            ttk.Label(info_frame, text=f"{file_size:.1f} KB").grid(
                row=1, column=1, sticky="w"
            )
        except Exception:
            pass

        # === ZONE D'ANALYSE ===
        analysis_frame = ttk.LabelFrame(
            main_frame, text="🔍 Analyse et solutions", padding="10"
        )
        analysis_frame.pack(fill="both", expand=True, pady=(0, 15))

        # === ZONE DE QUESTION MODIFIABLE ===
        question_frame = ttk.Frame(analysis_frame)
        question_frame.pack(fill="x", pady=(0, 10))

        question_header = ttk.Frame(question_frame)
        question_header.pack(fill="x")

        ttk.Label(
            question_header,
            text="❓ Question pour Mistral AI:",
            font=("TkDefaultFont", 9, "bold"),
        ).pack(side="left")

        ttk.Button(
            question_header,
            text="📋 Exemples",
            command=lambda: self.show_question_examples(question_text),
            width=12,
        ).pack(side="right")

        question_text = tk.Text(
            question_frame, height=4, wrap="word", font=("TkDefaultFont", 10)
        )
        question_scrollbar = ttk.Scrollbar(
            question_frame, orient="vertical", command=question_text.yview
        )
        question_text.configure(yscrollcommand=question_scrollbar.set)

        question_text.pack(side="left", fill="x", expand=True, pady=(5, 0))
        question_scrollbar.pack(side="right", fill="y", pady=(5, 0))

        # Question par défaut
        default_question = (
            "Proposes moi des solutions pour les erreurs dans le fichier log"
        )
        question_text.insert("1.0", default_question)  # Séparateur
        ttk.Separator(analysis_frame, orient="horizontal").pack(fill="x", pady=10)

        # Zone de texte pour l'analyse
        analysis_text = tk.Text(analysis_frame, wrap="word", font=("TkDefaultFont", 10))
        analysis_scrollbar = ttk.Scrollbar(
            analysis_frame, orient="vertical", command=analysis_text.yview
        )
        analysis_text.configure(yscrollcommand=analysis_scrollbar.set)

        analysis_text.pack(side="left", fill="both", expand=True)
        analysis_scrollbar.pack(side="right", fill="y")

        # Message initial
        initial_message = """📋 ANALYSE COMPLÈTE DU LOG COMFYUI AVEC MISTRAL AI

✏️ ÉTAPE 1 : Modifiez la question ci-dessus selon vos besoins
✅ ÉTAPE 2 : Cliquez sur "🚀 Lancer l'analyse" pour obtenir une analyse complète

L'analyse portera sur :
• Détection et analyse de toutes les erreurs
• Contexte global et séquence des événements
• Solutions détaillées pour chaque problème identifié
• Recommandations d'optimisation et de diagnostic
• Suggestions de configuration

Vous pouvez personnaliser la question pour obtenir :
• Une analyse focalisée sur un type d'erreur spécifique
• Des recommandations particulières
• Un diagnostic approfondi d'un problème précis

L'analyse sera automatiquement sauvegardée dans le répertoire configuré.

⏳ L'analyse peut prendre quelques secondes selon la taille du log...
"""
        analysis_text.insert("1.0", initial_message)
        analysis_text.config(state="disabled")

        # Label de statut
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=(0, 10))

        status_label = ttk.Label(
            status_frame,
            text="💡 Prêt pour l'analyse complète du log ComfyUI",
            font=("TkDefaultFont", 9),
        )
        status_label.pack(side="left")

        # === BOUTONS D'ACTION ===
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x")

        ttk.Button(
            buttons_frame,
            text="🚀 Lancer l'analyse",
            command=lambda: self.start_global_log_analysis(
                log_path, analysis_text, status_label, analysis_window, question_text
            ),
            style="Accent.TButton",
        ).pack(side="left", padx=(0, 15))

        ttk.Button(
            buttons_frame,
            text="💾 Sauvegarder",
            command=lambda: self.save_global_analysis(
                analysis_text.get("1.0", "end-1c"), popup_id
            ),
        ).pack(side="left", padx=(0, 15))

        ttk.Button(
            buttons_frame,
            text="📁 Ouvrir dossier",
            command=lambda: self.open_solutions_folder(),
        ).pack(side="left", padx=(0, 15))

        ttk.Button(
            buttons_frame, text="❌ Fermer", command=on_close
        ).pack(side="right")

    def start_global_log_analysis(
        self, log_path, analysis_text, status_label, window, question_text
    ):
        """Démarre l'analyse globale du log avec Mistral AI"""
        import threading
        from datetime import datetime

        def analyze_in_thread():
            try:
                # Récupérer la question personnalisée
                custom_question = question_text.get("1.0", "end-1c").strip()
                if not custom_question:
                    custom_question = "Proposes moi des solutions pour les erreurs dans le fichier log"

                # Mise à jour du statut
                status_label.config(text="⏳ Lecture du fichier log...")
                window.update()

                # Lire le contenu du log
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    log_content = f.read()

                if not log_content.strip():
                    analysis_text.config(state="normal")
                    analysis_text.delete("1.0", "end")
                    analysis_text.insert(
                        "1.0", "❌ Le fichier log est vide ou illisible."
                    )
                    analysis_text.config(state="disabled")
                    status_label.config(text="❌ Échec de l'analyse")
                    return

                # Mise à jour du statut
                status_label.config(text="🤖 Analyse en cours avec Mistral AI...")
                window.update()

                # Importer le module Mistral
                try:
                    from cy8_mistral import analyze_comfyui_log_complete

                    # Lancer l'analyse complète avec la question personnalisée
                    role = "Tu es un expert assistant Python et ComfyUI"

                    result = analyze_comfyui_log_complete(
                        log_content, custom_question, role
                    )

                    # Afficher le résultat
                    analysis_text.config(state="normal")
                    analysis_text.delete("1.0", "end")

                    formatted_result = f"""🤖 ANALYSE COMPLÈTE DU LOG COMFYUI
Analysé le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}

❓ Question posée : {custom_question}

{result}

---
💾 Cette analyse a été générée par Mistral AI et peut être sauvegardée pour référence future.
"""
                    analysis_text.insert("1.0", formatted_result)
                    analysis_text.config(state="disabled")

                    status_label.config(text="✅ Analyse terminée avec succès")

                except ImportError:
                    analysis_text.config(state="normal")
                    analysis_text.delete("1.0", "end")
                    analysis_text.insert(
                        "1.0",
                        "❌ Module Mistral AI non disponible. Vérifiez la configuration.",
                    )
                    analysis_text.config(state="disabled")
                    status_label.config(text="❌ Module Mistral AI manquant")

                except Exception as e:
                    analysis_text.config(state="normal")
                    analysis_text.delete("1.0", "end")
                    analysis_text.insert(
                        "1.0", f"❌ Erreur lors de l'analyse IA :\n{str(e)}"
                    )
                    analysis_text.config(state="disabled")
                    status_label.config(text="❌ Erreur lors de l'analyse")

            except Exception as e:
                analysis_text.config(state="normal")
                analysis_text.delete("1.0", "end")
                analysis_text.insert(
                    "1.0", f"❌ Erreur lors de la lecture du log :\n{str(e)}"
                )
                analysis_text.config(state="disabled")
                status_label.config(text="❌ Erreur de lecture")

        # Lancer l'analyse dans un thread séparé
        thread = threading.Thread(target=analyze_in_thread)
        thread.daemon = True
        thread.start()

    def show_question_examples(self, question_text_widget):
        """Affiche une popup avec des exemples de questions pour Mistral AI"""
        examples_window = tk.Toplevel(self.root)
        examples_window.title("📋 Exemples de questions pour Mistral AI")
        examples_window.geometry("800x600")
        examples_window.transient(self.root)
        examples_window.grab_set()
        center_window(examples_window, 800, 600)

        main_frame = ttk.Frame(examples_window, padding="15")
        main_frame.pack(fill="both", expand=True)

        # Titre
        ttk.Label(
            main_frame,
            text="📋 Exemples de questions pour Mistral AI",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(pady=(0, 15))

        # Zone de texte avec exemples
        examples_text = tk.Text(main_frame, wrap="word", font=("TkDefaultFont", 10))
        examples_scrollbar = ttk.Scrollbar(
            main_frame, orient="vertical", command=examples_text.yview
        )
        examples_text.configure(yscrollcommand=examples_scrollbar.set)

        examples_text.pack(side="left", fill="both", expand=True)
        examples_scrollbar.pack(side="right", fill="y")

        # Contenu des exemples
        examples_content = """🔍 QUESTIONS GÉNÉRALES
=======================
• Proposes moi des solutions pour les erreurs dans le fichier log
• Analyse toutes les erreurs et donne-moi un plan d'action détaillé
• Identifie les problèmes de performance et propose des optimisations

⚠️ PROBLÈMES SPÉCIFIQUES
=========================
• Focus sur les erreurs de modèles manquants et comment les résoudre
• Analyse les erreurs de mémoire (CUDA/RAM) et propose des solutions
• Identifie les problèmes de custom nodes et comment les corriger
• Focus sur les erreurs de connexion réseau ou d'API

🔧 DIAGNOSTIC TECHNIQUE
========================
• Analyse la séquence d'événements menant aux erreurs principales
• Identifie les dépendances manquantes et comment les installer
• Explique les erreurs de configuration et comment les corriger
• Détecte les conflits entre extensions/custom nodes

🚀 OPTIMISATION
===============
• Propose des améliorations de configuration pour éviter ces erreurs
• Suggest performance optimizations based on the log analysis
• Analyse les patterns d'utilisation et recommande des améliorations
• Identifie les goulots d'étranglement et propose des solutions

💡 QUESTIONS CRÉATIVES
=======================
• Si tu étais un développeur ComfyUI, comment débugguerais-tu ces problèmes ?
• Explique-moi comme si j'étais débutant comment résoudre ces erreurs
• Classe les erreurs par priorité et donne un plan de résolution étape par étape
• Quelles sont les erreurs critiques vs celles qui sont juste informationnelles ?

🎯 FOCUS CONTEXTUEL
===================
• Analyse seulement les erreurs des dernières 24h de ce log
• Focus sur les erreurs qui empêchent la génération d'images
• Identifie les erreurs liées au chargement des modèles Stable Diffusion
• Analyse les problèmes de workflow et de noeuds custom

💡 CONSEIL : Soyez spécifique dans vos questions pour obtenir des réponses plus précises !"""

        examples_text.insert("1.0", examples_content)
        examples_text.config(state="disabled")

        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(15, 0))

        def use_selected_question():
            """Utilise la question sélectionnée dans le widget principal"""
            try:
                selected_text = examples_text.selection_get()
                if selected_text and selected_text.startswith("•"):
                    # Nettoyer la question (enlever le bullet point)
                    clean_question = selected_text.replace("• ", "").strip()
                    question_text_widget.delete("1.0", "end")
                    question_text_widget.insert("1.0", clean_question)
                    examples_window.destroy()
                else:
                    tk.messagebox.showinfo(
                        "Info", "Sélectionnez une ligne commençant par • dans la liste"
                    )
            except tk.TclError:
                tk.messagebox.showinfo(
                    "Info",
                    "Sélectionnez une question dans la liste puis cliquez sur 'Utiliser'",
                )

        ttk.Button(
            buttons_frame,
            text="✅ Utiliser la sélection",
            command=use_selected_question,
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            buttons_frame,
            text="❌ Fermer",
            command=examples_window.destroy,
        ).pack(side="right")

    def save_global_analysis(self, analysis_content, popup_id=None):
        """Sauvegarde l'analyse globale dans un fichier avec identifiant de popup"""
        try:
            from datetime import datetime

            # Vérifier le contenu
            if not analysis_content or analysis_content.strip() == "":
                messagebox.showwarning("Attention", "Aucune analyse à sauvegarder.")
                return

            # Obtenir le répertoire de sauvegarde spécifique à l'environnement
            if self.current_environment_id:
                solutions_dir = self.db_manager.get_environment_analyses_directory(self.current_environment_id)
            else:
                # Répertoire par défaut si aucun environnement sélectionné
                solutions_dir = self.user_prefs.get_error_solutions_directory()
                if not os.path.exists(solutions_dir):
                    os.makedirs(solutions_dir, exist_ok=True)

            # Créer le nom de fichier avec timestamp et ID popup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if popup_id:
                filename = f"analyse_log_complete_{popup_id}_{timestamp}.txt"
            else:
                filename = f"analyse_log_complete_{timestamp}.txt"
            filepath = os.path.join(solutions_dir, filename)

            # Préparer le contenu avec en-tête
            header = f"""╔══════════════════════════════════════════════════════════╗
║                    ANALYSE LOG COMFYUI                   ║
╠══════════════════════════════════════════════════════════╣
║ 📋 Identifiant popup: {popup_id if popup_id else 'N/A':<30} ║
║ 📅 Date génération:   {datetime.now().strftime('%d/%m/%Y %H:%M:%S'):<30} ║
║ 🤖 Générée par:       Mistral AI                         ║
╚══════════════════════════════════════════════════════════╝

"""

            # Sauvegarder avec en-tête
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header)
                f.write(analysis_content)

            # Message de confirmation avec ID
            if popup_id:
                messagebox.showinfo(
                    "Sauvegarde réussie",
                    f"Analyse [{popup_id}] sauvegardée :\n{filepath}"
                )
            else:
                messagebox.showinfo(
                    "Sauvegarde réussie", f"Analyse sauvegardée :\n{filepath}"
                )

            print(f"💾 Analyse sauvegardée: {popup_id} -> {filename}")

            # Indexer l'analyse dans le RAG si disponible
            if self.rag_manager and self.rag_manager.is_available():
                # VALIDATION CRITIQUE: Vérifier l'environnement avant indexation
                if not self.current_environment_id:
                    print("❌ ERREUR CRITIQUE: Impossible d'indexer sans environment_id identifié")
                    messagebox.showwarning(
                        "Environnement requis",
                        "L'indexation RAG nécessite un environnement ComfyUI identifié.\n"
                        "Veuillez identifier l'environnement avant d'analyser les logs."
                    )
                    return

                try:
                    # Préparer les données d'analyse pour l'indexation
                    analysis_data = {
                        "timestamp": datetime.now().isoformat(),
                        "type": "log_analysis",
                        "popup_id": popup_id,
                        "filename": filename,
                        "full_analysis": analysis_content,
                        "environment_id": self.current_environment_id,  # OBLIGATOIRE
                        "filepath": filepath
                    }

                    # Vérifier la cohérence de l'environment_id
                    if self.rag_manager.environment_id != self.current_environment_id:
                        print(f"🔄 Synchronisation RAG: {self.rag_manager.environment_id} -> {self.current_environment_id}")
                        self.rag_manager.environment_id = self.current_environment_id
                        self.rag_manager._initialize_components()

                    # Indexer dans la base vectorielle
                    success = self.rag_manager.index_analysis_result(analysis_data)
                    if success:
                        print(f"🧠 Analyse indexée dans le RAG pour {self.current_environment_id}: {popup_id}")
                    else:
                        print(f"⚠️ Erreur indexation RAG: {popup_id}")

                except Exception as rag_error:
                    print(f"❌ Erreur indexation RAG: {rag_error}")

        except Exception as e:
            messagebox.showerror(
                "Erreur de sauvegarde",
                f"Impossible de sauvegarder l'analyse :\n{str(e)}",
            )

    # ===== MÉTHODES DE VALIDATION RAG =====

    def validate_rag_environment(self, operation_name: str = "opération RAG") -> bool:
        """
        Valider que le RAG peut fonctionner avec un environnement identifié

        Args:
            operation_name: Nom de l'opération pour le message d'erreur

        Returns:
            bool: True si tout est valide, False sinon
        """
        # Vérifier la disponibilité du RAG
        if not self.rag_manager or not self.rag_manager.is_available():
            print(f"❌ {operation_name}: RAG non disponible")
            return False

        # Vérifier qu'un environnement est identifié
        if not self.current_environment_id:
            print(f"❌ {operation_name}: Aucun environnement ComfyUI identifié")
            messagebox.showwarning(
                "Environnement requis",
                f"L'{operation_name} nécessite un environnement ComfyUI identifié.\n\n"
                "🔍 Allez dans l'onglet ComfyUI et cliquez sur 'Identifier l'environnement'."
            )
            return False

        # Vérifier la cohérence des environment_id
        if self.rag_manager.environment_id != self.current_environment_id:
            print(f"🔄 Synchronisation RAG pour {operation_name}: {self.rag_manager.environment_id} -> {self.current_environment_id}")
            self.rag_manager.environment_id = self.current_environment_id
            self.rag_manager._initialize_components()
            # Mettre à jour aussi le RAG temporel
            if self.temporal_rag:
                self.temporal_rag.rag_manager = self.rag_manager

        print(f"✅ {operation_name}: Validation RAG réussie pour environnement {self.current_environment_id}")
        return True

    def audit_rag_environment_consistency(self):
        """Auditer la cohérence des environment_id dans le RAG"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                print("❌ Audit impossible: RAG non disponible")
                return

            print("\n" + "="*60)
            print("🔍 AUDIT DE COHÉRENCE ENVIRONMENT_ID RAG")
            print("="*60)

            # 1. Vérifier l'état actuel
            print(f"🎯 Environment_ID actuel: {self.current_environment_id}")
            print(f"🎯 Environment_ID RAG: {self.rag_manager.environment_id}")

            # 2. Vérifier ChromaDB si disponible
            if self.rag_manager.collection:
                try:
                    results = self.rag_manager.collection.get(include=["metadatas"])
                    env_ids = set()
                    total_docs = 0

                    for metadata in results.get('metadatas', []):
                        env_id = metadata.get('environment_id', 'MANQUANT')
                        env_ids.add(env_id)
                        total_docs += 1

                    print(f"📚 ChromaDB - Documents totaux: {total_docs}")
                    print(f"📚 ChromaDB - Environment_IDs trouvés: {env_ids}")

                    # Compter par environnement
                    env_counts = {}
                    for metadata in results.get('metadatas', []):
                        env_id = metadata.get('environment_id', 'MANQUANT')
                        env_counts[env_id] = env_counts.get(env_id, 0) + 1

                    for env_id, count in env_counts.items():
                        status = "✅" if env_id == self.current_environment_id else "⚠️"
                        print(f"   {status} {env_id}: {count} documents")

                except Exception as e:
                    print(f"❌ Erreur audit ChromaDB: {e}")

            # 3. Vérifier SQLite constraints
            try:
                constraints = self.rag_manager.get_constraints()
                constraint_envs = set(c.get('environment_id') for c in constraints if c.get('environment_id'))

                print(f"🗃️ SQLite - Contraintes trouvées: {len(constraints)}")
                print(f"🗃️ SQLite - Environment_IDs: {constraint_envs}")

                for env_id in constraint_envs:
                    status = "✅" if env_id == self.current_environment_id else "⚠️"
                    env_constraints = [c for c in constraints if c.get('environment_id') == env_id]
                    print(f"   {status} {env_id}: {len(env_constraints)} contraintes")

            except Exception as e:
                print(f"❌ Erreur audit SQLite: {e}")

            # 4. Recommandations
            print("\n🎯 RECOMMANDATIONS:")
            if not self.current_environment_id:
                print("❌ CRITIQUE: Identifiez d'abord un environnement ComfyUI")
            elif self.rag_manager.environment_id != self.current_environment_id:
                print(f"⚠️ Incohérence détectée - Synchronisation recommandée")
            else:
                print("✅ Cohérence validée")

            print("="*60 + "\n")

        except Exception as e:
            print(f"❌ Erreur lors de l'audit: {e}")

    def ensure_analysis_has_environment_id(self, analysis_data: dict) -> dict:
        """
        S'assurer qu'une donnée d'analyse contient l'environment_id correct

        Args:
            analysis_data: Données d'analyse à valider

        Returns:
            dict: Données d'analyse avec environment_id garanti
        """
        # Forcer l'environment_id actuel
        analysis_data["environment_id"] = self.current_environment_id

        # Ajouter des métadonnées de validation
        analysis_data["validation"] = {
            "validated_at": datetime.now().isoformat(),
            "validated_environment": self.current_environment_id,
            "validation_source": "cy8_prompts_manager"
        }

        return analysis_data

    # ===== MÉTHODES DE GESTION DU CHAT RAG =====

    def initialize_chat_welcome(self):
        """Initialiser la conversation avec le message de bienvenue du RAG Hybride"""
        try:
            # Vérifier si le RAG est disponible
            if not self.rag_manager or not self.rag_manager.is_available():
                self.add_chat_message(
                    "system",
                    "⚠️ Le système RAG n'est pas disponible. Veuillez installer les dépendances :\n"
                    "pip install chromadb sentence-transformers"
                )
                self.chat_status_label.config(text="❌ RAG non disponible")
                return

            # VALIDATION CRITIQUE: Vérifier qu'un environnement est identifié
            print(f"🔍 DEBUG: Vérification environnement - current_environment_id = '{self.current_environment_id}'")
            print(f"🔍 DEBUG: Type = {type(self.current_environment_id)}")
            print(f"🔍 DEBUG: Booléen = {bool(self.current_environment_id)}")

            if not self.current_environment_id:
                print("❌ DEBUG: Condition 'not self.current_environment_id' = True")
                self.add_chat_message(
                    "system",
                    "❌ ERREUR CRITIQUE: Aucun environnement ComfyUI identifié !\n\n"
                    "Le système RAG nécessite un environnement identifié pour fonctionner.\n"
                    "🔍 Allez dans l'onglet ComfyUI et cliquez sur 'Identifier l'environnement'."
                )
                self.chat_status_label.config(text="❌ Environnement requis")
                return
            else:
                print(f"✅ DEBUG: Environnement OK = '{self.current_environment_id}'")

            # Mettre à jour le gestionnaire RAG avec l'environnement actuel
            if self.rag_manager.environment_id != self.current_environment_id:
                print(f"🔄 Mise à jour RAG: {self.rag_manager.environment_id} -> {self.current_environment_id}")
                self.rag_manager.environment_id = self.current_environment_id
                self.rag_manager._initialize_components()
                # Mettre à jour aussi le RAG temporel
                if self.temporal_rag:
                    self.temporal_rag.rag_manager = self.rag_manager

            # Générer le message de bienvenue avec les nouveaux modes
            current_mode = self.get_current_rag_mode()
            mode_names = {"rapide": "⚡ RAG Rapide", "expert": "🧠 RAG Expert"}

            welcome_message = f"""🧠 **Assistant RAG Hybride ComfyUI activé !**

Je suis votre assistant intelligent avec **deux modes** d'analyse :

🔄 **Modes disponibles :**
• **⚡ RAG Rapide** : Recherche vectorielle + Templates (< 1s, gratuit)
• **🧠 RAG Expert** : Recherche vectorielle + Mistral AI (2-5s, tokens)

📊 **Mode actuel :** {mode_names.get(current_mode, current_mode)}

💡 **Je peux vous aider avec :**
- Diagnostics d'erreurs ComfyUI (CUDA, custom nodes, modèles)
- Analyses de performance et optimisations
- Solutions basées sur votre historique
- Conseils préventifs personnalisés

🎯 **Conseils d'utilisation :**
- Mode **Rapide** pour les problèmes courants et diagnostics express
- Mode **Expert** pour les analyses complexes et solutions sur mesure

N'hésitez pas à me poser vos questions ! Cliquez sur ℹ️ pour plus d'infos sur les modes."""

            self.add_chat_message("assistant", welcome_message)
            self.chat_status_label.config(text=f"✅ RAG Hybride actif - Env: {self.current_environment_id or 'Aucun'}")

            # Mettre à jour les indicateurs RAG
            self.update_chat_rag_indicators()

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur initialisation chat: {e}")
            self.chat_status_label.config(text="❌ Erreur RAG")

    def add_chat_message(self, sender_type: str, message: str):
        """Ajouter un message à l'historique du chat"""
        print(f"🔧 DEBUG: add_chat_message appelé - type={sender_type}, message={message[:50]}...")
        try:
            # Vérifier que l'interface chat existe
            if not hasattr(self, 'chat_history') or not self.chat_history:
                print("❌ DEBUG: chat_history n'existe pas")
                return

            # Activer l'édition temporairement
            self.chat_history.config(state=tk.NORMAL)
            print("✅ DEBUG: Chat activé pour édition")

            # Ajouter le timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.chat_history.insert(tk.END, f"[{timestamp}] ", "timestamp")

            # Ajouter le message selon le type
            if sender_type == "user":
                self.chat_history.insert(tk.END, "Vous: ", "user")
                self.chat_history.insert(tk.END, f"{message}\n\n")
            elif sender_type == "assistant":
                self.chat_history.insert(tk.END, "🧠 Assistant: ", "assistant")
                self.chat_history.insert(tk.END, f"{message}\n\n")
            elif sender_type == "system":
                self.chat_history.insert(tk.END, "🔧 Système: ", "system")
                self.chat_history.insert(tk.END, f"{message}\n\n", "system")
            elif sender_type == "error":
                self.chat_history.insert(tk.END, "❌ Erreur: ", "error")
                self.chat_history.insert(tk.END, f"{message}\n\n", "error")

            # Désactiver l'édition
            self.chat_history.config(state=tk.DISABLED)

            # Faire défiler vers le bas
            self.chat_history.see(tk.END)
            print("✅ DEBUG: Message ajouté au chat avec succès")

        except Exception as e:
            print(f"❌ Erreur ajout message chat: {e}")
            import traceback
            traceback.print_exc()

    def send_chat_message(self):
        """Envoyer un message dans le chat"""
        try:
            # Récupérer le texte de l'utilisateur
            user_message = self.chat_input.get("1.0", tk.END).strip()
            if not user_message:
                return

            # Ajouter le message de l'utilisateur
            self.add_chat_message("user", user_message)

            # Effacer la zone de saisie
            self.clear_chat_input()

            # Traiter le message avec le RAG
            self.process_chat_message(user_message)

        except Exception as e:
            self.add_chat_message("error", f"Erreur envoi message: {e}")

    def process_chat_message(self, user_message: str):
        """Traiter un message utilisateur avec le RAG"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                self.add_chat_message("system", "Le système RAG n'est pas disponible.")
                return

            # NOUVEAU: Vérifier les commandes TODO en priorité
            if self.rag_manager.is_todo_command(user_message):
                result = self.rag_manager.process_todo_command(user_message, self.get_chat_history())

                if result["success"]:
                    # Traitement spécial selon le type de commande
                    if result.get("clear_history"):
                        # Mode focus : effacer l'historique
                        self.clear_chat_history()
                        self.add_chat_message("system", "🎯 Mode Focus activé - Historique effacé pour vous aider à vous concentrer.")

                    if result.get("restore_history"):
                        # Restaurer l'historique
                        self.restore_chat_history(result["restore_history"])
                        self.add_chat_message("system", "🔄 Historique restauré.")

                    # Afficher la réponse
                    response_type = "system" if result["mode"].startswith("focus") else "assistant"
                    self.add_chat_message(response_type, result["response"])
                else:
                    self.add_chat_message("error", result["response"])

                return

            # Détecter le type de demande
            message_lower = user_message.lower()

            # Commandes de test RAG
            if user_message.startswith("/test-rag"):
                self.handle_rag_test_command(user_message)
                return

            if user_message.startswith("/quick-test"):
                self.handle_quick_test_command()
                return

            # Commandes spéciales
            if "contrainte" in message_lower and ("ajouter" in message_lower or "nouveau" in message_lower):
                self.handle_add_constraint_request(user_message)
                return

            if "état" in message_lower and "serveur" in message_lower:
                self.handle_server_status_request()
                return

            if "erreur" in message_lower and ("récurrent" in message_lower or "fréquent" in message_lower):
                self.handle_recurring_errors_request()
                return

            # Recherche générale avec contexte RAG
            self.handle_general_query(user_message)

        except Exception as e:
            self.add_chat_message("error", f"Erreur traitement message: {e}")

    def handle_add_constraint_request(self, user_message: str):
        """Gérer une demande d'ajout de contrainte"""
        # Ouvrir le dialogue d'ajout de contrainte
        self.add_system_constraint()

    def handle_server_status_request(self):
        """Gérer une demande de statut du serveur"""
        try:
            status = self.rag_manager.get_server_status_summary()

            response = f"""📊 **État actuel du serveur ComfyUI**

🖥️ **Environnement:** {status.get('environment_id', 'Non défini')}
📈 **État:** {status['current_state']['value']}

"""

            if status.get('recurring_errors'):
                response += "⚠️ **Erreurs récurrentes:**\n"
                for error in status['recurring_errors'][:3]:
                    response += f"• {error['message']} (x{error['frequency']})\n"
                    if error.get('solution'):
                        response += f"  💡 Solution: {error['solution']}\n"
                response += "\n"

            if status.get('constraints'):
                response += "🚫 **Contraintes système:**\n"
                for constraint in status['constraints'][:3]:
                    response += f"• {constraint['type']}: {constraint['value']}\n"
                    if constraint.get('description'):
                        response += f"  📝 {constraint['description']}\n"

            self.add_chat_message("assistant", response)

        except Exception as e:
            self.add_chat_message("error", f"Erreur récupération statut: {e}")

    def handle_recurring_errors_request(self):
        """Gérer une demande sur les erreurs récurrentes"""
        try:
            status = self.rag_manager.get_server_status_summary()

            if not status.get('recurring_errors'):
                response = "✅ Aucune erreur récurrente détectée dans l'environnement actuel."
            else:
                response = "⚠️ **Erreurs récurrentes détectées:**\n\n"
                for i, error in enumerate(status['recurring_errors'], 1):
                    response += f"**{i}. {error['type'].upper()}** (x{error['frequency']})\n"
                    response += f"📝 Message: {error['message']}\n"
                    if error.get('solution'):
                        response += f"💡 Solution: {error['solution']}\n"
                    response += "\n"

            self.add_chat_message("assistant", response)

        except Exception as e:
            self.add_chat_message("error", f"Erreur récupération erreurs: {e}")

    def handle_general_query(self, user_message: str):
        """Gérer une requête générale avec le système RAG hybride"""
        try:
            # Vérifier si le RAG est disponible
            if not hasattr(self, 'rag_manager') or not self.rag_manager:
                self.add_chat_message("error",
                    "❌ **RAG non disponible**\n\n"
                    "Le système RAG n'est pas initialisé. Veuillez d'abord identifier un environnement ComfyUI.")
                return

            # Récupérer le mode sélectionné
            mode = getattr(self, 'rag_mode_var', tk.StringVar(value="rapide")).get()

            # Ajouter un message de traitement selon le mode
            if mode == "expert":
                self.add_chat_message("system", "🧠 Mode Expert activé - Analyse avec Mistral AI...")
            else:
                self.add_chat_message("system", "⚡ Mode Rapide activé - Recherche vectorielle...")

            # Appeler le RAG avec le mode sélectionné
            response = self.rag_manager.query_with_mode(user_message, mode=mode, max_results=5)

            if response["success"]:
                # Ajouter la réponse principale
                self.add_chat_message("assistant", response["response"])

                # Ajouter les métadonnées de performance
                metadata = response.get("metadata", {})
                response_time = metadata.get("response_time", 0)

                meta_info = f"⏱️ Temps de réponse: {response_time}s | Mode: {mode.title()}"

                if mode == "expert" and "mistral_tokens" in response:
                    meta_info += f" | Tokens: ~{response['mistral_tokens']}"

                if "documents_found" in response:
                    meta_info += f" | {response['documents_found']} analyses consultées"

                self.add_chat_message("system", meta_info)

                # Afficher les sources si disponibles
                if response.get("sources"):
                    sources_text = "📚 Sources consultées: " + ", ".join(response["sources"][:3])
                    if len(response["sources"]) > 3:
                        sources_text += f" (+{len(response['sources']) - 3} autres)"
                    self.add_chat_message("system", sources_text)

            else:
                self.add_chat_message("error",
                    f"❌ Erreur lors de la requête RAG:\n{response.get('response', 'Erreur inconnue')}")

        except Exception as e:
            self.add_chat_message("error", f"Erreur traitement requête: {e}")
            print(f"Erreur handle_general_query: {e}")  # Pour debug

    # === NOUVELLES MÉTHODES RAG HYBRIDE ===

    def on_rag_mode_changed(self):
        """Callback when RAG mode is changed"""
        try:
            mode = self.rag_mode_var.get()

            # Mettre à jour l'indicateur de performance/coût
            if mode == "rapide":
                self.mode_info_label.config(text="< 1s - Gratuit", foreground="green")
            elif mode == "expert":
                self.mode_info_label.config(text="2-5s - Tokens Mistral", foreground="orange")

            # Ajouter un message dans le chat pour informer du changement
            mode_names = {"rapide": "⚡ RAG Rapide", "expert": "🧠 RAG Expert"}
            self.add_chat_message("system", f"Mode changé vers: {mode_names.get(mode, mode)}")

        except Exception as e:
            print(f"Erreur changement mode RAG: {e}")

    def show_rag_modes_info(self):
        """Afficher les informations détaillées sur les modes RAG"""
        try:
            if hasattr(self, 'rag_manager') and self.rag_manager:
                mode_info = self.rag_manager.get_mode_info()
            else:
                # Informations par défaut si RAG pas disponible
                mode_info = {
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

            # Créer la popup d'information
            popup = tk.Toplevel(self.root)
            popup.title("ℹ️ Modes RAG - Guide d'utilisation")
            popup.transient(self.root)
            popup.grab_set()

            # Centrer la popup
            popup.geometry("600x450")
            popup.resizable(True, True)

            main_frame = ttk.Frame(popup, padding="15")
            main_frame.pack(fill="both", expand=True)

            # Titre
            title_label = ttk.Label(
                main_frame,
                text="🔄 Modes RAG Hybride - Guide d'utilisation",
                font=("TkDefaultFont", 14, "bold")
            )
            title_label.pack(pady=(0, 15))

            # Créer un notebook pour les deux modes
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill="both", expand=True, pady=(0, 15))

            # Onglet Mode Rapide
            rapid_frame = ttk.Frame(notebook, padding="10")
            notebook.add(rapid_frame, text="⚡ Mode Rapide")

            self._create_mode_info_tab(rapid_frame, mode_info["rapide"])

            # Onglet Mode Expert
            expert_frame = ttk.Frame(notebook, padding="10")
            notebook.add(expert_frame, text="🧠 Mode Expert")

            self._create_mode_info_tab(expert_frame, mode_info["expert"])

            # Bouton fermer
            ttk.Button(main_frame, text="Fermer", command=popup.destroy).pack()

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher les informations: {e}")

    def _create_mode_info_tab(self, parent, mode_data):
        """Créer le contenu d'un onglet d'information de mode"""

        # Nom du mode
        name_label = ttk.Label(parent, text=mode_data["name"], font=("TkDefaultFont", 12, "bold"))
        name_label.pack(pady=(0, 10))

        # Description
        desc_frame = ttk.LabelFrame(parent, text="Description", padding="10")
        desc_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(desc_frame, text=mode_data["description"], wraplength=500).pack()

        # Caractéristiques
        char_frame = ttk.LabelFrame(parent, text="Caractéristiques", padding="10")
        char_frame.pack(fill="x", pady=(0, 10))

        char_text = f"⏱️ Vitesse: {mode_data['speed']}\n"
        char_text += f"💰 Coût: {mode_data['cost']}\n"
        char_text += f"🎯 Précision: {mode_data['accuracy']}"

        ttk.Label(char_frame, text=char_text, justify="left").pack(anchor="w")

        # Idéal pour
        best_frame = ttk.LabelFrame(parent, text="Idéal pour", padding="10")
        best_frame.pack(fill="x")

        for item in mode_data["best_for"]:
            ttk.Label(best_frame, text=f"• {item}").pack(anchor="w")

    def get_current_rag_mode(self) -> str:
        """Retourner le mode RAG actuellement sélectionné"""
        return getattr(self, 'rag_mode_var', tk.StringVar(value="rapide")).get()

    def set_rag_mode(self, mode: str):
        """Définir le mode RAG"""
        if hasattr(self, 'rag_mode_var'):
            self.rag_mode_var.set(mode)
            self.on_rag_mode_changed()

    def generate_expert_server_report(self, user_message: str):
        """Générer un rapport d'expert sur l'état du serveur ComfyUI"""
        try:
            if not self.current_environment_id:
                self.add_chat_message("assistant",
                    "⚠️ **Environnement non identifié**\n\n"
                    "Pour générer un rapport exhaustif, je dois d'abord identifier l'environnement ComfyUI.\n"
                    "📋 Allez dans l'onglet ComfyUI et cliquez sur '🔍 Identifier l'environnement'.")
                return

            # Récupérer les données d'environnement
            server_status = self.get_current_server_status()
            recent_analyses = self.get_recent_log_analyses(self.current_environment_id, limit=20)
            rag_stats = self.get_rag_statistics()

            # Générer le rapport d'expert
            report = self.create_expert_server_report(server_status, recent_analyses, rag_stats)

            self.add_chat_message("assistant", report)

        except Exception as e:
            self.add_chat_message("error", f"Erreur génération rapport serveur: {e}")

    def create_expert_server_report(self, server_status, recent_analyses, rag_stats):
        """Créer un rapport d'expert détaillé sur le serveur"""

        lines = []
        lines.append("🔍 **RAPPORT EXPERT - ÉTAT SERVEUR COMFYUI**")
        lines.append("=" * 60)
        lines.append("")

        # Informations d'environnement
        lines.append(f"🆔 **Environnement identifié:** `{self.current_environment_id}`")
        lines.append(f"⏰ **Rapport généré le:** {time.strftime('%d/%m/%Y à %H:%M:%S')}")
        lines.append("")

        # État du serveur
        lines.append("🖥️ **ÉTAT DU SERVEUR**")
        if server_status and server_status.get('status') == 'online':
            lines.append("✅ **Statut:** Serveur en ligne et accessible")
            if 'system_stats' in server_status:
                stats = server_status['system_stats']
                lines.append(f"🧠 **RAM:** {stats.get('ram', 'Non détecté')}")
                lines.append(f"🎮 **VRAM:** {stats.get('vram', 'Non détecté')}")
        else:
            lines.append("❌ **Statut:** Serveur inaccessible ou hors ligne")
        lines.append("")

        # Analyse des logs récents
        lines.append("📊 **ANALYSE DES LOGS RÉCENTS**")
        if recent_analyses:
            # Catégoriser les analyses
            errors = [a for a in recent_analyses if 'error' in a.get('log_type', '').lower() or 'failed' in a.get('message', '').lower()]
            warnings = [a for a in recent_analyses if 'warning' in a.get('log_type', '').lower()]
            custom_nodes_issues = [a for a in recent_analyses if 'custom' in a.get('message', '').lower() and 'node' in a.get('message', '').lower()]

            lines.append(f"📈 **Total d'événements analysés:** {len(recent_analyses)}")
            lines.append(f"❌ **Erreurs critiques:** {len(errors)}")
            lines.append(f"⚠️ **Avertissements:** {len(warnings)}")
            lines.append(f"🔌 **Problèmes custom nodes:** {len(custom_nodes_issues)}")
            lines.append("")

            # Top 3 des erreurs les plus récentes
            if errors:
                lines.append("🚨 **TOP 3 ERREURS RÉCENTES:**")
                for i, error in enumerate(errors[:3], 1):
                    lines.append(f"**{i}.** {error.get('message', 'Message non disponible')}")
                    lines.append(f"   📅 {error.get('timestamp', 'Date inconnue')}")
                lines.append("")

            # Problèmes de custom nodes
            if custom_nodes_issues:
                lines.append("🔌 **PROBLÈMES CUSTOM NODES:**")
                for issue in custom_nodes_issues[:3]:
                    lines.append(f"• {issue.get('message', 'Message non disponible')}")
                lines.append("")

        else:
            lines.append("ℹ️ Aucune analyse de log disponible pour cet environnement.")
            lines.append("")

        # État du système RAG
        lines.append("🧠 **ÉTAT DU SYSTÈME RAG**")
        lines.append(f"📚 **Documents indexés:** {rag_stats.get('total_docs', 0)}")
        lines.append(f"🔄 **Dernière indexation:** {rag_stats.get('last_indexed', 'Jamais')}")
        lines.append("")

        # Recommandations d'expert
        lines.append("💡 **RECOMMANDATIONS D'EXPERT**")

        if recent_analyses:
            error_count = len([a for a in recent_analyses if 'error' in a.get('log_type', '').lower()])
            if error_count > 5:
                lines.append("🔧 **Action recommandée:** Redémarrage du serveur ComfyUI")
                lines.append("   Raison: Nombre élevé d'erreurs détectées")
            elif error_count > 0:
                lines.append("🔍 **Action recommandée:** Vérification des custom nodes")
                lines.append("   Raison: Erreurs sporadiques détectées")
            else:
                lines.append("✅ **Système stable:** Aucune action immédiate requise")
        else:
            lines.append("📋 **Action recommandée:** Analyser les logs ComfyUI")
            lines.append("   Raison: Aucune donnée d'analyse disponible")

        lines.append("")
        lines.append("🎯 **Pour plus de détails, consultez l'onglet Log ou Environnement**")

        return "\n".join(lines)

    def get_current_server_status(self):
        """Récupérer l'état actuel du serveur (simulé)"""
        try:
            # Test rapide de connectivité ComfyUI
            import requests
            server_info = os.getenv("COMFYUI_SERVER", "127.0.0.1:8188")
            response = requests.get(f"http://{server_info}/system_stats", timeout=2)

            if response.status_code == 200:
                return {
                    'status': 'online',
                    'system_stats': response.json()
                }
            else:
                return {'status': 'error', 'code': response.status_code}

        except Exception as e:
            return {'status': 'offline', 'error': str(e)}

    def generate_expert_system_info(self, user_message: str):
        """Générer une réponse d'expert pour les informations système"""
        try:
            if not self.current_environment_id:
                self.add_chat_message("assistant",
                    "⚠️ **Environnement non identifié**\n\n"
                    "Pour accéder aux informations système, je dois d'abord identifier l'environnement ComfyUI.\n"
                    "📋 Allez dans l'onglet ComfyUI et cliquez sur '🔍 Identifier l'environnement'.")
                return

            # Rechercher les informations système dans les analyses
            recent_analyses = self.get_recent_log_analyses(self.current_environment_id, limit=50)

            # Extraire les informations système spécifiques
            pytorch_info = None
            cuda_info = None
            vram_info = None
            ram_info = None
            python_info = None

            for analysis in recent_analyses:
                message = analysis.get('message', '').lower()

                # PyTorch version
                if 'pytorch version' in message:
                    import re
                    pytorch_match = re.search(r'pytorch version:\s*([^\s]+)', message)
                    if pytorch_match:
                        pytorch_info = pytorch_match.group(1)

                        # Extraire CUDA depuis PyTorch (ex: 2.1.2+cu118)
                        cuda_match = re.search(r'\+cu(\d+)', pytorch_info)
                        if cuda_match:
                            cuda_version = cuda_match.group(1)
                            cuda_info = f"CUDA {cuda_version[:2]}.{cuda_version[2:]}"  # cu118 -> CUDA 11.8

                # VRAM/RAM
                if 'vram' in message and 'ram' in message:
                    import re
                    vram_match = re.search(r'vram\s+(\d+)\s*mb', message)
                    ram_match = re.search(r'total\s+ram\s+(\d+)\s*mb', message)
                    if vram_match:
                        vram_info = f"{vram_match.group(1)} MB"
                    if ram_match:
                        ram_info = f"{ram_match.group(1)} MB"

                # Python info depuis les paths
                if 'python' in message and 'embeded' in message:
                    python_info = "Python Embedded (ComfyUI)"

            # Générer la réponse d'expert
            response = []
            response.append("🔍 **INFORMATIONS SYSTÈME - ENVIRONNEMENT COMFYUI**")
            response.append("=" * 55)
            response.append("")
            response.append(f"🆔 **Environnement:** `{self.current_environment_id}`")
            response.append("")

            # Section PyTorch/CUDA
            response.append("🧠 **FRAMEWORKS & ACCÉLÉRATION:**")
            if pytorch_info:
                response.append(f"• **PyTorch:** {pytorch_info}")
                if cuda_info:
                    response.append(f"• **CUDA:** {cuda_info} (intégrée à PyTorch)")
                else:
                    response.append("• **CUDA:** Version intégrée (détails dans PyTorch)")
            else:
                response.append("• **PyTorch:** ⚠️ Version non détectée dans les logs")
                response.append("• **CUDA:** ⚠️ Information non disponible")

            response.append("")

            # Section Mémoire
            response.append("💾 **RESSOURCES MÉMOIRE:**")
            if vram_info:
                response.append(f"• **VRAM GPU:** {vram_info}")
            else:
                response.append("• **VRAM GPU:** ⚠️ Non détectée")

            if ram_info:
                response.append(f"• **RAM Système:** {ram_info}")
            else:
                response.append("• **RAM Système:** ⚠️ Non détectée")

            response.append("")

            # Section Python
            response.append("🐍 **ENVIRONNEMENT PYTHON:**")
            if python_info:
                response.append(f"• **Type:** {python_info}")
            else:
                response.append("• **Type:** Python (détection automatique)")

            if hasattr(self, 'current_python_path') and self.current_python_path:
                response.append(f"• **Chemin:** `{self.current_python_path}`")

            response.append("")

            # Conseils d'expert
            response.append("💡 **CONSEILS D'EXPERT:**")

            if pytorch_info and '2.1' in pytorch_info:
                response.append("⚠️ **PyTorch ancien détecté**")
                response.append("   • Version recommandée: PyTorch 2.4+")
                response.append("   • Risque: Chargement non sécurisé des modèles")
                response.append("   • Action: Mise à jour recommandée")
                response.append("")

            if vram_info and 'MB' in vram_info:
                vram_value = int(vram_info.split()[0])
                if vram_value < 6000:  # Moins de 6GB
                    response.append("⚠️ **VRAM limitée détectée**")
                    response.append("   • Utiliser des modèles optimisés")
                    response.append("   • Réduire la taille des batches")
                    response.append("   • Considérer l'offloading CPU")
                elif vram_value >= 12000:  # 12GB+
                    response.append("✅ **VRAM excellente**")
                    response.append("   • Capable de gérer les gros modèles")
                    response.append("   • Workflows complexes supportés")

            response.append("")
            response.append("🔍 **Note:** Informations extraites des logs ComfyUI récents")
            response.append("📋 **Pour plus de détails:** Consultez l'onglet Log")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"Erreur extraction informations système: {e}")

    def generate_expert_error_analysis(self, user_message: str):
        """Générer une analyse d'expert pour les erreurs"""
        try:
            # Rechercher des erreurs similaires dans les analyses
            relevant_errors = []
            custom_nodes_info = {}

            if self.current_environment_id:
                recent_analyses = self.get_recent_log_analyses(self.current_environment_id, limit=50)
                # Filtrer pour ne garder que les erreurs - utiliser les vrais types de la DB
                relevant_errors = [a for a in recent_analyses if
                                   a.get('log_type', '').upper() in ['ERREUR', 'ERROR'] or
                                   a.get('level', '').upper() in ['ERROR', 'WARNING', 'ATTENTION'] or
                                   'error' in a.get('message', '').lower() or
                                   'failed' in a.get('message', '').lower() or
                                   'exception' in a.get('message', '').lower()]

                # Extraire les noms de custom nodes des messages d'erreur
                for error in relevant_errors:
                    message = error.get('message', '')
                    # Chercher les patterns de noms de custom nodes - patterns améliorés
                    import re
                    patterns = [
                        r'custom_nodes[/\\]([^/\\\\s]+)',                    # custom_nodes/nom
                        r'ComfyUI[/\\]custom_nodes[/\\]([^/\\\\s]+)',       # ComfyUI/custom_nodes/nom
                        r'([a-zA-Z_][a-zA-Z0-9_-]*[-_]node[-_]?[a-zA-Z0-9_-]*)', # xxx-node-xxx
                        r'([a-zA-Z_][a-zA-Z0-9_-]*[-_]suite[-_]?[a-zA-Z0-9_-]*)', # xxx-suite-xxx
                        r'from\s+([a-zA-Z_][a-zA-Z0-9_-]+)\s+import',       # from module import
                        r'module\s+[\'"]([^\'"]+)[\'"]',                      # module "nom"
                        r'([a-zA-Z_][a-zA-Z0-9_-]*comfy[a-zA-Z0-9_-]*)',    # xxxcomfyxxx
                        r'`([^`]+)`\s*(?:custom|node|suite)',               # `nom` custom/node/suite
                        r'([a-zA-Z_][a-zA-Z0-9_-]{2,})\s*(?:load|install|fail|error)', # nom load/fail/error
                    ]

                    for pattern in patterns:
                        matches = re.finditer(pattern, message, re.IGNORECASE)
                        for match in matches:
                            node_name = match.group(1)
                            # Filtrer les faux positifs et garder seulement les noms valides
                            false_positives = [
                                'line', 'file', 'module', 'import', 'error', 'warning', 'python',
                                'load', 'failed', 'custom', 'node', 'suite', 'config', 'json',
                                'path', 'bin', 'was', 'comfyui', 'main', 'py', 'lib', 'site',
                                'packages', 'torch', 'numpy', 'api'
                            ]
                            if (len(node_name) >= 3 and
                                node_name.lower() not in false_positives and
                                not node_name.isdigit()):
                                custom_nodes_info[node_name] = custom_nodes_info.get(node_name, 0) + 1

            response = []
            response.append("🔍 **ANALYSE D'EXPERT - GESTION D'ERREURS**")
            response.append("=" * 50)
            response.append("")

            if relevant_errors:
                response.append(f"📊 **{len(relevant_errors)} erreurs analysées** dans l'environnement `{self.current_environment_id}`")
                response.append("")

                # Noms de custom nodes détectés
                if custom_nodes_info:
                    response.append("🔌 **CUSTOM NODES PROBLÉMATIQUES IDENTIFIÉS:**")
                    for node_name, count in sorted(custom_nodes_info.items(), key=lambda x: x[1], reverse=True):
                        response.append(f"• **{node_name}** - {count} erreur(s)")
                    response.append("")

                # Analyser les patterns d'erreurs
                error_patterns = {}
                for error in relevant_errors:
                    message = error.get('message', '')
                    # Simplifier le message pour identifier les patterns
                    if 'cuda' in message.lower():
                        error_patterns['CUDA/GPU'] = error_patterns.get('CUDA/GPU', 0) + 1
                    elif 'custom' in message.lower() and 'node' in message.lower():
                        error_patterns['Custom Nodes'] = error_patterns.get('Custom Nodes', 0) + 1
                    elif 'memory' in message.lower():
                        error_patterns['Mémoire'] = error_patterns.get('Mémoire', 0) + 1
                    elif 'model' in message.lower():
                        error_patterns['Modèles'] = error_patterns.get('Modèles', 0) + 1
                    elif 'dependency' in message.lower() or 'import' in message.lower():
                        error_patterns['Dépendances'] = error_patterns.get('Dépendances', 0) + 1
                    else:
                        error_patterns['Autres'] = error_patterns.get('Autres', 0) + 1

                if error_patterns:
                    response.append("📈 **RÉPARTITION DES ERREURS:**")
                    for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
                        response.append(f"• **{pattern}:** {count} occurrence(s)")
                    response.append("")

                # Solutions recommandées
                response.append("💡 **SOLUTIONS RECOMMANDÉES:**")

                if error_patterns.get('CUDA/GPU', 0) > 0:
                    response.append("🎮 **Problèmes GPU/CUDA:**")
                    response.append("   • Vérifier que CUDA est installé correctement")
                    response.append("   • Redémarrer ComfyUI pour réinitialiser la mémoire GPU")
                    response.append("   • Réduire la taille des modèles ou batch size")
                    response.append("")

                if error_patterns.get('Custom Nodes', 0) > 0:
                    response.append("🔌 **Problèmes Custom Nodes:**")
                    if custom_nodes_info:
                        response.append("   • **Nodes identifiés avec problèmes:**")
                        for node_name, count in list(custom_nodes_info.items())[:3]:
                            response.append(f"     - {node_name} ({count} erreur(s))")
                    response.append("   • Mettre à jour ComfyUI Manager")
                    response.append("   • Réinstaller les custom nodes défaillants")
                    response.append("   • Vérifier les dépendances Python avec:")
                    response.append("     `pip install -r requirements.txt`")
                    response.append("")

                if error_patterns.get('Dépendances', 0) > 0:
                    response.append("📦 **Problèmes Dépendances:**")
                    response.append("   • Vérifier l'environnement Python")
                    response.append("   • Réinstaller les packages manquants")
                    response.append("   • Utiliser l'environnement Python embedded de ComfyUI")
                    response.append("")

                if error_patterns.get('Mémoire', 0) > 0:
                    response.append("🧠 **Problèmes Mémoire:**")
                    response.append("   • Fermer les applications non utilisées")
                    response.append("   • Utiliser des modèles plus légers")
                    response.append("   • Redémarrer ComfyUI")
                    response.append("")

            else:
                response.append("✅ **Aucune erreur récente détectée** dans cet environnement.")
                response.append("")
                response.append("💡 **Conseils préventifs:**")
                response.append("• Surveillez régulièrement les logs")
                response.append("• Maintenez ComfyUI à jour")
                response.append("• Sauvegardez vos workflows importants")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"Erreur analyse erreurs: {e}")

    def generate_expert_optimization_advice(self, user_message: str):
        """Générer des conseils d'optimisation d'expert"""
        response = []
        response.append("⚡ **CONSEILS D'OPTIMISATION COMFYUI**")
        response.append("=" * 45)
        response.append("")

        response.append("🎯 **OPTIMISATIONS PERFORMANCE:**")
        response.append("")

        response.append("🖥️ **Système:**")
        response.append("• Fermer les applications inutiles")
        response.append("• Utiliser un SSD pour les modèles")
        response.append("• Augmenter la RAM si possible")
        response.append("")

        response.append("🎮 **GPU/CUDA:**")
        response.append("• Utiliser les derniers drivers NVIDIA")
        response.append("• Activer la compilation optimisée")
        response.append("• Surveiller la température GPU")
        response.append("")

        response.append("🔧 **ComfyUI:**")
        response.append("• Mettre à jour régulièrement")
        response.append("• Désactiver les custom nodes inutilisés")
        response.append("• Utiliser le mode --cpu si problèmes GPU")
        response.append("")

        response.append("📦 **Modèles:**")
        response.append("• Privilégier les modèles optimisés")
        response.append("• Utiliser des versions quantifiées")
        response.append("• Organiser les modèles par dossiers")

        self.add_chat_message("assistant", "\n".join(response))

    def generate_intelligent_response(self, user_message: str):
        """Générer une réponse intelligente pour les requêtes générales"""
        try:
            # Rechercher des problèmes similaires mais avec une meilleure présentation
            if self.rag_manager and self.rag_manager.is_available():
                similar_issues = self.rag_manager.search_similar_issues(user_message, limit=3)

                if similar_issues:
                    response = []
                    response.append(f"🔍 **Recherche pour:** {user_message}")
                    response.append("")
                    response.append("📋 **Analyses pertinentes trouvées:**")
                    response.append("")

                    for i, issue in enumerate(similar_issues, 1):
                        content = issue.get('content', '')
                        # Extraire des informations utiles du contenu
                        if len(content) > 200:
                            content = content[:200] + "..."

                        response.append(f"**{i}.** {content}")

                        metadata = issue.get('metadata', {})
                        if metadata.get('timestamp'):
                            response.append(f"   📅 {metadata['timestamp']}")
                        response.append("")

                    # Ajouter une suggestion d'action
                    response.append("💡 **Suggestion:**")
                    response.append("Consultez les onglets Log ou Environnement pour plus de détails sur votre configuration actuelle.")

                    self.add_chat_message("assistant", "\n".join(response))

                else:
                    self.add_chat_message("assistant",
                        f"🔍 Aucune analyse pertinente trouvée pour '{user_message}'.\n\n"
                        "💡 **Suggestions:**\n"
                        "• Essayez 'rapport serveur' pour un diagnostic complet\n"
                        "• Utilisez 'aide erreurs' pour l'analyse des problèmes\n"
                        "• Tapez 'optimisation' pour des conseils de performance")
            else:
                self.add_chat_message("assistant",
                    "⚠️ **Système RAG non disponible**\n\n"
                    "Je ne peux pas effectuer de recherches intelligentes pour le moment.\n"
                    "Vérifiez que l'environnement est identifié et que le RAG est initialisé.")

        except Exception as e:
            self.add_chat_message("error", f"Erreur génération réponse: {e}")

    def send_quick_message(self, message: str):
        """Envoyer un message rapide prédéfini"""
        self.add_chat_message("user", message)
        self.process_chat_message(message)

    def clear_chat_input(self):
        """Effacer la zone de saisie"""
        self.chat_input.delete("1.0", tk.END)

    def get_chat_history(self) -> List[Dict]:
        """Récupérer l'historique du chat sous forme de liste"""
        try:
            history = []
            content = self.chat_display.get("1.0", tk.END).strip()

            if not content:
                return history

            # Parser le contenu du chat
            lines = content.split('\n')
            current_message = None

            for line in lines:
                if line.startswith('[') and '] ' in line:
                    # Nouvelle entrée de message
                    if current_message:
                        history.append(current_message)

                    # Extraire timestamp et type
                    timestamp_end = line.find('] ')
                    if timestamp_end > 0:
                        timestamp = line[1:timestamp_end]
                        rest = line[timestamp_end + 2:]

                        # Déterminer le type de sender
                        if rest.startswith('🔧 Système:'):
                            sender_type = 'system'
                            message = rest[12:].strip()
                        elif rest.startswith('🧠 Assistant:'):
                            sender_type = 'assistant'
                            message = rest[14:].strip()
                        elif rest.startswith('Vous:'):
                            sender_type = 'user'
                            message = rest[5:].strip()
                        else:
                            sender_type = 'unknown'
                            message = rest

                        current_message = {
                            'timestamp': timestamp,
                            'sender_type': sender_type,
                            'message': message
                        }
                elif current_message:
                    # Continuer le message précédent
                    current_message['message'] += '\n' + line

            # Ajouter le dernier message
            if current_message:
                history.append(current_message)

            return history

        except Exception as e:
            self.logger.error(f"❌ Erreur récupération historique chat: {e}")
            return []

    def clear_chat_history(self):
        """Effacer l'historique du chat"""
        try:
            self.chat_display.config(state="normal")
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state="disabled")
        except Exception as e:
            self.logger.error(f"❌ Erreur effacement historique: {e}")

    def restore_chat_history(self, history: List[Dict]):
        """Restaurer l'historique du chat depuis une liste"""
        try:
            # Effacer d'abord
            self.clear_chat_history()

            # Restaurer les messages
            for entry in history:
                timestamp = entry.get('timestamp', time.strftime("%H:%M:%S"))
                sender_type = entry.get('sender_type', 'unknown')
                message = entry.get('message', '')

                self.add_chat_message(sender_type, message)

        except Exception as e:
            self.logger.error(f"❌ Erreur restauration historique: {e}")

    def on_enter_pressed(self, event):
        """Gérer la touche Entrée dans le chat"""
        if event.state & 0x4:  # Ctrl+Enter
            return None  # Laisser passer pour nouvelle ligne
        else:
            self.send_chat_message()
            return "break"  # Empêcher le saut de ligne

    def refresh_chat_context(self):
        """Rafraîchir le contexte du chat"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                self.add_chat_message("system", "RAG non disponible pour actualiser le contexte.")
                return

            # Mettre à jour l'environnement
            if self.current_environment_id:
                self.rag_manager.environment_id = self.current_environment_id
                self.rag_manager._initialize_components()

            # Générer un nouveau contexte
            context = self.rag_manager.generate_chat_context()
            self.add_chat_message("system", f"🔄 **Contexte actualisé:**\n\n{context}")

            # Mettre à jour le statut
            self.chat_status_label.config(text=f"✅ RAG actif - Env: {self.current_environment_id or 'Aucun'}")

        except Exception as e:
            self.add_chat_message("error", f"Erreur actualisation contexte: {e}")

    def add_system_constraint(self):
        """Ajouter une contrainte système via dialogue"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                messagebox.showwarning("RAG non disponible", "Le système RAG n'est pas disponible.")
                return

            # Dialogue pour saisir la contrainte
            dialog = tk.Toplevel(self.root)
            dialog.title("Ajouter une contrainte système")
            dialog.geometry("500x300")
            dialog.transient(self.root)
            dialog.grab_set()

            # Variables
            constraint_type = tk.StringVar(value="package_version")
            constraint_value = tk.StringVar()
            constraint_description = tk.StringVar()

            # Interface
            ttk.Label(dialog, text="Type de contrainte:").pack(pady=5)
            type_combo = ttk.Combobox(dialog, textvariable=constraint_type, values=[
                "package_version", "hardware_limitation", "memory_limit",
                "gpu_compatibility", "python_version", "custom_node_conflict"
            ])
            type_combo.pack(pady=5, padx=20, fill="x")

            ttk.Label(dialog, text="Valeur de la contrainte:").pack(pady=(10,5))
            ttk.Entry(dialog, textvariable=constraint_value).pack(pady=5, padx=20, fill="x")

            ttk.Label(dialog, text="Description (optionnel):").pack(pady=(10,5))
            description_text = tk.Text(dialog, height=4)
            description_text.pack(pady=5, padx=20, fill="both", expand=True)

            # Boutons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=10)

            def save_constraint():
                if not constraint_value.get():
                    messagebox.showwarning("Champ requis", "Veuillez saisir une valeur.")
                    return

                description = description_text.get("1.0", tk.END).strip()
                self.rag_manager.add_constraint(
                    constraint_type.get(),
                    constraint_value.get(),
                    description
                )

                # Ajouter un message de confirmation dans le chat
                self.add_chat_message("system",
                    f"✅ Contrainte ajoutée: {constraint_type.get()} = {constraint_value.get()}")

                dialog.destroy()

            ttk.Button(button_frame, text="Sauvegarder", command=save_constraint).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Annuler", command=dialog.destroy).pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur ajout contrainte: {e}")

    def search_error_history(self):
        """Rechercher dans l'historique des erreurs"""
        try:
            # Dialogue de recherche
            search_dialog = tk.Toplevel(self.root)
            search_dialog.title("Rechercher une erreur")
            search_dialog.geometry("400x150")
            search_dialog.transient(self.root)
            search_dialog.grab_set()

            search_var = tk.StringVar()

            ttk.Label(search_dialog, text="Rechercher une erreur:").pack(pady=10)
            search_entry = ttk.Entry(search_dialog, textvariable=search_var, width=50)
            search_entry.pack(pady=5, padx=20)
            search_entry.focus()

            def perform_search():
                query = search_var.get().strip()
                if not query:
                    return

                search_dialog.destroy()

                # Effectuer la recherche
                self.add_chat_message("user", f"Recherche: {query}")
                self.handle_general_query(query)

            button_frame = ttk.Frame(search_dialog)
            button_frame.pack(pady=10)

            ttk.Button(button_frame, text="Rechercher", command=perform_search).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Annuler", command=search_dialog.destroy).pack(side="left", padx=5)

            # Bind Enter
            search_entry.bind("<Return>", lambda e: perform_search())

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur recherche: {e}")

    # ===== FIN MÉTHODES CHAT RAG =====

    # ===== MÉTHODES PYTHON EMBEDDED =====

    def detect_python_manually(self):
        """Détection manuelle du Python embedded"""
        try:
            print("🐍 Détection manuelle du Python ComfyUI...")
            from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

            self.python_status_label.config(text="🔍 Détection en cours...", foreground="blue")
            self.root.update()

            with ComfyUICustomNodeCaller() as caller:
                python_path = caller.get_python_path_from_comfyui()

                if python_path:
                    print(f"✅ Python path détecté manuellement: {python_path}")
                    self.detected_python_path = python_path

                    # Mettre à jour l'interface
                    self.python_status_label.config(
                        text=f"✅ Détecté: {python_path.split('/')[-1] if '/' in python_path else python_path}",
                        foreground="green"
                    )

                    self.python_prefix_entry.config(state="normal")
                    self.python_prefix_entry.delete(0, tk.END)
                    self.python_prefix_entry.insert(0, f'"{python_path}" -m ')
                    self.python_prefix_entry.config(state="readonly")

                    self.execute_python_btn.config(state="normal")

                    messagebox.showinfo(
                        "Python Détecté",
                        f"Python ComfyUI détecté:\n\n{python_path}\n\n"
                        "Vous pouvez maintenant exécuter des commandes Python."
                    )
                else:
                    self.python_status_label.config(text="❌ Non détecté", foreground="red")
                    messagebox.showerror(
                        "Détection échouée",
                        "Impossible de détecter le Python ComfyUI.\n\n"
                        "Vérifiez que:\n"
                        "• ComfyUI est démarré\n"
                        "• Le custom node PythonPathNode est installé"
                    )

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erreur détection manuelle: {error_msg}")
            self.python_status_label.config(text="❌ Erreur", foreground="red")
            messagebox.showerror("Erreur", f"Erreur lors de la détection:\n\n{error_msg}")

    def execute_python_command(self):
        """Exécuter une commande Python dans l'environnement ComfyUI"""
        try:
            command = self.python_command_entry.get().strip()
            if not command:
                messagebox.showwarning("Commande vide", "Veuillez saisir une commande Python.")
                return

            if not hasattr(self, 'detected_python_path') or not self.detected_python_path:
                messagebox.showerror("Python non détecté", "Veuillez d'abord détecter l'environnement Python.")
                return

            print(f"🐍 Exécution de la commande: {command}")

            # Construire la commande complète
            full_command = f'"{self.detected_python_path}" -m {command}'

            # Créer une fenêtre pour afficher le résultat
            result_window = tk.Toplevel(self.root)
            result_window.title(f"Résultat: python -m {command}")
            result_window.geometry("600x400")

            # Zone de texte pour le résultat
            result_frame = ttk.Frame(result_window)
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            result_text = tk.Text(result_frame, wrap="word", font=("Consolas", 9))
            result_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=result_text.yview)
            result_text.configure(yscrollcommand=result_scroll.set)

            result_text.pack(side="left", fill="both", expand=True)
            result_scroll.pack(side="right", fill="y")

            # Bouton fermer
            ttk.Button(
                result_window,
                text="Fermer",
                command=result_window.destroy
            ).pack(pady=(0, 10))

            # Afficher la commande
            result_text.insert("end", f"$ {full_command}\n\n")
            result_text.update()

            # Exécuter la commande en arrière-plan
            import threading
            import subprocess

            def run_command():
                try:
                    result = subprocess.run(
                        full_command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    # Mettre à jour l'interface dans le thread principal
                    def update_result():
                        if result.returncode == 0:
                            result_text.insert("end", "✅ SUCCÈS\n\n")
                            if result.stdout:
                                result_text.insert("end", "SORTIE:\n")
                                result_text.insert("end", result.stdout)
                        else:
                            result_text.insert("end", f"❌ ERREUR (code {result.returncode})\n\n")
                            if result.stderr:
                                result_text.insert("end", "ERREUR:\n")
                                result_text.insert("end", result.stderr)

                        result_text.see("end")

                    self.root.after(0, update_result)

                except subprocess.TimeoutExpired:
                    def show_timeout():
                        result_text.insert("end", "⏱️ TIMEOUT - Commande interrompue après 30s\n")
                        result_text.see("end")
                    self.root.after(0, show_timeout)

                except Exception as e:
                    def show_error():
                        result_text.insert("end", f"❌ ERREUR D'EXÉCUTION:\n{e}\n")
                        result_text.see("end")
                    self.root.after(0, show_error)

            # Lancer l'exécution en arrière-plan
            thread = threading.Thread(target=run_command, daemon=True)
            thread.start()

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erreur exécution commande: {error_msg}")
            messagebox.showerror("Erreur", f"Erreur lors de l'exécution:\n\n{error_msg}")

    # ===== FIN MÉTHODES PYTHON EMBEDDED =====

    # ===== MÉTHODES SCAN RAG =====

    def scan_and_index_existing_analyses(self, environment_id, logger=None):
        """Scanner et indexer automatiquement les analyses existantes"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                print("⚠️ RAG non disponible pour le scan")
                return

            print(f"🔍 Scan des analyses pour l'environnement: {environment_id}")

            # Obtenir le répertoire d'analyses pour cet environnement
            analyses_dir = self.db_manager.get_environment_analyses_directory(environment_id)
            if not analyses_dir or not os.path.exists(analyses_dir):
                print(f"📭 Aucun répertoire d'analyses trouvé pour {environment_id}")
                return

            print(f"📁 Répertoire d'analyses: {analyses_dir}")

            # Chercher les fichiers d'analyses
            analysis_files = []
            for root, dirs, files in os.walk(analyses_dir):
                for file in files:
                    if (file.endswith(('.json', '.txt', '.md')) and
                        any(keyword in file.lower() for keyword in ['analysis', 'analyse', 'log'])):
                        filepath = os.path.join(root, file)
                        analysis_files.append(filepath)

            print(f"📄 Fichiers d'analyses trouvés: {len(analysis_files)}")

            if not analysis_files:
                print("📭 Aucun fichier d'analyse à indexer")
                self.update_chat_rag_indicators()
                return

            # Indexer les analyses
            indexed_count = 0
            skipped_count = 0

            for filepath in analysis_files:
                try:
                    # Vérifier si déjà indexé en se basant sur le nom du fichier
                    if self.is_analysis_already_indexed(filepath):
                        skipped_count += 1
                        continue

                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if not content.strip():
                        continue

                    # Créer les données d'analyse
                    analysis_data = {
                        "timestamp": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                        "type": "stored_analysis",
                        "filename": os.path.basename(filepath),
                        "full_analysis": content,
                        "environment_id": environment_id,
                        "filepath": filepath,
                        "auto_indexed": True  # Marquer comme indexé automatiquement
                    }

                    # Indexer
                    success = self.rag_manager.index_analysis_result(analysis_data)
                    if success:
                        indexed_count += 1
                        print(f"✅ Indexé: {os.path.basename(filepath)}")
                        if logger:
                            logger.info(f"Analyse indexée: {os.path.basename(filepath)}")
                    else:
                        print(f"❌ Échec indexation: {os.path.basename(filepath)}")

                except Exception as e:
                    print(f"❌ Erreur fichier {filepath}: {e}")

            print(f"🎉 Scan terminé: {indexed_count} indexés, {skipped_count} ignorés")
            if logger:
                logger.info(f"Scan RAG terminé: {indexed_count}/{len(analysis_files)} analyses indexées")

            # Mettre à jour les indicateurs dans l'onglet Chat
            self.update_chat_rag_indicators()

        except Exception as e:
            print(f"❌ Erreur scan RAG: {e}")
            if logger:
                logger.error(f"Erreur scan RAG: {e}")

    def is_analysis_already_indexed(self, filepath):
        """Vérifier si une analyse est déjà indexée"""
        try:
            if not self.rag_manager or not self.rag_manager.collection:
                return False

            filename = os.path.basename(filepath)

            # Rechercher par nom de fichier dans les métadonnées
            results = self.rag_manager.collection.get(
                where={"filename": filename},
                include=["metadatas"]
            )

            return len(results['metadatas']) > 0

        except Exception as e:
            print(f"⚠️ Erreur vérification indexation {filepath}: {e}")
            return False

    def update_chat_rag_indicators(self):
        """Mettre à jour les indicateurs RAG dans l'onglet Chat"""
        try:
            if not hasattr(self, 'rag_status_frame'):
                return

            # Obtenir les statistiques RAG
            stats = self.get_rag_statistics()

            # Mettre à jour les labels d'indicateurs
            if hasattr(self, 'rag_docs_count_label'):
                self.rag_docs_count_label.config(text=f"{stats['total_docs']}")

            if hasattr(self, 'rag_env_label'):
                self.rag_env_label.config(text=f"{stats['current_env'] or 'Aucun'}")

            if hasattr(self, 'rag_status_indicator'):
                if stats['is_available'] and stats['total_docs'] > 0:
                    self.rag_status_indicator.config(text="🟢", foreground="green")
                elif stats['is_available']:
                    self.rag_status_indicator.config(text="🟡", foreground="orange")
                else:
                    self.rag_status_indicator.config(text="🔴", foreground="red")

            print(f"📊 Indicateurs RAG mis à jour: {stats['total_docs']} docs")

        except Exception as e:
            print(f"⚠️ Erreur mise à jour indicateurs RAG: {e}")

    def get_rag_statistics(self):
        """Obtenir les statistiques du RAG"""
        try:
            stats = {
                'is_available': False,
                'total_docs': 0,
                'current_env': self.current_environment_id,
                'last_indexed': None
            }

            if self.rag_manager and self.rag_manager.is_available():
                stats['is_available'] = True

                if self.rag_manager.collection:
                    stats['total_docs'] = self.rag_manager.collection.count()

                    # Obtenir la dernière analyse indexée
                    if stats['total_docs'] > 0:
                        try:
                            results = self.rag_manager.collection.get(
                                limit=1,
                                include=["metadatas"]
                            )
                            if results['metadatas']:
                                stats['last_indexed'] = results['metadatas'][0].get('timestamp')
                        except Exception as e:
                            # Fallback si get() échoue
                            print(f"⚠️ Impossible de récupérer les métadonnées: {e}")
                            stats['last_indexed'] = "Récente"

            return stats

        except Exception as e:
            print(f"⚠️ Erreur statistiques RAG: {e}")
            return {
                'is_available': False,
                'total_docs': 0,
                'current_env': self.current_environment_id,
                'last_indexed': None
            }

    def manual_rag_scan(self):
        """Scanner manuellement les analyses via bouton dans l'onglet Chat"""
        try:
            if not self.current_environment_id:
                messagebox.showwarning(
                    "Environnement requis",
                    "Vous devez d'abord identifier un environnement ComfyUI.\n\n"
                    "Allez dans l'onglet ComfyUI et cliquez sur 'Identifier l'environnement'."
                )
                return

            if not self.rag_manager or not self.rag_manager.is_available():
                messagebox.showerror(
                    "RAG non disponible",
                    "Le système RAG n'est pas disponible.\n\n"
                    "Vérifiez que les dépendances sont installées."
                )
                return

            # Demander confirmation
            result = messagebox.askyesno(
                "Scanner les analyses",
                f"Scanner et indexer les analyses de l'environnement '{self.current_environment_id}' ?\n\n"
                "Cette opération peut prendre quelques instants."
            )

            if not result:
                return

            # Mettre à jour le statut
            old_status = self.chat_status_label.cget("text")
            self.chat_status_label.config(text="🔍 Scan en cours...", foreground="blue")
            self.root.update()

            try:
                # Lancer le scan
                self.scan_and_index_existing_analyses(self.current_environment_id)

                # Afficher le résultat
                stats = self.get_rag_statistics()
                messagebox.showinfo(
                    "Scan terminé",
                    f"Scan terminé avec succès !\n\n"
                    f"Documents indexés: {stats['total_docs']}\n"
                    f"Environnement: {stats['current_env']}"
                )

            except Exception as scan_error:
                messagebox.showerror("Erreur scan", f"Erreur lors du scan:\n\n{scan_error}")

            finally:
                # Restaurer le statut
                self.chat_status_label.config(text=old_status, foreground="black")

        except Exception as e:
            print(f"❌ Erreur scan manuel: {e}")
            messagebox.showerror("Erreur", f"Erreur lors du scan manuel:\n\n{e}")

    def send_environment_context_to_rag(self, environment_id, extra_paths_data=None, server_status=None):
        """Envoyer le contexte complet de l'environnement au RAG"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                print("⚠️ RAG non disponible, envoi du contexte annulé")
                return

            print(f"🧠 Envoi du contexte environnement {environment_id} au RAG...")

            # 1. Préparer les informations d'environnement
            env_info = {
                "environment_id": environment_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "identification_type": "comfyui_custom_node"
            }

            # 2. Ajouter les extra paths si disponibles
            if extra_paths_data:
                env_info["extra_paths"] = extra_paths_data
                env_info["comfyui_root"] = extra_paths_data.get("comfyui_root", "")

                # Extraire informations clés
                if "extra_paths" in extra_paths_data:
                    paths_config = extra_paths_data["extra_paths"]
                    env_info["custom_nodes_paths"] = []
                    env_info["models_paths"] = []

                    for section, paths in paths_config.items():
                        if isinstance(paths, dict):
                            for key, path in paths.items():
                                if "custom_nodes" in key.lower():
                                    env_info["custom_nodes_paths"].append(path)
                                elif any(model_type in key.lower() for model_type in ["checkpoints", "vae", "loras", "embeddings"]):
                                    env_info["models_paths"].append(path)

            # 3. Ajouter l'état du serveur
            if server_status:
                env_info["server_status"] = server_status

            # 4. Récupérer les dernières analyses de logs
            recent_analyses = self.get_recent_log_analyses(environment_id, limit=50)
            if recent_analyses:
                env_info["recent_log_analyses"] = recent_analyses

                # Catégoriser les analyses
                categories = {
                    "errors": [],
                    "custom_nodes_issues": [],
                    "performance_issues": [],
                    "server_status": [],
                    "warnings": []
                }

                for analysis in recent_analyses:
                    log_type = analysis.get("log_type", "").lower()
                    message = analysis.get("message", "").lower()

                    if "error" in log_type or "failed" in message:
                        categories["errors"].append(analysis)
                    elif "custom" in message and "node" in message:
                        categories["custom_nodes_issues"].append(analysis)
                    elif any(perf_word in message for perf_word in ["slow", "performance", "memory", "gpu", "cuda"]):
                        categories["performance_issues"].append(analysis)
                    elif any(status_word in message for status_word in ["server", "starting", "ready", "listening"]):
                        categories["server_status"].append(analysis)
                    elif "warning" in log_type:
                        categories["warnings"].append(analysis)

                env_info["categorized_analyses"] = categories

            # 5. Créer le rapport contextualisé pour le RAG
            context_report = self.create_rag_context_report(env_info)

            # 6. Indexer le contexte dans le RAG
            self.rag_manager.index_analysis_result({
                "timestamp": time.time(),
                "type": "environment_context",
                "analysis_type": "environment_context",
                "content": context_report,
                "environment_id": environment_id,
                "context_type": "complete_environment_state",
                "categories": list(env_info.get("categorized_analyses", {}).keys())
            })

            print(f"✅ Contexte environnement envoyé au RAG: {len(context_report)} caractères")

            # Mettre à jour les indicateurs
            self.update_chat_rag_indicators()

        except Exception as e:
            print(f"❌ Erreur envoi contexte au RAG: {e}")

    def get_recent_log_analyses(self, environment_id, limit=50):
        """Récupérer les analyses de logs récentes pour un environnement"""
        try:
            if not self.db_manager:
                return []

            # Récupérer les analyses récentes de la base de données
            all_analyses = self.db_manager.get_analysis_results(environment_id)

            # Convertir en format attendu et limiter
            formatted_analyses = []
            for analysis in all_analyses[:limit]:  # Limiter au nombre demandé
                # Format: (id, environment_id, fichier, type, niveau, message, details, timestamp_analyse)
                formatted_analysis = {
                    "id": analysis[0],
                    "environment_id": analysis[1],
                    "file": analysis[2],
                    "log_type": analysis[3],
                    "level": analysis[4],
                    "message": analysis[5],
                    "details": analysis[6],
                    "timestamp": analysis[7]
                }
                formatted_analyses.append(formatted_analysis)

            return formatted_analyses

        except Exception as e:
            print(f"❌ Erreur récupération analyses récentes: {e}")
            return []

    def create_rag_context_report(self, env_info):
        """Créer un rapport contextualisé pour le RAG"""
        try:
            report_lines = []

            # En-tête spécialisé pour le RAG
            report_lines.append("=== RAPPORT CONTEXTE COMFYUI POUR RAG EXPERT ===")
            report_lines.append(f"Environnement: {env_info['environment_id']}")
            report_lines.append(f"Timestamp: {env_info['timestamp']}")
            report_lines.append("")

            # Contexte d'expertise
            report_lines.append("CONTEXTE D'EXPERTISE:")
            report_lines.append("- Tu es un expert en maintenance applicative ComfyUI")
            report_lines.append("- Tu es spécialisé en Python et environnements virtuels")
            report_lines.append("- Tu connais les problèmes courants de ComfyUI et leurs solutions")
            report_lines.append("- Tu peux diagnostiquer les erreurs de custom nodes et de dépendances")
            report_lines.append("")

            # Informations d'environnement
            if "comfyui_root" in env_info:
                report_lines.append(f"RACINE COMFYUI: {env_info['comfyui_root']}")
                report_lines.append("")

            # Custom nodes et chemins
            if "custom_nodes_paths" in env_info:
                report_lines.append("CUSTOM NODES DETECTES:")
                for path in env_info["custom_nodes_paths"]:
                    report_lines.append(f"- {path}")
                report_lines.append("")

            # Modèles disponibles
            if "models_paths" in env_info:
                report_lines.append("CHEMINS MODELES:")
                for path in env_info["models_paths"]:
                    report_lines.append(f"- {path}")
                report_lines.append("")

            # État du serveur
            if "server_status" in env_info:
                status = env_info["server_status"]
                report_lines.append("ETAT SERVEUR:")
                report_lines.append(f"- Statut: {status.get('status', 'inconnu')}")
                if "system_stats" in status:
                    stats = status["system_stats"]
                    report_lines.append(f"- RAM: {stats.get('ram', 'N/A')}")
                    report_lines.append(f"- VRAM: {stats.get('vram', 'N/A')}")
                report_lines.append("")

            # Analyses catégorisées
            if "categorized_analyses" in env_info:
                categories = env_info["categorized_analyses"]

                # Erreurs critiques
                if categories["errors"]:
                    report_lines.append("ERREURS CRITIQUES DETECTEES:")
                    for error in categories["errors"][:10]:  # Limiter à 10
                        report_lines.append(f"- {error.get('timestamp', 'N/A')}: {error.get('message', 'N/A')}")
                    report_lines.append("")

                # Problèmes de custom nodes
                if categories["custom_nodes_issues"]:
                    report_lines.append("PROBLEMES CUSTOM NODES:")
                    for issue in categories["custom_nodes_issues"][:10]:
                        report_lines.append(f"- {issue.get('timestamp', 'N/A')}: {issue.get('message', 'N/A')}")
                    report_lines.append("")

                # Problèmes de performance
                if categories["performance_issues"]:
                    report_lines.append("PROBLEMES PERFORMANCE:")
                    for perf in categories["performance_issues"][:10]:
                        report_lines.append(f"- {perf.get('timestamp', 'N/A')}: {perf.get('message', 'N/A')}")
                    report_lines.append("")

                # Avertissements
                if categories["warnings"]:
                    report_lines.append("AVERTISSEMENTS:")
                    for warning in categories["warnings"][:10]:
                        report_lines.append(f"- {warning.get('timestamp', 'N/A')}: {warning.get('message', 'N/A')}")
                    report_lines.append("")

            # Instructions pour le RAG
            report_lines.append("INSTRUCTIONS POUR REPONSES:")
            report_lines.append("- Utilise ces informations pour contextualiser tes réponses")
            report_lines.append("- Priorise les erreurs critiques dans tes diagnostics")
            report_lines.append("- Propose des solutions basées sur l'environnement identifié")
            report_lines.append("- Référence les chemins et configurations spécifiques")
            report_lines.append("- Suggère des optimisations de performance si pertinent")

            return "\n".join(report_lines)

        except Exception as e:
            print(f"❌ Erreur création rapport contexte: {e}")
            return f"Erreur création rapport pour {env_info.get('environment_id', 'inconnu')}: {e}"

    # ===== FIN MÉTHODES SCAN RAG =====

    # ===== MÉTHODES TERMINAL =====

    def execute_terminal_command(self):
        """Exécute une commande dans le terminal"""
        try:
            command = self.terminal_input.get().strip()
            if not command:
                return

            # Ajouter à l'historique
            if command not in self.terminal_history:
                self.terminal_history.append(command)
            self.terminal_history_index = -1

            # Afficher la commande
            self.append_terminal_output(f"\n{self.terminal_cwd}> {command}\n", "command")

            # Vider l'input
            self.terminal_input.delete(0, tk.END)

            # Gérer les commandes intégrées
            if command.lower() in ['cls', 'clear']:
                self.terminal_output.delete(1.0, tk.END)
                return
            elif command.lower() == 'exit':
                self.append_terminal_output("Fermeture du terminal...\n", "info")
                return
            elif command.startswith('cd '):
                self.change_terminal_directory(command[3:].strip())
                return

            # Exécuter la commande
            self.run_command_in_subprocess(command)

        except Exception as e:
            self.append_terminal_output(f"❌ Erreur: {e}\n", "error")

    def run_command_in_subprocess(self, command):
        """Exécute une commande en subprocess"""
        try:
            import subprocess
            import threading

            def run_process():
                try:
                    # Interrompre le processus précédent s'il existe
                    self.interrupt_terminal_command()

                    # Créer le processus
                    startupinfo = None
                    if hasattr(subprocess, 'STARTUPINFO'):
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    self.current_process = subprocess.Popen(
                        command,
                        shell=True,
                        cwd=self.terminal_cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        universal_newlines=True,
                        startupinfo=startupinfo
                    )

                    # Pour les commandes simples, utiliser communicate()
                    # Pour les commandes longues, utiliser les threads
                    simple_commands = ['echo', 'dir', 'ls', 'pwd', 'cd', 'python --version', 'which', 'where']
                    is_simple = any(command.strip().lower().startswith(cmd) for cmd in simple_commands)

                    if is_simple:
                        # Commande simple : utiliser communicate()
                        try:
                            stdout, stderr = self.current_process.communicate(timeout=10)

                            # Afficher la sortie
                            if stdout:
                                def show_output():
                                    self.append_terminal_output(stdout, "output")
                                self.root.after(0, show_output)

                            if stderr:
                                def show_error():
                                    self.append_terminal_output(stderr, "error")
                                self.root.after(0, show_error)

                            returncode = self.current_process.returncode

                        except subprocess.TimeoutExpired:
                            self.current_process.kill()
                            def show_timeout():
                                self.append_terminal_output("⏱️ Timeout - commande interrompue\n", "warning")
                            self.root.after(0, show_timeout)
                            returncode = -1

                    else:
                        # Commande complexe : utiliser les threads
                        def read_output(pipe, tag):
                            try:
                                for line in iter(pipe.readline, ''):
                                    if line:
                                        # Utiliser une fonction locale pour capturer les variables correctement
                                        def append_line(text=line, tag_name=tag):
                                            self.append_terminal_output(text, tag_name)
                                        self.root.after(0, append_line)
                            except Exception as e:
                                print(f"Erreur lecture thread {tag}: {e}")

                        # Threads pour stdout et stderr
                        stdout_thread = threading.Thread(target=read_output, args=(self.current_process.stdout, "output"))
                        stderr_thread = threading.Thread(target=read_output, args=(self.current_process.stderr, "error"))

                        stdout_thread.daemon = True
                        stderr_thread.daemon = True
                        stdout_thread.start()
                        stderr_thread.start()

                        # Attendre la fin
                        returncode = self.current_process.wait()

                        # Attendre que les threads terminent
                        stdout_thread.join(timeout=2)
                        stderr_thread.join(timeout=2)

                    # Message de fin
                    if returncode == 0:
                        def append_success():
                            self.append_terminal_output(f"\n✅ Commande terminée (code: {returncode})\n", "success")
                        self.root.after(0, append_success)
                    else:
                        def append_error():
                            self.append_terminal_output(f"\n❌ Commande terminée avec erreur (code: {returncode})\n", "error")
                        self.root.after(0, append_error)

                    # Indexer dans le RAG si activé
                    if hasattr(self, 'terminal_rag_enabled') and self.terminal_rag_enabled.get():
                        self.index_terminal_session(command, returncode)

                except Exception as e:
                    self.root.after(0, lambda: self.append_terminal_output(f"\n❌ Erreur subprocess: {e}\n", "error"))
                finally:
                    self.current_process = None

            # Lancer en thread séparé
            thread = threading.Thread(target=run_process)
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.append_terminal_output(f"❌ Erreur lancement commande: {e}\n", "error")

    def interrupt_terminal_command(self):
        """Interrompt la commande en cours"""
        try:
            if self.current_process and self.current_process.poll() is None:
                self.current_process.terminate()
                try:
                    self.current_process.wait(timeout=2)
                except:
                    self.current_process.kill()
                self.append_terminal_output("\n🛑 Commande interrompue\n", "warning")
                self.current_process = None
        except Exception as e:
            self.append_terminal_output(f"❌ Erreur interruption: {e}\n", "error")

    def change_terminal_directory(self, path):
        """Change le répertoire de travail du terminal"""
        try:
            import os

            if not path:
                path = os.path.expanduser("~")
            else:
                path = os.path.expandvars(os.path.expanduser(path))

            if os.path.exists(path) and os.path.isdir(path):
                self.terminal_cwd = os.path.abspath(path)
                self.terminal_cwd_var.set(self.terminal_cwd)
                self.append_terminal_output(f"📁 Répertoire changé: {self.terminal_cwd}\n", "info")
            else:
                self.append_terminal_output(f"❌ Répertoire non trouvé: {path}\n", "error")

        except Exception as e:
            self.append_terminal_output(f"❌ Erreur changement répertoire: {e}\n", "error")

    def browse_terminal_directory(self):
        """Ouvre un sélecteur de dossier pour le terminal"""
        try:
            import tkinter.filedialog as fd

            directory = fd.askdirectory(
                title="Sélectionner le répertoire de travail",
                initialdir=self.terminal_cwd
            )

            if directory:
                self.change_terminal_directory(directory)

        except Exception as e:
            self.append_terminal_output(f"❌ Erreur sélection répertoire: {e}\n", "error")

    def on_terminal_key_press(self, event):
        """Gère les touches spéciales dans le terminal"""
        try:
            if event.keysym == 'Return':
                self.execute_terminal_command()
                return 'break'
            elif event.keysym == 'Up':
                self.navigate_terminal_history(-1)
                return 'break'
            elif event.keysym == 'Down':
                self.navigate_terminal_history(1)
                return 'break'
            elif event.keysym == 'Tab':
                # Auto-complétion simple (TODO: améliorer)
                return 'break'
        except Exception as e:
            print(f"❌ Erreur gestion touche terminal: {e}")

    def navigate_terminal_history(self, direction):
        """Navigue dans l'historique des commandes"""
        try:
            if not self.terminal_history:
                return

            # Mettre à jour l'index
            self.terminal_history_index += direction

            # Borner l'index
            if self.terminal_history_index < -len(self.terminal_history):
                self.terminal_history_index = -len(self.terminal_history)
            elif self.terminal_history_index > -1:
                self.terminal_history_index = -1
                self.terminal_input.delete(0, tk.END)
                return

            # Afficher la commande
            command = self.terminal_history[self.terminal_history_index]
            self.terminal_input.delete(0, tk.END)
            self.terminal_input.insert(0, command)

        except Exception as e:
            print(f"❌ Erreur navigation historique: {e}")

    def append_terminal_output(self, text, tag="output"):
        """Ajoute du texte à la sortie du terminal"""
        try:
            # CRITIQUE: Activer le widget Text temporairement
            self.terminal_output.config(state=tk.NORMAL)

            # Obtenir la position actuelle
            start_pos = self.terminal_output.index(tk.END)

            # Insérer le texte
            self.terminal_output.insert(tk.END, text)

            # Appliquer le tag si spécifié
            if tag != "output":
                end_pos = self.terminal_output.index(tk.END)
                self.terminal_output.tag_add(tag, start_pos, end_pos)

            # Scroll automatique
            self.terminal_output.see(tk.END)

            # Force refresh pour s'assurer que l'affichage est mis à jour
            self.terminal_output.update_idletasks()

            # CRITIQUE: Redésactiver le widget pour éviter l'édition manuelle
            self.terminal_output.config(state=tk.DISABLED)

        except Exception as e:
            print(f"❌ Erreur ajout texte terminal: {e}")
            # En cas d'erreur avec les tags, essayer sans tag
            try:
                self.terminal_output.config(state=tk.NORMAL)
                self.terminal_output.insert(tk.END, text)
                self.terminal_output.see(tk.END)
                self.terminal_output.config(state=tk.DISABLED)
            except Exception as e2:
                print(f"❌ Erreur critique terminal: {e2}")

    def save_terminal_session(self):
        """Sauvegarde la session du terminal"""
        try:
            import tkinter.filedialog as fd
            from datetime import datetime

            # Nom de fichier par défaut
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"terminal_session_{timestamp}.log"

            filename = fd.asksaveasfilename(
                title="Sauvegarder la session terminal",
                defaultextension=".log",
                filetypes=[("Fichiers log", "*.log"), ("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
                initialname=default_name
            )

            if filename:
                content = self.terminal_output.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"=== Session Terminal - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                    f.write(f"Répertoire de travail: {self.terminal_cwd}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(content)

                self.append_terminal_output(f"\n💾 Session sauvegardée: {filename}\n", "success")

        except Exception as e:
            self.append_terminal_output(f"❌ Erreur sauvegarde: {e}\n", "error")

    def clear_terminal_output(self):
        """Efface la sortie du terminal"""
        try:
            # Activer le widget pour permettre la suppression
            self.terminal_output.config(state=tk.NORMAL)
            self.terminal_output.delete(1.0, tk.END)
            self.terminal_output.config(state=tk.DISABLED)

            # Afficher le message de confirmation
            self.append_terminal_output("Terminal effacé\n", "info")
        except Exception as e:
            self.append_terminal_output(f"❌ Erreur effacement: {e}\n", "error")

    def index_terminal_session(self, command, returncode):
        """Indexe une session terminal dans le RAG"""
        try:
            if not hasattr(self, 'rag_manager') or not self.rag_manager:
                return

            from datetime import datetime
            import os

            # Créer le document pour le RAG
            content = f"""=== Session Terminal ===
Timestamp: {datetime.now().isoformat()}
Répertoire: {self.terminal_cwd}
Commande: {command}
Code retour: {returncode}
Environnement: {os.environ.get('VIRTUAL_ENV', 'système')}

=== Contexte ===
Application: cy8_prompts_manager
Module: Terminal intégré
Utilisateur: Session interactive

=== Analyse ===
"""

            # Ajouter une analyse simple
            if returncode == 0:
                content += "✅ Commande exécutée avec succès\n"
            else:
                content += f"❌ Commande échouée (code {returncode})\n"

            if command.startswith(('pip ', 'conda ', 'npm ')):
                content += "📦 Gestion de packages détectée\n"
            elif command.startswith(('git ', 'svn ')):
                content += "🔧 Commande de contrôle de version\n"
            elif command.startswith(('python ', 'node ', 'java ')):
                content += "🐍 Exécution de script/programme\n"

            # Ajouter au RAG en utilisant la méthode correcte
            terminal_analysis = {
                'timestamp': datetime.now().isoformat(),
                'command': command,
                'returncode': returncode,
                'working_directory': self.terminal_cwd,
                'type': 'terminal_session',
                'environment_id': getattr(self, 'current_environment_id', 'unknown'),
                'content': content,
                'category': 'terminal',
                'element': 'command_execution',
                'message': f"Commande: {command}"
            }

            self.rag_manager.index_analysis_result(terminal_analysis)

            print(f"📚 Session terminal indexée dans le RAG: {command}")

        except Exception as e:
            print(f"❌ Erreur indexation terminal RAG: {e}")

    def toggle_rag_indexing(self):
        """Active/désactive l'indexation RAG du terminal"""
        try:
            if hasattr(self, 'terminal_rag_enabled'):
                state = "activée" if self.terminal_rag_enabled.get() else "désactivée"
                print(f"🔄 Indexation RAG terminal {state}")

                # Message dans le terminal si visible
                if hasattr(self, 'append_terminal_output'):
                    self.append_terminal_output(f"\n📚 Indexation RAG {state}\n", "info")
        except Exception as e:
            print(f"❌ Erreur toggle RAG: {e}")

    def initialize_terminal_welcome(self):
        """Initialise le terminal avec un message de bienvenue"""
        try:
            import os
            from datetime import datetime

            welcome_msg = f"""⚡ Terminal cy8_prompts_manager ⚡
═══════════════════════════════════════
📅 Session: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📁 Répertoire: {os.getcwd()}
🐍 Python: {hasattr(self, 'python_version') and getattr(self, 'python_version', 'Détection...')}
🔧 RAG: {'Activé' if hasattr(self, 'terminal_rag_enabled') and self.terminal_rag_enabled.get() else 'Désactivé'}

Tapez vos commandes ci-dessous. Utilisez ↑/↓ pour naviguer dans l'historique.
═══════════════════════════════════════

"""
            self.append_terminal_output(welcome_msg, "info")

            # Afficher la première invite de commande
            self.append_terminal_output(f"{self.terminal_cwd}> ", "command")

        except Exception as e:
            print(f"❌ Erreur initialisation welcome: {e}")

    # ===== MÉTHODES DE GESTION RAG =====

    def examine_rag_index(self):
        """Examiner l'index RAG et afficher les statistiques détaillées"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                self.add_chat_message("error", "❌ RAG non disponible")
                return

            # Obtenir les statistiques détaillées
            stats = self.rag_manager.get_collection_stats()

            response = []
            response.append("🔍 **EXAMEN DE L'INDEX RAG**")
            response.append("=" * 40)
            response.append("")

            if stats.get('total_documents', 0) > 0:
                response.append(f"📊 **Statistiques générales:**")
                response.append(f"• Documents indexés: {stats.get('total_documents', 0)}")
                response.append(f"• Environnement actuel: {self.current_environment_id}")
                response.append(f"• Base ChromaDB: {'✅ Active' if self.rag_manager.collection else '❌ Non disponible'}")
                response.append("")

                # Analyser les types de documents
                if self.rag_manager.collection:
                    try:
                        results = self.rag_manager.collection.get(
                            limit=100,
                            include=["metadatas"]
                        )

                        if results and results.get('metadatas'):
                            types_count = {}
                            env_count = {}

                            for metadata in results['metadatas']:
                                doc_type = metadata.get('analysis_type', 'unknown')
                                env_id = metadata.get('environment_id', 'unknown')

                                types_count[doc_type] = types_count.get(doc_type, 0) + 1
                                env_count[env_id] = env_count.get(env_id, 0) + 1

                            response.append("📋 **Types de documents:**")
                            for doc_type, count in sorted(types_count.items(), key=lambda x: x[1], reverse=True):
                                response.append(f"• {doc_type}: {count}")

                            response.append("")
                            response.append("🏠 **Répartition par environnement:**")
                            for env_id, count in sorted(env_count.items(), key=lambda x: x[1], reverse=True):
                                response.append(f"• {env_id}: {count}")

                    except Exception as e:
                        response.append(f"⚠️ Erreur analyse détaillée: {e}")

            else:
                response.append("📭 **Index vide**")
                response.append("• Aucun document indexé")
                response.append("• Lancez une analyse ou utilisez 'Ré-indexer'")

            response.append("")
            response.append("💡 **Actions disponibles:**")
            response.append("• 🔄 **Ré-indexer**: Recharger toutes les analyses")
            response.append("• 📊 **Stats RAG**: Statistiques complètes")
            response.append("• 🧠 **Test recherche**: Tester la recherche vectorielle")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur examen RAG: {e}")

    def reindex_rag_analyses(self):
        """Relancer l'indexation complète des analyses"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                self.add_chat_message("error", "❌ RAG non disponible")
                return

            self.add_chat_message("system", "🔄 Démarrage de la ré-indexation...")

            # Lancer l'indexation en arrière-plan
            import threading

            def reindex_thread():
                try:
                    # Scanner et indexer les analyses
                    environment_id = self.current_environment_id or "default"
                    self.scan_and_index_existing_analyses(environment_id)

                    # Mettre à jour l'interface dans le thread principal
                    self.root.after(0, lambda: self.add_chat_message("assistant",
                        "✅ **Ré-indexation terminée**\n\n"
                        "🎉 Toutes les analyses ont été ré-indexées avec succès.\n"
                        "📊 Utilisez 'Stats RAG' pour voir les nouveaux résultats."))

                except Exception as e:
                    self.root.after(0, lambda: self.add_chat_message("error",
                        f"❌ **Erreur ré-indexation:** {e}"))

            thread = threading.Thread(target=reindex_thread, daemon=True)
            thread.start()

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur lancement ré-indexation: {e}")

    def show_rag_statistics(self):
        """Afficher les statistiques complètes du RAG"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                self.add_chat_message("error", "❌ RAG non disponible")
                return

            stats = self.rag_manager.get_collection_stats()

            response = []
            response.append("📊 **STATISTIQUES RAG COMPLÈTES**")
            response.append("=" * 45)
            response.append("")

            # Statistiques de base
            response.append("🔢 **Métriques principales:**")
            response.append(f"• Documents totaux: {stats.get('total_documents', 0)}")
            response.append(f"• Environnement: {self.current_environment_id}")
            response.append(f"• Dernière indexation: {stats.get('last_indexed', 'Jamais')}")
            response.append("")

            # État des composants
            response.append("⚙️ **État des composants:**")
            response.append(f"• ChromaDB: {'✅ Connecté' if self.rag_manager.collection else '❌ Déconnecté'}")
            response.append(f"• Modèle embeddings: {'✅ Chargé' if self.rag_manager.embeddings_model else '❌ Non chargé'}")
            response.append(f"• Mode actuel: {self.get_current_rag_mode()}")
            response.append("")

            # Performances récentes
            if hasattr(self.rag_manager, 'query_history'):
                recent_queries = getattr(self.rag_manager, 'query_history', [])
                if recent_queries:
                    response.append("⚡ **Performances récentes:**")
                    response.append(f"• Requêtes traitées: {len(recent_queries)}")
                    avg_time = sum(q.get('duration', 0) for q in recent_queries[-10:]) / min(10, len(recent_queries))
                    response.append(f"• Temps moyen réponse: {avg_time:.2f}s")

            # Actions recommandées
            doc_count = stats.get('total_documents', 0)
            response.append("")
            response.append("💡 **Recommandations:**")
            if doc_count == 0:
                response.append("• 🔄 Lancer 'Ré-indexer' pour indexer les analyses")
                response.append("• 📝 Créer des analyses Mistral pour alimenter le RAG")
            elif doc_count < 10:
                response.append("• 📈 Index léger - plus d'analyses amélioreront la précision")
                response.append("• 🎯 Continuer à utiliser ComfyUI pour enrichir la base")
            else:
                response.append("• ✅ Index bien fourni - RAG opérationnel")
                response.append("• 🔍 Utiliser la recherche d'erreurs pour tester le système")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur statistiques RAG: {e}")

    def show_current_server_state(self):
        """Afficher l'état actuel du serveur basé sur les analyses récentes"""
        try:
            if not self.temporal_rag:
                self.add_chat_message("error", "❌ RAG temporel non disponible")
                return

            self.add_chat_message("system", "🔥 Recherche de l'état actuel du serveur...")

            # Rechercher les informations d'état récentes (24h)
            recent_results = self.temporal_rag.search_recent_only(
                query="état serveur erreur status ready listening",
                max_age_hours=24,
                limit=5
            )

            response = []
            response.append("🔥 **ÉTAT ACTUEL DU SERVEUR**")
            response.append("=" * 40)
            response.append("")

            if recent_results:
                response.append(f"📊 **Analyses récentes trouvées**: {len(recent_results)} (dernières 24h)")
                response.append("")

                # Analyser les résultats récents
                errors_found = 0
                warnings_found = 0
                successes_found = 0

                for result in recent_results:
                    content = result.get('content', '').lower()
                    age = result.get('age_days', 'N/A')

                    if any(keyword in content for keyword in ['error', 'failed', 'exception']):
                        errors_found += 1
                    elif any(keyword in content for keyword in ['warning', 'attention']):
                        warnings_found += 1
                    elif any(keyword in content for keyword in ['success', 'ready', 'loaded']):
                        successes_found += 1

                # Évaluation de l'état
                if errors_found == 0 and successes_found > 0:
                    response.append("✅ **État**: Serveur opérationnel")
                elif errors_found > successes_found:
                    response.append("❌ **État**: Problèmes détectés")
                else:
                    response.append("⚠️ **État**: État mixte - surveillance requise")

                response.append("")
                response.append("📈 **Répartition récente**:")
                response.append(f"• ✅ Succès: {successes_found}")
                response.append(f"• ⚠️ Avertissements: {warnings_found}")
                response.append(f"• ❌ Erreurs: {errors_found}")

                # Afficher les derniers événements
                response.append("")
                response.append("🕒 **Derniers événements**:")
                for i, result in enumerate(recent_results[:3]):
                    age = result.get('age_days', 'N/A')
                    content_preview = result.get('content', '')[:100] + "..."
                    response.append(f"• **Événement {i+1}** (il y a {age} jours):")
                    response.append(f"  {content_preview}")

            else:
                response.append("📭 **Aucune analyse récente trouvée**")
                response.append("• Pas d'activité dans les dernières 24h")
                response.append("• Le serveur pourrait être inactif")
                response.append("• Lancez ComfyUI pour générer des logs")

            response.append("")
            response.append("💡 **Recommandation**: Utilisez '📈 Évolution' pour voir les tendances sur plusieurs jours")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur état actuel: {e}")

    def show_temporal_analysis(self):
        """Afficher l'analyse de la distribution temporelle des données"""
        try:
            if not self.temporal_rag:
                self.add_chat_message("error", "❌ RAG temporel non disponible")
                return

            # Obtenir la distribution temporelle
            distribution = self.temporal_rag.get_temporal_distribution()

            response = []
            response.append("🕒 **ANALYSE TEMPORELLE DES DONNÉES**")
            response.append("=" * 45)
            response.append("")

            if "error" not in distribution:
                # Statistiques générales
                response.append("📊 **Vue d'ensemble**:")
                response.append(f"• Documents totaux: {distribution.get('total_documents', 0)}")
                response.append(f"• Documents horodatés: {distribution.get('documents_with_timestamp', 0)}")
                response.append(f"• Période couverte: {distribution.get('age_span_days', 0)} jours")
                response.append("")

                # Fraîcheur des données
                response.append("🔥 **Fraîcheur des données**:")
                response.append(f"• Dernières 24h: {distribution.get('recent_24h', 0)} ({distribution.get('percentage_recent_24h', 0)}%)")
                response.append(f"• Dernière semaine: {distribution.get('recent_week', 0)} ({distribution.get('percentage_recent_week', 0)}%)")
                response.append(f"• Dernier mois: {distribution.get('recent_month', 0)}")
                response.append("")

                # Dates clés
                oldest = distribution.get('oldest_document', 'N/A')
                newest = distribution.get('newest_document', 'N/A')
                if oldest != 'N/A':
                    try:
                        oldest_date = datetime.fromisoformat(oldest.replace('Z', '+00:00'))
                        oldest = oldest_date.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                if newest != 'N/A':
                    try:
                        newest_date = datetime.fromisoformat(newest.replace('Z', '+00:00'))
                        newest = newest_date.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass

                response.append("📅 **Chronologie**:")
                response.append(f"• Plus ancienne analyse: {oldest}")
                response.append(f"• Plus récente analyse: {newest}")
                response.append("")

                # Évaluation de la qualité temporelle
                recent_24h_pct = distribution.get('percentage_recent_24h', 0)
                if recent_24h_pct >= 30:
                    response.append("✅ **Qualité temporelle**: Excellente")
                    response.append("   Données très récentes et à jour")
                elif recent_24h_pct >= 10:
                    response.append("⚠️ **Qualité temporelle**: Correcte")
                    response.append("   Mix d'analyses récentes et anciennes")
                else:
                    response.append("❌ **Qualité temporelle**: Faible")
                    response.append("   Données majoritairement anciennes")

            else:
                response.append(f"❌ **Erreur**: {distribution['error']}")

            response.append("")
            response.append("💡 **Utilisation**: Les recherches RAG privilégient automatiquement les analyses récentes")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur analyse temporelle: {e}")

    def show_temporal_evolution(self):
        """Afficher l'évolution temporelle avec comparaison récent vs ancien"""
        try:
            if not self.temporal_rag:
                self.add_chat_message("error", "❌ RAG temporel non disponible")
                return

            # Comparer différentes périodes
            recent_24h = self.temporal_rag.search_recent_only("erreur PyTorch CUDA version", max_age_hours=24, limit=3)
            recent_week = self.temporal_rag.search_with_temporal_priority("erreur PyTorch CUDA version", recent_weight=1.5, max_age_days=7, limit=3)

            response = []
            response.append("📈 **ÉVOLUTION TEMPORELLE DU SERVEUR**")
            response.append("=" * 45)
            response.append("")

            # Analyse des tendances
            response.append("🔍 **Analyse comparative**:")
            response.append(f"• Activité récente (24h): {len(recent_24h)} événements")
            response.append(f"• Activité semaine: {len(recent_week)} événements")
            response.append("")

            if recent_24h:
                response.append("🔥 **Dernières 24 heures**:")
                for i, result in enumerate(recent_24h):
                    age = result.get('age_days', 'N/A')
                    preview = result.get('content', '')[:80] + "..."
                    response.append(f"• **Événement {i+1}** (il y a {age} jours):")
                    response.append(f"  {preview}")
                response.append("")

            # Tendance d'activité
            if len(recent_24h) > len(recent_week) // 3:
                response.append("📈 **Tendance**: Activité en hausse")
                response.append("   Le serveur est plus actif récemment")
            elif len(recent_24h) == 0 and len(recent_week) > 0:
                response.append("📉 **Tendance**: Activité en baisse")
                response.append("   Le serveur était plus actif auparavant")
            else:
                response.append("➡️ **Tendance**: Activité stable")
                response.append("   Niveau d'activité constant")

            response.append("")
            response.append("💡 **Conseil**: Utilisez '🔥 État actuel' pour un diagnostic immédiat")
            response.append("🔧 **Action**: Consultez l'onglet Log pour plus de détails")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur évolution temporelle: {e}")

    def reset_rag_completely(self):
        """Réinitialisation complète du RAG - Remise à zéro totale"""
        try:
            # Demander confirmation avec un dialog détaillé
            from tkinter import messagebox

            confirm = messagebox.askyesno(
                "⚠️ RÉINITIALISATION COMPLÈTE RAG",
                "🗑️ Cette action va SUPPRIMER DÉFINITIVEMENT :\n\n"
                "• Toutes les analyses indexées\n"
                "• La base vectorielle ChromaDB\n"
                "• Les métadonnées temporelles\n"
                "• L'historique des recherches\n\n"
                "⚠️ ATTENTION : Cette action est IRRÉVERSIBLE !\n\n"
                "Êtes-vous sûr de vouloir tout effacer ?",
                icon="warning"
            )

            if not confirm:
                self.add_chat_message("system", "🔄 Réinitialisation annulée par l'utilisateur")
                return

            self.add_chat_message("system", "🗑️ DÉMARRAGE RÉINITIALISATION COMPLÈTE RAG...")

            # 1. Supprimer TOUTES les analyses de la base de données
            try:
                self.db_manager.clear_analysis_results()  # Supprime toutes les analyses
                self.add_chat_message("system", "✅ Analyses supprimées de la base de données")
            except Exception as e:
                self.add_chat_message("error", f"❌ Erreur suppression analyses DB: {e}")

            # 1.5. Supprimer toutes les actions d'environnement
            try:
                # Nettoyer la table env_action
                self.db_manager.cursor.execute("DELETE FROM env_action")
                self.db_manager.conn.commit()
                self.add_chat_message("system", "✅ Actions d'environnement supprimées")
            except Exception as e:
                self.add_chat_message("error", f"❌ Erreur suppression actions: {e}")

            # 2. Fermer et supprimer la collection ChromaDB actuelle
            if self.rag_manager:
                try:
                    # Supprimer la collection si elle existe
                    if hasattr(self.rag_manager, 'collection') and self.rag_manager.collection:
                        try:
                            # Récupérer le client ChromaDB
                            chroma_client = self.rag_manager.collection._client if hasattr(self.rag_manager.collection, '_client') else None
                            collection_name = self.rag_manager.collection.name if hasattr(self.rag_manager.collection, 'name') else "comfyui_analyses_default"

                            # Supprimer la collection
                            if chroma_client:
                                chroma_client.delete_collection(name=collection_name)
                                self.add_chat_message("system", f"✅ Collection ChromaDB '{collection_name}' supprimée")
                        except Exception as e:
                            print(f"⚠️ Erreur suppression collection: {e}")

                        # Nettoyer les références
                        self.rag_manager.collection = None

                    # Nettoyer le client ChromaDB
                    if hasattr(self.rag_manager, 'chroma_client'):
                        self.rag_manager.chroma_client = None

                except Exception as e:
                    print(f"⚠️ Erreur fermeture RAG: {e}")

            # Nettoyer complètement les managers
            self.rag_manager = None
            self.temporal_rag = None

            # 3. Supprimer le dossier ChromaDB (chemin dynamique)
            import shutil
            import time
            vector_db_path = os.path.join(os.getcwd(), "data", "analyses", "vector_db")

            if os.path.exists(vector_db_path):
                try:
                    # Petite pause pour laisser ChromaDB se fermer
                    time.sleep(1)
                    shutil.rmtree(vector_db_path)
                    self.add_chat_message("system", f"✅ Dossier ChromaDB supprimé: {vector_db_path}")
                except Exception as e:
                    self.add_chat_message("error", f"❌ Erreur suppression ChromaDB: {e}")
                    self.add_chat_message("system", "⚠️ Fichiers ChromaDB verrouillés - redémarrez l'application pour finir le nettoyage")
            else:
                self.add_chat_message("system", "ℹ️ Dossier ChromaDB déjà absent")

            # 4. Supprimer les fichiers d'analyses (utiliser chemins dynamiques)
            analyses_dirs = [
                os.path.join(os.getcwd(), "data", "analyses"),
                "G:/tmp/analyses"  # Dossier temporaire s'il existe
            ]

            for analyses_dir in analyses_dirs:
                if os.path.exists(analyses_dir):
                    try:
                        # Supprimer seulement les fichiers .txt/.json, garder la structure
                        for root, dirs, files in os.walk(analyses_dir):
                            # Ignorer le dossier vector_db qu'on a déjà traité
                            if 'vector_db' in root:
                                continue
                            for file in files:
                                if file.endswith(('.txt', '.json', '.log')):
                                    file_path = os.path.join(root, file)
                                    os.remove(file_path)
                        self.add_chat_message("system", f"✅ Analyses supprimées: {analyses_dir}")
                    except Exception as e:
                        self.add_chat_message("error", f"❌ Erreur suppression analyses: {e}")

            # 4. Réinitialiser les managers
            self.rag_manager = None
            self.temporal_rag = None

            # 5. Recréer le RAG propre
            if RAG_AVAILABLE:
                try:
                    from cy8_rag_manager import RAGManager
                    from cy8_temporal_rag import TemporalRAGManager

                    self.rag_manager = RAGManager(self.db_manager, self.current_environment_id)
                    self.temporal_rag = TemporalRAGManager(self.rag_manager)

                    self.add_chat_message("system", "✅ RAG réinitialisé avec succès")
                    self.add_chat_message("system", "✅ Extension temporelle recréée")

                except Exception as e:
                    self.add_chat_message("error", f"❌ Erreur recréation RAG: {e}")

            # 6. Message de succès
            response = []
            response.append("🎉 **RÉINITIALISATION COMPLÈTE TERMINÉE**")
            response.append("=" * 45)
            response.append("")
            response.append("✅ **Actions effectuées:**")
            response.append("• Base vectorielle ChromaDB supprimée")
            response.append("• Fichiers d'analyses nettoyés")
            response.append("• RAG recréé à neuf")
            response.append("• Extension temporelle réinitialisée")
            response.append("")
            response.append("🚀 **Prochaines étapes:**")
            response.append("1. Relancer ComfyUI dans votre nouvel environnement")
            response.append("2. Générer quelques analyses Mistral")
            response.append("3. Utiliser '🔬 Test Efficacité' pour évaluer")
            response.append("4. Le RAG se reconstituera automatiquement")
            response.append("")
            response.append("💡 **Le RAG est maintenant propre et prêt à apprendre !**")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur réinitialisation RAG: {e}")

    def clean_custom_environments(self):
        """Nettoyer spécifiquement les environnements custom du RAG"""
        try:
            if not self.rag_manager or not self.rag_manager.collection:
                self.add_chat_message("error", "❌ RAG non disponible")
                return

            self.add_chat_message("system", "🧹 Nettoyage des environnements custom...")

            # Lister les environnements dans le RAG
            results = self.rag_manager.collection.get(
                limit=1000,
                include=["metadatas"]
            )

            if not results or not results.get('metadatas'):
                self.add_chat_message("system", "📭 Aucun document à nettoyer")
                return

            # Identifier les environnements custom (commençant par G11_, TEST_, etc.)
            custom_env_patterns = ['G11_', 'TEST_', 'CUSTOM_', 'DEV_']
            docs_to_delete = []
            env_counts = {}

            for i, metadata in enumerate(results['metadatas']):
                env_id = metadata.get('environment_id', '')

                # Vérifier si c'est un environnement custom
                is_custom = any(env_id.startswith(pattern) for pattern in custom_env_patterns)

                if is_custom:
                    docs_to_delete.append(results['ids'][i])
                    env_counts[env_id] = env_counts.get(env_id, 0) + 1

            if docs_to_delete:
                # Supprimer les documents custom
                try:
                    self.rag_manager.collection.delete(ids=docs_to_delete)

                    response = []
                    response.append("🧹 **NETTOYAGE ENVIRONNEMENTS CUSTOM**")
                    response.append("=" * 45)
                    response.append("")
                    response.append(f"✅ **{len(docs_to_delete)} documents supprimés**")
                    response.append("")
                    response.append("🗑️ **Environnements nettoyés:**")
                    for env_id, count in env_counts.items():
                        response.append(f"• {env_id}: {count} documents")
                    response.append("")
                    response.append("💡 **Les environnements de production sont conservés**")

                    self.add_chat_message("assistant", "\n".join(response))

                except Exception as e:
                    self.add_chat_message("error", f"❌ Erreur suppression: {e}")
            else:
                self.add_chat_message("system", "ℹ️ Aucun environnement custom trouvé à nettoyer")

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur nettoyage custom: {e}")

    def test_rag_efficiency(self):
        """Tester l'efficacité du RAG après réinitialisation"""
        try:
            if not self.rag_manager or not self.rag_manager.is_available():
                self.add_chat_message("error", "❌ RAG non disponible pour les tests")
                return

            self.add_chat_message("system", "🔬 Test d'efficacité du RAG en cours...")

            # 1. Statistiques de base
            stats = self.rag_manager.get_collection_stats()
            doc_count = stats.get('total_documents', 0)

            response = []
            response.append("🔬 **TEST D'EFFICACITÉ RAG**")
            response.append("=" * 35)
            response.append("")

            # 2. Évaluation quantitative
            response.append("📊 **Métriques quantitatives:**")
            response.append(f"• Documents indexés: {doc_count}")

            if doc_count == 0:
                response.append("❌ **État**: RAG vide")
                response.append("📝 **Action requise**: Générer des analyses")
            elif doc_count < 5:
                response.append("⚠️ **État**: RAG insuffisant")
                response.append("📈 **Recommandation**: Ajouter plus d'analyses")
            elif doc_count < 20:
                response.append("🟡 **État**: RAG fonctionnel")
                response.append("✅ **Recommandation**: Continuer à alimenter")
            else:
                response.append("✅ **État**: RAG optimal")
                response.append("🎯 **Qualité**: Prêt pour assistance")

            response.append("")

            # 3. Test de recherche si possible
            if doc_count > 0:
                response.append("🔍 **Test de recherche:**")
                try:
                    test_queries = [
                        "erreur PyTorch",
                        "CUDA problème",
                        "serveur status"
                    ]

                    for query in test_queries:
                        results = self.rag_manager.search_similar_issues(query, limit=2)
                        response.append(f"• '{query}': {len(results)} résultats")

                    response.append("✅ **Recherche**: Fonctionnelle")

                except Exception as search_error:
                    response.append(f"❌ **Erreur recherche**: {search_error}")

            # 4. Test temporel si disponible
            if self.temporal_rag and doc_count > 0:
                response.append("")
                response.append("🕒 **Test temporel:**")
                try:
                    distribution = self.temporal_rag.get_temporal_distribution()
                    if "error" not in distribution:
                        recent_pct = distribution.get('percentage_recent_24h', 0)
                        response.append(f"• Analyses récentes: {recent_pct}%")

                        if recent_pct > 50:
                            response.append("✅ **Fraîcheur**: Excellente")
                        elif recent_pct > 20:
                            response.append("🟡 **Fraîcheur**: Correcte")
                        else:
                            response.append("⚠️ **Fraîcheur**: Faible")
                    else:
                        response.append("❌ **Temporel**: Non fonctionnel")

                except Exception as temporal_error:
                    response.append(f"❌ **Erreur temporel**: {temporal_error}")

            # 5. Recommandations finales
            response.append("")
            response.append("💡 **Recommandations:**")

            if doc_count == 0:
                response.append("1. 🚀 Démarrer ComfyUI")
                response.append("2. 📝 Générer 5-10 analyses Mistral")
                response.append("3. 🔄 Relancer ce test")
            elif doc_count < 10:
                response.append("1. 📈 Continuer à générer des analyses")
                response.append("2. 🎯 Varier les types d'erreurs/succès")
                response.append("3. ⏰ Attendre quelques jours d'utilisation")
            else:
                response.append("1. ✅ RAG opérationnel")
                response.append("2. 🔥 Utiliser 'État actuel' pour tester")
                response.append("3. 💬 Poser des questions au chat")

            response.append("")
            response.append("🎯 **Le RAG est maintenant évalué et prêt !**")

            self.add_chat_message("assistant", "\n".join(response))

        except Exception as e:
            self.add_chat_message("error", f"❌ Erreur test efficacité: {e}")

    # ===== MÉTHODES DE TEST RAG =====

    def run_rag_test_suite(self):
        """Lancer la suite complète de tests RAG"""
        if not self.rag_tester:
            self.add_chat_message("error", "❌ Testeur RAG non disponible")
            return

        # VALIDATION CRITIQUE: Vérifier qu'un environnement est identifié (comme dans le chat)
        print(f"🔍 DEBUG BOUTON: Vérification environnement - current_environment_id = '{self.current_environment_id}'")
        print(f"🔍 DEBUG BOUTON: Type = {type(self.current_environment_id)}")
        print(f"🔍 DEBUG BOUTON: Booléen = {bool(self.current_environment_id)}")

        if not self.current_environment_id:
            print("❌ DEBUG BOUTON: Condition 'not self.current_environment_id' = True")
            self.add_chat_message(
                "system",
                "❌ ERREUR CRITIQUE: Aucun environnement ComfyUI identifié !\n\n"
                "Le système RAG nécessite un environnement identifié pour fonctionner.\n"
                "🔍 Allez dans l'onglet ComfyUI et cliquez sur 'Identifier l'environnement'."
            )
            return
        else:
            print(f"✅ DEBUG BOUTON: Environnement OK = '{self.current_environment_id}'")

        # Synchroniser le RAG Manager avec l'environnement actuel
        if hasattr(self, 'rag_manager') and self.rag_manager:
            if self.rag_manager.environment_id != self.current_environment_id:
                print(f"🔄 Mise à jour RAG bouton: {self.rag_manager.environment_id} -> {self.current_environment_id}")
                self.rag_manager.environment_id = self.current_environment_id
                self.rag_manager._initialize_components()
                self.add_chat_message("system", f"🔄 RAG synchronisé avec l'environnement: {self.current_environment_id}")

        self.add_chat_message("system", "🧪 Lancement de la suite complète de tests RAG...")

        # DEBUG: Vérifier l'état avant les tests
        debug_info = []
        debug_info.append(f"🔍 Current environment ID: {self.current_environment_id}")
        if hasattr(self, 'rag_manager') and self.rag_manager:
            debug_info.append(f"🧠 RAG Manager environment: {self.rag_manager.environment_id}")
            debug_info.append(f"📊 RAG disponible: {self.rag_manager.is_available()}")
        if hasattr(self, 'rag_tester') and self.rag_tester:
            debug_info.append(f"🧪 RAG Tester environment: {self.rag_tester.environment_id}")

        print("🔍 DEBUG TESTS RAG:")
        for info in debug_info:
            print(f"   {info}")

        def run_tests():
            print("🧪 Thread de test démarré...")
            try:
                print(f"   📍 Environment ID: {self.current_environment_id}")
                print(f"   🧠 RAG Manager disponible: {bool(self.rag_manager)}")
                print(f"   🧪 RAG Tester disponible: {bool(self.rag_tester)}")

                print("   ⏳ Appel de run_complete_test_suite()...")
                results = self.rag_tester.run_complete_test_suite()

                print(f"   ✅ Tests terminés, résultats reçus: {bool(results)}")
                if results:
                    print(f"      Keys: {list(results.keys())}")

                # Afficher les résultats dans le chat (thread-safe)
                print("   📤 Programmation de l'affichage des résultats...")
                self.root.after(0, lambda: self.display_test_results(results))

            except Exception as e:
                print(f"   ❌ Exception dans run_tests: {e}")
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: self.add_chat_message("error", f"❌ Erreur lors des tests: {e}"))

        # Lancer les tests en arrière-plan
        threading.Thread(target=run_tests, daemon=True).start()

    def run_quick_rag_test(self):
        """Lancer un test rapide du RAG"""
        if not self.rag_tester:
            self.add_chat_message("error", "❌ Testeur RAG non disponible")
            return

        # VALIDATION: Vérifier l'environnement (même que le test complet)
        if not self.current_environment_id:
            self.add_chat_message(
                "system",
                "❌ ERREUR CRITIQUE: Aucun environnement ComfyUI identifié !\n\n"
                "Le système RAG nécessite un environnement identifié pour fonctionner.\n"
                "🔍 Allez dans l'onglet ComfyUI et cliquez sur 'Identifier l'environnement'."
            )
            return

        # Synchroniser le RAG Manager
        if hasattr(self, 'rag_manager') and self.rag_manager:
            if self.rag_manager.environment_id != self.current_environment_id:
                self.rag_manager.environment_id = self.current_environment_id
                self.rag_manager._initialize_components()

        self.add_chat_message("system", "⚡ Lancement du test rapide RAG...")

        def run_test():
            print("⚡ Thread de test rapide démarré...")
            try:
                print(f"   📍 Environment ID: {self.current_environment_id}")
                print(f"   🧠 RAG Manager disponible: {bool(self.rag_manager)}")
                print(f"   🧪 RAG Tester disponible: {bool(self.rag_tester)}")

                print("   ⏳ Appel de run_quick_test()...")
                results = self.rag_tester.run_quick_test()

                print(f"   ✅ Test rapide terminé, résultats reçus: {bool(results)}")
                if results:
                    print(f"      Keys: {list(results.keys())}")

                # Afficher les résultats dans le chat (thread-safe)
                print("   📤 Programmation de l'affichage des résultats...")
                self.root.after(0, lambda: self.display_quick_test_results(results))

            except Exception as e:
                print(f"   ❌ Exception dans run_test: {e}")
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: self.add_chat_message("error", f"❌ Erreur lors du test rapide: {e}"))

        # Lancer le test en arrière-plan
        threading.Thread(target=run_test, daemon=True).start()

    def handle_rag_test_command(self, command: str):
        """Gérer les commandes de test RAG depuis le chat"""
        parts = command.split()

        if len(parts) == 1:
            # /test-rag simple
            self.run_rag_test_suite()
        elif len(parts) == 2:
            test_type = parts[1].lower()
            if test_type == "quick":
                self.run_quick_rag_test()
            elif test_type == "indexing":
                self.test_rag_indexing()
            elif test_type == "learning":
                self.test_rag_learning()
            elif test_type == "performance":
                self.test_rag_performance()
            else:
                self.add_chat_message("error", f"❌ Type de test inconnu: {test_type}")
                self.show_test_help()
        else:
            self.show_test_help()

    def handle_quick_test_command(self):
        """Gérer la commande /quick-test"""
        self.run_quick_rag_test()

    def test_rag_indexing(self):
        """Tester spécifiquement l'indexation RAG"""
        if not self.rag_tester:
            self.add_chat_message("error", "❌ Testeur RAG non disponible")
            return

        self.add_chat_message("system", "📚 Test de l'indexation RAG...")

        def run_test():
            try:
                result = self.rag_tester._test_new_data_indexing()
                message = f"📚 **Test d'indexation:** {'✅ Réussi' if result.get('status') == 'success' else '❌ Échoué'}\n"
                message += f"📊 Documents indexés: {result.get('documents_after', 0) - result.get('documents_before', 0)}\n"
                message += f"🔍 Recherche fonctionnelle: {'Oui' if result.get('immediate_search_found') else 'Non'}"

                self.root.after(0, lambda: self.add_chat_message("assistant", message))

            except Exception as e:
                self.root.after(0, lambda: self.add_chat_message("error", f"❌ Erreur test indexation: {e}"))

        threading.Thread(target=run_test, daemon=True).start()

    def test_rag_learning(self):
        """Tester spécifiquement l'apprentissage RAG"""
        if not self.rag_tester:
            self.add_chat_message("error", "❌ Testeur RAG non disponible")
            return

        self.add_chat_message("system", "🧠 Test de l'apprentissage RAG...")

        def run_test():
            try:
                result = self.rag_tester._test_chat_learning()
                message = f"🧠 **Test d'apprentissage:** {'✅ Réussi' if result.get('status') == 'success' else '❌ Échoué'}\n"
                message += f"💬 Conversations testées: {result.get('conversations_tested', 0)}\n"
                message += f"🎯 Mémorisation: {'Bonne' if result.get('memory_working') else 'Problématique'}"

                self.root.after(0, lambda: self.add_chat_message("assistant", message))

            except Exception as e:
                self.root.after(0, lambda: self.add_chat_message("error", f"❌ Erreur test apprentissage: {e}"))

        threading.Thread(target=run_test, daemon=True).start()

    def test_rag_performance(self):
        """Tester spécifiquement les performances RAG"""
        if not self.rag_tester:
            self.add_chat_message("error", "❌ Testeur RAG non disponible")
            return

        self.add_chat_message("system", "⚡ Test des performances RAG...")

        def run_test():
            try:
                result = self.rag_tester._test_performance()
                message = f"⚡ **Test de performance:** {'✅ Bon' if result.get('status') == 'success' else '❌ Dégradé'}\n"
                message += f"🕒 Temps de recherche: {result.get('avg_search_time', 0):.2f}s\n"
                message += f"📊 Qualité des résultats: {result.get('result_quality', 'Inconnue')}"

                self.root.after(0, lambda: self.add_chat_message("assistant", message))

            except Exception as e:
                self.root.after(0, lambda: self.add_chat_message("error", f"❌ Erreur test performance: {e}"))

        threading.Thread(target=run_test, daemon=True).start()

    def display_test_results(self, results: dict):
        """Afficher les résultats complets des tests dans le chat"""
        print(f"🖥️ DEBUG display_test_results appelé avec: {type(results)}")
        print(f"   Keys disponibles: {results.keys() if results else 'None'}")

        if not results:
            self.add_chat_message("error", "❌ Aucun résultat de test reçu")
            return

        # En-tête avec environnement
        env_id = results.get('environment_id', 'inconnu')
        message = f"🧪 **RÉSULTATS COMPLETS DES TESTS RAG**\n"
        message += f"🏷️  Environnement: `{env_id}`\n\n"

        # Résumé global (nouvelle structure)
        summary = results.get('summary', {})
        if summary:
            success_rate = summary.get('success_rate_percent', 0)
            overall_rating = summary.get('overall_rating', 'unknown')

            # Emoji de statut basé sur l'évaluation
            rating_emoji = {
                'excellent': '✅',
                'good': '👍',
                'fair': '⚠️',
                'poor': '❌'
            }.get(overall_rating, '❓')

            message += f"📊 **Score global:** {success_rate}% {rating_emoji}\n"
            message += f"🏆 **Évaluation:** {overall_rating.title()}\n\n"

            # Stats détaillées
            total = summary.get('total_tests', 0)
            success = summary.get('successful_tests', 0)
            errors = summary.get('error_tests', 0)
            skipped = summary.get('skipped_tests', 0)

            message += f"� **Statistiques:**\n"
            message += f"   • Total: {total} tests\n"
            message += f"   • Réussis: {success} ✅\n"
            if errors > 0:
                message += f"   • Erreurs: {errors} ❌\n"
            if skipped > 0:
                message += f"   • Ignorés: {skipped} ⏭️\n"
            message += "\n"

        # Détail par test
        tests = results.get('tests', {})
        if tests:
            message += "📋 **Détail des tests:**\n"
            for test_name, test_result in tests.items():
                status = test_result.get('status', 'unknown')
                emoji = {
                    'success': '✅',
                    'error': '❌',
                    'skipped': '⏭️'
                }.get(status, '❓')

                test_label = test_name.replace('_', ' ').title()
                message += f"{emoji} {test_label}\n"

                # Informations spécifiques selon le test
                if status == 'success':
                    if test_name == 'initial_state':
                        doc_count = test_result.get('document_count', 0)
                        message += f"   � {doc_count} documents indexés\n"
                    elif test_name == 'new_data_indexing':
                        indexed = test_result.get('indexing_successful', False)
                        found = test_result.get('immediate_search_found', False)
                        if indexed and found:
                            message += f"   ✅ Indexation et recherche fonctionnelles\n"
                    elif test_name == 'performance':
                        avg_time = test_result.get('avg_search_time', 0)
                        rating = test_result.get('performance_rating', 'unknown')
                        message += f"   ⚡ Temps moyen: {avg_time:.3f}s ({rating})\n"

                elif status == 'error':
                    error = test_result.get('error', 'Erreur inconnue')
                    message += f"   ⚠️ {error[:100]}\n"

            message += "\n"

        # Recommandations
        recommendations = summary.get('recommendations', []) if summary else []
        if recommendations:
            message += "💡 **Recommandations:**\n"
            for rec in recommendations:
                message += f"{rec}\n"
            message += "\n"

        # Date du test
        test_date = results.get('test_date', '')
        if test_date:
            message += f"🕐 Test effectué: {test_date}\n"

        print(f"📤 Envoi du message de résultats ({len(message)} caractères)")
        self.add_chat_message("assistant", message)

    def display_quick_test_results(self, results: dict):
        """Afficher les résultats du test rapide dans le chat"""
        print(f"🖥️ DEBUG display_quick_test_results appelé avec: {type(results)}")
        print(f"   Keys disponibles: {results.keys() if results else 'None'}")

        if not results:
            self.add_chat_message("error", "❌ Aucun résultat de test rapide reçu")
            return

        success = results.get('success', False)
        status_emoji = "✅" if success else "❌"
        status_text = "Fonctionnel" if success else "Problème détecté"

        message = f"⚡ **TEST RAPIDE RAG:** {status_emoji} {status_text}\n\n"

        # Vérifications
        indexing = results.get('indexing_works')
        search = results.get('search_works')
        performance = results.get('performance_ok')

        message += "**Vérifications:**\n"

        if indexing is not None:
            emoji = "✅" if indexing else "❌"
            message += f"{emoji} Indexation: {'OK' if indexing else 'Échec'}\n"

        if search is not None:
            emoji = "✅" if search else "❌"
            message += f"{emoji} Recherche: {'OK' if search else 'Échec'}\n"

        if performance is not None:
            emoji = "✅" if performance else "⚠️"
            message += f"{emoji} Performance: {'Acceptable' if performance else 'Dégradée'}\n"

        # Durée du test
        duration = results.get('test_duration')
        if duration:
            message += f"\n⏱️ Durée: {duration}s\n"

        # Détails supplémentaires
        details = results.get('details')
        if details:
            message += f"\n📝 {details}\n"

        # Erreur si présente
        error = results.get('error')
        if error:
            message += f"\n❌ **Erreur:** {error}\n"

        # Timestamp
        timestamp = results.get('timestamp')
        if timestamp:
            message += f"\n� Test effectué: {timestamp}\n"

        print(f"📤 Envoi du message de test rapide ({len(message)} caractères)")
        self.add_chat_message("assistant", message)

    def show_test_help(self):
        """Afficher l'aide pour les commandes de test"""
        help_message = """🧪 **COMMANDES DE TEST RAG DISPONIBLES:**

**Commandes principales:**
• `/test-rag` - Suite complète de tests
• `/quick-test` - Test rapide de fonctionnement

**Tests spécifiques:**
• `/test-rag indexing` - Test de l'indexation
• `/test-rag learning` - Test de l'apprentissage
• `/test-rag performance` - Test des performances

**Boutons interface:**
• 🧪 Test RAG - Lance la suite complète
• ⚡ Test rapide - Vérification basique

Les tests vérifient que le RAG apprend correctement de vos échanges et des nouveaux logs indexés."""

        self.add_chat_message("system", help_message)

    # ===== FIN MÉTHODES TERMINAL =====


# === CLASSE POUR LES DIALOGUES D'ENVIRONNEMENT ===

class EnvironmentDialog:
    """Dialogue pour ajouter/modifier un environnement ComfyUI"""

    def __init__(self, parent, title, current_data=None):
        self.result = None

        # Créer la fenêtre de dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)

        # Centrer la fenêtre
        self.dialog.transient(parent)
        self.dialog.grab_set()
        center_window(self.dialog, 500, 300)

        # Variables pour les champs
        self.env_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.path_var = tk.StringVar()

        # Si modification, préremplir avec les données actuelles
        if current_data:
            self.env_id_var.set(current_data[0])
            self.name_var.set(current_data[1])
            self.path_var.set(current_data[2])

        self.setup_ui()

        # Focus sur le premier champ
        self.env_id_entry.focus()

        # Raccourcis clavier
        self.dialog.bind('<Return>', lambda e: self.validate_and_save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())

    def setup_ui(self):
        """Configuration de l'interface du dialogue"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Titre
        title_label = ttk.Label(
            main_frame,
            text="Configuration de l'environnement ComfyUI",
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Formulaire
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x", pady=(0, 20))

        # ID de l'environnement
        ttk.Label(form_frame, text="ID de l'environnement:").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        self.env_id_entry = ttk.Entry(
            form_frame, textvariable=self.env_id_var, width=40
        )
        self.env_id_entry.grid(row=0, column=1, sticky="ew", pady=(0, 10), padx=(10, 0))

        ttk.Label(form_frame, text="(ex: comfyui_main, comfyui_dev)",
                 foreground="gray").grid(
            row=1, column=1, sticky="w", padx=(10, 0), pady=(0, 10)
        )

        # Nom de l'environnement
        ttk.Label(form_frame, text="Nom d'affichage:").grid(
            row=2, column=0, sticky="w", pady=(0, 10)
        )
        self.name_entry = ttk.Entry(
            form_frame, textvariable=self.name_var, width=40
        )
        self.name_entry.grid(row=2, column=1, sticky="ew", pady=(0, 10), padx=(10, 0))

        ttk.Label(form_frame, text="(ex: ComfyUI Principal, ComfyUI Développement)",
                 foreground="gray").grid(
            row=3, column=1, sticky="w", padx=(10, 0), pady=(0, 10)
        )

        # Chemin du répertoire
        ttk.Label(form_frame, text="Répertoire ComfyUI:").grid(
            row=4, column=0, sticky="w", pady=(0, 10)
        )

        path_frame = ttk.Frame(form_frame)
        path_frame.grid(row=4, column=1, sticky="ew", pady=(0, 10), padx=(10, 0))

        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=35)
        self.path_entry.pack(side="left", fill="x", expand=True)

        ttk.Button(
            path_frame, text="Parcourir...", command=self.browse_folder, width=12
        ).pack(side="right", padx=(5, 0))

        ttk.Label(form_frame, text="(Répertoire racine de ComfyUI)",
                 foreground="gray").grid(
            row=5, column=1, sticky="w", padx=(10, 0), pady=(0, 20)
        )

        # Configuration des colonnes
        form_frame.columnconfigure(1, weight=1)

        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x")

        ttk.Button(
            buttons_frame, text="Annuler", command=self.cancel
        ).pack(side="right", padx=(10, 0))

        ttk.Button(
            buttons_frame, text="Valider", command=self.validate_and_save
        ).pack(side="right")

    def browse_folder(self):
        """Ouvrir un dialogue de sélection de dossier"""
        from tkinter import filedialog

        folder = filedialog.askdirectory(
            title="Sélectionner le répertoire ComfyUI",
            initialdir=self.path_var.get() if self.path_var.get() else "C:\\"
        )

        if folder:
            self.path_var.set(folder)

    def validate_and_save(self):
        """Valider les données et sauvegarder"""
        env_id = self.env_id_var.get().strip()
        name = self.name_var.get().strip()
        path = self.path_var.get().strip()

        # Validation
        if not env_id:
            messagebox.showerror("Erreur", "L'ID de l'environnement est obligatoire.")
            return

        if not name:
            messagebox.showerror("Erreur", "Le nom d'affichage est obligatoire.")
            return

        if not path:
            messagebox.showerror("Erreur", "Le répertoire ComfyUI est obligatoire.")
            return

        # Vérifier que le répertoire existe
        if not os.path.exists(path):
            response = messagebox.askyesno(
                "Répertoire inexistant",
                f"Le répertoire '{path}' n'existe pas.\n\n"
                "Voulez-vous continuer quand même ?"
            )
            if not response:
                return

        # Validation de l'ID (pas d'espaces, caractères spéciaux limités)
        import re
        if not re.match(r'^[A-Za-z0-9_-]+$', env_id):
            messagebox.showerror(
                "ID invalide",
                "L'ID ne peut contenir que des lettres, chiffres, tirets et underscores."
            )
            return

        # Créer le résultat sous forme de dictionnaire
        self.result = {
            "id": env_id,
            "name": name,
            "path": path
        }

        print(f"✅ DEBUG EnvironmentDialog: Validation réussie")
        print(f"   self.result = {self.result}")
        print(f"   Type: {type(self.result)}")

        self.dialog.destroy()

    def _save_identified_environment(self, environment_info: dict):
        """Sauvegarder automatiquement l'environnement identifié"""
        try:
            if not environment_info or not environment_info.get("environment_id"):
                return

            env_id = environment_info["environment_id"]

            # Créer un nom d'affichage intelligent
            display_name = f"ComfyUI {env_id}"

            # Déterminer le chemin le plus probable
            comfyui_path = "/"  # Par défaut
            if environment_info.get("potential_paths"):
                for path in environment_info["potential_paths"]:
                    if "comfyui" in path.lower() and os.path.exists(path):
                        comfyui_path = path
                        break

            # Vérifier si l'environnement existe déjà
            existing_envs = self.db_manager.get_all_environments()
            for env in existing_envs:
                if env[1] == env_id:  # ID existe déjà
                    print(f"📝 Environnement {env_id} existe déjà, mise à jour...")
                    return

            # Ajouter le nouvel environnement
            success = self.db_manager.add_environment(env_id, display_name, comfyui_path)
            if success:
                print(f"💾 Environnement {env_id} sauvegardé automatiquement")
                # Rafraîchir l'affichage des environnements
                if hasattr(self, 'refresh_environments'):
                    self.refresh_environments()
            else:
                print(f"⚠️ Échec de la sauvegarde automatique de {env_id}")

        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde automatique: {e}")


        # Validation de l'ID (pas d'espaces, caractères spéciaux limités)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', env_id):
            messagebox.showerror(
                "Erreur",
                "L'ID ne peut contenir que des lettres, chiffres, tirets et underscores."
            )
            return

        # Tout est valide
        self.result = (env_id, name, path)
        self.dialog.destroy()

    def cancel(self):
        """Annuler le dialogue"""
        self.dialog.destroy()


def main():
    """Point d'entrée principal"""
    app = cy8_prompts_manager()
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.run()


if __name__ == "__main__":
    main()

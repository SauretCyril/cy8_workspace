import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import json
import subprocess
from datetime import datetime
from PIL import Image, ImageTk

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

        # Gestionnaire d'index d'images optimisé
        self.image_index = ImageIndexManager()
        self.fast_processor = get_image_processor()
        print(
            f"🖼️ Processeur d'images: {self.fast_processor.get_performance_info()['backend']}"
        )

        # Connecter le callback de sauvegarde
        self.table_manager.set_save_callback(self.save_current_info)

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

        # Initialiser le tableau des environnements après la création de l'interface
        self.root.after(100, self.refresh_environments)

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
        Colonnes: ID, Name, Status, Model, Comment, Parent
        """
        table_frame = ttk.LabelFrame(parent, text="Liste des Prompts", padding="5")
        table_frame.pack(fill="both", expand=True)

        # Treeview pour les prompts
        columns = ("id", "name", "status", "model", "comment", "parent")
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

        self.prompts_tree.column("id", width=50)
        self.prompts_tree.column("name", width=200)
        self.prompts_tree.column("status", width=80)
        self.prompts_tree.column("model", width=150)
        self.prompts_tree.column("comment", width=200)
        self.prompts_tree.column("parent", width=60)

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
        default_log_path = os.getenv(
            "COMFYUI_FILE_LOG", "E:/Comfyui_G11/ComfyUI/user/comfyui.log"
        )
        self.comfyui_log_path = tk.StringVar(value=default_log_path)
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

        # === SECTION 1.5: CONFIGURATION DES SOLUTIONS D'ERREURS ===
        solutions_config_frame = ttk.LabelFrame(
            log_frame, text="🤖 Configuration des solutions IA", padding="10"
        )
        solutions_config_frame.pack(fill="x", pady=(0, 15))

        # Ligne de configuration du répertoire
        solutions_dir_frame = ttk.Frame(solutions_config_frame)
        solutions_dir_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(solutions_dir_frame, text="Répertoire des solutions:", width=20).pack(
            side="left"
        )

        # Variable pour le répertoire des solutions
        self.error_solutions_dir = tk.StringVar()
        self.error_solutions_dir.set(self.user_prefs.get_error_solutions_directory())

        solutions_dir_entry = ttk.Entry(
            solutions_dir_frame, textvariable=self.error_solutions_dir, width=50
        )
        solutions_dir_entry.pack(side="left", padx=(10, 5), fill="x", expand=True)

        ttk.Button(
            solutions_dir_frame,
            text="📁 Parcourir",
            command=self.browse_solutions_directory,
            width=12,
        ).pack(side="right")

        # Info sur les solutions
        solutions_info_frame = ttk.Frame(solutions_config_frame)
        solutions_info_frame.pack(fill="x")

        ttk.Label(
            solutions_info_frame,
            text="💡 Double-cliquez sur une erreur pour obtenir une solution IA. Les solutions sont sauvegardées.",
            font=("TkDefaultFont", 8),
            foreground="gray",
        ).pack(anchor="w")

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

        # Boutons d'actions pour les environnements
        env_actions_frame = ttk.Frame(environments_frame)
        env_actions_frame.pack(fill="x")

        ttk.Button(
            env_actions_frame,
            text="🔄 Actualiser environnements",
            command=self.refresh_environments,
            width=25,
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
            stats_window.update_idletasks()
            x = (stats_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (stats_window.winfo_screenheight() // 2) - (400 // 2)
            stats_window.geometry(f"500x400+{x}+{y}")

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
            for prompt_id, name, parent, model, workflow, status, comment in prompts:
                self.prompts_tree.insert(
                    "",
                    "end",
                    iid=str(prompt_id),
                    values=(prompt_id, name, status, model, comment, parent or ""),
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
                name, prompt_values, workflow, url, parent, model, comment, status = (
                    data
                )

                # Mettre à jour les informations générales
                self.name_var.set(name or "")
                self.url_var.set(url or "")
                self.comment_var.set(comment or "")
                self.model_var.set(model or "")
                self.status_var.set(status or "new")

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

            name, prompt_values, workflow, url, parent, model, comment, status = data

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

            name, prompt_values, workflow, url, parent, model, comment, status = data

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

            name, prompt_values_json, workflow_json, url, model, comment, status = data

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
                name, prompt_values, workflow, url, model, comment, _ = data

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
                name, prompt_values, workflow, url, parent, model, comment, status = (
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
                messagebox.showwarning(
                    "Dossier introuvable",
                    f"Le dossier d'images n'existe pas:\n{images_path}",
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
            for _, _, _, _, _, status, _ in prompts:
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
        """Exporter des données JSON"""
        messagebox.showinfo("Export", "Fonctionnalité d'export à implémenter")

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
        filter_types = ["Statut d'exécution", "Modèle", "Hiérarchie", "Nom", "Statut"]
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
            # prompt est un tuple: (id, name, parent, model, workflow, status, comment) - format get_all_prompts
            prompt_id, name, parent, model, workflow, status, comment = prompt

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
            prompt_id, name, parent, model, workflow, status, comment = prompt

            # Format des valeurs pour l'affichage (même format que load_prompts)
            display_values = (
                prompt_id,
                name or "",
                status or "new",
                model or "",
                comment or "",
                parent or "",
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
        """Identifier l'environnement ComfyUI en récupérant les extra paths via le custom node"""
        import logging
        import time

        # Configuration du logging pour cette fonction
        logger = logging.getLogger(__name__)

        print("\n" + "=" * 60)
        print("🚀 DÉBUT - Identification de l'environnement ComfyUI")
        print("=" * 60)
        logger.info("Début de l'identification de l'environnement ComfyUI")

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
                        text="⏳ Exécution du custom node en cours...",
                        foreground="orange",
                    )
                    self.root.update()

                    # Récupération des extra paths depuis ComfyUI via le custom node
                    print("📂 Récupération des extra paths...")
                    logger.info("Début de récupération des extra paths")
                    extra_paths_data = self._get_extra_paths_from_comfyui()

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

    def _get_extra_paths_from_comfyui(self):
        """Récupérer les extra paths depuis ComfyUI (méthode temporaire)"""
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Pour l'instant, on lit directement le fichier de configuration
            import os
            import yaml

            print("  📁 Recherche du fichier extra_model_paths.yaml...")
            logger.info(
                "Début de recherche du fichier de configuration extra_model_paths.yaml"
            )

            config_path = os.path.expanduser("~/.config/ComfyUI/extra_model_paths.yaml")
            print(f"  🔍 Vérification: {config_path}")

            if os.path.exists(config_path):
                print(f"  ✅ Fichier trouvé: {config_path}")
                logger.info(f"Fichier de configuration trouvé: {config_path}")

                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                print(
                    f"  ✅ Configuration chargée: {len(config) if config else 0} entrées"
                )
                logger.info(
                    f"Configuration chargée avec {len(config) if config else 0} entrées"
                )
                return config
            else:
                print("  ❌ Fichier non trouvé à l'emplacement standard")
                logger.info(
                    "Fichier non trouvé à l'emplacement standard, recherche dans d'autres emplacements"
                )

                # Essayer d'autres emplacements possibles
                possible_paths = [
                    os.path.expanduser("~/ComfyUI/extra_model_paths.yaml"),
                    "E:/Comfyui_G11/ComfyUI/extra_model_paths.yaml",
                    "C:/ComfyUI/extra_model_paths.yaml",
                ]

                for path in possible_paths:
                    print(f"  🔍 Vérification: {path}")
                    if os.path.exists(path):
                        print(f"  ✅ Fichier trouvé: {path}")
                        logger.info(f"Fichier de configuration trouvé: {path}")

                        with open(path, "r", encoding="utf-8") as f:
                            config = yaml.safe_load(f)

                        print(
                            f"  ✅ Configuration chargée: {len(config) if config else 0} entrées"
                        )
                        logger.info(
                            f"Configuration chargée avec {len(config) if config else 0} entrées"
                        )

                        # Retourner dans le format attendu par _extract_config_id_from_extra_paths
                        result = {
                            "comfyui_root": os.path.dirname(
                                path
                            ),  # Racine du ComfyUI trouvé
                            "config_path": path,
                            "extra_paths": config,
                        }
                        print(
                            f"  📋 Format de retour: comfyui_root={result['comfyui_root']}"
                        )
                        logger.info(
                            f"Données formatées avec comfyui_root: {result['comfyui_root']}"
                        )
                        return result

                print("  ❌ Aucun fichier de configuration trouvé")
                logger.warning(
                    "Aucun fichier de configuration extra_model_paths.yaml trouvé"
                )
                return None

        except Exception as e:
            print(f"  ❌ Erreur lors de la lecture: {e}")
            logger.error(f"Erreur lors de la lecture du fichier de configuration: {e}")
            return None

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

    def browse_solutions_directory(self):
        """Ouvrir un dialogue pour sélectionner le répertoire des solutions"""
        from tkinter import filedialog

        initial_dir = self.error_solutions_dir.get() or "g:/temp"

        directory = filedialog.askdirectory(
            title="Sélectionner le répertoire pour les solutions d'erreurs",
            initialdir=initial_dir,
        )

        if directory:
            self.error_solutions_dir.set(directory)
            # Sauvegarder dans les préférences
            self.user_prefs.set_error_solutions_directory(directory)
            messagebox.showinfo(
                "Configuration", f"Répertoire des solutions mis à jour :\n{directory}"
            )

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
        self.current_environment_id = environment_id
        print(f"🌍 Environnement identifié: {environment_id}")

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
            # Effacer le tableau
            for item in self.environments_tree.get_children():
                self.environments_tree.delete(item)

            # Récupérer les environnements depuis la base
            environments = self.db_manager.get_all_environments()

            for env in environments:
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
                self.environments_tree.insert(
                    "", "end", values=(env_id, name, path, last_analysis_str, status)
                )

            print(
                f"Tableau des environnements actualisé : {len(environments)} environnements"
            )

        except Exception as e:
            print(f"Erreur lors de l'actualisation des environnements : {e}")
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

        # Charger les résultats d'analyse pour cet environnement
        self.load_environment_analysis_results(environment_id)

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
                        # Gestion silencieuse des données legacy ou corrompues
                        # Essayer d'extraire quelques informations du message direct
                        if " | " in message:
                            parts = message.split(" | ", 1)
                            if len(parts) > 1:
                                display_message = parts[0]
                                details_info = parts[1]

                        # Debug uniquement si les détails ne sont pas vides
                        if details and details.strip():
                            print(f"⚠️ Données legacy détectées pour résultat {result_id} (format JSON attendu)")
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
                solutions_dir = self.error_solutions_dir.get()
                # Créer le dossier s'il n'existe pas
                os.makedirs(solutions_dir, exist_ok=True)
                print(f"📁 Ouverture du répertoire global: {solutions_dir}")

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

        except Exception as e:
            messagebox.showerror(
                "Erreur de sauvegarde",
                f"Impossible de sauvegarder l'analyse :\n{str(e)}",
            )


def main():
    """Point d'entrée principal"""
    app = cy8_prompts_manager()
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.run()


if __name__ == "__main__":
    main()

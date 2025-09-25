#!/usr/bin/env python3
"""
Exemple d'utilisation des préférences utilisateur cy8
"""

# Exemples tirés du code cy8_prompts_manager_main.py

# 1. LECTURE de préférences au démarrage
def init_images_paths(self):
    # Charger depuis les préférences
    saved_main_path = self.user_prefs.get_preference("images_collecte_path")
    saved_trash_path = self.user_prefs.get_preference("images_trash_path")
    saved_central_path = self.user_prefs.get_preference("images_central_path")

    # Utiliser valeur par défaut si pas trouvée
    main_path = saved_main_path or os.getenv("IMAGES_COLLECTE") or default_images_dir

# 2. ÉCRITURE de préférences lors de changements
def apply_images_paths(self):
    # Sauvegarder les nouveaux chemins
    self.user_prefs.set_preference("images_collecte_path", self.images_path_var.get())
    self.user_prefs.set_preference("images_trash_path", self.temp_path_var.get())
    self.user_prefs.set_preference("images_central_path", self.central_path_var.get())

# 3. Gestion de la base de données actuelle
def change_database(self):
    if nouveau_chemin:
        # Sauvegarder automatiquement comme dernière base utilisée
        self.user_prefs.set_last_database_path(nouveau_chemin)

# 4. Géométrie de fenêtre
def on_closing(self):
    # Sauvegarder la position/taille de la fenêtre
    geometry = self.root.geometry()
    self.user_prefs.set_window_geometry(geometry)

# 5. ACCÈS depuis l'interface utilisateur
def ouvrir_preferences_dialog(self):
    """Exemple de dialogue de préférences"""

    # Lire les préférences actuelles
    theme = self.user_prefs.get_preference("theme", "dark")
    language = self.user_prefs.get_preference("language", "fr")
    auto_save = self.user_prefs.get_preference("auto_save", True)

    # Interface pour modifier
    # ... code GUI ...

    # Sauvegarder les modifications
    if user_clicked_ok:
        self.user_prefs.set_preference("theme", nouveau_theme)
        self.user_prefs.set_preference("language", nouvelle_langue)
        self.user_prefs.set_preference("auto_save", nouveau_auto_save)

# 6. Informations sur les préférences
def debug_preferences(self):
    info = self.user_prefs.get_preferences_info()
    print(f"Répertoire: {info['preferences_dir']}")
    print(f"Fichier préfs: {info['preferences_file']}")
    print(f"Fichier cookies: {info['cookies_file']}")
    print(f"Nombre bases récentes: {info['recent_databases_count']}")

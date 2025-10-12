import os
import sqlite3
import json
from datetime import datetime
from cy8_paths import normalize_path, ensure_dir, get_default_db_path


class cy8_database_manager:
    """Gestionnaire de base de données pour les prompts - Version cy8"""

    def __init__(self, db_path=None):
        # Utiliser le chemin par défaut si aucun chemin n'est fourni
        if db_path is None:
            db_path = get_default_db_path()

        # Normaliser et s'assurer que le répertoire existe
        self.db_path = normalize_path(db_path)
        ensure_dir(self.db_path)
        self.conn = None
        self.cursor = None
        self.status_options = ("new", "test", "ok", "nok")

    def init_database(self, mode="init"):
        """
        Initialise la base de données
        mode="init" : Recrée la base et ajoute le prompt par défaut
        mode="dev"  : Crée la base si elle n'existe pas, n'ajoute pas le prompt par défaut
        """
        if mode == "init":
            # Mode init: Supprime la base existante et recrée
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    prompt_values JSON,
                    workflow JSON,
                    url TEXT,
                    parent INTEGER,
                    model TEXT,
                    comment TEXT,
                    status TEXT DEFAULT 'new'
                )
            """
            )

            # Créer la table prompt_image pour stocker les images générées
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_image (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    environment_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE
                )
            """
            )

            # Créer la table environnements
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS environnements (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    description TEXT,
                    last_analysis TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Créer la table resultats_analyses
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS resultats_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    environment_id TEXT NOT NULL,
                    fichier TEXT,
                    type TEXT,
                    niveau TEXT,
                    message TEXT,
                    details TEXT,
                    timestamp_analyse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (environment_id) REFERENCES environnements (id) ON DELETE CASCADE
                )
            """
            )

            # Créer la table env_action pour les actions par environnement
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS env_action (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    environment_id TEXT NOT NULL,
                    short_desc TEXT NOT NULL,
                    action_cmd TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (environment_id) REFERENCES environnements (id) ON DELETE CASCADE
                )
            """
            )

            # Créer la table all_models pour stocker tous les modèles détectés
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS all_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    metadata TEXT,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Créer la table association_model_workflow pour lier modèles et prompts
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS association_model_workflow (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    model_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE,
                    FOREIGN KEY (model_id) REFERENCES all_models (id) ON DELETE CASCADE,
                    UNIQUE(prompt_id, model_id)
                )
            """
            )

            self.conn.commit()
            self.ensure_additional_columns()
            self.add_default_environments()
            self.add_default_basic_prompt()
        else:  # mode == "dev"
            # Mode dev: Crée la base si elle n'existe pas
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()

            # Vérifier si la table prompts existe déjà
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'"
            )
            table_exists = self.cursor.fetchone() is not None

            if table_exists:
                # La table existe, valider sa structure
                is_valid, message = self.validate_database_structure()
                if not is_valid:
                    # Ne réparer que si le problème n'est pas juste une table manquante
                    if "Table 'prompts' manquante" not in message:
                        print(f"Structure invalide détectée: {message}")
                        # Corriger automatiquement la structure
                        fix_success, fix_message = self.fix_database_structure()
                        if fix_success:
                            print(f"Structure corrigée: {fix_message}")
                        else:
                            print(f"Erreur lors de la correction: {fix_message}")
                            raise Exception(
                                f"Impossible de corriger la structure de la base: {fix_message}"
                            )
                    else:
                        # Table manquante, la créer normalement
                        self.cursor.execute(
                            """
                            CREATE TABLE prompts (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                prompt_values JSON,
                                workflow JSON,
                                url TEXT,
                                parent INTEGER,
                                model TEXT,
                                comment TEXT,
                                status TEXT DEFAULT 'new'
                            )
                        """
                        )

                        # Créer la table prompt_image
                        self.cursor.execute(
                            """
                            CREATE TABLE IF NOT EXISTS prompt_image (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                prompt_id INTEGER NOT NULL,
                                image_path TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE
                            )
                        """
                        )

                        self.conn.commit()
                        print("Tables 'prompts' et 'prompt_image' créées avec succès")
                else:
                    print(f"Structure de la base validée: {message}")
            else:
                # La table n'existe pas, la créer
                self.cursor.execute(
                    """
                    CREATE TABLE prompts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        prompt_values JSON,
                        workflow JSON,
                        url TEXT,
                        parent INTEGER,
                        model TEXT,
                        comment TEXT,
                        status TEXT DEFAULT 'new'
                    )
                """
                )

                # Créer la table prompt_image
                self.cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS prompt_image (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id INTEGER NOT NULL,
                        image_path TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE
                    )
                """
                )

                self.conn.commit()
                print("Tables 'prompts' et 'prompt_image' créées avec succès")

            self.ensure_additional_columns()
            self.ensure_environment_tables()

    def ensure_additional_columns(self):
        """Assurer que toutes les colonnes additionnelles existent"""
        try:
            # Vérifier si les colonnes existent
            self.cursor.execute("PRAGMA table_info(prompts)")
            columns = [row[1] for row in self.cursor.fetchall()]

            # Gestion spéciale pour la colonne image (legacy)
            if "image" in columns:
                self.remove_legacy_image_column(columns)
                # Re-vérifier les colonnes après suppression
                self.cursor.execute("PRAGMA table_info(prompts)")
                columns = [row[1] for row in self.cursor.fetchall()]

            # Ajouter les colonnes manquantes
            alterations = []
            status_missing = "status" not in columns
            comment_missing = "comment" not in columns

            if "parent" not in columns:
                alterations.append("ALTER TABLE prompts ADD COLUMN parent INTEGER")
            if "model" not in columns:
                alterations.append("ALTER TABLE prompts ADD COLUMN model TEXT")
            if comment_missing:
                alterations.append("ALTER TABLE prompts ADD COLUMN comment TEXT")
            if status_missing:
                alterations.append(
                    "ALTER TABLE prompts ADD COLUMN status TEXT DEFAULT 'new'"
                )
            if "file" not in columns:
                alterations.append("ALTER TABLE prompts ADD COLUMN file TEXT")
            if "id_env" not in columns:
                alterations.append("ALTER TABLE prompts ADD COLUMN id_env TEXT")

            for statement in alterations:
                self.cursor.execute(statement)

            if alterations:
                self.conn.commit()

            # Mise à jour des valeurs par défaut pour le statut
            if status_missing:
                try:
                    self.cursor.execute(
                        "UPDATE prompts SET status='new' WHERE status IS NULL OR TRIM(status)=''"
                    )
                    self.conn.commit()
                except sqlite3.OperationalError:
                    pass

            # S'assurer que la table prompt_image existe avec environment_id
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='prompt_image'"
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    """
                    CREATE TABLE prompt_image (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id INTEGER NOT NULL,
                        image_path TEXT NOT NULL,
                        environment_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE
                    )
                """
                )
                self.conn.commit()
                print("Table 'prompt_image' créée avec succès")
            else:
                # Vérifier si la colonne environment_id existe et l'ajouter si nécessaire
                self.cursor.execute("PRAGMA table_info(prompt_image)")
                image_columns = [row[1] for row in self.cursor.fetchall()]

                if "environment_id" not in image_columns:
                    self.cursor.execute(
                        "ALTER TABLE prompt_image ADD COLUMN environment_id TEXT"
                    )
                    self.conn.commit()
                    print("Colonne 'environment_id' ajoutée à la table 'prompt_image'")

            # S'assurer que les tables de modèles existent
            self.ensure_models_tables()

        except sqlite3.OperationalError as e:
            print(f"Erreur lors de l'ajout des colonnes : {e}")

    def ensure_models_tables(self):
        """S'assurer que les tables de modèles existent"""
        try:
            # Vérifier si la table all_models existe
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='all_models'"
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    """
                    CREATE TABLE all_models (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        path TEXT NOT NULL,
                        metadata TEXT,
                        type TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                print("✅ Table 'all_models' créée avec succès")

            # Vérifier si la table association_model_workflow existe
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='association_model_workflow'"
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    """
                    CREATE TABLE association_model_workflow (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id INTEGER NOT NULL,
                        model_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE,
                        FOREIGN KEY (model_id) REFERENCES all_models (id) ON DELETE CASCADE,
                        UNIQUE(prompt_id, model_id)
                    )
                """
                )
                print("✅ Table 'association_model_workflow' créée avec succès")

            self.conn.commit()

        except Exception as e:
            print(f"❌ Erreur création tables modèles: {e}")

    def remove_legacy_image_column(self, existing_columns):
        """Supprimer la colonne image legacy et migrer les données"""
        desired_columns = [
            "id",
            "name",
            "prompt_values",
            "workflow",
            "url",
            "parent",
            "model",
            "comment",
            "status",
        ]

        try:
            self.cursor.execute("PRAGMA foreign_keys=off")
            self.cursor.execute("DROP TABLE IF EXISTS prompts_old")
            self.cursor.execute("BEGIN")
            self.cursor.execute("ALTER TABLE prompts RENAME TO prompts_old")

            # Créer la nouvelle table
            self.cursor.execute(
                """
                CREATE TABLE prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    prompt_values JSON,
                    workflow JSON,
                    url TEXT,
                    parent INTEGER,
                    model TEXT,
                    comment TEXT,
                    status TEXT DEFAULT 'new'
                )
            """
            )

            # Créer la table prompt_image
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_image (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE
                )
            """
            )

            # Migrer les données
            select_parts = []
            for column in desired_columns:
                if column in existing_columns:
                    select_parts.append(column)
                elif column == "status":
                    select_parts.append("'new'")
                else:
                    select_parts.append("NULL")

            insert_columns = ", ".join(desired_columns)
            select_clause = ", ".join(select_parts)
            self.cursor.execute(
                f"INSERT INTO prompts ({insert_columns}) SELECT {select_clause} FROM prompts_old"
            )
            self.cursor.execute("DROP TABLE prompts_old")
            self.conn.commit()

        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Impossible de supprimer la colonne image : {e}")
        finally:
            try:
                self.cursor.execute("PRAGMA foreign_keys=on")
            except sqlite3.Error:
                pass

    def add_default_basic_prompt(self):
        """Ajouter le prompt par défaut basique"""
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

        default_workflow = {
            "3": {
                "inputs": {
                    "seed": 934966995009374,
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
                "class_type": "KSampler",
                "_meta": {"title": "KSampler"},
            },
            "4": {
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"},
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"},
            },
            "5": {
                "inputs": {"width": 512, "height": 512, "batch_size": 1},
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"},
            },
            "6": {
                "inputs": {"text": "", "speak_and_recognation": True, "clip": ["4", 1]},
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "positive"},
            },
            "7": {
                "inputs": {"text": "", "speak_and_recognation": True, "clip": ["4", 1]},
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "negative"},
            },
            "8": {
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"},
            },
            "9": {
                "inputs": {"filename_prefix": "ComfyUI", "images": ["8", 0]},
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"},
            },
        }

        self.cursor.execute(
            "INSERT INTO prompts (name, prompt_values, workflow, url, model, status, comment) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "basic",
                json.dumps(default_values, ensure_ascii=False),
                json.dumps(default_workflow, ensure_ascii=False),
                "",
                "",
                "new",
                "",
            ),
        )
        self.conn.commit()

    def derive_model_from_workflow(self, workflow_data):
        """Extraire le nom du modèle depuis le workflow JSON - Fonction originale"""
        if not workflow_data:
            return ""

        if isinstance(workflow_data, dict):
            workflow_dict = workflow_data
        else:
            try:
                workflow_dict = json.loads(workflow_data)
            except (TypeError, json.JSONDecodeError):
                return ""

        if not isinstance(workflow_dict, dict):
            return ""

        def normalize(model_name: str) -> str:
            base = os.path.basename(model_name)
            root, _ = os.path.splitext(base)
            return root or base or model_name

        def extract_model_name(raw_value):
            if isinstance(raw_value, str) and raw_value:
                return normalize(raw_value)
            if isinstance(raw_value, (list, tuple)):
                for item in raw_value:
                    if isinstance(item, str) and item:
                        return normalize(item)
            return ""

        for node in workflow_dict.values():
            if not isinstance(node, dict):
                continue
            class_type = node.get("class_type")
            if not isinstance(class_type, str):
                continue
            inputs = node.get("inputs", {})
            if not isinstance(inputs, dict):
                continue

            if class_type == "CheckpointLoaderSimple":
                model_name = extract_model_name(inputs.get("ckpt_name"))
                if model_name:
                    return model_name
            if class_type.lower() == "unetloader":
                model_name = extract_model_name(inputs.get("unet_name"))
                if model_name:
                    return model_name
        return ""

    def get_all_prompts(self):
        """Récupérer tous les prompts avec toutes les colonnes"""
        self.cursor.execute(
            "SELECT id, name, parent, model, workflow, status, comment, id_env FROM prompts"
        )
        results = []
        for row in self.cursor.fetchall():
            prompt_id, name, parent, model, workflow, status, comment, id_env = row
            # Dériver le modèle si vide
            if not model and workflow:
                model = self.derive_model_from_workflow(workflow)
            results.append((prompt_id, name, parent, model, workflow, status, comment, id_env))
        return results

    def get_prompt_by_id(self, prompt_id):
        """Récupérer un prompt par son ID"""
        self.cursor.execute(
            "SELECT name, prompt_values, workflow, url, parent, model, comment, status, file, id_env FROM prompts WHERE id=?",
            (prompt_id,),
        )
        return self.cursor.fetchone()

    def update_prompt(
        self, prompt_id, name, prompt_values, workflow, url, model, comment, status, file=None, id_env=None
    ):
        """Mettre à jour un prompt complet"""
        self.cursor.execute(
            "UPDATE prompts SET name=?, prompt_values=?, workflow=?, url=?, model=?, comment=?, status=?, file=?, id_env=? WHERE id=?",
            (name, prompt_values, workflow, url, model, comment, status, file, id_env, prompt_id),
        )
        self.conn.commit()

    def create_prompt(
        self, name, prompt_values, workflow, url, model, status, comment, parent=None, file=None, id_env=None
    ):
        """Créer un nouveau prompt"""
        self.cursor.execute(
            "INSERT INTO prompts (name, prompt_values, workflow, url, model, status, comment, parent, file, id_env) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, prompt_values, workflow, url, model, status, comment, parent, file, id_env),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def delete_prompt(self, prompt_id):
        """Supprimer un prompt"""
        self.cursor.execute("DELETE FROM prompts WHERE id=?", (prompt_id,))
        self.conn.commit()

    def prompt_name_exists(self, name):
        """Vérifier si un nom de prompt existe"""
        self.cursor.execute("SELECT 1 FROM prompts WHERE name=? LIMIT 1", (name,))
        return self.cursor.fetchone() is not None

    def validate_database_structure(self):
        """Valider la structure de la base de données"""
        try:
            # Vérifier que la table prompts existe
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'"
            )
            if not self.cursor.fetchone():
                return False, "Table 'prompts' manquante"

            # Vérifier les colonnes obligatoires
            self.cursor.execute("PRAGMA table_info(prompts)")
            columns_info = self.cursor.fetchall()
            existing_columns = {col[1]: col[2] for col in columns_info}  # {nom: type}

            required_columns = {
                "id": "INTEGER",
                "name": "TEXT",
                "prompt_values": "JSON",
                "workflow": "JSON",
                "url": "TEXT",
                "model": "TEXT",
                "comment": "TEXT",
                "status": "TEXT",
            }

            missing_columns = []
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    missing_columns.append(f"{col_name} ({col_type})")

            if missing_columns:
                return False, f"Colonnes manquantes: {', '.join(missing_columns)}"

            # Vérifier la contrainte PRIMARY KEY sur id
            primary_key_found = False
            for col_info in columns_info:
                if col_info[1] == "id" and col_info[5] == 1:  # col_info[5] est pk
                    primary_key_found = True
                    break

            if not primary_key_found:
                return False, "Clé primaire manquante sur la colonne 'id'"

            return True, "Structure valide"

        except Exception as e:
            return False, f"Erreur lors de la validation: {e}"

    def fix_database_structure(self):
        """Tenter de corriger la structure de la base de données"""
        try:
            print("Tentative de correction de la structure de la base...")

            # Sauvegarder les données existantes si la table existe
            backup_data = []
            try:
                self.cursor.execute("SELECT * FROM prompts")
                backup_data = self.cursor.fetchall()
                print(f"Sauvegarde de {len(backup_data)} prompts existants")
            except:
                print("Aucune donnée existante à sauvegarder")

            # Supprimer l'ancienne table si elle existe
            self.cursor.execute("DROP TABLE IF EXISTS prompts")

            # Recréer la table avec la bonne structure
            self.cursor.execute(
                """
                CREATE TABLE prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    prompt_values JSON,
                    workflow JSON,
                    url TEXT,
                    parent INTEGER,
                    model TEXT,
                    comment TEXT,
                    status TEXT DEFAULT 'new'
                )
            """
            )

            # Créer la table prompt_image
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_image (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE
                )
            """
            )

            # Restaurer les données si possible
            if backup_data:
                for row in backup_data:
                    try:
                        # Adapter selon le nombre de colonnes dans la sauvegarde
                        if len(row) >= 8:
                            self.cursor.execute(
                                """
                                INSERT INTO prompts (id, name, prompt_values, workflow, url, parent, model, comment, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                                row[:9],
                            )  # Prendre les 9 premières colonnes
                        else:
                            # Structure ancienne, adapter
                            name = row[1] if len(row) > 1 else "Prompt sans nom"
                            prompt_values = row[2] if len(row) > 2 else "{}"
                            workflow = row[3] if len(row) > 3 else "{}"
                            url = row[4] if len(row) > 4 else ""
                            model = row[5] if len(row) > 5 else ""
                            comment = row[6] if len(row) > 6 else ""
                            status = row[7] if len(row) > 7 else "new"

                            self.cursor.execute(
                                """
                                INSERT INTO prompts (name, prompt_values, workflow, url, model, comment, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    name,
                                    prompt_values,
                                    workflow,
                                    url,
                                    model,
                                    comment,
                                    status,
                                ),
                            )
                    except Exception as e:
                        print(f"Erreur lors de la restauration du prompt {row}: {e}")
                        continue

                print(f"Restauration terminée")

            self.conn.commit()
            self.ensure_additional_columns()

            return True, "Structure corrigée avec succès"

        except Exception as e:
            return False, f"Erreur lors de la correction: {e}"

    def add_prompt_image(self, prompt_id, image_path, environment_id=None):
        """Ajouter une image à un prompt avec l'ID d'environnement"""
        try:
            self.cursor.execute(
                "INSERT INTO prompt_image (prompt_id, image_path, environment_id) VALUES (?, ?, ?)",
                (prompt_id, image_path, environment_id),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout de l'image : {e}")
            return False

    def get_prompt_images(self, prompt_id):
        """Récupérer toutes les images d'un prompt"""
        try:
            self.cursor.execute(
                """
                SELECT id, image_path, environment_id, created_at
                FROM prompt_image
                WHERE prompt_id = ?
                ORDER BY created_at DESC
                """,
                (prompt_id,),
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des images : {e}")
            return []

    def get_images_by_environment(self, environment_id):
        """Récupérer toutes les images d'un environnement spécifique"""
        try:
            self.cursor.execute(
                """
                SELECT pi.id, pi.prompt_id, pi.image_path, pi.created_at, p.name as prompt_name
                FROM prompt_image pi
                JOIN prompts p ON pi.prompt_id = p.id
                WHERE pi.environment_id = ?
                ORDER BY pi.created_at DESC
                """,
                (environment_id,),
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des images par environnement : {e}")
            return []

    def delete_prompt_image(self, image_id):
        """Supprimer une image"""
        try:
            self.cursor.execute("DELETE FROM prompt_image WHERE id = ?", (image_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression de l'image : {e}")
            return False

    def delete_prompt_images(self, prompt_id):
        """Supprimer toutes les images d'un prompt"""
        try:
            self.cursor.execute(
                "DELETE FROM prompt_image WHERE prompt_id = ?", (prompt_id,)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression des images : {e}")
            return False

    def close(self):
        """Fermer la connexion"""
        if self.conn:
            self.conn.close()

    def ensure_environment_tables(self):
        """S'assurer que les tables d'environnement existent"""
        try:
            # Créer la table environnements si elle n'existe pas
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS environnements (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    description TEXT,
                    last_analysis TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Créer la table resultats_analyses si elle n'existe pas
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS resultats_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    environment_id TEXT NOT NULL,
                    fichier TEXT,
                    type TEXT,
                    niveau TEXT,
                    message TEXT,
                    details TEXT,
                    timestamp_analyse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (environment_id) REFERENCES environnements (id) ON DELETE CASCADE
                )
            """
            )

            # Créer la table env_action pour les actions par environnement
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS env_action (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    environment_id TEXT NOT NULL,
                    short_desc TEXT NOT NULL,
                    action_cmd TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (environment_id) REFERENCES environnements (id) ON DELETE CASCADE
                )
            """
            )

            self.conn.commit()
            print("Tables d'environnement créées/vérifiées avec succès")

            # Ajouter les environnements par défaut si la table est vide
            self.cursor.execute("SELECT COUNT(*) FROM environnements")
            if self.cursor.fetchone()[0] == 0:
                self.add_default_environments()

        except sqlite3.Error as e:
            print(f"Erreur lors de la création des tables d'environnement : {e}")

    def add_default_environments(self):
        """Ajouter les 5 environnements par défaut"""
        default_environments = [
            ("G11_01", "G11_01", "H:\\comfyui\\G11_01", "Environnement ComfyUI G11_01"),
            ("G11_02", "G11_02", "H:\\comfyui\\G11_02", "Environnement ComfyUI G11_02"),
            ("G11_03", "G11_03", "H:\\comfyui\\G11_03", "Environnement ComfyUI G11_03"),
            ("G11_04", "G11_04", "H:\\comfyui\\G11_04", "Environnement ComfyUI G11_04"),
            ("G11_05", "G11_05", "H:\\comfyui\\G11_05", "Environnement ComfyUI G11_05"),
        ]

        try:
            for env_id, name, path, description in default_environments:
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO environnements (id, name, path, description)
                    VALUES (?, ?, ?, ?)
                """,
                    (env_id, name, path, description),
                )
            self.conn.commit()
            print("Environnements par défaut ajoutés avec succès")
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout des environnements par défaut : {e}")

    def get_all_environments(self):
        """Récupérer tous les environnements"""
        try:
            self.cursor.execute(
                """
                SELECT id, name, path, description, last_analysis, created_at, updated_at
                FROM environnements
                ORDER BY name
            """
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des environnements : {e}")
            return []

    def update_environment_analysis(self, environment_id):
        """Mettre à jour la date de dernière analyse d'un environnement"""
        try:
            self.cursor.execute(
                """
                UPDATE environnements
                SET last_analysis = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (environment_id,),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de la mise à jour de l'environnement : {e}")
            return False

    def clear_analysis_results(self, environment_id=None):
        """Effacer les résultats d'analyse (tous ou pour un environnement spécifique)"""
        try:
            if environment_id:
                self.cursor.execute(
                    "DELETE FROM resultats_analyses WHERE environment_id = ?",
                    (environment_id,),
                )
            else:
                self.cursor.execute("DELETE FROM resultats_analyses")
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de l'effacement des résultats d'analyse : {e}")
            return False

    def get_environment_analyses_directory(self, environment_id):
        """Récupérer le répertoire d'analyses pour un environnement"""
        try:
            self.cursor.execute(
                "SELECT path FROM environnements WHERE id = ?",
                (environment_id,),
            )
            result = self.cursor.fetchone()
            if result and result[0]:
                # Créer le chemin du répertoire analyses
                analyses_dir = os.path.join(result[0], "analyses")
                # Créer le répertoire s'il n'existe pas
                os.makedirs(analyses_dir, exist_ok=True)
                return analyses_dir
            else:
                # Répertoire par défaut si l'environnement n'est pas trouvé
                default_dir = f"g:/temp/analyses/{environment_id}"
                os.makedirs(default_dir, exist_ok=True)
                return default_dir
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération du répertoire analyses : {e}")
            # Répertoire par défaut en cas d'erreur
            default_dir = f"g:/temp/analyses/{environment_id}"
            os.makedirs(default_dir, exist_ok=True)
            return default_dir

    def add_analysis_result(
        self, environment_id, fichier, type_result, niveau, message, details=""
    ):
        """Ajouter un résultat d'analyse"""
        try:
            self.cursor.execute(
                """
                INSERT INTO resultats_analyses
                (environment_id, fichier, type, niveau, message, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (environment_id, fichier, type_result, niveau, message, details),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout du résultat d'analyse : {e}")
            return False

    def get_analysis_results(self, environment_id=None):
        """Récupérer les résultats d'analyse (tous ou pour un environnement spécifique)"""
        try:
            if environment_id:
                self.cursor.execute(
                    """
                    SELECT id, environment_id, fichier, type, niveau, message, details, timestamp_analyse
                    FROM resultats_analyses
                    WHERE environment_id = ?
                    ORDER BY timestamp_analyse DESC
                """,
                    (environment_id,),
                )
            else:
                self.cursor.execute(
                    """
                    SELECT id, environment_id, fichier, type, niveau, message, details, timestamp_analyse
                    FROM resultats_analyses
                    ORDER BY timestamp_analyse DESC
                """
                )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des résultats d'analyse : {e}")
            return []

    def get_environment_by_id(self, environment_id):
        """Récupérer un environnement par son ID"""
        try:
            self.cursor.execute(
                """
                SELECT id, name, path, description, last_analysis, created_at, updated_at
                FROM environnements
                WHERE id = ?
            """,
                (environment_id,),
            )
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de l'environnement : {e}")
            return None

    # === MÉTHODES CRUD POUR LES ENVIRONNEMENTS ===

    def add_environment(self, env_id, name, path, description=""):
        """Ajouter un nouvel environnement"""
        try:
            current_time = datetime.now().isoformat()
            self.cursor.execute(
                """
                INSERT INTO environnements (id, name, path, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (env_id, name, path, description, current_time, current_time),
            )
            self.conn.commit()
            print(f"Environnement '{name}' ajouté avec succès (ID: {env_id})")
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout de l'environnement : {e}")
            return False

    def update_environment(self, old_env_id, new_env_id, name, path, description=""):
        """Mettre à jour un environnement existant"""
        try:
            current_time = datetime.now().isoformat()

            # Si l'ID change, on doit mettre à jour toutes les références
            if old_env_id != new_env_id:
                # Mettre à jour les analyses liées (si la table existe)
                try:
                    self.cursor.execute(
                        "UPDATE analyses SET environment_id = ? WHERE environment_id = ?",
                        (new_env_id, old_env_id)
                    )
                except sqlite3.OperationalError:
                    # Table analyses n'existe pas, on continue
                    pass

                # Mettre à jour les images liées (si la table existe)
                try:
                    self.cursor.execute(
                        "UPDATE prompt_images SET environment_id = ? WHERE environment_id = ?",
                        (new_env_id, old_env_id)
                    )
                except sqlite3.OperationalError:
                    # Table prompt_images n'existe pas, on continue
                    pass

            # Mettre à jour l'environnement
            self.cursor.execute(
                """
                UPDATE environnements
                SET id = ?, name = ?, path = ?, description = ?, updated_at = ?
                WHERE id = ?
            """,
                (new_env_id, name, path, description, current_time, old_env_id),
            )

            self.conn.commit()
            print(f"Environnement mis à jour avec succès (ID: {new_env_id})")
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de la mise à jour de l'environnement : {e}")
            return False

    def delete_environment(self, env_id):
        """Supprimer un environnement et toutes ses données associées"""
        try:
            # Supprimer les analyses liées (si la table existe)
            try:
                self.cursor.execute(
                    "DELETE FROM analyses WHERE environment_id = ?",
                    (env_id,)
                )
            except sqlite3.OperationalError:
                # Table analyses n'existe pas, on continue
                pass

            # Supprimer les images liées (si la table existe)
            try:
                self.cursor.execute(
                    "DELETE FROM prompt_images WHERE environment_id = ?",
                    (env_id,)
                )
            except sqlite3.OperationalError:
                # Table prompt_images n'existe pas, on continue
                pass

            # Supprimer l'environnement
            self.cursor.execute(
                "DELETE FROM environnements WHERE id = ?",
                (env_id,)
            )

            self.conn.commit()
            print(f"Environnement '{env_id}' et toutes ses données supprimés avec succès")
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression de l'environnement : {e}")
            return False

    # === MÉTHODES CRUD POUR LES ACTIONS D'ENVIRONNEMENT ===

    def get_env_actions(self, environment_id):
        """Récupérer toutes les actions pour un environnement"""
        try:
            self.cursor.execute(
                """
                SELECT id, environment_id, short_desc, action_cmd, created_at, updated_at
                FROM env_action
                WHERE environment_id = ?
                ORDER BY created_at DESC
                """,
                (environment_id,)
            )
            rows = self.cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "environment_id": row[1],
                    "short_desc": row[2],
                    "action_cmd": row[3],
                    "created_at": row[4],
                    "updated_at": row[5]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Erreur lors de la récupération des actions: {e}")
            return []

    def add_env_action(self, environment_id, short_desc, action_cmd=""):
        """Ajouter une nouvelle action pour un environnement"""
        try:
            self.cursor.execute(
                """
                INSERT INTO env_action (environment_id, short_desc, action_cmd)
                VALUES (?, ?, ?)
                """,
                (environment_id, short_desc, action_cmd)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Erreur lors de l'ajout de l'action: {e}")
            return None

    # ===== GESTION DES MODÈLES =====

    def update_all_models(self, models_list):
        """
        Mettre à jour la table all_models avec la liste des modèles détectés

        Args:
            models_list: Liste des modèles avec leurs informations
        """
        try:
            # Vider la table actuelle
            self.cursor.execute("DELETE FROM all_models")

            # Insérer tous les nouveaux modèles
            for model in models_list:
                self.cursor.execute(
                    """
                    INSERT INTO all_models (name, path, metadata, type)
                    VALUES (?, ?, ?, ?)
                    """,
                    (model['name'], model['path'], model['metadata'], model['type'])
                )

            self.conn.commit()
            print(f"✅ Table all_models mise à jour avec {len(models_list)} modèles")

        except Exception as e:
            print(f"❌ Erreur mise à jour all_models: {e}")
            self.conn.rollback()

    def get_all_models(self):
        """
        Récupérer tous les modèles de la table all_models

        Returns:
            Liste des modèles avec leurs informations
        """
        try:
            self.cursor.execute(
                """
                SELECT id, name, path, metadata, type, created_at, updated_at
                FROM all_models
                ORDER BY name
                """
            )
            rows = self.cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "metadata": row[3],
                    "type": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"❌ Erreur récupération modèles: {e}")
            return []

    def get_models_by_type(self, model_type):
        """
        Récupérer les modèles d'un type spécifique

        Args:
            model_type: Type de modèle à filtrer

        Returns:
            Liste des modèles du type spécifié
        """
        try:
            self.cursor.execute(
                """
                SELECT id, name, path, metadata, type, created_at, updated_at
                FROM all_models
                WHERE type = ?
                ORDER BY name
                """,
                (model_type,)
            )
            rows = self.cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "metadata": row[3],
                    "type": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"❌ Erreur récupération modèles par type: {e}")
            return []

    def get_unique_model_types(self):
        """
        Récupérer la liste unique des types de modèles

        Returns:
            Liste des types sans doublons
        """
        try:
            self.cursor.execute(
                """
                SELECT DISTINCT type
                FROM all_models
                ORDER BY type
                """
            )
            rows = self.cursor.fetchall()

            return [row[0] for row in rows]

        except Exception as e:
            print(f"❌ Erreur récupération types modèles: {e}")
            return []

    def associate_model_to_prompt(self, prompt_id, model_id):
        """
        Associer un modèle à un prompt

        Args:
            prompt_id: ID du prompt
            model_id: ID du modèle
        """
        try:
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO association_model_workflow (prompt_id, model_id)
                VALUES (?, ?)
                """,
                (prompt_id, model_id)
            )
            self.conn.commit()

        except Exception as e:
            print(f"❌ Erreur association modèle-prompt: {e}")

    def get_models_for_prompt(self, prompt_id):
        """
        Récupérer les modèles associés à un prompt

        Args:
            prompt_id: ID du prompt

        Returns:
            Liste des modèles associés
        """
        try:
            self.cursor.execute(
                """
                SELECT m.id, m.name, m.path, m.metadata, m.type, m.created_at, m.updated_at
                FROM all_models m
                INNER JOIN association_model_workflow amw ON m.id = amw.model_id
                WHERE amw.prompt_id = ?
                ORDER BY m.name
                """,
                (prompt_id,)
            )
            rows = self.cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "metadata": row[3],
                    "type": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"❌ Erreur récupération modèles du prompt: {e}")
            return []

    def clear_prompt_models(self, prompt_id):
        """
        Supprimer toutes les associations de modèles pour un prompt

        Args:
            prompt_id: ID du prompt
        """
        try:
            self.cursor.execute(
                "DELETE FROM association_model_workflow WHERE prompt_id = ?",
                (prompt_id,)
            )
            self.conn.commit()

        except Exception as e:
            print(f"❌ Erreur suppression associations: {e}")

    def extract_models_from_workflow(self, workflow_data, prompt_id):
        """
        Extraire et associer les modèles utilisés dans un workflow

        Args:
            workflow_data: Données du workflow JSON
            prompt_id: ID du prompt
        """
        if not workflow_data:
            return

        try:
            # Vider les associations existantes
            self.clear_prompt_models(prompt_id)

            # Parser le workflow pour trouver les modèles
            import json
            if isinstance(workflow_data, str):
                workflow = json.loads(workflow_data)
            else:
                workflow = workflow_data

            # Types de nodes qui utilisent des modèles
            model_nodes = {
                'CheckpointLoaderSimple': ('ckpt_name', 'checkpoints'),
                'LoraLoader': ('lora_name', 'loras'),
                'VAELoader': ('vae_name', 'vae'),
                'ControlNetLoader': ('control_net_name', 'controlnet'),
                'UpscaleModelLoader': ('model_name', 'upscale_models'),
                'CLIPTextEncode': None,  # Pas de modèle direct
                'CLIPVisionLoader': ('clip_name', 'clip_vision')
            }

            found_models = []

            for node_id, node_data in workflow.items():
                class_type = node_data.get('class_type', '')
                inputs = node_data.get('inputs', {})

                if class_type in model_nodes and model_nodes[class_type]:
                    param_name, model_type = model_nodes[class_type]
                    model_name = inputs.get(param_name)

                    if model_name:
                        # Trouver le modèle dans la base
                        self.cursor.execute(
                            "SELECT id FROM all_models WHERE name = ? AND type = ?",
                            (model_name, model_type)
                        )
                        model_row = self.cursor.fetchone()

                        if model_row:
                            model_id = model_row[0]
                            self.associate_model_to_prompt(prompt_id, model_id)
                            found_models.append(model_name)

            print(f"✅ Modèles associés au prompt {prompt_id}: {found_models}")

        except Exception as e:
            print(f"❌ Erreur extraction modèles du workflow: {e}")

    def update_env_action(self, action_id, short_desc, action_cmd):
        """Mettre à jour une action existante"""
        try:
            self.cursor.execute(
                """
                UPDATE env_action
                SET short_desc = ?, action_cmd = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (short_desc, action_cmd, action_id)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'action: {e}")
            return False

    def delete_env_action(self, action_id):
        """Supprimer une action"""
        try:
            self.cursor.execute("DELETE FROM env_action WHERE id = ?", (action_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur lors de la suppression de l'action: {e}")
            return False

#!/usr/bin/env python3
"""
Gestionnaire d'index optimisé pour les images de la galerie
Utilise SQLite pour indexer et accélérer l'affichage des images
"""

import os
import sqlite3
import hashlib
import time
from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk
from typing import List, Dict, Optional, Tuple
import threading
import json

class ImageIndexManager:
    """Gestionnaire d'index SQLite pour optimiser l'affichage des images"""

    def __init__(self, db_path: str = None):
        """Initialiser le gestionnaire d'index

        Args:
            db_path: Chemin vers la base de données. Si None, utilise un fichier par défaut.
        """
        if db_path is None:
            db_path = os.path.join(os.path.expanduser("~"), "cy8_images_index.db")

        self.db_path = db_path
        self.connection = None
        self.thumbnail_cache = {}  # Cache mémoire des miniatures
        self.deleted_images = set()  # Images marquées comme supprimées

        # Configuration
        self.thumbnail_size = (150, 150)
        self.supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}

        self._init_database()

    def _init_database(self):
        """Initialiser la base de données SQLite"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.execute("PRAGMA foreign_keys = ON")

            # Table principale pour l'index des images
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS image_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_mtime REAL NOT NULL,
                    file_hash TEXT,
                    width INTEGER,
                    height INTEGER,
                    thumbnail_data BLOB,
                    is_deleted INTEGER DEFAULT 0,
                    created_at REAL DEFAULT (julianday('now')),
                    updated_at REAL DEFAULT (julianday('now'))
                )
            """)

            # Index pour optimiser les requêtes
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_path ON image_index(file_path)
            """)
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_mtime ON image_index(file_mtime DESC)
            """)
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_is_deleted ON image_index(is_deleted)
            """)

            self.connection.commit()
            print(f"✅ Index d'images initialisé: {self.db_path}")

        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de l'index: {e}")
            raise

    def _get_file_hash(self, file_path: str) -> str:
        """Calculer le hash MD5 d'un fichier pour détecter les changements"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Lire par chunks pour les gros fichiers
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def _create_thumbnail(self, image_path: str) -> Optional[bytes]:
        """Créer une miniature et la convertir en bytes pour stockage"""
        try:
            with Image.open(image_path) as img:
                # Créer la miniature
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)

                # Convertir en bytes pour stockage
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                return buffer.getvalue()
        except Exception as e:
            print(f"Erreur création miniature {image_path}: {e}")
            return None

    def scan_directory(self, directory: str, force_refresh: bool = False) -> Dict:
        """Scanner un répertoire et mettre à jour l'index

        Args:
            directory: Répertoire à scanner
            force_refresh: Forcer la régénération des miniatures

        Returns:
            Dictionnaire avec les statistiques du scan
        """
        if not os.path.exists(directory):
            return {"error": "Répertoire inexistant", "count": 0}

        stats = {
            "total_files": 0,
            "new_files": 0,
            "updated_files": 0,
            "deleted_files": 0,
            "errors": 0,
            "scan_time": 0
        }

        start_time = time.time()

        try:
            # 1. Scanner tous les fichiers du répertoire
            current_files = set()

            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.splitext(file.lower())[1] in self.supported_extensions:
                        current_files.add(file_path)
                        stats["total_files"] += 1

            # 2. Vérifier chaque fichier dans l'index
            for file_path in current_files:
                try:
                    self._process_image_file(file_path, force_refresh, stats)
                except Exception as e:
                    print(f"Erreur traitement {file_path}: {e}")
                    stats["errors"] += 1

            # 3. Marquer les fichiers supprimés (non trouvés)
            cursor = self.connection.execute("""
                SELECT file_path FROM image_index
                WHERE file_path LIKE ? AND is_deleted = 0
            """, (f"{directory}%",))

            indexed_files = {row[0] for row in cursor.fetchall()}
            deleted_files = indexed_files - current_files

            for deleted_file in deleted_files:
                self.connection.execute("""
                    UPDATE image_index
                    SET is_deleted = 1, updated_at = julianday('now')
                    WHERE file_path = ?
                """, (deleted_file,))
                stats["deleted_files"] += 1

            self.connection.commit()
            stats["scan_time"] = time.time() - start_time

            print(f"📊 Scan terminé: {stats['total_files']} fichiers, {stats['new_files']} nouveaux, {stats['updated_files']} mis à jour, {stats['deleted_files']} supprimés en {stats['scan_time']:.2f}s")

        except Exception as e:
            print(f"❌ Erreur lors du scan: {e}")
            stats["error"] = str(e)

        return stats

    def _process_image_file(self, file_path: str, force_refresh: bool, stats: Dict):
        """Traiter un fichier image individuel"""
        try:
            # Obtenir les informations du fichier
            stat = os.stat(file_path)
            file_size = stat.st_size
            file_mtime = stat.st_mtime
            file_name = os.path.basename(file_path)

            # Vérifier si le fichier existe déjà dans l'index
            cursor = self.connection.execute("""
                SELECT id, file_mtime, file_hash, thumbnail_data
                FROM image_index WHERE file_path = ?
            """, (file_path,))

            existing = cursor.fetchone()

            if existing and not force_refresh:
                existing_id, existing_mtime, existing_hash, existing_thumbnail = existing

                # Vérifier si le fichier a été modifié
                if abs(existing_mtime - file_mtime) < 1:  # Tolérance d'1 seconde
                    return  # Fichier inchangé

            # Fichier nouveau ou modifié - traiter
            print(f"🔄 Traitement: {file_name}")

            # Calculer le hash et créer la miniature
            file_hash = self._get_file_hash(file_path)
            thumbnail_data = self._create_thumbnail(file_path)

            # Obtenir les dimensions de l'image
            width, height = 0, 0
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
            except Exception:
                pass

            if existing:
                # Mettre à jour l'enregistrement existant
                self.connection.execute("""
                    UPDATE image_index SET
                        file_name = ?, file_size = ?, file_mtime = ?,
                        file_hash = ?, width = ?, height = ?,
                        thumbnail_data = ?, is_deleted = 0,
                        updated_at = julianday('now')
                    WHERE file_path = ?
                """, (file_name, file_size, file_mtime, file_hash,
                     width, height, thumbnail_data, file_path))
                stats["updated_files"] += 1
            else:
                # Créer un nouvel enregistrement
                self.connection.execute("""
                    INSERT INTO image_index
                    (file_path, file_name, file_size, file_mtime, file_hash,
                     width, height, thumbnail_data, is_deleted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (file_path, file_name, file_size, file_mtime, file_hash,
                     width, height, thumbnail_data))
                stats["new_files"] += 1

        except Exception as e:
            print(f"❌ Erreur traitement {file_path}: {e}")
            raise

    def get_images(self, directory: str, include_deleted: bool = False,
                   limit: int = None, offset: int = 0) -> List[Dict]:
        """Récupérer la liste des images indexées

        Args:
            directory: Répertoire de base
            include_deleted: Inclure les images marquées comme supprimées
            limit: Nombre maximum d'images à retourner
            offset: Décalage pour la pagination

        Returns:
            Liste des informations d'images
        """
        try:
            query = """
                SELECT file_path, file_name, file_size, file_mtime,
                       width, height, is_deleted, thumbnail_data
                FROM image_index
                WHERE file_path LIKE ?
            """
            params = [f"{directory}%"]

            if not include_deleted:
                query += " AND is_deleted = 0"

            query += " ORDER BY file_mtime DESC"

            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

            cursor = self.connection.execute(query, params)

            images = []
            for row in cursor.fetchall():
                (file_path, file_name, file_size, file_mtime,
                 width, height, is_deleted, thumbnail_data) = row

                images.append({
                    "file_path": file_path,
                    "file_name": file_name,
                    "file_size": file_size,
                    "file_mtime": file_mtime,
                    "width": width,
                    "height": height,
                    "is_deleted": bool(is_deleted),
                    "thumbnail_data": thumbnail_data
                })

            return images

        except Exception as e:
            print(f"❌ Erreur récupération images: {e}")
            return []

    def get_thumbnail(self, file_path: str) -> Optional[ImageTk.PhotoImage]:
        """Récupérer la miniature d'une image depuis l'index

        Args:
            file_path: Chemin vers l'image

        Returns:
            PhotoImage de la miniature ou None
        """
        # Vérifier le cache mémoire d'abord
        if file_path in self.thumbnail_cache:
            return self.thumbnail_cache[file_path]

        try:
            cursor = self.connection.execute("""
                SELECT thumbnail_data, is_deleted FROM image_index
                WHERE file_path = ?
            """, (file_path,))

            result = cursor.fetchone()
            if not result:
                return None

            thumbnail_data, is_deleted = result

            if is_deleted:
                # Retourner une icône de corbeille
                return self._create_trash_icon()

            if thumbnail_data:
                # Convertir les bytes en PhotoImage
                import io
                image = Image.open(io.BytesIO(thumbnail_data))
                photo = ImageTk.PhotoImage(image)

                # Mettre en cache
                self.thumbnail_cache[file_path] = photo
                return photo

        except Exception as e:
            print(f"❌ Erreur récupération miniature {file_path}: {e}")

        return None

    def _create_trash_icon(self) -> ImageTk.PhotoImage:
        """Créer une icône de corbeille pour les images supprimées"""
        try:
            # Créer une image simple de corbeille
            img = Image.new('RGBA', self.thumbnail_size, (240, 240, 240, 255))

            # Dessiner une corbeille simple (rectangle avec couvercle)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)

            # Fond gris clair
            draw.rectangle([10, 10, 140, 140], fill=(220, 220, 220, 255), outline=(180, 180, 180, 255))

            # Corbeille
            draw.rectangle([40, 60, 110, 120], fill=(160, 160, 160, 255), outline=(100, 100, 100, 255))
            draw.rectangle([35, 50, 115, 65], fill=(160, 160, 160, 255), outline=(100, 100, 100, 255))

            # Symbole suppression
            draw.line([50, 70, 50, 110], fill=(100, 100, 100, 255), width=2)
            draw.line([65, 70, 65, 110], fill=(100, 100, 100, 255), width=2)
            draw.line([80, 70, 80, 110], fill=(100, 100, 100, 255), width=2)
            draw.line([95, 70, 95, 110], fill=(100, 100, 100, 255), width=2)

            return ImageTk.PhotoImage(img)

        except Exception as e:
            print(f"❌ Erreur création icône corbeille: {e}")
            return None

    def mark_deleted(self, file_path: str):
        """Marquer une image comme supprimée (soft delete)

        Args:
            file_path: Chemin vers l'image à marquer
        """
        try:
            self.connection.execute("""
                UPDATE image_index
                SET is_deleted = 1, updated_at = julianday('now')
                WHERE file_path = ?
            """, (file_path,))
            self.connection.commit()

            # Supprimer du cache mémoire
            if file_path in self.thumbnail_cache:
                del self.thumbnail_cache[file_path]

            print(f"🗑️ Image marquée comme supprimée: {os.path.basename(file_path)}")

        except Exception as e:
            print(f"❌ Erreur marquage suppression {file_path}: {e}")

    def restore_deleted(self, file_path: str):
        """Restaurer une image marquée comme supprimée

        Args:
            file_path: Chemin vers l'image à restaurer
        """
        try:
            # Vérifier que le fichier existe toujours
            if os.path.exists(file_path):
                self.connection.execute("""
                    UPDATE image_index
                    SET is_deleted = 0, updated_at = julianday('now')
                    WHERE file_path = ?
                """, (file_path,))
                self.connection.commit()

                # Supprimer du cache pour forcer le rechargement
                if file_path in self.thumbnail_cache:
                    del self.thumbnail_cache[file_path]

                print(f"♻️ Image restaurée: {os.path.basename(file_path)}")
            else:
                print(f"⚠️ Impossible de restaurer, fichier inexistant: {file_path}")

        except Exception as e:
            print(f"❌ Erreur restauration {file_path}: {e}")

    def clear_cache(self):
        """Vider le cache mémoire des miniatures"""
        self.thumbnail_cache.clear()
        print("🧹 Cache mémoire vidé")

    def get_stats(self) -> Dict:
        """Obtenir les statistiques de l'index"""
        try:
            cursor = self.connection.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN is_deleted = 0 THEN 1 END) as active,
                    COUNT(CASE WHEN is_deleted = 1 THEN 1 END) as deleted,
                    SUM(file_size) as total_size
                FROM image_index
            """)

            total, active, deleted, total_size = cursor.fetchone()

            return {
                "total_images": total or 0,
                "active_images": active or 0,
                "deleted_images": deleted or 0,
                "total_size_mb": round((total_size or 0) / (1024 * 1024), 2),
                "cache_size": len(self.thumbnail_cache)
            }

        except Exception as e:
            print(f"❌ Erreur récupération statistiques: {e}")
            return {}

    def close(self):
        """Fermer la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            print("✅ Index d'images fermé")

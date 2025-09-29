#!/usr/bin/env python3
"""
Wrapper pour utiliser le processeur d'images Rust avec fallback sur PIL
"""

import os
import sys
from typing import Optional, Tuple, Union
from PIL import Image
import hashlib

class FastImageProcessor:
    """Processeur d'images optimisé avec support Rust optionnel"""

    def __init__(self):
        self.rust_available = False
        self.rust_module = None

        # Tenter d'importer le module Rust
        try:
            # Ajouter le chemin du module Rust compilé
            rust_path = os.path.join(os.path.dirname(__file__), "..", "rust_image_processor", "target", "release")
            if rust_path not in sys.path:
                sys.path.insert(0, rust_path)

            import rust_image_processor
            self.rust_module = rust_image_processor
            self.rust_available = True
            print("🚀 Processeur Rust activé - Performance optimale")

        except ImportError:
            print("⚡ Processeur Python (PIL) - Performance standard")

    def create_thumbnail(self, image_path: str, width: int = 150, height: int = 150) -> Optional[bytes]:
        """Créer une miniature optimisée

        Args:
            image_path: Chemin vers l'image
            width: Largeur de la miniature
            height: Hauteur de la miniature

        Returns:
            Données PNG de la miniature en bytes
        """
        if self.rust_available:
            try:
                return self.rust_module.create_thumbnail_fast(image_path, width, height)
            except Exception as e:
                print(f"⚠️ Erreur Rust pour {image_path}, fallback PIL: {e}")

        # Fallback sur PIL
        return self._create_thumbnail_pil(image_path, width, height)

    def _create_thumbnail_pil(self, image_path: str, width: int, height: int) -> Optional[bytes]:
        """Créer une miniature avec PIL (fallback)"""
        try:
            with Image.open(image_path) as img:
                # Créer la miniature
                img.thumbnail((width, height), Image.Resampling.LANCZOS)

                # Convertir en bytes
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                return buffer.getvalue()

        except Exception as e:
            print(f"❌ Erreur PIL pour {image_path}: {e}")
            return None

    def get_dimensions(self, image_path: str) -> Optional[Tuple[int, int]]:
        """Obtenir les dimensions d'une image

        Args:
            image_path: Chemin vers l'image

        Returns:
            Tuple (largeur, hauteur) ou None si erreur
        """
        if self.rust_available:
            try:
                return self.rust_module.get_image_dimensions(image_path)
            except Exception:
                pass

        # Fallback sur PIL
        try:
            with Image.open(image_path) as img:
                return img.size
        except Exception:
            return None

    def calculate_hash(self, image_path: str) -> str:
        """Calculer le hash d'une image

        Args:
            image_path: Chemin vers l'image

        Returns:
            Hash hexadécimal du fichier
        """
        if self.rust_available:
            try:
                return self.rust_module.calculate_image_hash(image_path)
            except Exception:
                pass

        # Fallback sur Python
        try:
            hash_md5 = hashlib.md5()
            with open(image_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def get_performance_info(self) -> dict:
        """Obtenir les informations de performance"""
        return {
            "rust_available": self.rust_available,
            "backend": "Rust" if self.rust_available else "PIL (Python)",
            "estimated_speed": "5-10x plus rapide" if self.rust_available else "Standard",
            "recommended_action": "Aucune" if self.rust_available else "Installer Rust pour de meilleures performances"
        }

# Instance globale pour réutilisation
_processor_instance = None

def get_image_processor() -> FastImageProcessor:
    """Obtenir l'instance globale du processeur d'images"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = FastImageProcessor()
    return _processor_instance

# Fonctions de commodité
def create_thumbnail_fast(image_path: str, width: int = 150, height: int = 150) -> Optional[bytes]:
    """Créer une miniature rapidement"""
    return get_image_processor().create_thumbnail(image_path, width, height)

def get_image_dimensions_fast(image_path: str) -> Optional[Tuple[int, int]]:
    """Obtenir les dimensions rapidement"""
    return get_image_processor().get_dimensions(image_path)

def calculate_image_hash_fast(image_path: str) -> str:
    """Calculer le hash rapidement"""
    return get_image_processor().calculate_hash(image_path)

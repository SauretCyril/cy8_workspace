#!/usr/bin/env python3
"""
Gestionnaire de modèles ComfyUI
Récupère et gère les modèles disponibles dans ComfyUI
"""

import os
import requests
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin


class ComfyUIModelsManager:
    """Gestionnaire pour récupérer et organiser les modèles ComfyUI"""

    def __init__(self, server_url: str = "http://127.0.0.1:8188"):
        """
        Initialiser le gestionnaire de modèles

        Args:
            server_url: URL du serveur ComfyUI
        """
        self.server_url = server_url
        self.models_cache = {}
        self.model_types_cache = []
        self.last_refresh = 0
        self.cache_duration = 300  # 5 minutes

    def get_model_types(self) -> List[str]:
        """
        Récupérer la liste des types de modèles disponibles

        Returns:
            Liste des types de modèles (checkpoints, loras, etc.)
        """
        try:
            url = urljoin(self.server_url, "/models")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            model_types = response.json()
            self.model_types_cache = model_types
            return model_types

        except Exception as e:
            print(f"Erreur récupération types de modèles: {e}")
            return self.model_types_cache  # Retourner le cache en cas d'erreur

    def get_models_by_type(self, model_type: str) -> List[str]:
        """
        Récupérer la liste des modèles d'un type spécifique

        Args:
            model_type: Type de modèle (checkpoints, loras, etc.)

        Returns:
            Liste des noms de modèles de ce type
        """
        try:
            url = urljoin(self.server_url, f"/models/{model_type}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"Erreur récupération modèles {model_type}: {e}")
            return []

    def get_all_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupérer tous les modèles de tous les types

        Returns:
            Dictionnaire avec les modèles organisés par type
        """
        # Vérifier le cache
        current_time = time.time()
        if (current_time - self.last_refresh) < self.cache_duration and self.models_cache:
            return self.models_cache

        all_models = {}
        model_types = self.get_model_types()

        print(f"📋 Récupération des modèles pour {len(model_types)} types...")

        for model_type in model_types:
            print(f"🔍 Récupération {model_type}...")
            models_list = self.get_models_by_type(model_type)

            all_models[model_type] = []

            for model_name in models_list:
                model_info = {
                    'name': model_name,
                    'type': model_type,
                    'path': self._get_model_path(model_type, model_name),
                    'metadata': self._get_model_metadata(model_type, model_name)
                }
                all_models[model_type].append(model_info)

        self.models_cache = all_models
        self.last_refresh = current_time

        print(f"✅ Récupération terminée: {sum(len(models) for models in all_models.values())} modèles")
        return all_models

    def _get_model_path(self, model_type: str, model_name: str) -> str:
        """
        Construire le chemin complet du modèle

        Args:
            model_type: Type de modèle
            model_name: Nom du modèle

        Returns:
            Chemin complet estimé du modèle
        """
        # Chemins typiques ComfyUI
        type_paths = {
            'checkpoints': 'models/checkpoints',
            'loras': 'models/loras',
            'vae': 'models/vae',
            'embeddings': 'models/embeddings',
            'controlnet': 'models/controlnet',
            'upscale_models': 'models/upscale_models',
            'diffusers': 'models/diffusers',
            'style_models': 'models/style_models',
            'hypernetworks': 'models/hypernetworks',
            'clip_vision': 'models/clip_vision'
        }

        base_path = type_paths.get(model_type, f'models/{model_type}')
        return f"{base_path}/{model_name}"

    def _get_model_metadata(self, model_type: str, model_name: str) -> Dict[str, Any]:
        """
        Récupérer les métadonnées d'un modèle

        Args:
            model_type: Type de modèle
            model_name: Nom du modèle

        Returns:
            Dictionnaire des métadonnées
        """
        # Pour l'instant, métadonnées basiques
        # TODO: Implémenter la lecture des métadonnées réelles des fichiers
        metadata = {
            'size': 'Unknown',
            'format': self._get_file_format(model_name),
            'description': '',
            'tags': [],
            'created_date': '',
            'hash': ''
        }

        return metadata

    def _get_file_format(self, model_name: str) -> str:
        """
        Déterminer le format du fichier à partir de son extension

        Args:
            model_name: Nom du fichier modèle

        Returns:
            Format du fichier (safetensors, ckpt, etc.)
        """
        if model_name.endswith('.safetensors'):
            return 'safetensors'
        elif model_name.endswith('.ckpt'):
            return 'ckpt'
        elif model_name.endswith('.pth'):
            return 'pytorch'
        elif model_name.endswith('.bin'):
            return 'binary'
        else:
            return 'unknown'

    def get_models_flat_list(self) -> List[Dict[str, Any]]:
        """
        Récupérer tous les modèles dans une liste plate

        Returns:
            Liste de tous les modèles avec leurs informations
        """
        all_models = self.get_all_models()
        flat_list = []

        model_id = 1
        for model_type, models in all_models.items():
            for model in models:
                model_entry = {
                    'id': model_id,
                    'name': model['name'],
                    'type': model_type,
                    'path': model['path'],
                    'metadata': json.dumps(model['metadata'])
                }
                flat_list.append(model_entry)
                model_id += 1

        return flat_list

    def get_unique_model_types(self) -> List[str]:
        """
        Récupérer la liste unique des types de modèles (sans doublons)

        Returns:
            Liste des types de modèles uniques
        """
        all_models = self.get_all_models()
        return list(all_models.keys())


def test_models_manager():
    """Test du gestionnaire de modèles"""
    print("🧪 Test du gestionnaire de modèles ComfyUI")
    print("=" * 60)

    manager = ComfyUIModelsManager()

    # Test 1: Types de modèles
    print("📋 Test 1: Récupération des types de modèles")
    model_types = manager.get_model_types()
    print(f"✅ Types trouvés: {len(model_types)}")
    for i, model_type in enumerate(model_types[:5]):  # Afficher les 5 premiers
        print(f"   {i+1}. {model_type}")
    if len(model_types) > 5:
        print(f"   ... et {len(model_types) - 5} autres")

    # Test 2: Modèles par type
    print(f"\n📋 Test 2: Modèles par type (exemple: checkpoints)")
    checkpoints = manager.get_models_by_type("checkpoints")
    print(f"✅ Checkpoints trouvés: {len(checkpoints)}")
    for i, checkpoint in enumerate(checkpoints[:3]):  # Afficher les 3 premiers
        print(f"   {i+1}. {checkpoint}")
    if len(checkpoints) > 3:
        print(f"   ... et {len(checkpoints) - 3} autres")

    # Test 3: Tous les modèles
    print(f"\n📋 Test 3: Récupération de tous les modèles")
    all_models = manager.get_all_models()
    total_models = sum(len(models) for models in all_models.values())
    print(f"✅ Total modèles: {total_models}")

    # Test 4: Liste plate
    print(f"\n📋 Test 4: Liste plate des modèles")
    flat_list = manager.get_models_flat_list()
    print(f"✅ Modèles dans la liste plate: {len(flat_list)}")
    if flat_list:
        print(f"   Exemple: {flat_list[0]}")

    print("\n✅ Tests terminés")


if __name__ == "__main__":
    test_models_manager()

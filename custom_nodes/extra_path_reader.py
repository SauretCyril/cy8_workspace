import os
import yaml
import json


from safetensors.torch import safe_open

class ExtraPathReader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("extra_paths_json",)
    FUNCTION = "read_paths"
    CATEGORY = "Utility"

    def _find_comfyui_root(self):
        """Trouve la racine du serveur ComfyUI en remontant depuis custom_nodes"""
        current_path = os.path.dirname(__file__)

        # Remonter jusqu'à trouver un dossier contenant les marqueurs de ComfyUI
        while current_path and current_path != os.path.dirname(current_path):
            # Vérifier la présence de fichiers/dossiers typiques de ComfyUI
            if (os.path.exists(os.path.join(current_path, "main.py")) and
                os.path.exists(os.path.join(current_path, "custom_nodes")) and
                os.path.exists(os.path.join(current_path, "models"))):
                return current_path
            current_path = os.path.dirname(current_path)

        return None

    def read_paths(self):
        # Trouver la racine du serveur ComfyUI dynamiquement
        comfyui_root = self._find_comfyui_root()

        if not comfyui_root:
            return ("Impossible de localiser la racine du serveur ComfyUI",)

        config_path = os.path.join(comfyui_root, "extra_model_paths.yaml")

        if not os.path.exists(config_path):
            return (f"Fichier extra_model_paths.yaml introuvable au chemin: {config_path}",)

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if config is None:
                return ("Fichier extra_model_paths.yaml vide ou invalide",)

            # Ajouter la racine ComfyUI détectée dans le résultat
            result = {
                "comfyui_root": comfyui_root,
                "config_path": config_path,
                "extra_paths": config
            }

            return (json.dumps(result, indent=2),)

        except Exception as e:
            return (f"Erreur lors de la lecture du fichier: {str(e)}",)


class PythonPathNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_python_path"

    def get_python_path(self):
        import sys
        return (sys.executable,)


class LoadModelMetadata:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_path": ("STRING", {"default": "models/Stable-diffusion/model.safetensors"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("metadata",)
    FUNCTION = "read_metadata"
    CATEGORY = "Custom/Model"

    def read_metadata(self, model_path):
        if not os.path.exists(model_path):
            return ("Fichier introuvable : " + model_path,)

        try:
            with safe_open(model_path, framework="pt") as f:
                metadata = f.metadata()
            formatted = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
            return (formatted,)
        except Exception as e:
            return (f"Erreur lors de la lecture : {str(e)}",)


# Enregistrement du node pour ComfyUI
NODE_CLASS_MAPPINGS = {
    "ExtraPathReader": ExtraPathReader,
    "LoadModelMetadata": LoadModelMetadata,
    "PythonPathNode": PythonPathNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExtraPathReader": "Extra Path Reader",
     "LoadModelMetadata": "📦 Lire métadonnées modèle"
}

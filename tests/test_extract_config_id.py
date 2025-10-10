#!/usr/bin/env python3
"""
Test de la fonction d'extraction d'ID depuis les extra paths
"""

import json


def test_extract_config_id():
    """Tester l'extraction d'ID de configuration depuis les données de test"""
    print("🧪 Test d'extraction d'ID de configuration")
    print("=" * 45)

    # Données de test basées sur le résultat du custom node
    test_data = {
        "comfyui": {
            "base_path": "G:/ComfyUI_G11/ComfyUI",
            "is_default": True,
            "checkpoints": "H:/comfyui/models/checkpoints",
            "embeddings": "H:/comfyui/models/embeddings",
            "loras": "H:/comfyui/models/loras",
            "vae": "H:/comfyui/models/vae",
            "clip_vision": "H:/comfyui/models/clip_vision",
            "style_models": "H:/comfyui/models/style_models",
            "controlnet": "H:/comfyui/models/controlnet",
            "upscale_models": "H:/comfyui/models/upscale_models",
            "custom_nodes": "H:/comfyui/G11_04/custom_nodes",
        }
    }

    print("📋 Données de test:")
    print(json.dumps(test_data, indent=2))
    print()

    # Test de notre fonction d'extraction
    config_id = extract_config_id_from_extra_paths(test_data)

    print(f"🆔 ID extrait: '{config_id}'")

    if config_id == "G11_04":
        print("✅ SUCCESS - ID correctement extrait!")
    else:
        print(f"❌ FAILED - Attendu 'G11_04', obtenu '{config_id}'")

    # Test avec d'autres variations
    print("\n🔍 Test avec différentes variations:")

    variations = [
        {
            "name": "Variation 1 - custom_nodes dans le chemin",
            "data": {
                "comfyui": {
                    "custom_nodes": "H:/comfyui/Production/custom_nodes",
                    "checkpoints": "H:/comfyui/models/checkpoints",
                }
            },
            "expected": "Production",
        },
        {
            "name": "Variation 2 - base_path avec ComfyUI",
            "data": {
                "comfyui": {
                    "base_path": "D:/AI/TestEnv/ComfyUI",
                    "checkpoints": "D:/AI/models/checkpoints",
                }
            },
            "expected": "TestEnv",
        },
        {
            "name": "Variation 3 - chemins avec sous-dossiers",
            "data": {
                "models": {
                    "checkpoints": "C:/ComfyUI/MySetup/ComfyUI/models/checkpoints",
                    "loras": "C:/ComfyUI/MySetup/models/loras",
                }
            },
            "expected": "MySetup",
        },
    ]

    for variation in variations:
        print(f"\n  {variation['name']}:")
        extracted = extract_config_id_from_extra_paths(variation["data"])
        expected = variation["expected"]
        status = "✅" if extracted == expected else "❌"
        print(f"    {status} Extrait: '{extracted}', Attendu: '{expected}'")


def extract_config_id_from_extra_paths(extra_paths_config):
    """Fonction d'extraction mise à jour (copie de celle dans le code principal)"""
    if not extra_paths_config or not isinstance(extra_paths_config, dict):
        return None

    import re

    # PRIORISER les chemins custom_nodes pour une détection plus précise
    custom_nodes_candidates = []
    other_candidates = []

    # Chercher dans toutes les valeurs de configuration
    for key, paths in extra_paths_config.items():
        if isinstance(paths, dict):
            # Parcourir tous les chemins dans cette section
            for path_key, path_value in paths.items():
                if isinstance(path_value, str):
                    # Chercher spécifiquement les chemins custom_nodes en priorité
                    if (
                        "custom_nodes" in path_key.lower()
                        or "custom_nodes" in path_value
                    ):
                        # Pattern spécifique pour custom_nodes: H:/comfyui/ID/custom_nodes
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
                                custom_nodes_candidates.append(candidate_id)

                    # Autres patterns pour chemins généraux
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
                                other_candidates.append(candidate_id)

        elif isinstance(paths, str):
            # Traiter le cas où la valeur est directement une chaîne
            if "custom_nodes" in paths:
                pattern = r".*[/\\]comfyui[/\\]([^/\\]+)[/\\]custom_nodes"
                match = re.search(pattern, paths, re.IGNORECASE)
                if match:
                    candidate_id = match.group(1)
                    custom_nodes_candidates.append(candidate_id)

    # Retourner le premier candidat custom_nodes s'il y en a un
    if custom_nodes_candidates:
        return custom_nodes_candidates[0]

    # Sinon, retourner le premier autre candidat
    if other_candidates:
        # Filtrer les doublons et les noms génériques
        filtered_candidates = []
        for candidate in other_candidates:
            if candidate not in filtered_candidates and candidate.lower() not in [
                "program files",
                "program files (x86)",
                "users",
            ]:
                filtered_candidates.append(candidate)

        if filtered_candidates:
            return filtered_candidates[0]

    # Si aucun ID spécifique n'est trouvé, retourner un ID par défaut basé sur le base_path si disponible
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


if __name__ == "__main__":
    test_extract_config_id()

    print("\n" + "=" * 50)
    print("💡 Cette fonction d'extraction est maintenant intégrée")
    print("   dans l'application principale pour identifier")
    print("   automatiquement l'environnement ComfyUI.")
    print("=" * 50)

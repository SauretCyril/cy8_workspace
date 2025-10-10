import requests
import os
import platform
import re
import json

def test_standard_identification():
    print('=== TEST IDENTIFICATION STANDARD API ===')

    server_url = "http://127.0.0.1:8188"

    # 1. Test de connexion
    print('🔗 Test de connexion au serveur ComfyUI...')
    try:
        response = requests.get(f"{server_url}/system_stats", timeout=10)
        if response.status_code == 200:
            print('✅ Serveur accessible')
            stats = response.json()
            print(f'📊 Stats reçues: {len(stats)} entrées')

            # Afficher les stats pour voir s'il y a des indices
            print('\n=== SYSTEM STATS ===')
            for key, value in stats.items():
                print(f'{key}: {value}')
                # Chercher des patterns dans les valeurs
                if isinstance(value, str):
                    patterns = [r'([A-Z]\d+[_-]\d+)', r'([A-Z]\d+)']
                    for pattern in patterns:
                        match = re.search(pattern, value.upper())
                        if match:
                            print(f'  -> Pattern trouvé: {match.group(1)}')
        else:
            print(f'❌ Erreur de connexion: {response.status_code}')
            return

    except Exception as e:
        print(f'❌ Impossible de se connecter: {e}')
        return

    # 2. Test object_info
    print('\n🔗 Test object_info...')
    try:
        response = requests.get(f"{server_url}/object_info", timeout=10)
        if response.status_code == 200:
            object_info = response.json()
            print(f'✅ Object info reçu: {len(object_info)} types')
        else:
            print(f'❌ Erreur object_info: {response.status_code}')
            object_info = {}
    except Exception as e:
        print(f'❌ Erreur object_info: {e}')
        object_info = {}

    # 3. Analyser les chemins potentiels
    print('\n📂 Analyse des chemins potentiels...')
    potential_paths = []

    # Variables d'environnement
    env_vars = ['COMFYUI_PATH', 'COMFYUI_ROOT', 'COMFYUI_DIR', 'PYTHONPATH', 'PATH', 'PWD', 'CD']
    for var in env_vars:
        value = os.environ.get(var)
        if value and 'comfyui' in value.lower():
            potential_paths.append(value)
            print(f'📂 Variable {var}: {value}')

    # Répertoire courant
    try:
        cwd = os.getcwd()
        if 'comfyui' in cwd.lower():
            potential_paths.append(cwd)
            print(f'📂 Répertoire courant: {cwd}')
    except:
        pass

    print(f'\nChemins potentiels trouvés: {len(potential_paths)}')
    for path in potential_paths:
        print(f'  - {path}')

    # 4. Appliquer la logique d'extraction
    print('\n🔍 Application de la logique d\'extraction...')

    if not potential_paths:
        print('⚠️ Aucun chemin potentiel trouvé')
        # Fallback basé sur le hostname
        hostname = platform.node()
        print(f'🖥️ Hostname: {hostname}')

        hostname_patterns = [
            r'([A-Z]\d+[-_]\d+)',  # H12-01 ou H12_01
            r'([A-Z]\d+)',  # H12
        ]

        for pattern in hostname_patterns:
            match = re.search(pattern, hostname.upper())
            if match:
                env_id = match.group(1).replace('-', '_')
                print(f'✅ Environment ID dérivé du hostname: {env_id}')
                return env_id

        print('❌ Aucun pattern trouvé dans le hostname')
        return None

    # Patterns de recherche
    patterns = [
        r".*[/\\]([A-Z]\d+_\d+)[/\\]?",  # H12_01, G11_03
        r".*[/\\]Comfyui[_-]([A-Z]\d+[_-]\d+)[/\\]?",  # Comfyui_H12_01
        r".*[/\\]comfyui[/\\]([A-Z]\d+[_-]\d+)[/\\]?",  # comfyui/H12_01
        r".*[/\\]ComfyUI[_-]([A-Z]\d+[_-]\d+)[/\\]?",  # ComfyUI_H12_01
        r".*([A-Z]\d+[_-]\d+).*ComfyUI",  # H12_01 quelque part avant ComfyUI
    ]

    for path in potential_paths:
        print(f'🔍 Analyse du chemin: {path}')

        for i, pattern in enumerate(patterns):
            match = re.search(pattern, path, re.IGNORECASE)
            if match:
                env_id = match.group(1).replace('-', '_').upper()
                print(f'✅ Environment ID trouvé (pattern {i+1}): {env_id}')
                return env_id

    return None

if __name__ == "__main__":
    result = test_standard_identification()
    print(f'\n🎯 RÉSULTAT FINAL: {result}')

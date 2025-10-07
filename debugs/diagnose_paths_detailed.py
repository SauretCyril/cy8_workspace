import os
import platform
import re

print('=== DIAGNOSTIC DÉTAILLÉ DES CHEMINS ===')
print(f'Hostname: {platform.node()}')
print(f'Username: {os.environ.get("USERNAME", "N/A")}')
print(f'Répertoire courant: {os.getcwd()}')

# Toutes les variables d'environnement qui pourraient contenir ComfyUI
env_vars = [
    'COMFYUI_PATH', 'COMFYUI_ROOT', 'COMFYUI_DIR',
    'PYTHONPATH', 'PATH', 'PWD', 'CD'
]

potential_paths = []

print('\n=== VARIABLES D\'ENVIRONNEMENT ===')
for var in env_vars:
    value = os.environ.get(var)
    if value:
        print(f'{var}: {value}')
        if 'comfyui' in value.lower():
            potential_paths.append(value)
            print(f'  -> AJOUTÉ aux chemins potentiels')

# Répertoire courant
try:
    cwd = os.getcwd()
    print(f'\nRépertoire courant: {cwd}')
    if 'comfyui' in cwd.lower():
        potential_paths.append(cwd)
        print('  -> AJOUTÉ aux chemins potentiels')
except:
    pass

print(f'\n=== CHEMINS POTENTIELS TROUVÉS ({len(potential_paths)}) ===')
for i, path in enumerate(potential_paths):
    print(f'{i+1}. {path}')

# Patterns de détection
patterns = [
    r".*[/\\]([A-Z]\d+_\d+)[/\\]?",  # H12_01, G11_03
    r".*[/\\]Comfyui[_-]([A-Z]\d+[_-]\d+)[/\\]?",  # Comfyui_H12_01
    r".*[/\\]comfyui[/\\]([A-Z]\d+[_-]\d+)[/\\]?",  # comfyui/H12_01
    r".*[/\\]ComfyUI[_-]([A-Z]\d+[_-]\d+)[/\\]?",  # ComfyUI_H12_01
    r".*([A-Z]\d+[_-]\d+).*ComfyUI",  # H12_01 quelque part avant ComfyUI
]

print('\n=== ANALYSE DES PATTERNS ===')
found_ids = []

for i, path in enumerate(potential_paths):
    print(f'\n📂 Chemin {i+1}: {path}')

    for j, pattern in enumerate(patterns):
        match = re.search(pattern, path, re.IGNORECASE)
        if match:
            env_id = match.group(1).replace('-', '_').upper()
            print(f'  ✅ Pattern {j+1}: {env_id}')
            if env_id not in found_ids:
                found_ids.append(env_id)
        else:
            print(f'  ❌ Pattern {j+1}: aucun match')

print(f'\n=== RÉSULTATS ===')
print(f'IDs trouvés: {found_ids}')
if found_ids:
    print(f'Premier ID retourné: {found_ids[0]}')
else:
    print('Aucun ID trouvé')

# Analyse du PATH en détail
print('\n=== ANALYSE DÉTAILLÉE DU PATH ===')
path_env = os.environ.get('PATH', '')
path_entries = path_env.split(os.pathsep)
comfyui_entries = [entry for entry in path_entries if 'comfyui' in entry.lower()]

print(f'Entrées PATH contenant "comfyui": {len(comfyui_entries)}')
for i, entry in enumerate(comfyui_entries):
    print(f'{i+1}. {entry}')
    for j, pattern in enumerate(patterns):
        match = re.search(pattern, entry, re.IGNORECASE)
        if match:
            env_id = match.group(1).replace('-', '_').upper()
            print(f'    -> Pattern {j+1}: {env_id}')

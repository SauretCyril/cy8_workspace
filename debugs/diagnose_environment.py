import os
import platform
import re

print('=== DIAGNOSTIC ENVIRONNEMENT ===')
print(f'Hostname: {platform.node()}')
print(f'Username: {os.environ.get("USERNAME", "N/A")}')
print(f'Répertoire courant: {os.getcwd()}')

# Variables d'environnement
env_vars = ['COMFYUI_PATH', 'COMFYUI_ROOT', 'COMFYUI_DIR', 'PATH']
for var in env_vars:
    value = os.environ.get(var)
    if value and 'comfyui' in value.lower():
        print(f'{var}: {value}')

# Analyse des chemins
patterns = [
    r'.*[/\\]([A-Z]\d+_\d+)[/\\]?',
    r'.*[/\\]Comfyui[_-]([A-Z]\d+[_-]\d+)[/\\]?',
    r'.*([A-Z]\d+[_-]\d+).*ComfyUI'
]

test_paths = [
    'H:/ComfyUI_H12_01/',
    'H:/Comfyui_H12_01/ComfyUI/',
    'H:/H12_01/ComfyUI/',
    'G:/Comfyui_G11_03/'
]

print('\n=== TEST PATTERNS ===')
for path in test_paths:
    print(f'Test chemin: {path}')
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, path, re.IGNORECASE)
        if match:
            env_id = match.group(1).replace('-', '_').upper()
            print(f'  Pattern {i+1}: {env_id}')

# Analyse du PATH système
print('\n=== ANALYSE PATH ===')
path_env = os.environ.get('PATH', '')
path_entries = path_env.split(os.pathsep)
for entry in path_entries:
    if 'comfyui' in entry.lower():
        print(f'PATH entry: {entry}')
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, entry, re.IGNORECASE)
            if match:
                env_id = match.group(1).replace('-', '_').upper()
                print(f'  -> Pattern {i+1}: {env_id}')

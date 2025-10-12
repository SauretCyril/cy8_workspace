import json
import os

# Chemin vers ton workflow
workflow_path = "path/to/your/workflow.json"
custom_nodes_dir = "ComfyUI/custom_nodes"

# Charge le workflow
with open(workflow_path, "r", encoding="utf-8") as f:
    workflow = json.load(f)

# Récupère tous les types de nodes utilisés
used_nodes = {node["type"] for node in workflow["nodes"]}

# Liste les nodes disponibles dans ton installation
available_nodes = set()
for root, dirs, files in os.walk(custom_nodes_dir):
    for file in files:
        if file.endswith(".py"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                content = f.read()
                # Recherche naïve des définitions de nodes
                if "NODE_CLASS_MAPPINGS" in content:
                    available_nodes.update(content.split("NODE_CLASS_MAPPINGS")[1])

# Compare et affiche les nodes manquants
missing_nodes = [node for node in used_nodes if node not in str(available_nodes)]

if missing_nodes:
    print("🧩 Nodes manquants détectés :")
    for node in missing_nodes:
        print(f" - {node}")
    print("\n👉 Tu peux les rechercher manuellement dans ComfyUI-Manager ou automatiser leur installation.")
else:
    print("✅ Tous les nodes sont disponibles.")

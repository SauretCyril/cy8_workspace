#!/usr/bin/env python3
"""
Test direct du workflow ComfyUI pour diagnostiquer l'erreur 400
"""
import sys
import os
sys.path.append('src')

from cy6_wkf001_Basic import comfyui_basic_task

def test_direct_workflow():
    """Test direct d'exécution de workflow"""
    workflow_file = "data/Workflows/test_workflow.json"
    values_file = "data/Workflows/test_values.json"

    print(f"Test avec:")
    print(f"  Workflow: {workflow_file}")
    print(f"  Values: {values_file}")

    if not os.path.exists(workflow_file):
        print(f"❌ Fichier workflow introuvable: {workflow_file}")
        return

    if not os.path.exists(values_file):
        print(f"❌ Fichier values introuvable: {values_file}")
        return

    try:
        print("🔄 Création de la tâche ComfyUI...")
        task = comfyui_basic_task()

        print("🔄 Envoi à la queue ComfyUI...")
        prompt_id = task.addToQueue(workflow_file, values_file)

        print(f"✅ Prompt envoyé avec ID: {prompt_id}")

        print("🔄 Récupération des images...")
        images = task.GetImages(prompt_id)

        if images:
            print(f"✅ {len(images)} images récupérées")
        else:
            print("⚠️  Aucune image récupérée")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_workflow()

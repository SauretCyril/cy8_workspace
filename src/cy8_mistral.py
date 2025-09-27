import requests
import sys
import os
import time
from dotenv import load_dotenv


def get_mistral_answer(question, role, texte):
    try:
        # Charger le fichier .env
        load_dotenv()

        # Récupérer la clé API Mistral depuis les variables d'environnement
        print(f"Python utilisé dans cy_mistral.py : {sys.executable}")
        api_key = os.getenv("MISTRAL_API_KEY")

        if not api_key:
            raise ValueError("La clé API Mistral n'est pas définie dans le fichier .env")

        # Construire les messages pour l'API
        messages = [
            {"role": "system", "content": role},
            {"role": "user", "content": f"Contenu: {texte}\n\nQuestion: {question}"}
        ]

        # Configuration de la requête à l'API Mistral
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Données à envoyer à l'API Mistral
        data = {
            "model": "mistral-medium",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 9000  # Augmenter cette valeur (était 5000)
        }

        # Appel à l'API Mistral
        time.sleep(10)
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Ajoute cette ligne
        response_json = response.json()
        if "choices" in response_json and response_json["choices"]:
            content = response_json["choices"][0]["message"]["content"]
            print(f"dbg-678 : Réponse de l'API Mistral: {content}")
            return content
        else:
            # Retourner le message d'erreur de l'API si présent
            error_msg = response_json.get("error", "Réponse inattendue de l'API Mistral")
            return f'{{"error": "{error_msg}"}}'
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            print(f"dbg-678 : Trop de requêtes envoyées à l'API Mistral: {e}")
            return '{"error": "Trop de requêtes envoyées à l\'API Mistral. Merci de patienter avant de réessayer."}'
        else:
            print(f"dbg-678 : Erreur de l'API Mistral: {e}")
            return f'{{"error": "Erreur lors de l\'appel à l\'API Mistral: {str(e)}"}}'
    except Exception as e:
        print(f"dbg-678 : Erreur inattendue: {e}")
        return f'{{"error": "Erreur lors de l\'appel à l\'API Mistral: {str(e)}"}}'

"""
Gestionnaire d'identifiants uniques pour les popups
Facilite la communication et le debug des interfaces
"""

from datetime import datetime
import threading


class PopupIdManager:
    """Gestionnaire centralisé des identifiants de popups"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PopupIdManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            self._popup_counter = 0
            self._active_popups = {}
            self._popup_history = []
            self._initialized = True

    def get_next_id(self) -> str:
        """Générer le prochain identifiant de popup"""
        with self._lock:
            self._popup_counter += 1
            popup_id = f"POP{self._popup_counter:03d}"
            return popup_id

    def register_popup(self, popup_id: str, title: str, popup_type: str = "dialog"):
        """Enregistrer une popup active"""
        popup_info = {
            "title": title,
            "type": popup_type,
            "created_at": datetime.now().strftime("%H:%M:%S"),
            "status": "active"
        }

        with self._lock:
            self._active_popups[popup_id] = popup_info
            self._popup_history.append({
                "id": popup_id,
                "title": title,
                "type": popup_type,
                "timestamp": datetime.now().isoformat()
            })

        print(f"📋 Popup créée: {popup_id} - {title}")

    def unregister_popup(self, popup_id: str):
        """Désenregistrer une popup fermée"""
        with self._lock:
            if popup_id in self._active_popups:
                popup_info = self._active_popups[popup_id]
                popup_info["status"] = "closed"
                popup_info["closed_at"] = datetime.now().strftime("%H:%M:%S")
                del self._active_popups[popup_id]
                print(f"✅ Popup fermée: {popup_id}")

    def get_active_popups(self) -> dict:
        """Obtenir la liste des popups actives"""
        with self._lock:
            return self._active_popups.copy()

    def get_popup_history(self) -> list:
        """Obtenir l'historique des popups"""
        with self._lock:
            return self._popup_history.copy()

    def format_title(self, base_title: str, popup_type: str = "dialog") -> tuple:
        """Formater un titre avec identifiant unique"""
        popup_id = self.get_next_id()
        formatted_title = f"[{popup_id}] {base_title}"
        self.register_popup(popup_id, base_title, popup_type)
        return popup_id, formatted_title

    def print_status(self):
        """Afficher le statut des popups pour debug"""
        print(f"\n📊 État des popups:")
        print(f"   Actives: {len(self._active_popups)}")
        print(f"   Total créées: {self._popup_counter}")

        if self._active_popups:
            print("   🔍 Popups actives:")
            for popup_id, info in self._active_popups.items():
                print(f"     - {popup_id}: {info['title']} ({info['created_at']})")


# Instance globale
popup_manager = PopupIdManager()


def get_popup_id(title: str, popup_type: str = "dialog") -> tuple:
    """Fonction helper pour obtenir un ID de popup"""
    return popup_manager.format_title(title, popup_type)


def close_popup(popup_id: str):
    """Fonction helper pour fermer une popup"""
    popup_manager.unregister_popup(popup_id)

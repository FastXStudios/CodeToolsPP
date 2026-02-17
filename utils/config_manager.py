import json
import os

class ConfigManager:
    """Gestiona la configuración persistente de la aplicación"""
    
    def __init__(self, config_file="data/config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Carga la configuración desde el archivo"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._default_config()
        return self._default_config()
    
    def _default_config(self):
        """Configuración por defecto"""
        return {
            "theme": "dark",
            "last_folder": "",
            "window_geometry": "1200x800",
            "show_hidden_files": False,
            "auto_expand_depth": 1,
            "preview_window_visible": True,
            "recent_folders": [],
            "animated_toolbar_background": True
        }
    
    def save(self):
        """Guarda la configuración actual"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Obtiene un valor de configuración"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Establece un valor de configuración"""
        self.config[key] = value
        self.save()
    
    def add_recent_folder(self, folder_path):
        """Agrega una carpeta al historial"""
        recent = self.config.get("recent_folders", [])
        if folder_path in recent:
            recent.remove(folder_path)
        recent.insert(0, folder_path)
        self.config["recent_folders"] = recent[:10]  # Mantener solo las últimas 10
        self.save()
    
    def get_recent_folders(self):
        """Obtiene el historial de carpetas"""
        return self.config.get("recent_folders", [])

import json
import os

class ThemeManager:
    """Gestor de temas con 5 opciones profesionales"""
    
    THEMES = {
        "light": {
            "name": "Claro",
            "bg": "#ffffff",
            "fg": "#000000",
            "secondary_bg": "#f8f9fa",
            "accent": "#3498db",
            "accent_hover": "#2980b9",
            "border": "#dce1e8",
            "tree_bg": "#ffffff",
            "tree_fg": "#2c3e50",
            "tree_selected_bg": "#3498db",
            "tree_selected_fg": "#000000",
            "button_bg": "#3498db",
            "button_fg": "#000000",
            "button_hover": "#2980b9",
            "status_bg": "#ecf0f1",
            "status_fg": "#000000",
            "warning": "#e74c3c",
            "success": "#27ae60",
            "info": "#3498db"
        },
        "pink_pastel": {
            "name": "Pink Pastel",
            "bg": "#fff0f6",
            "fg": "#3a2e39",
            "secondary_bg": "#ffe3ec",
            "accent": "#ff8fab",
            "accent_hover": "#ff6f91",
            "border": "#f8c8dc",
            "tree_bg": "#fff0f6",
            "tree_fg": "#3a2e39",
            "tree_selected_bg": "#ff8fab",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#ff8fab",
            "button_fg": "#ffffff",
            "button_hover": "#ff6f91",
            "status_bg": "#ffe3ec",
            "status_fg": "#3a2e39",
            "warning": "#ff4d6d",
            "success": "#57cc99",
            "info": "#a0c4ff"
        },
        "dark": {
            "name": "Oscuro",
            "bg": "#1e1e1e",
            "fg": "#d4d4d4",
            "secondary_bg": "#252526",
            "accent": "#007acc",
            "accent_hover": "#005a9e",
            "border": "#3e3e42",
            "tree_bg": "#252526",
            "tree_fg": "#cccccc",
            "tree_selected_bg": "#094771",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#0e639c",
            "button_fg": "#ffffff",
            "button_hover": "#1177bb",
            "status_bg": "#007acc",
            "status_fg": "#ffffff",
            "warning": "#f48771",
            "success": "#89d185",
            "info": "#75beff"
        },
        "darkForce": {
            "name": "Oscuro Profundo",
            "bg": "#121212",              # fondo principal más profundo
            "fg": "#e0e0e0",              # texto ligeramente más claro
            "secondary_bg": "#1a1a1a",    # paneles secundarios
            "accent": "#3399ff",          # azul más vivo para contraste
            "accent_hover": "#1f6feb",
            "border": "#2a2a2a",          # borde más discreto
            "tree_bg": "#181818",         # árbol más oscuro
            "tree_fg": "#dddddd",
            "tree_selected_bg": "#1f3a5f", # selección menos brillante pero intensa
            "tree_selected_fg": "#ffffff",
            "button_bg": "#1f6feb",
            "button_fg": "#ffffff",
            "button_hover": "#2b7cff",
            "status_bg": "#1a1a1a",
            "status_fg": "#cccccc",
            "warning": "#ff6b6b",
            "success": "#4caf50",
            "info": "#4da6ff"
        },
        "rose_gold": {
            "name": "Rose Gold",
            "bg": "#1f1a1d",
            "fg": "#ffeef2",
            "secondary_bg": "#2a2326",
            "accent": "#e8a0bf",
            "accent_hover": "#d67fa7",
            "border": "#3a2f34",
            "tree_bg": "#2a2326",
            "tree_fg": "#ffeef2",
            "tree_selected_bg": "#e8a0bf",
            "tree_selected_fg": "#1f1a1d",
            "button_bg": "#e8a0bf",
            "button_fg": "#1f1a1d",
            "button_hover": "#d67fa7",
            "status_bg": "#2a2326",
            "status_fg": "#ffeef2",
            "warning": "#ff6b81",
            "success": "#6dd3a0",
            "info": "#f8b4d9"
        },
        "blue_night": {
            "name": "Azul Nocturno",
            "bg": "#0f1419",
            "fg": "#bfbdb6",
            "secondary_bg": "#1a1f29",
            "accent": "#59c2ff",
            "accent_hover": "#39a2df",
            "border": "#2d3640",
            "tree_bg": "#1a1f29",
            "tree_fg": "#bfbdb6",
            "tree_selected_bg": "#273747",
            "tree_selected_fg": "#59c2ff",
            "button_bg": "#1565c0",
            "button_fg": "#ffffff",
            "button_hover": "#1976d2",
            "status_bg": "#0d47a1",
            "status_fg": "#ffffff",
            "warning": "#ff6b6b",
            "success": "#51cf66",
            "info": "#59c2ff"
        },
        "purple_neon": {
            "name": "Morado Neón",
            "bg": "#1a0933",
            "fg": "#e0c3fc",
            "secondary_bg": "#2d1454",
            "accent": "#bf40bf",
            "accent_hover": "#9f209f",
            "border": "#4a2770",
            "tree_bg": "#2d1454",
            "tree_fg": "#e0c3fc",
            "tree_selected_bg": "#6a1b9a",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#8e24aa",
            "button_fg": "#ffffff",
            "button_hover": "#7b1fa2",
            "status_bg": "#6a1b9a",
            "status_fg": "#ffffff",
            "warning": "#ff4081",
            "success": "#69f0ae",
            "info": "#bf40bf"
        },
        "matrix": {
            "name": "Verde Matrix",
            "bg": "#0d0208",
            "fg": "#00ff41",
            "secondary_bg": "#1a1a1a",
            "accent": "#00ff41",
            "accent_hover": "#00cc33",
            "border": "#003b00",
            "tree_bg": "#0d0208",
            "tree_fg": "#00ff41",
            "tree_selected_bg": "#003b00",
            "tree_selected_fg": "#00ff41",
            "button_bg": "#008f11",
            "button_fg": "#00ff41",
            "button_hover": "#00b814",
            "status_bg": "#001a00",
            "status_fg": "#00ff41",
            "warning": "#ff0000",
            "success": "#00ff41",
            "info": "#00ff41"
        },
        "solar_warm": {
            "name": "Solar Cálido",
            "bg": "#fdf6e3",
            "fg": "#000000",
            "secondary_bg": "#eee8d5",
            "accent": "#b58900",
            "accent_hover": "#9c6f00",
            "border": "#d5cdb6",
            "tree_bg": "#fdf6e3",
            "tree_fg": "#3c3836",
            "tree_selected_bg": "#b58900",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#b58900",
            "button_fg": "#000000",
            "button_hover": "#9c6f00",
            "status_bg": "#eee8d5",
            "status_fg": "#000000",
            "warning": "#dc322f",
            "success": "#859900",
            "info": "#268bd2"
        },
        "barbie_glam": {
            "name": "Barbie Glam",
            "bg": "#14080e",
            "fg": "#ffffff",
            "secondary_bg": "#2a0d1a",
            "accent": "#ff007f",
            "accent_hover": "#e60073",
            "border": "#3d1024",
            "tree_bg": "#2a0d1a",
            "tree_fg": "#ffffff",
            "tree_selected_bg": "#ff007f",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#ff007f",
            "button_fg": "#ffffff",
            "button_hover": "#e60073",
            "status_bg": "#2a0d1a",
            "status_fg": "#ffffff",
            "warning": "#ff4d4d",
            "success": "#00f5d4",
            "info": "#ff99cc"
        },
        "deep_ocean": {
            "name": "Océano Profundo",
            "bg": "#0b1e2d",
            "fg": "#d6e4f0",
            "secondary_bg": "#112b3c",
            "accent": "#1f8ef1",
            "accent_hover": "#0d6efd",
            "border": "#1c3a4b",
            "tree_bg": "#112b3c",
            "tree_fg": "#d6e4f0",
            "tree_selected_bg": "#1f8ef1",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#1f8ef1",
            "button_fg": "#ffffff",
            "button_hover": "#0d6efd",
            "status_bg": "#0b1e2d",
            "status_fg": "#d6e4f0",
            "warning": "#ff6b6b",
            "success": "#38d39f",
            "info": "#4dabf7"
        },
        "sakura_soft": {
            "name": "Sakura Suave",
            "bg": "#1e1a24",
            "fg": "#ffffff",
            "secondary_bg": "#2a2438",
            "accent": "#ff79c6",
            "accent_hover": "#ff5eb3",
            "border": "#3b3350",
            "tree_bg": "#2a2438",
            "tree_fg": "#ffffff",
            "tree_selected_bg": "#ff79c6",
            "tree_selected_fg": "#1e1a24",
            "button_bg": "#ff79c6",
            "button_fg": "#ffffff",        # ← ahora blanco
            "button_hover": "#ff5eb3",
            "status_bg": "#2a2438",
            "status_fg": "#ffffff",
            "warning": "#ff5555",
            "success": "#50fa7b",
            "info": "#8be9fd"
        },
        "lavender_dream": {
            "name": "Lavender Dream",
            "bg": "#f8f4ff",
            "fg": "#2b2d42",
            "secondary_bg": "#e6dcff",
            "accent": "#b983ff",
            "accent_hover": "#9d6bff",
            "border": "#d4c6ff",
            "tree_bg": "#f8f4ff",
            "tree_fg": "#2b2d42",
            "tree_selected_bg": "#b983ff",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#b983ff",
            "button_fg": "#ffffff",
            "button_hover": "#9d6bff",
            "status_bg": "#e6dcff",
            "status_fg": "#2b2d42",
            "warning": "#ff6b6b",
            "success": "#4caf50",
            "info": "#7b2cbf"
        },

        "crimson_blood": {
            "name": "Crimson Blood",
            "bg": "#0f0a0a",
            "fg": "#ffeaea",
            "secondary_bg": "#1a0f0f",
            "accent": "#b11226",
            "accent_hover": "#8f0e1f",
            "border": "#2a1515",
            "tree_bg": "#1a0f0f",
            "tree_fg": "#ffeaea",
            "tree_selected_bg": "#b11226",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#b11226",
            "button_fg": "#ffffff",
            "button_hover": "#8f0e1f",
            "status_bg": "#1a0f0f",
            "status_fg": "#ffeaea",
            "warning": "#ff4d4d",
            "success": "#3ddc97",
            "info": "#ff8787"
        },

        "pure_white_pro": {
            "name": "Pure White Pro",
            "bg": "#ffffff",
            "fg": "#111111",
            "secondary_bg": "#f5f7fa",
            "accent": "#111111",
            "accent_hover": "#333333",
            "border": "#e0e6ed",
            "tree_bg": "#ffffff",
            "tree_fg": "#111111",
            "tree_selected_bg": "#111111",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#111111",
            "button_fg": "#ffffff",
            "button_hover": "#333333",
            "status_bg": "#f5f7fa",
            "status_fg": "#111111",
            "warning": "#e63946",
            "success": "#2a9d8f",
            "info": "#457b9d"
        },
        "arctic_minimal": {
            "name": "Ártico Minimal",
            "bg": "#1c1f26",
            "fg": "#e6edf3",
            "secondary_bg": "#242933",
            "accent": "#4f9cff",
            "accent_hover": "#3a86ff",
            "border": "#2e3440",
            "tree_bg": "#242933",
            "tree_fg": "#e6edf3",
            "tree_selected_bg": "#4f9cff",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#4f9cff",
            "button_fg": "#ffffff",
            "button_hover": "#3a86ff",
            "status_bg": "#242933",
            "status_fg": "#e6edf3",
            "warning": "#ff7b72",
            "success": "#3fb950",
            "info": "#79c0ff"
        },
        "ember_dark": {
            "name": "Ember Oscuro",
            "bg": "#181414",
            "fg": "#fff4f0",               # ← super claro cálido
            "secondary_bg": "#221a1a",
            "accent": "#ff7849",
            "accent_hover": "#ff5e2b",
            "border": "#3a2a2a",
            "tree_bg": "#221a1a",
            "tree_fg": "#fff4f0",          # ← texto del tree más brillante
            "tree_selected_bg": "#ff7849",
            "tree_selected_fg": "#181414",
            "button_bg": "#ff7849",
            "button_fg": "#fff4f0",        # ← texto botón claro también
            "button_hover": "#ff5e2b",
            "status_bg": "#221a1a",
            "status_fg": "#fff4f0",
            "warning": "#ff4d4d",
            "success": "#4caf50",
            "info": "#ffb347"
        },
        "aurora": {
            "name": "Aurora",
            "bg": "#141e30",
            "fg": "#f0f6ff",
            "secondary_bg": "#1f2a44",
            "accent": "#7f5af0",
            "accent_hover": "#6246ea",
            "border": "#2d3a5a",
            "tree_bg": "#1b2440",
            "tree_fg": "#f0f6ff",
            "tree_selected_bg": "#6246ea",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#7f5af0",
            "button_fg": "#ffffff",
            "button_hover": "#6246ea",
            "status_bg": "#1f2a44",
            "status_fg": "#f0f6ff",
            "warning": "#ff6b6b",
            "success": "#2ecc71",
            "info": "#4cc9f0"
        },
        "sunset_neon": {
            "name": "Sunset Neon",
            "bg": "#1a0f0f",
            "fg": "#fff5f0",
            "secondary_bg": "#2b1616",
            "accent": "#ff4d6d",
            "accent_hover": "#e03150",
            "border": "#402020",
            "tree_bg": "#2b1616",
            "tree_fg": "#fff5f0",
            "tree_selected_bg": "#ff4d6d",
            "tree_selected_fg": "#1a0f0f",
            "button_bg": "#ff4d6d",
            "button_fg": "#ffffff",
            "button_hover": "#e03150",
            "status_bg": "#2b1616",
            "status_fg": "#fff5f0",
            "warning": "#ff8787",
            "success": "#69db7c",
            "info": "#ffa94d"
        },
        "cosmic_purple": {
            "name": "Cosmic Purple",
            "bg": "#0d0614",              # más oscuro y profundo
            "fg": "#f5e9ff",              # texto más brillante
            "secondary_bg": "#170b24",
            "accent": "#c026ff",          # púrpura más saturado
            "accent_hover": "#a000f5",
            "border": "#2a1140",
            "tree_bg": "#170b24",
            "tree_fg": "#f5e9ff",
            "tree_selected_bg": "#c026ff",
            "tree_selected_fg": "#0d0614",
            "button_bg": "#c026ff",
            "button_fg": "#ffffff",
            "button_hover": "#a000f5",
            "status_bg": "#170b24",
            "status_fg": "#f5e9ff",
            "warning": "#ff4d6d",
            "success": "#39ffb6",
            "info": "#8a2eff"
        },
        "cyber_blue": {
            "name": "Cyber Blue",
            "bg": "#0a0f1c",
            "fg": "#ffffff",
            "secondary_bg": "#11182a",
            "accent": "#00c2ff",
            "accent_hover": "#009edb",
            "border": "#1e2a44",
            "tree_bg": "#11182a",
            "tree_fg": "#ffffff",
            "tree_selected_bg": "#00c2ff",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#00c2ff",
            "button_fg": "#ffffff",
            "button_hover": "#009edb",
            "status_bg": "#11182a",
            "status_fg": "#ffffff",
            "warning": "#ff6b6b",
            "success": "#38d39f",
            "info": "#4dabf7"
        },
        "forest_glass": {
            "name": "Forest Glass",
            "bg": "#0f1a14",
            "fg": "#ffffff",
            "secondary_bg": "#16251d",
            "accent": "#2ecc71",
            "accent_hover": "#27ae60",
            "border": "#1f3328",
            "tree_bg": "#16251d",
            "tree_fg": "#ffffff",
            "tree_selected_bg": "#2ecc71",
            "tree_selected_fg": "#ffffff",
            "button_bg": "#2ecc71",
            "button_fg": "#ffffff",
            "button_hover": "#27ae60",
            "status_bg": "#16251d",
            "status_fg": "#ffffff",
            "warning": "#ff7675",
            "success": "#2ecc71",
            "info": "#74b9ff"
        },
    }

    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.current_theme = "solar_warm"
        self._observers = []  # ← AGREGAR
        if config_manager:
            self.current_theme = config_manager.get("theme", "solar_warm")
    
    def get_theme(self, theme_name=None):
        """Obtiene un tema por nombre o el actual"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.THEMES.get(theme_name, self.THEMES["dark"])
    
    def subscribe(self, callback):
        """Registra una ventana para recibir actualizaciones de tema."""
        if callback not in self._observers:
            self._observers.append(callback)

    def unsubscribe(self, callback):
        """Elimina el registro de una ventana."""
        if callback in self._observers:
            self._observers.remove(callback)

    def set_theme(self, theme_name):
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            if self.config_manager:
                self.config_manager.set("theme", theme_name)
            # ← AGREGAR: notificar a todos los observers
            self._notify_observers()
            return True
        return False

    def _notify_observers(self):
        dead = []
        for cb in self._observers:
            try:
                cb()
            except Exception:
                dead.append(cb)
        for cb in dead:
            self._observers.remove(cb)
    
    def get_all_themes(self):
        """Retorna todos los temas disponibles"""
        return self.THEMES
    
    def get_theme_names(self):
        """Retorna lista de nombres de temas"""
        return list(self.THEMES.keys())
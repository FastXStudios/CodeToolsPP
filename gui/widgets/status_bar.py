import tkinter as tk
from tkinter import ttk, Canvas

class StatusBar(tk.Frame):
    """Barra de estado moderna con información en tiempo real"""
    
    def __init__(self, parent, theme_manager, language_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        
        self.configure(relief="flat", bd=0, height=35)
        
        # Etiquetas de estado
        self.labels = {}
        self._stats_cache = {
            "total_files": 0,
            "selected_files": 0,
            "total_lines": 0,
            "size_formatted": "0 B",
        }
        
        # Frame interno con padding
        inner_frame = tk.Frame(self)
        inner_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Total de archivos
        self.labels['files'] = tk.Label(
            inner_frame, text="Files: 0", 
            anchor="w", font=("Segoe UI", 9)
        )
        self.labels['files'].pack(side="left", padx=10)
        
        # Separador vertical moderno
        self._add_separator(inner_frame)
        
        # Archivos seleccionados
        self.labels['selected'] = tk.Label(
            inner_frame, text="Selected: 0", 
            anchor="w", font=("Segoe UI", 9, "bold")
        )
        self.labels['selected'].pack(side="left", padx=10)
        
        # Separador
        self._add_separator(inner_frame)
        
        # Líneas de código
        self.labels['lines'] = tk.Label(
            inner_frame, text="Lines: 0", 
            anchor="w", font=("Segoe UI", 9)
        )
        self.labels['lines'].pack(side="left", padx=10)
        
        # Separador
        self._add_separator(inner_frame)
        
        # Tamaño total
        self.labels['size'] = tk.Label(
            inner_frame, text="Size: 0 B", 
            anchor="w", font=("Segoe UI", 9)
        )
        self.labels['size'].pack(side="left", padx=10)
        
        # Mensaje general (derecha) con icono
        self.labels['message'] = tk.Label(
            inner_frame, text="● Ready", 
            anchor="e", font=("Segoe UI", 9), fg="#27ae60"
        )
        self.labels['message'].pack(side="right", fill="x", expand=True, padx=10)
        
        self.apply_theme()
    
    def _add_separator(self, parent):
        """Agrega un separador vertical moderno"""
        canvas = Canvas(parent, width=2, height=20, highlightthickness=0)
        canvas.pack(side="left", padx=5)
        self.separators = getattr(self, 'separators', [])
        self.separators.append(canvas)
    
    def apply_theme(self):
        """Aplica el tema actual"""
        theme = self.theme_manager.get_theme()
        self.configure(bg=theme['status_bg'])
        
        # Buscar inner frame
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=theme['status_bg'])
        
        for label in self.labels.values():
            label.configure(
                bg=theme['status_bg'],
                fg=theme['status_fg'],
            )
        
        # Actualizar separadores
        if hasattr(self, 'separators'):
            for sep in self.separators:
                sep.configure(bg=theme['status_bg'])
                sep.delete("all")
                sep.create_rectangle(0, 2, 2, 18, fill=theme['border'], outline="")
    
    def update_files(self, count):
        """Actualiza contador de archivos"""
        lang = self.language_manager
        self._stats_cache["total_files"] = count
        self.labels['files'].config(text=f"{lang.get_text('status_files')}: {count:,}")
    
    def update_selected(self, count):
        """Actualiza contador de seleccionados con color"""
        lang = self.language_manager
        theme = self.theme_manager.get_theme()
        self._stats_cache["selected_files"] = count
        color = theme['success'] if count > 0 else theme['status_fg']
        self.labels['selected'].config(
            text=f"{lang.get_text('status_selected')}: {count:,}",
            fg=color
        )
    
    def update_lines(self, count):
        """Actualiza contador de líneas"""
        lang = self.language_manager
        self._stats_cache["total_lines"] = count
        self.labels['lines'].config(text=f"{lang.get_text('status_lines')}: {count:,}")
    
    def update_size(self, size_formatted):
        """Actualiza tamaño total"""
        lang = self.language_manager
        self._stats_cache["size_formatted"] = size_formatted
        self.labels['size'].config(text=f"{lang.get_text('status_size')}: {size_formatted}")
    
    def set_message(self, message, duration=3000, msg_type="info"):
        """Muestra un mensaje temporal con icono"""
        theme = self.theme_manager.get_theme()
        
        # Iconos y colores según tipo
        if msg_type == "success":
            icon = "●"
            color = theme['success']
        elif msg_type == "error":
            icon = "●"
            color = theme['warning']
        elif msg_type == "warning":
            icon = "●"
            color = "#f39c12"
        else:  # info
            icon = "●"
            color = theme['info']
        
        self.labels['message'].config(
            text=f"{icon} {message}",
            fg=color
        )
        
        if duration > 0:
            self.after(duration, lambda: self.labels['message'].config(
                text=f"● {self.language_manager.get_text('status_ready')}",
                fg=theme['success']
            ))
    
    def update_all(self, stats):
        """Actualiza todas las estadísticas"""
        self.update_files(stats.get('total_files', 0))
        self.update_selected(stats.get('selected_files', 0))
        self.update_lines(stats.get('total_lines', 0))
        self.update_size(stats.get('size_formatted', '0 B'))
    
    def update_ui_language(self):
        """Actualiza los textos al cambiar de idioma en tiempo real."""
        self.update_files(self._stats_cache.get("total_files", 0))
        self.update_selected(self._stats_cache.get("selected_files", 0))
        self.update_lines(self._stats_cache.get("total_lines", 0))
        self.update_size(self._stats_cache.get("size_formatted", "0 B"))
        theme = self.theme_manager.get_theme()
        self.labels['message'].config(
            text=f"● {self.language_manager.get_text('status_ready')}",
            fg=theme['success']
        )

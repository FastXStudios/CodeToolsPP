import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk, ImageDraw

class ModernButton(tk.Button):
    """Botón moderno simple y funcional basado en tk.Button"""
    
    def __init__(self, parent, text="", icon=None, command=None, 
                 bg_color="#3498db", hover_color="#2980b9", 
                 text_color="#ffffff", width=120, height=40,
                 border_radius=8, **kwargs):
        
        # Crear botón base
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=text_color,
            activebackground=hover_color,
            activeforeground=text_color,
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            **kwargs
        )
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.icon = icon
        
        # Si hay icono, agregarlo
        if icon:
            self.config(image=icon, compound="left", padx=10)
        
        # Bindings para hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Mouse entra al botón"""
        self.config(bg=self.hover_color)
    
    def _on_leave(self, event):
        """Mouse sale del botón"""
        self.config(bg=self.bg_color)
    
    def configure_colors(self, bg_color=None, hover_color=None, text_color=None):
        """Reconfigura los colores del botón"""
        if bg_color:
            self.bg_color = bg_color
            self.config(bg=bg_color)
        if hover_color:
            self.hover_color = hover_color
            self.config(activebackground=hover_color)
        if text_color:
            self.text_color = text_color
            self.config(fg=text_color, activeforeground=text_color)
    
    def set_enabled(self, enabled):
        """Habilita/deshabilita el botón"""
        if enabled:
            self.config(state="normal", bg=self.bg_color)
        else:
            self.config(state="disabled", bg="#95a5a6")


class IconButton(tk.Button):
    """Botón solo con icono (más pequeño)"""
    
    def __init__(self, parent, icon=None, command=None, 
                 bg_color="#3498db", hover_color="#2980b9",
                 size=36, **kwargs):
        
        super().__init__(
            parent,
            image=icon,
            command=command,
            bg=bg_color,
            activebackground=hover_color,
            relief="flat",
            bd=0,
            width=size,
            height=size,
            cursor="hand2",
            **kwargs
        )
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        # Bindings para hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Mouse entra al botón"""
        self.config(bg=self.hover_color)
    
    def _on_leave(self, event):
        """Mouse sale del botón"""
        self.config(bg=self.bg_color)
    
    def configure_colors(self, bg_color=None, hover_color=None, text_color=None):
        """Reconfigura los colores del botón"""
        if bg_color:
            self.bg_color = bg_color
            self.config(bg=bg_color)
        if hover_color:
            self.hover_color = hover_color
            self.config(activebackground=hover_color)
    
    def set_enabled(self, enabled):
        """Habilita/deshabilita el botón"""
        if enabled:
            self.config(state="normal", bg=self.bg_color)
        else:
            self.config(state="disabled", bg="#95a5a6")


class ModernToggleButton(tk.Button):
    """Botón con estado on/off"""
    
    def __init__(self, parent, text="", icon=None, command=None,
                 bg_color="#3498db", hover_color="#2980b9",
                 active_color="#27ae60", **kwargs):
        
        self.active_color = active_color
        self.is_active = False
        self.toggle_command = command
        
        super().__init__(
            parent,
            text=text,
            command=self._toggle,
            bg=bg_color,
            fg="#ffffff",
            activebackground=hover_color,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            **kwargs
        )
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.icon = icon
        
        if icon:
            self.config(image=icon, compound="left")
        
        # Bindings para hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _toggle(self):
        """Alterna el estado"""
        self.is_active = not self.is_active
        
        if self.is_active:
            self.bg_color = self.active_color
            self.hover_color = "#229954"
        else:
            self.bg_color = "#3498db"
            self.hover_color = "#2980b9"
        
        self.config(bg=self.bg_color, activebackground=self.hover_color)
        
        if self.toggle_command:
            self.toggle_command(self.is_active)
    
    def _on_enter(self, event):
        """Mouse entra al botón"""
        self.config(bg=self.hover_color)
    
    def _on_leave(self, event):
        """Mouse sale del botón"""
        self.config(bg=self.bg_color)
    
    def set_active(self, active):
        """Establece el estado activo"""
        self.is_active = active
        if self.is_active:
            self.bg_color = self.active_color
            self.hover_color = "#229954"
        else:
            self.bg_color = "#3498db"
            self.hover_color = "#2980b9"
        self.config(bg=self.bg_color, activebackground=self.hover_color)
    
    def configure_colors(self, bg_color=None, hover_color=None, text_color=None):
        """Reconfigura los colores del botón"""
        if bg_color:
            self.bg_color = bg_color
            self.config(bg=bg_color)
        if hover_color:
            self.hover_color = hover_color
            self.config(activebackground=hover_color)
    
    def set_enabled(self, enabled):
        """Habilita/deshabilita el botón"""
        if enabled:
            self.config(state="normal", bg=self.bg_color)
        else:
            self.config(state="disabled", bg="#95a5a6")
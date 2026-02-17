import tkinter as tk
from tkinter import ttk

class CustomToplevel(tk.Toplevel):
    """
    Ventana Toplevel personalizada sin decoraciones nativas.
    
    Características:
    - Sin botones nativos (X, minimizar, maximizar)
    - Arrastrable desde la barra de título
    - Redimensionable desde bordes/esquinas
    - Cierre con ESC
    - Tamaños mínimo/máximo configurables
    
    Uso:
        class MiDialogo(CustomToplevel):
            def __init__(self, parent, theme_manager, **kwargs):
                super().__init__(
                    parent=parent,
                    theme_manager=theme_manager,
                    title="Mi Diálogo",
                    size="800x600",
                    min_size=(600, 400),
                    max_size=(1200, 800),
                    **kwargs
                )
                self._create_content()
            
            def _create_content(self):
                # Crear widgets dentro de self.content_frame
                pass
    """
    
    def __init__(self, parent, theme_manager, title="Ventana", size="720x540",
                 min_size=(580, 420), max_size=(1400, 900), **kwargs):
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self._min_width, self._min_height = min_size
        self._max_width, self._max_height = max_size
        
        # Variables para drag & resize
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._resize_start_w = 0
        self._resize_start_h = 0
        
        # Configuración inicial
        self.title(title)
        self.geometry(size)
        self.minsize(*min_size)
        self.resizable(True, True)
        self.configure(bd=0, highlightthickness=0)
        
        # Crear estructura base
        self._create_base_structure()
        
        # Aplicar overrideredirect al final
        self.update_idletasks()
        self.overrideredirect(True)
        
        # Configuración final
        self.bind("<Escape>", lambda e: self.destroy())
        # self.grab_set()
        self.lift()
        self.attributes('-topmost', True)
        # self.after(100, lambda: self.attributes('-topmost', False))
        
        # Suscribir a tema E idioma
        self.theme_manager.subscribe(self.apply_base_theme)
        if hasattr(theme_manager, '_observers'):  # por si acaso
            pass
        self.bind("<Destroy>", self._on_destroy)
        
        # Centrar en padre
        self._center_on_parent(parent)
        self.theme_manager.subscribe(self.apply_base_theme)
        self.bind("<Destroy>", self._on_destroy)
        
        
    def _on_destroy(self, event):
        if event.widget is self:
            self.theme_manager.unsubscribe(self.apply_base_theme)
            # Si tiene language_manager, desuscribir también
            if hasattr(self, 'language_manager') and self.language_manager:
                try:
                    self.language_manager.unsubscribe(self.update_ui_language)
                except Exception:
                    pass
        
    def _create_base_structure(self):
        """Crea la estructura base de la ventana"""
        # Frame raíz
        self._root_frame = tk.Frame(self, bd=0)
        self._root_frame.pack(fill="both", expand=True)
        
        # Barra de título
        self._title_bar = tk.Frame(self._root_frame, height=36)
        self._title_bar.pack(fill="x", side="top")
        self._title_bar.pack_propagate(False)
        
        # Bindear drag a la barra de título
        self._title_bar.bind("<Button-1>", self._start_drag)
        self._title_bar.bind("<B1-Motion>", self._do_drag)
        
        # Contenedor del título (izquierda)
        self.title_container = tk.Frame(self._title_bar)
        self.title_container.pack(side="left", padx=12, fill="y")
        self.title_container.bind("<Button-1>", self._start_drag)
        self.title_container.bind("<B1-Motion>", self._do_drag)
        
        # Label del título (placeholder, las subclases pueden personalizarlo)
        self.title_label = tk.Label(
            self.title_container,
            text=self.title(),
            font=("Segoe UI", 10, "bold")
        )
        self.title_label.pack(side="left")
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._do_drag)
        
        # Botón cerrar
        self.close_button = tk.Label(
            self._title_bar,
            text="  ×  ",
            font=("Segoe UI", 14),
            cursor="hand2",
            padx=6
        )
        self.close_button.pack(side="right", padx=4)
        self.close_button.bind("<Button-1>", lambda e: self.destroy())
        self.close_button.bind("<Enter>", self._close_hover_on)
        self.close_button.bind("<Leave>", self._close_hover_off)
        
        # Separador bajo título
        self._sep_title = tk.Frame(self._root_frame, height=1)
        self._sep_title.pack(fill="x")
        
        # Frame de contenido (aquí van los widgets de las subclases)
        self.content_frame = tk.Frame(self._root_frame)
        self.content_frame.pack(fill="both", expand=True)
        
        # Crear grips de redimensionamiento
        self._create_resize_grips()
    
    def _create_resize_grips(self):
        """Crea áreas para redimensionar la ventana"""
        grip_size = 10
        
        # Esquina inferior derecha
        self._resize_grip_se = tk.Frame(self._root_frame, width=grip_size, height=grip_size, cursor="size_nw_se")
        self._resize_grip_se.place(relx=1.0, rely=1.0, anchor="se")
        self._resize_grip_se.bind("<Button-1>", lambda e: self._start_resize(e, "se"))
        self._resize_grip_se.bind("<B1-Motion>", lambda e: self._do_resize(e, "se"))
        
        # Borde derecho
        self._resize_grip_e = tk.Frame(self._root_frame, width=grip_size, cursor="size_we")
        self._resize_grip_e.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
        self._resize_grip_e.bind("<Button-1>", lambda e: self._start_resize(e, "e"))
        self._resize_grip_e.bind("<B1-Motion>", lambda e: self._do_resize(e, "e"))
        
        # Borde inferior
        self._resize_grip_s = tk.Frame(self._root_frame, height=grip_size, cursor="size_ns")
        self._resize_grip_s.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        self._resize_grip_s.bind("<Button-1>", lambda e: self._start_resize(e, "s"))
        self._resize_grip_s.bind("<B1-Motion>", lambda e: self._do_resize(e, "s"))
    
    # ─────────────────────────────────────────────────────────────────
    # DRAG & DROP
    # ─────────────────────────────────────────────────────────────────
    
    def _start_drag(self, event):
        """Inicia el arrastre de la ventana"""
        self._drag_start_x = event.x
        self._drag_start_y = event.y
    
    def _do_drag(self, event):
        """Arrastra la ventana"""
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")
    
    # ─────────────────────────────────────────────────────────────────
    # RESIZE
    # ─────────────────────────────────────────────────────────────────
    
    def _start_resize(self, event, direction):
        """Inicia el redimensionamiento"""
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._resize_start_w = self.winfo_width()
        self._resize_start_h = self.winfo_height()
    
    def _do_resize(self, event, direction):
        """Redimensiona la ventana con límites"""
        dx = event.x_root - self._resize_start_x
        dy = event.y_root - self._resize_start_y
        
        if "e" in direction:
            new_w = max(self._min_width, min(self._max_width, self._resize_start_w + dx))
            self.geometry(f"{new_w}x{self.winfo_height()}")
        
        if "s" in direction:
            new_h = max(self._min_height, min(self._max_height, self._resize_start_h + dy))
            self.geometry(f"{self.winfo_width()}x{new_h}")
    
    # ─────────────────────────────────────────────────────────────────
    # HOVER EFFECTS
    # ─────────────────────────────────────────────────────────────────
    
    def _close_hover_on(self, e):
        """Efecto hover del botón cerrar"""
        t = self.theme_manager.get_theme()
        self.close_button.configure(bg=t.get("warning", "#e74c3c"), fg="#ffffff")
    
    def _close_hover_off(self, e):
        """Quita efecto hover del botón cerrar"""
        t = self.theme_manager.get_theme()
        self.close_button.configure(bg=t["secondary_bg"], fg=t["fg"])
    
    # ─────────────────────────────────────────────────────────────────
    # THEMING BASE
    # ─────────────────────────────────────────────────────────────────
    
    def apply_base_theme(self):
        """Aplica tema base a la estructura (las subclases deben llamar esto)"""
        t = self.theme_manager.get_theme()
        
        # *** CAMBIAR ESTA LÍNEA - AGREGAR highlightthickness ***
        self.configure(bg=t["border"], highlightthickness=1, highlightbackground=t["border"])
        self._root_frame.configure(bg=t["bg"])
        
        # Título
        self._title_bar.configure(bg=t["secondary_bg"])
        self.title_container.configure(bg=t["secondary_bg"])
        self.title_label.configure(bg=t["secondary_bg"], fg=t["fg"])
        self.close_button.configure(bg=t["secondary_bg"], fg=t["fg"])
        
        # Separador
        self._sep_title.configure(bg=t["border"])
        
        # Contenido
        self.content_frame.configure(bg=t["bg"])
        
        # Grips (invisibles)
        for grip in [self._resize_grip_se, self._resize_grip_e, self._resize_grip_s]:
            grip.configure(bg=t["bg"])
    
    # ─────────────────────────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────────────────────────
    
    def _center_on_parent(self, parent):
        """Centra la ventana sobre el padre"""
        try:
            parent.update_idletasks()
        except Exception:
            pass
        self.update_idletasks()
        pw = max(parent.winfo_width(), 200)
        ph = max(parent.winfo_height(), 120)
        px = max(parent.winfo_x(), 0)
        py = max(parent.winfo_y(), 0)
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        # Evitar posiciones fuera de pantalla (especialmente con overrideredirect).
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, min(x, max(0, sw - w)))
        y = max(0, min(y, max(0, sh - h)))
        self.geometry(f"+{x}+{y}")
    
    def add_title_icon(self, icon_image):
        """Agrega un icono al título (lado izquierdo)"""
        if icon_image:
            t = self.theme_manager.get_theme()
            lbl_ico = tk.Label(
                self.title_container,
                image=icon_image,
                bg=t["secondary_bg"],
                bd=0,
                highlightthickness=0
            )
            lbl_ico.image = icon_image
            lbl_ico.pack(side="left", padx=(0, 6), before=self.title_label)
            lbl_ico.bind("<Button-1>", self._start_drag)
            lbl_ico.bind("<B1-Motion>", self._do_drag)
            return lbl_ico
        return None

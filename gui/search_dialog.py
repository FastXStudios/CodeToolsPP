import sys
import tkinter as tk
from tkinter import ttk
import os
from gui.components import CustomToplevel
from utils.helpers import resource_path

class SearchDialog(tk.Toplevel):
    """Diálogo de búsqueda avanzada de archivos — UI profesional con soporte de temas"""

    # ── Íconos usados (todos desde assets/icons/) ──────────────────────────
    # search.png          → lupa / buscar
    # close.png           → cerrar ventana
    # file.png            → icono genérico de archivo en resultados
    # folder.png          → carpeta en breadcrumb / ruta raíz
    # check.png           → seleccionar todos
    # trash.png           → limpiar resultados
    # filter.png          → opciones / filtros
    # info.png            → estado / sin resultados
    # -------------------------------------------------------------------
    
    def __init__(self, parent, tree_view, file_manager, theme_manager, language_manager):
        super().__init__(parent)
        
        self.tree_view        = tree_view
        self.file_manager     = file_manager
        self.theme_manager    = theme_manager
        self.language_manager = language_manager
        self.results          = []
        self._icon_cache      = {}

        # Variables para drag & drop de ventana
        self._drag_start_x = 0
        self._drag_start_y = 0

        lang = language_manager
        self.title(lang.get_text("search_title"))
        self.geometry("720x540")
        self.minsize(580, 420)
        self.resizable(True, True)
        
        # *** QUITAR TRANSIENT - NO ES COMPATIBLE CON OVERRIDEREDIRECT ***
        # self.transient(parent)  # ← COMENTAR O BORRAR ESTA LÍNEA
        
        # Eliminar borde nativo y usar el nuestro
        self.configure(bd=0, highlightthickness=0)

        self._load_icons()
        self._create_widgets()
        self._center_on_parent(parent)

        # Aplicar overrideredirect al final
        self.update_idletasks()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.lift()
        self.apply_theme()

        # Cerrar con ESC
        self.bind("<Escape>", lambda e: self.destroy())

        # Foco en el entry al abrir
        self.after(50, self.search_entry.focus_set)
        
        # ← AGREGAR al final del __init__:
        self.theme_manager.subscribe(self.apply_theme)
        self.language_manager.subscribe(self._on_language_change)
        self.bind("<Destroy>", self._on_destroy)
        
    def _on_language_change(self):
        """Actualiza TODOS los textos cuando cambia el idioma"""
        lang = self.language_manager
        try:
            # Título
            self._title_label.configure(text=lang.get_text("search_title"))
            
            # Label "Buscar:"
            if hasattr(self, '_labels') and len(self._labels) > 0:
                self._labels[0].configure(text=lang.get_text("search_label"))
            
            # Botones
            self.search_btn.configure(text=f"  {lang.get_text('search_btn')}")
            self.select_all_btn.configure(text=f"  {lang.get_text('search_select_all')}")
            self.clear_btn.configure(text=f"  {lang.get_text('search_clear')}")
            self._btn_close_footer.configure(text=f"  {lang.get_text('search_close')}")
            
            # Checkboxes - ACTUALIZAR TEXTOS
            if hasattr(self, '_checkbuttons') and len(self._checkbuttons) >= 3:
                self._checkbuttons[0].configure(text=lang.get_text("search_case_sensitive"))
                self._checkbuttons[1].configure(text=lang.get_text("search_extension_only"))
                self._checkbuttons[2].configure(text=lang.get_text("search_include_dirs"))
            
            # Labels de resultados
            self._results_label.configure(text=lang.get_text("search_results"))
            
            # Placeholder del estado vacío
            if not self.search_entry.get().strip():
                self._empty_label.configure(text=lang.get_text("search_placeholder"))
            
        except Exception as e:
            print(f"Error updating search dialog language: {e}")
    # ─────────────────────────────────────────────────────────────────────
    # ICONOS
    # ─────────────────────────────────────────────────────────────────────
    
    # Actualizar _on_destroy para desuscribir idioma también:
    def _on_destroy(self, event):
        if event.widget is self:
            self.theme_manager.unsubscribe(self.apply_theme)
            self.language_manager.unsubscribe(self._on_language_change)
            
    def _load_icons(self):
        """Carga los iconos PNG necesarios (con fallback silencioso)."""
        try:
            from PIL import Image, ImageTk
            icon_dir = resource_path("assets/icons")
            icon_size = (16, 16)
            self._icon_cache = []
            
            # *** OBTENER COLOR DE FONDO ***
            t = self.theme_manager.get_theme()
            sec_bg = t["secondary_bg"]
            btn_bg = t["button_bg"]  # ← AGREGAR ESTA LÍNEA
            
            def _rgb(hex_color):
                """Convierte hex a RGB"""
                h = hex_color.lstrip("#")
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

            def load(name, bg_color=None):
                path = os.path.join(icon_dir, name)
                if os.path.exists(path):
                    img = Image.open(path).convert("RGBA").resize(icon_size, Image.Resampling.LANCZOS)
                    
                    # Aplicar fondo si se especifica
                    if bg_color:
                        bg_img = Image.new("RGBA", img.size, _rgb(bg_color) + (255,))
                        bg_img.paste(img, mask=img.split()[3])
                        photo = ImageTk.PhotoImage(bg_img.convert("RGB"), master=self)
                        self._icon_cache.append(photo)
                        return photo
                    
                    photo = ImageTk.PhotoImage(img, master=self)
                    self._icon_cache.append(photo)
                    return photo
                return None

            self._icons = {
                "search":   load("search.png", btn_bg), 
                "search_title":  load("search.png", sec_bg), 
                "close":    load("close.png"),
                "file":     load("file.png"),
                "folder":   load("folder.png"),
                "check":    load("check.png"),
                "trash":    load("trash.png"),
                "filter":   load("filter.png"),
                "info":     load("info.png"),
            }
        except Exception:
            self._icons = {}

    def _icon(self, name):
        return self._icons.get(name)

    # ─────────────────────────────────────────────────────────────────────
    # CONSTRUCCIÓN DE WIDGETS
    # ─────────────────────────────────────────────────────────────────────

    def _create_widgets(self):
        lang = self.language_manager

        # ── Contenedor raíz con borde visual ────────────────────────────
        self._root_frame = tk.Frame(self, bd=0)
        self._root_frame.pack(fill="both", expand=True)

        # ── Barra de título personalizada ────────────────────────────────
        self._title_bar = tk.Frame(self._root_frame, height=36)
        self._title_bar.pack(fill="x", side="top")
        self._title_bar.pack_propagate(False)

        # *** AGREGAR BINDING PARA ARRASTRAR ***
        self._title_bar.bind("<Button-1>", self._start_drag)
        self._title_bar.bind("<B1-Motion>", self._do_drag)
        # *** FIN ***

        # Icono + título
        title_inner = tk.Frame(self._title_bar)
        title_inner.pack(side="left", padx=12, fill="y")
        self._title_icon_label = None

        # *** AGREGAR ESTO ***
        title_inner.bind("<Button-1>", self._start_drag)
        title_inner.bind("<B1-Motion>", self._do_drag)
        # *** FIN ***

        ico = self._icon("search_title")
        if ico:
            lbl_ico = tk.Label(title_inner, image=ico, bg=self._title_bar.cget("bg"))
            lbl_ico.image = ico
            lbl_ico.pack(side="left", padx=(0, 6))
            self._title_icon_label = lbl_ico
            # *** AGREGAR ESTO ***
            lbl_ico.bind("<Button-1>", self._start_drag)
            lbl_ico.bind("<B1-Motion>", self._do_drag)
            # *** FIN ***

        self._title_label = tk.Label(
            title_inner,
            text=lang.get_text("search_title"),
            font=("Segoe UI", 10, "bold"),
        )
        self._title_label.pack(side="left")
        # *** AGREGAR ESTO ***
        self._title_label.bind("<Button-1>", self._start_drag)
        self._title_label.bind("<B1-Motion>", self._do_drag)
        # *** FIN ***

        # *** FALTABA ESTO - BOTÓN CERRAR ***
        self._btn_close = tk.Label(
            self._title_bar,
            text="  ×  ",
            font=("Segoe UI", 14),
            cursor="hand2",
            padx=6,
        )
        self._btn_close.pack(side="right", padx=12)
        self._btn_close.bind("<Button-1>", lambda e: self.destroy())
        # *** FIN ***
        
        self._btn_close.bind("<Enter>", self._close_hover_on)
        self._btn_close.bind("<Leave>", self._close_hover_off)

        # ── Separador fino bajo el título ────────────────────────────────
        self._sep_title = tk.Frame(self._root_frame, height=1)
        self._sep_title.pack(fill="x")

        # ── Cuerpo principal ─────────────────────────────────────────────
        body = tk.Frame(self._root_frame)
        body.pack(fill="both", expand=True, padx=16, pady=14)

        # ── Sección de búsqueda ──────────────────────────────────────────
        search_section = tk.Frame(body)
        search_section.pack(fill="x", pady=(0, 10))

        self._search_label = tk.Label(
            search_section,
            text=lang.get_text("search_label"),
            font=("Segoe UI", 9),
        )
        self._search_label.pack(side="left", padx=(0, 8))
        self._labels = [self._search_label]

        # Entry con borde simulado
        self._entry_frame = tk.Frame(search_section, bd=0, highlightthickness=1)
        self._entry_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.search_entry = tk.Entry(
            self._entry_frame,
            font=("Segoe UI", 10),
            bd=0,
            highlightthickness=0,
        )
        self.search_entry.pack(fill="x", padx=8, pady=5)
        self.search_entry.bind("<Return>",    lambda e: self._perform_search())
        self.search_entry.bind("<FocusIn>",   self._entry_focus_in)
        self.search_entry.bind("<FocusOut>",  self._entry_focus_out)
        self.search_entry.bind("<KeyRelease>", self._on_key_release)

        # Botón Buscar
        ico_s = self._icon("search")
        self.search_btn = tk.Button(
            search_section,
            text=lang.get_text("search_btn") if not ico_s else f"  {lang.get_text('search_btn')}",
            image=ico_s,
            compound="left" if ico_s else "none",
            command=self._perform_search,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=14,
            pady=6,
        )
        self.search_btn.pack(side="left")
        self._bind_hover(self.search_btn, "accent")

        # ── Opciones / filtros ───────────────────────────────────────────
        options_outer = tk.Frame(body)
        options_outer.pack(fill="x", pady=(0, 12))

        ico_f = self._icon("filter")
        if ico_f:
            lbl_filt = tk.Label(options_outer, image=ico_f)
            lbl_filt.image = ico_f
            lbl_filt.pack(side="left", padx=(0, 6))
            self._labels.append(lbl_filt)

        self.case_sensitive_var   = tk.BooleanVar(value=False)
        self.match_extension_var  = tk.BooleanVar(value=False)
        self.search_dirs_var      = tk.BooleanVar(value=False)

        opts = [
            (lang.get_text("search_case_sensitive"),  self.case_sensitive_var),
            (lang.get_text("search_extension_only"),  self.match_extension_var),
            (lang.get_text("search_include_dirs") if hasattr(lang, "get_text") else "Incluir carpetas",
             self.search_dirs_var),
        ]

        self._checkbuttons = []
        for text, var in opts:
            cb = tk.Checkbutton(
                options_outer,
                text=text,
                variable=var,
                font=("Segoe UI", 9),
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                command=self._on_option_change,
            )
            cb.pack(side="left", padx=(0, 18))
            self._checkbuttons.append(cb)

        # ── Separador ────────────────────────────────────────────────────
        self._sep_mid = tk.Frame(body, height=1)
        self._sep_mid.pack(fill="x", pady=(0, 10))

        # ── Cabecera de resultados ───────────────────────────────────────
        res_header = tk.Frame(body)
        res_header.pack(fill="x", pady=(0, 6))

        self._results_label = tk.Label(
            res_header,
            text=lang.get_text("search_results"),
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self._results_label.pack(side="left")

        self._count_label = tk.Label(
            res_header,
            text="",
            font=("Segoe UI", 9),
            anchor="w",
        )
        self._count_label.pack(side="left", padx=(8, 0))

        # ── Listbox de resultados ────────────────────────────────────────
        list_frame = tk.Frame(body)
        list_frame.pack(fill="both", expand=True)

        # Scrollbar vertical estilizada
        self._scrollbar_y = ttk.Scrollbar(list_frame, orient="vertical")
        self._scrollbar_y.pack(side="right", fill="y")

        self._scrollbar_x = ttk.Scrollbar(list_frame, orient="horizontal")
        self._scrollbar_x.pack(side="bottom", fill="x")

        self.results_listbox = tk.Listbox(
            list_frame,
            font=("Consolas", 9),
            bd=0,
            highlightthickness=1,
            selectmode="extended",
            activestyle="none",
            yscrollcommand=self._scrollbar_y.set,
            xscrollcommand=self._scrollbar_x.set,
        )
        self.results_listbox.pack(side="left", fill="both", expand=True)
        self._scrollbar_y.config(command=self.results_listbox.yview)
        self._scrollbar_x.config(command=self.results_listbox.xview)

        self.results_listbox.bind("<Double-Button-1>", self._on_result_double_click)
        self.results_listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        # ── Estado vacío ─────────────────────────────────────────────────
        self._empty_frame = tk.Frame(list_frame)
        ico_i = self._icon("info")
        if ico_i:
            lbl_ei = tk.Label(self._empty_frame, image=ico_i)
            lbl_ei.image = ico_i
            lbl_ei.pack()
        self._empty_label = tk.Label(
            self._empty_frame,
            text=lang.get_text("search_placeholder"),  # ✅ Usar traducción
            font=("Segoe UI", 10),
        )
        self._empty_label.pack(pady=4)
        self._empty_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ── Barra de acciones (footer) ───────────────────────────────────
        self._sep_footer = tk.Frame(self._root_frame, height=1)
        self._sep_footer.pack(fill="x", side="bottom")

        footer = tk.Frame(self._root_frame, height=44)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        footer_inner = tk.Frame(footer)
        footer_inner.pack(fill="both", expand=True, padx=14, pady=8)

        # Botón: Seleccionar todos
        ico_c = self._icon("check")
        self.select_all_btn = tk.Button(
            footer_inner,
            text=f"  {lang.get_text('search_select_all')}",
            image=ico_c,
            compound="left" if ico_c else "none",
            command=self._select_all_results,
            font=("Segoe UI", 9),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=10,
            pady=4,
            state="disabled",
        )
        self.select_all_btn.pack(side="left", padx=(0, 6))
        self._bind_hover(self.select_all_btn, "secondary")

        # Botón: Limpiar
        ico_t = self._icon("trash")
        self.clear_btn = tk.Button(
            footer_inner,
            text=f"  {lang.get_text('search_clear')}",
            image=ico_t,
            compound="left" if ico_t else "none",
            command=self._clear_results,
            font=("Segoe UI", 9),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=10,
            pady=4,
        )
        self.clear_btn.pack(side="left")
        self._bind_hover(self.clear_btn, "secondary")

        # Selección info (derecha)
        self._selection_label = tk.Label(
            footer_inner,
            text="",
            font=("Segoe UI", 8),
            anchor="e",
        )
        self._selection_label.pack(side="right", padx=(0, 8))

        # Botón: Cerrar
        ico_x = self._icon("close")
        close_btn = tk.Button(
            footer_inner,
            text=f"  {lang.get_text('search_close')}",
            image=ico_x,
            compound="left" if ico_x else "none",
            command=self.destroy,
            font=("Segoe UI", 9),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=10,
            pady=4,
        )
        close_btn.pack(side="right", padx=(6, 0))
        self._bind_hover(close_btn, "secondary")
        self._btn_close_footer = close_btn

        # Guardamos referencias para el theming
        self._all_buttons = [
            self.search_btn, self.select_all_btn,
            self.clear_btn, self._btn_close_footer,
        ]
        # Guardamos referencias para el theming
        self._all_buttons = [
            self.search_btn, self.select_all_btn,
            self.clear_btn, self._btn_close_footer,
        ]
        
        # *** AGREGAR ESTO AL FINAL ***
        self._create_resize_grips()
        # *** FIN ***

    # ─────────────────────────────────────────────────────────────────────
    # THEMING
    # ─────────────────────────────────────────────────────────────────────

    def apply_theme(self):
        """Aplica el tema activo de ThemeManager a toda la ventana."""
        # Mantener referencias previas durante el recambio para evitar
        # que Tk destruya imágenes aún enlazadas a botones/labels.
        prev_icon_cache = getattr(self, "_icon_cache", [])
        self._prev_icon_cache_hold = prev_icon_cache

        t = self.theme_manager.get_theme()
        self._load_icons()

        bg         = t["bg"]
        fg         = t["fg"]
        sec_bg     = t["secondary_bg"]
        accent     = t["accent"]
        border     = t["border"]
        tree_bg    = t["tree_bg"]
        tree_fg    = t["tree_fg"]
        sel_bg     = t["tree_selected_bg"]
        sel_fg     = t["tree_selected_fg"]
        btn_bg     = t["button_bg"]
        btn_fg     = t["button_fg"]
        btn_hover  = t["button_hover"]
        status_bg  = t["status_bg"]

        self.configure(bg="#000000", highlightthickness=1, highlightbackground="#000000")  # ← AGREGAR highlightthickness
        self._root_frame.configure(bg=bg)

        # Título
        self._title_bar.configure(bg=sec_bg)
        self._title_label.configure(bg=sec_bg, fg=fg)
        self._btn_close.configure(bg=sec_bg, fg=fg)
        if self._title_icon_label and self._title_icon_label.winfo_exists():
            ico_title = self._icon("search_title")
            if ico_title:
                self._title_icon_label.configure(image=ico_title, bg=sec_bg)
                self._title_icon_label.image = ico_title

        # Separadores
        self._sep_title.configure(bg=border)
        self._sep_mid.configure(bg=border)
        self._sep_footer.configure(bg=border)

        # Cuerpo
        for w in self._root_frame.winfo_children():
            if isinstance(w, tk.Frame) and w not in (
                self._title_bar, self._sep_title, self._sep_mid,
                self._sep_footer,
            ):
                w.configure(bg=bg)

        # Forzar bg en todos los frames anidados del body
        self._set_bg_recursive(self._root_frame, bg, exclude={
            self._title_bar, self._sep_title, self._sep_mid, self._sep_footer,
        })

        # Título bar override (ya seteado arriba)
        self._title_bar.configure(bg=sec_bg)
        for child in self._title_bar.winfo_children():
            if isinstance(child, (tk.Label, tk.Frame)):
                child.configure(bg=sec_bg)
                if isinstance(child, tk.Label):
                    child.configure(fg=fg)

        # Footer
        footer_widgets = self._sep_footer.master  # el Toplevel
        # buscar el footer frame directamente
        for w in self._root_frame.winfo_children():
            if isinstance(w, tk.Frame) and w.winfo_height() == 44:
                w.configure(bg=sec_bg)
                self._set_bg_recursive(w, sec_bg)

        # Labels generales
        for lbl in self._labels:
            try:
                lbl.configure(bg=bg, fg=fg)
            except Exception:
                pass

        self._results_label.configure(bg=bg, fg=fg)
        self._count_label.configure(bg=bg, fg=t.get("info", accent))
        self._selection_label.configure(bg=sec_bg, fg=t.get("fg", fg))

        # Checkbuttons
        for cb in self._checkbuttons:
            cb.configure(
                bg=bg, fg=fg,
                selectcolor=accent,
                activebackground=bg,
                activeforeground=fg,
            )

        # Entry
        self._entry_frame.configure(
            bg=tree_bg,
            highlightcolor=accent,
            highlightbackground=border,
        )
        self.search_entry.configure(
            bg=tree_bg, fg=tree_fg,
            insertbackground=fg,
        )

        # Listbox
        self.results_listbox.configure(
            bg=tree_bg, fg=tree_fg,
            selectbackground=sel_bg,
            selectforeground=sel_fg,
            highlightcolor=accent,
            highlightbackground=border,
        )

        # Estado vacío
        self._empty_frame.configure(bg=tree_bg)
        self._empty_label.configure(bg=tree_bg, fg=t.get("fg", fg))

        # Botón primario (buscar)
        self.search_btn.configure(
            bg=btn_bg, fg=btn_fg,
            activebackground=btn_hover,
            activeforeground=btn_fg,
        )
        ico_s = self._icon("search")
        self.search_btn.configure(image=ico_s, compound="left" if ico_s else "none")
        if ico_s:
            self.search_btn.image = ico_s

        # Botones secundarios
        ico_check = self._icon("check")
        self.select_all_btn.configure(image=ico_check, compound="left" if ico_check else "none")
        if ico_check:
            self.select_all_btn.image = ico_check
        ico_trash = self._icon("trash")
        self.clear_btn.configure(image=ico_trash, compound="left" if ico_trash else "none")
        if ico_trash:
            self.clear_btn.image = ico_trash
        ico_close = self._icon("close")
        self._btn_close_footer.configure(image=ico_close, compound="left" if ico_close else "none")
        if ico_close:
            self._btn_close_footer.image = ico_close
        for btn in [self.select_all_btn, self.clear_btn, self._btn_close_footer]:
            btn.configure(
                bg=sec_bg, fg=fg,
                activebackground=border,
                activeforeground=fg,
                disabledforeground=t.get("border", border),
            )

        # Botón cerrar (×) en title bar
        self._btn_close.configure(bg=sec_bg, fg=fg)

        # Scrollbars (ttk style)
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Vertical.TScrollbar",
            background=border,
            troughcolor=sec_bg,
            arrowcolor=fg,
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=border,
            troughcolor=sec_bg,
            arrowcolor=fg,
        )

        # Liberar caché anterior cuando el loop ya aplicó los nuevos íconos.
        self.after_idle(lambda: setattr(self, "_prev_icon_cache_hold", []))

    def _set_bg_recursive(self, widget, color, exclude=None):
        """Aplica bg recursivamente, saltando widgets excluidos."""
        if exclude and widget in exclude:
            return
        try:
            if isinstance(widget, (tk.Frame, tk.Label, tk.Checkbutton)):
                widget.configure(bg=color)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._set_bg_recursive(child, color, exclude)

    # ─────────────────────────────────────────────────────────────────────
    # HOVER HELPERS
    # ─────────────────────────────────────────────────────────────────────

    def _bind_hover(self, btn, style="accent"):
        """Aplica efecto hover a un botón."""
        def on_enter(e):
            t = self.theme_manager.get_theme()
            if style == "accent":
                btn.configure(bg=t["button_hover"])
            else:
                btn.configure(bg=t["border"])

        def on_leave(e):
            t = self.theme_manager.get_theme()
            if style == "accent":
                btn.configure(bg=t["button_bg"])
            else:
                btn.configure(bg=t["secondary_bg"])

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _close_hover_on(self, e):
        t = self.theme_manager.get_theme()
        self._btn_close.configure(bg=t.get("warning", "#e74c3c"), fg="#ffffff")

    def _close_hover_off(self, e):
        t = self.theme_manager.get_theme()
        self._btn_close.configure(bg=t["secondary_bg"], fg=t["fg"])

    # ─────────────────────────────────────────────────────────────────────
    # ENTRY FOCUS
    # ─────────────────────────────────────────────────────────────────────

    def _entry_focus_in(self, e):
        t = self.theme_manager.get_theme()
        self._entry_frame.configure(highlightbackground=t["accent"])

    def _entry_focus_out(self, e):
        t = self.theme_manager.get_theme()
        self._entry_frame.configure(highlightbackground=t["border"])

    # ─────────────────────────────────────────────────────────────────────
    # LÓGICA DE BÚSQUEDA
    # ─────────────────────────────────────────────────────────────────────

    def _on_key_release(self, e):
        """Oculta el estado vacío mientras el usuario escribe."""
        if self.search_entry.get().strip():
            self._empty_frame.place_forget()
        else:
            self._empty_frame.place(relx=0.5, rely=0.5, anchor="center")

    def _on_option_change(self):
        """Re-lanza búsqueda si hay texto."""
        if self.search_entry.get().strip() and self.results:
            self._perform_search()

    def _perform_search(self):
        lang = self.language_manager
        query = self.search_entry.get().strip()
        if not query:
            return

        if not self.file_manager.root_path:
            return

        self._clear_results(keep_query=True)
        self._empty_frame.place_forget()

        case_sensitive  = self.case_sensitive_var.get()
        match_extension = self.match_extension_var.get()
        include_dirs    = self.search_dirs_var.get()

        search_query = query if case_sensitive else query.lower()

        self.results = []
        self._search_in_directory(
            self.file_manager.root_path,
            search_query,
            case_sensitive,
            match_extension,
            include_dirs,
        )

        t = self.theme_manager.get_theme()

        if self.results:
            for filepath in self.results:
                relpath = self.file_manager.get_relative_path(filepath)
                # Prefijo visual por tipo
                prefix = "  " if os.path.isdir(filepath) else "  "
                self.results_listbox.insert(tk.END, f"{prefix}{relpath}")

            # Colorear pares/impares
            for i in range(len(self.results)):
                row_bg = t["tree_bg"] if i % 2 == 0 else self._mix_colors(t["tree_bg"], t["secondary_bg"])
                self.results_listbox.itemconfigure(i, background=row_bg, foreground=t["tree_fg"])

            count = len(self.results)
            self._count_label.configure(
                text=f"— {count} resultado{'s' if count != 1 else ''} encontrado{'s' if count != 1 else ''}"
            )
            self.select_all_btn.config(state="normal")
        else:
            ico_i = self._icon("info")
            self._empty_label.configure(text=lang.get_text("search_no_results"))
            self._empty_frame.configure(bg=t["tree_bg"])
            self._empty_label.configure(bg=t["tree_bg"], fg=t.get("fg", "#cccccc"))
            self._empty_frame.place(relx=0.5, rely=0.5, anchor="center")
            self._count_label.configure(text="— 0 resultados")

    def _mix_colors(self, c1, c2):
        """Mezcla dos colores hex al 50%."""
        try:
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
            r = (r1 + r2) // 2
            g = (g1 + g2) // 2
            b = (b1 + b2) // 2
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return c1

    def _search_in_directory(self, dirpath, query, case_sensitive, match_extension, include_dirs):
        """Búsqueda recursiva."""
        try:
            for item in os.listdir(dirpath):
                fullpath = os.path.join(dirpath, item)
                filename = item if case_sensitive else item.lower()

                if match_extension:
                    ext = os.path.splitext(item)[1]
                    if not case_sensitive:
                        ext = ext.lower()
                    match = query in ext
                else:
                    match = query in filename

                if match:
                    if os.path.isfile(fullpath):
                        self.results.append(fullpath)
                    elif os.path.isdir(fullpath) and include_dirs:
                        self.results.append(fullpath)

                if os.path.isdir(fullpath):
                    self._search_in_directory(
                        fullpath, query, case_sensitive, match_extension, include_dirs
                    )
        except PermissionError:
            pass

    # ─────────────────────────────────────────────────────────────────────
    # ACCIONES
    # ─────────────────────────────────────────────────────────────────────

    def _on_result_double_click(self, event):
        """Navega al archivo en el tree al hacer doble click."""
        selection = self.results_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index < len(self.results):
            filepath = self.results[index]
            # TODO: navegar y marcar en el tree_view
            # self.tree_view.navigate_to(filepath)

    def _on_listbox_select(self, event):
        """Actualiza el contador de selección."""
        n = len(self.results_listbox.curselection())
        if n > 1:
            self._selection_label.configure(text=f"{n} seleccionados")
        elif n == 1:
            self._selection_label.configure(text="1 seleccionado")
        else:
            self._selection_label.configure(text="")

    def _select_all_results(self):
        """Marca todos los resultados en el tree view."""
        lang = self.language_manager

        for filepath in self.results:
            if os.path.isfile(filepath):
                self.tree_view.selection_manager.select_item(filepath)

        self.tree_view.refresh_tree()

        # Feedback visual temporal
        original = self.select_all_btn.cget("text")
        ok_text  = f"  {'¡Marcados!' if lang.current_language == 'es' else 'Marked!'}"
        t = self.theme_manager.get_theme()
        self.select_all_btn.configure(text=ok_text, bg=t.get("success", "#27ae60"), fg="#ffffff")
        self.after(2000, lambda: self.select_all_btn.configure(
            text=original,
            bg=t["secondary_bg"],
            fg=t["fg"],
        ))

    def _clear_results(self, keep_query=False):
        """Limpia los resultados."""
        self.results_listbox.delete(0, tk.END)
        self.results = []
        self._count_label.configure(text="")
        self._selection_label.configure(text="")
        self.select_all_btn.config(state="disabled")

        if not keep_query:
            self.search_entry.delete(0, tk.END)
            t = self.theme_manager.get_theme()
            lang = self.language_manager  # ✅ Agregar esta línea
            self._empty_label.configure(text=lang.get_text("search_placeholder"))  # ✅ Usar traducción
            self._empty_frame.configure(bg=t["tree_bg"])
            self._empty_label.configure(bg=t["tree_bg"])
            self._empty_frame.place(relx=0.5, rely=0.5, anchor="center")

    # ─────────────────────────────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────────────────────────────

    def _center_on_parent(self, parent):
        """Centra la ventana sobre el padre."""
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w  = self.winfo_width()
        h  = self.winfo_height()
        x  = px + (pw - w) // 2
        y  = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")
        
    def _start_drag(self, event):
        """Inicia el arrastre de la ventana"""
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _do_drag(self, event):
        """Arrastra la ventana"""
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")
        
    def _do_drag(self, event):
        """Arrastra la ventana"""
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")
    
    # *** AGREGAR ESTOS 3 MÉTODOS NUEVOS ***
    def _create_resize_grips(self):
        """Crea áreas para redimensionar"""
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
    
    def _start_resize(self, event, direction):
        """Inicia redimensionamiento"""
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._resize_start_w = self.winfo_width()
        self._resize_start_h = self.winfo_height()
    
    def _do_resize(self, event, direction):
        """Redimensiona con límites"""
        dx = event.x_root - self._resize_start_x
        dy = event.y_root - self._resize_start_y
        
        min_w, min_h = 580, 420
        max_w, max_h = 1400, 900
        
        if "e" in direction:
            new_w = max(min_w, min(max_w, self._resize_start_w + dx))
            self.geometry(f"{new_w}x{self.winfo_height()}")
        
        if "s" in direction:
            new_h = max(min_h, min(max_h, self._resize_start_h + dy))
            self.geometry(f"{self.winfo_width()}x{new_h}")

import tkinter as tk
from tkinter import ttk
import os
import sys
import threading
import subprocess
import matplotlib
from gui.components import CustomToplevel
from utils.helpers import resource_path
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class _LoadingOverlay(tk.Frame):
    """Overlay de carga con barra de progreso indeterminada."""

    def __init__(self, parent, theme_manager, message="Analizando..."):
        super().__init__(parent, bd=0)
        
        self.theme_manager = theme_manager
        self._anim_id = None

        t = theme_manager.get_theme()

        self.configure(bg=t["bg"])

        spacer_top = tk.Frame(self, bg=t["bg"])
        spacer_top.pack(fill="both", expand=True)

        inner = tk.Frame(self, bg=t["secondary_bg"], padx=32, pady=28)
        inner.pack()

        self._msg_lbl = tk.Label(
            inner,
            text=message,
            font=("Segoe UI", 11, "bold"),
            bg=t["secondary_bg"],
            fg=t["fg"],
        )
        self._msg_lbl.pack(pady=(0, 14))

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Load.Horizontal.TProgressbar",
            troughcolor=t["border"],
            background=t["accent"],
            thickness=6,
        )
        self._bar = ttk.Progressbar(
            inner,
            mode="indeterminate",
            style="Load.Horizontal.TProgressbar",
            length=280,
        )
        self._bar.pack(pady=(0, 10))
        self._determinate = False

        self._sub_lbl = tk.Label(
            inner,
            text="Por favor espera...",
            font=("Segoe UI", 8),
            bg=t["secondary_bg"],
            fg=t["border"],
        )
        self._sub_lbl.pack()

        spacer_bot = tk.Frame(self, bg=t["bg"])
        spacer_bot.pack(fill="both", expand=True)

    def start(self):
        self._bar.configure(mode="indeterminate", maximum=100)
        self._bar.start(12)
        self._determinate = False

    def stop(self):
        self._bar.stop()

    def set_message(self, msg):
        try:
            self._msg_lbl.configure(text=msg)
        except Exception:
            pass

    def set_sub(self, msg):
        try:
            self._sub_lbl.configure(text=msg)
        except Exception:
            pass

    def set_bar(self, pct):
        try:
            if pct is None:
                if not self._determinate:
                    return
                self._bar.stop()
                self._bar.configure(mode="indeterminate")
                self._bar.start(12)
                self._determinate = False
            else:
                if not self._determinate:
                    self._bar.stop()
                    self._bar.configure(mode="determinate", maximum=100)
                    self._determinate = True
                self._bar["value"] = pct
        except Exception:
            pass


class DashboardWindow(CustomToplevel):
    """Dashboard profesional metricas, graficas, TODOs, duplicados."""

    def __init__(self, parent, theme_manager, file_manager,
                code_analyzer, project_stats, language_manager):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title=language_manager.get_text("btn_dashboard"),
            size="1060x720",
            min_size=(800, 560),
            max_size=(1600, 1000)
        )
        
        self.file_manager     = file_manager
        self.code_analyzer    = code_analyzer
        self.project_stats    = project_stats
        self.language_manager = language_manager

        self._last_theme_key = None
        self._icons          = {}
        self._lang_icons     = {}
        self._tab_btns       = []
        self._active_tab     = 0
        self._loading        = False
        self._selected_files = []
        self._todo_issue_rows = []
        self._todo_issue_map = {}
        
        # *** SOBRESCRIBIR BOTON CERRAR ***
        self.close_button.bind("<Button-1>", lambda e: self.destroy())
        
        # *** AGREGAR ICONO AL TITULO ***
        self._load_icons()
        ico_stats = self._icon("dashboard")
        if ico_stats:
            self.add_title_icon(ico_stats)

        self._build_ui()
        self.apply_theme()
        self.language_manager.subscribe(self.update_ui_language)

    _IGNORED_DIRS = {
        "node_modules", "venv", ".venv", "env", ".env",
        "__pycache__", ".git", ".svn", ".hg", "dist", "build",
    }
    _IGNORED_EXTS = {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
        ".whl", ".egg", ".pyc", ".pyo",
    }

    def _dbg(self, message):
        try:
            print(f"[Dashboard][Top] {message}")
        except Exception:
            pass
        

    def update_ui_language(self):
        lang = self.language_manager
        self.title_label.configure(text=lang.get_text("btn_dashboard"))
        
        # Los tabs
        tab_labels = [
            lang.get_text("tab_stats"),
            lang.get_text("tab_todos"),
            lang.get_text("tab_dupes"),
            lang.get_text("tab_metrics"),
        ]
        for btn, label in zip(self._tab_btns, tab_labels):
            try:
                btn.configure(text=f"  {label}")
            except Exception:
                pass
        
        if hasattr(self, '_header_titles') and hasattr(self, '_header_buttons'):
            # Recorrer los headers y actualizar segun el tipo de pagina
            for i, (title_lbl, btn) in enumerate(zip(self._header_titles, self._header_buttons)):
                try:
                    # Identificar de que pagina estÃƒÆ’Ã‚Â¡ buscando el parent
                    parent_frame = title_lbl.master.master  # bar -> page
                    
                    # Buscar el aÃƒâ€šÃ‚Â­ndice de la pagina
                    if parent_frame in self._pages:
                        page_idx = self._pages.index(parent_frame)
                        
                        # Actualizar segaÃƒâ€šÃ‚Âºn la pagina
                        if page_idx == 1:  # TODOs page
                            title_lbl.configure(text=lang.get_text("dash_todos_title"))
                            btn.configure(text=f"  {lang.get_text('dash_scan_btn')}")
                        elif page_idx == 2:  # Duplicates page
                            title_lbl.configure(text=lang.get_text("dash_dupes_title"))
                            btn.configure(text=f"  {lang.get_text('dash_dupes_btn')}")
                except:
                    pass
        
        # STATS PAGE - Tarjetas y Cards
        if hasattr(self, 'card_files'):
            self.card_files._title_lbl.configure(text=lang.get_text("dash_files"))
            self.card_lines._title_lbl.configure(text=lang.get_text("dash_lines"))
            self.card_size._title_lbl.configure(text=lang.get_text("dash_size"))
        
        if hasattr(self, '_files_chart_card'):
            self._files_chart_card._title_lbl.configure(text=lang.get_text("dash_files_by_ext"))
        
        if hasattr(self, '_lines_chart_card'):
            self._lines_chart_card._title_lbl.configure(text=lang.get_text("dash_lines_by_lang"))
        
        if hasattr(self, '_distribution_card'):
            self._distribution_card._title_lbl.configure(text=lang.get_text("dash_distribution"))
        
        # TODOS PAGE - Tarjetas y Cards
        if hasattr(self, 'todos_card_errors'):
            self.todos_card_errors._title_lbl.configure(text=lang.get_text("dash_errors"))
            self.todos_card_todos._title_lbl.configure(text=lang.get_text("dash_todos"))
            self.todos_card_fixmes._title_lbl.configure(text=lang.get_text("dash_fixmes"))
        
        if hasattr(self, '_todos_results_card'):
            self._todos_results_card._title_lbl.configure(text=lang.get_text("dash_results"))
        if hasattr(self, "todos_tree"):
            self.todos_tree.heading("kind", text=lang.get_text("dash_col_type"))
            self.todos_tree.heading("file", text=lang.get_text("dash_col_file"))
            self.todos_tree.heading("line", text=lang.get_text("dash_col_line"))
            self.todos_tree.heading("message", text=lang.get_text("dash_col_message"))
        if hasattr(self, "_todos_hint") and not getattr(self, "_todo_issue_rows", []):
            self._todos_hint.configure(text=lang.get_text("dash_select_finding"))
        if hasattr(self, '_todos_open_btn'):
            self._todos_open_btn.configure(text=lang.get_text("dash_open_with"))
        if hasattr(self, '_todos_go_btn'):
            self._todos_go_btn.configure(text=lang.get_text("dash_go"))
        
        # DUPLICATES PAGE - Tarjetas y Cards
        if hasattr(self, 'dupes_card'):
            self.dupes_card._title_lbl.configure(text=lang.get_text("dash_cases_found"))
            self.dupes_lines_card._title_lbl.configure(text=lang.get_text("dash_lines_dupes"))
        
        if hasattr(self, '_dupes_details_card'):
            self._dupes_details_card._title_lbl.configure(text=lang.get_text("dash_details"))
        
        # METRICS PAGE - Cards
        if hasattr(self, '_top_lines_card'):
            self._top_lines_card._title_lbl.configure(text=lang.get_text("dash_top_lines"))
        
        if hasattr(self, '_top_size_card'):
            self._top_size_card._title_lbl.configure(text=lang.get_text("dash_top_size"))
        if hasattr(self, '_dupes_overlay'):
            self._dupes_overlay.set_message(lang.get_text("dash_searching_duplicates"))
        
        # Actualizar tabla de distribucicon si hay datos
        if hasattr(self, '_selected_files') and self._selected_files:
            try:
                stats = self.project_stats.calculate_stats(self._selected_files)
                self._update_language_table(stats)
            except:
                pass
        if hasattr(self, "top_lines_frame") and hasattr(self, "top_size_frame"):
            try:
                self._update_metrics_tables(self._selected_files)
            except Exception:
                pass

    def _load_icons(self, bg=None):
        try:
            from PIL import Image, ImageTk
            from utils.file_icons import FileIconManager
            
            icon_dir = resource_path("assets/icons")
            t = self.theme_manager.get_theme()
            c = bg or t["secondary_bg"]

            def _rgb(h):
                h = h.lstrip("#")
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

            def load(name, size=(16, 16), bg_color=None):
                path = os.path.join(icon_dir, name)
                if not os.path.exists(path):
                    return None
                img = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                # Usar el color de fondo especificado o el por defecto
                bg_to_use = bg_color if bg_color else c
                bg_img = Image.new("RGBA", img.size, _rgb(bg_to_use) + (255,))
                bg_img.paste(img, mask=img.split()[3])
                return ImageTk.PhotoImage(bg_img.convert("RGB"))

            # Iconos para diferentes contextos
            self._icons = {
                # Iconos con fondo de titulo/card (secondary_bg) - estos aparecen en headers de cards
                "dashboard":   load("dashboard.png", (16, 16), c),
                "stats":   load("chart-pie.png", (16, 16), c),
                "metrics": load("chart-bar.png", (16, 16), c),
                "todos":   load("todo.png", (16, 16), c),
                "dupes":   load("duplicate.png", (16, 16), c),
                "trophy":  load("trophy.png", (16, 16), c),
                "file":    load("file.png", (13, 13), c),
                
                # Iconos para botones (button_bg)
                "scan":    load("scan.png", (16, 16), t["button_bg"]),
                
                # Icono de cerrar
                "close":   load("close.png", (16, 16), c),
            }
            
            # a NUEVO: Cargar iconos de lenguajes AUTOMaÃƒâ€šÃ‚ÂTICAMENTE
            icon_manager = FileIconManager()
            language_map = self.project_stats.LANGUAGE_MAP
            
            self._lang_icons = {}
            for ext, lang_name in language_map.items():
                if ext in icon_manager.ICON_MAP:
                    icon_name = icon_manager.ICON_MAP[ext]
                    icon = load(icon_name, (16, 16), c)
                    if icon:
                        self._lang_icons[lang_name] = icon
            
        except Exception as e:
            print(f"Error loading icons: {e}")
            self._icons = {}
            self._lang_icons = {}

    def _icon(self, name):
        return self._icons.get(name)

    # UI BUILD

    def _build_ui(self):
        lang = self.language_manager
        # Tab bar
        self._tab_bar = tk.Frame(self.content_frame, height=38)  # a CAMBIAR
        self._tab_bar.pack(fill="x")
        self._tab_bar.pack_propagate(False)

        tab_defs = [
            ("stats",   lang.get_text("tab_stats")),
            ("todos",   lang.get_text("tab_todos")),
            ("dupes",   lang.get_text("tab_dupes")),
            ("metrics", lang.get_text("tab_metrics")),
        ]
        self._tab_btns = []
        for i, (ico_key, label) in enumerate(tab_defs):
            btn = tk.Label(
                self._tab_bar, text=f"  {label}",
                font=("Segoe UI", 9), cursor="hand2",
                padx=14, pady=8,
            )
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, idx=i: self._switch_tab(idx))
            btn.bind("<Enter>",    lambda e, b=btn: self._tab_hover_on(b))
            btn.bind("<Leave>",    lambda e, b=btn: self._tab_hover_off(b))
            self._tab_btns.append(btn)

        self._sep_tabs = tk.Frame(self.content_frame, height=1)  # a CAMBIAR
        self._sep_tabs.pack(fill="x")

        # PaÃƒâ€šÃ‚Â¡ginas
        self._pages_frame = tk.Frame(self.content_frame)  # a CAMBIAR
        self._pages_frame.pack(fill="both", expand=True)

        self._pages = [tk.Frame(self._pages_frame, bd=0) for _ in range(4)]

        self._build_stats_page(self._pages[0])
        self._build_todos_page(self._pages[1])
        self._build_dupes_page(self._pages[2])
        self._build_metrics_page(self._pages[3])

        self._show_page(0)

    # paginas

    def _build_stats_page(self, parent):
        # Container principal - 2 columnas
        lang = self.language_manager
        main_container = tk.Frame(parent)
        main_container.pack(fill="both", expand=True, padx=14, pady=14)
        
        # Columna izquierda (65% del ancho)
        left_col = tk.Frame(main_container)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 7))
        
        # Columna derecha (35% del ancho)
        right_col = tk.Frame(main_container)
        right_col.pack(side="right", fill="both", expand=False, padx=(7, 0))
        right_col.configure(width=350)
        right_col.pack_propagate(False)
        
        # IZQUIERDA: Tarjetas + GraÃƒâ€šÃ‚Â¡ficos
        cards_frame = tk.Frame(left_col)
        cards_frame.pack(fill="x", pady=(0, 8))

        # Cargar iconos para las tarjetas
        from utils.file_icons import FileIconManager
        icon_mgr = FileIconManager()
        icon_files = icon_mgr.load_icon('folder.png', (20, 20))
        icon_lines = icon_mgr.load_icon('code.png', (20, 20))
        icon_size = icon_mgr.load_icon('database.png', (20, 20))

        self.card_files = self._stat_card(cards_frame, lang.get_text("dash_files"), "0", icon_files)
        self.card_files.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self.card_lines = self._stat_card(cards_frame, lang.get_text("dash_lines"), "0", icon_lines)
        self.card_lines.pack(side="left", fill="both", expand=True, padx=(2, 2))

        self.card_size = self._stat_card(cards_frame, lang.get_text("dash_size"), "0 KB", icon_size)
        self.card_size.pack(side="left", fill="both", expand=True, padx=(4, 0))
        
        # GraÃƒâ€šÃ‚Â¡ficos (maÃƒâ€šÃ‚Â¡s compactos)
        charts_row = tk.Frame(left_col)
        charts_row.pack(fill="both", expand=True, pady=(0, 8))
        
        lc = self._card(charts_row, lang.get_text("dash_files_by_ext"), "stats")
        lc.pack(side="left", fill="both", expand=True, padx=(0, 4))
        self.files_chart_frame = tk.Frame(lc, height=200)
        self.files_chart_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.files_chart_frame.pack_propagate(False)
        
            # a GUARDAR REFERENCIA
        self._files_chart_card = lc
        
        rc = self._card(charts_row, lang.get_text("dash_lines_by_lang"), "metrics")
        rc.pack(side="left", fill="both", expand=True, padx=(4, 0))
        self.lines_chart_frame = tk.Frame(rc, height=200)
        self.lines_chart_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.lines_chart_frame.pack_propagate(False)
        
        # a GUARDAR REFERENCIA
        self._lines_chart_card = rc
        
        # DERECHA: Tabla de lenguajes (ocupa toda la columna)
        lang_card = self._card(right_col, lang.get_text("dash_distribution"), "file")
        lang_card.pack(fill="both", expand=True)
        
        # a GUARDAR REFERENCIA
        self._distribution_card = lang_card
        
        self.lang_table_frame = tk.Frame(lang_card)
        self.lang_table_frame.pack(fill="both", expand=True, padx=8, pady=8)

    def _stat_card(self, parent, title, value, icon=None):
        """Tarjeta moderna para estadaÃƒâ€šÃ‚Â­stica."""
        card = tk.Frame(parent, bd=0, highlightthickness=1, relief="solid")
        
        # Header con icono
        header_frame = tk.Frame(card)
        header_frame.pack(padx=12, pady=(10, 2), fill="x")
        
        if icon:
            icon_lbl = tk.Label(header_frame, image=icon)
            icon_lbl.image = icon
            icon_lbl.pack(side="left", padx=(0, 6))
        
        title_lbl = tk.Label(  # a GUARDAR REFERENCIA
            header_frame, text=title,
            font=("Segoe UI", 9), anchor="w"
        )
        title_lbl.pack(side="left")
        
        value_lbl = tk.Label(
            card, text=value,
            font=("Segoe UI", 18, "bold"), anchor="w"
        )
        value_lbl.pack(padx=12, pady=(0, 10), fill="x")
        
        card._value_lbl = value_lbl
        card._title_lbl = title_lbl  # a NUEVA REFERENCIA
        return card

    def _build_todos_page(self, parent):
        """TODOs page con diseaÃƒâ€šÃ‚Â±o mejorado - tarjetas de resumen + lista"""
        lang = self.language_manager
        
        # Header con botcon
        title = lang.get_text("dash_todos_title")
        btn_text = lang.get_text("dash_scan_btn")
        
        header_bar = self._page_header(parent, title, btn_text, "scan", self._scan_todos_async)
    
        # a MARCAR QUaÃƒÂ¢Ã¢â€šÂ¬Ã‚Â° TIPO DE PaÃƒâ€šÃ‚ÂGINA ES
        header_bar._page_type = "todos"
        
        # Container principal
        main_container = tk.Frame(parent)
        main_container.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        
        # Cargar iconos
        from utils.file_icons import FileIconManager
        icon_mgr = FileIconManager()
        icon_error = icon_mgr.load_icon('error.png', (18, 18))  # o 'close.png'
        icon_todo = icon_mgr.load_icon('todo.png', (18, 18))
        icon_fixme = icon_mgr.load_icon('settings.png', (18, 18))  # o 'tool.png'
        
        # Tarjetas de resumen en la parte superior
        summary_frame = tk.Frame(main_container)
        summary_frame.pack(fill="x", pady=(0, 8))
        
        self.todos_card_errors = self._mini_card(summary_frame, lang.get_text("dash_errors"), "0", "#e74c3c", icon_error)
        self.todos_card_errors.pack(side="left", fill="both", expand=True, padx=(0, 4))
        
        self.todos_card_todos = self._mini_card(summary_frame, lang.get_text("dash_todos"), "0", "#3498db", icon_todo)
        self.todos_card_todos.pack(side="left", fill="both", expand=True, padx=(2, 2))
        
        self.todos_card_fixmes = self._mini_card(summary_frame, lang.get_text("dash_fixmes"), "0", "#f39c12", icon_fixme)
        self.todos_card_fixmes.pack(side="left", fill="both", expand=True, padx=(4, 0))
        
        # Lista de resultados
        c = self._card(main_container, lang.get_text("dash_results"), "file")  # a CAMBIAR
        c.pack(fill="both", expand=True)
        self._todos_results_host = tk.Frame(c)
        self._todos_results_host.pack(fill="both", expand=True, padx=8, pady=8)

        self._todos_toolbar = tk.Frame(self._todos_results_host)
        self._todos_toolbar.pack(fill="x", pady=(0, 6))

        self._todos_hint = tk.Label(
            self._todos_toolbar,
            text=lang.get_text("dash_select_finding"),
            font=("Segoe UI", 8),
            anchor="w",
        )
        self._todos_hint.pack(side="left", fill="x", expand=True)

        self._todos_open_btn = tk.Button(
            self._todos_toolbar,
            text=lang.get_text("dash_open_with"),
            command=lambda: self._open_selected_issue(use_open_with=True),
            font=("Segoe UI", 8),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=10,
            pady=4,
            state="disabled",
        )
        self._todos_open_btn.pack(side="right", padx=(6, 0))
        self._style_btn(self._todos_open_btn)

        self._todos_go_btn = tk.Button(
            self._todos_toolbar,
            text=lang.get_text("dash_go"),
            command=self._open_selected_issue,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=12,
            pady=4,
            state="disabled",
        )
        self._todos_go_btn.pack(side="right")
        self._style_btn(self._todos_go_btn)

        tree_wrap = tk.Frame(self._todos_results_host)
        tree_wrap.pack(fill="both", expand=True)

        self.todos_tree = ttk.Treeview(
            tree_wrap,
            columns=("kind", "file", "line", "message"),
            show="headings",
            selectmode="browse",
        )
        self.todos_tree.heading("kind", text=lang.get_text("dash_col_type"))
        self.todos_tree.heading("file", text=lang.get_text("dash_col_file"))
        self.todos_tree.heading("line", text=lang.get_text("dash_col_line"))
        self.todos_tree.heading("message", text=lang.get_text("dash_col_message"))
        self.todos_tree.column("kind", width=90, minwidth=70, anchor="w")
        self.todos_tree.column("file", width=280, minwidth=180, anchor="w")
        self.todos_tree.column("line", width=70, minwidth=60, anchor="e")
        self.todos_tree.column("message", width=520, minwidth=260, anchor="w")
        self.todos_tree.pack(side="left", fill="both", expand=True)

        self._todos_tree_sb = tk.Scrollbar(tree_wrap, orient="vertical", command=self.todos_tree.yview, width=8)
        self._todos_tree_sb.pack(side="right", fill="y")
        self.todos_tree.configure(yscrollcommand=self._todos_tree_sb.set)

        self.todos_tree.bind("<<TreeviewSelect>>", self._on_todo_row_select)
        self.todos_tree.bind("<Double-Button-1>", lambda _e: self._open_selected_issue())

        # a GUARDAR REFERENCIA AL CARD
        self._todos_results_card = c
        
        self._todos_overlay = _LoadingOverlay(c, self.theme_manager, lang.get_text("dash_scanning_code"))

    def _build_dupes_page(self, parent):
        """Ccodigo Duplicado con mejor diseaÃƒâ€šÃ‚Â±o"""
        lang = self.language_manager
        
        # Header con botcon
        title = lang.get_text("dash_dupes_title")
        btn_text = lang.get_text("dash_dupes_btn")
        
        header_bar = self._page_header(parent, title, btn_text, "scan", self._scan_dupes_async)
        
        # a MARCAR QUaÃƒÂ¢Ã¢â€šÂ¬Ã‚Â° TIPO DE PaÃƒâ€šÃ‚ÂGINA ES
        header_bar._page_type = "dupes"
        
        # Container principal
        main_container = tk.Frame(parent)
        main_container.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        
        # Cargar iconos
        from utils.file_icons import FileIconManager
        icon_mgr = FileIconManager()
        icon_dupes = icon_mgr.load_icon('alerts.png', (18, 18))
        icon_lines = icon_mgr.load_icon('code.png', (18, 18))
        
        # Tarjeta de resumen
        summary_frame = tk.Frame(main_container)
        summary_frame.pack(fill="x", pady=(0, 8))
        
        self.dupes_card = self._mini_card(summary_frame, lang.get_text("dash_cases_found"), "0", "#9b59b6", icon_dupes)
        self.dupes_card.pack(side="left", fill="both", expand=True, padx=(0, 4))
        
        self.dupes_lines_card = self._mini_card(summary_frame, lang.get_text("dash_lines_dupes"), "0", "#e67e22", icon_lines)
        self.dupes_lines_card.pack(side="left", fill="both", expand=True, padx=(4, 0))
        
        # Lista de resultados
        c = self._card(main_container, lang.get_text("dash_details"), "dupes")
        c.pack(fill="both", expand=True)
        self.duplicates_text = self._text_widget(c)
        
        # a GUARDAR REFERENCIA
        self._dupes_details_card = c
        
        self._dupes_overlay = _LoadingOverlay(c, self.theme_manager, lang.get_text("dash_searching_duplicates"))

    def _build_metrics_page(self, parent):
        """Top Archivos - Dos columnas lado a lado"""
        lang = self.language_manager
        # Container principal con dos columnas
        main_container = tk.Frame(parent)
        main_container.pack(fill="both", expand=True, padx=14, pady=14)
        
        # Columna izquierda - Top por laÃƒâ€šÃ‚Â­neas
        left_col = tk.Frame(main_container)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 7))
        
        lc = self._card(left_col, lang.get_text("dash_top_lines"), "trophy")
        lc.pack(fill="both", expand=True)
        
        # a GUARDAR REFERENCIA
        self._top_lines_card = lc
        
        # Scroll para la columna izquierda
        left_canvas = tk.Canvas(lc, bd=0, highlightthickness=0)
        left_scrollbar = tk.Scrollbar(lc, orient="vertical", command=left_canvas.yview, width=6)
        self.top_lines_frame = tk.Frame(left_canvas)
        
        self.top_lines_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        
        left_canvas.create_window((0, 0), window=self.top_lines_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        self._top_lines_canvas = left_canvas
        self._top_lines_scrollbar = left_scrollbar
        
        left_scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=8)
        left_canvas.pack(side="left", fill="both", expand=True, padx=(8, 2), pady=8)
        
        def _scroll_left(event):
            try:
                if left_canvas.winfo_exists():
                    delta = -1 if event.num == 4 else 1 if event.num == 5 else int(-1 * (event.delta / 120))
                    left_canvas.yview_scroll(delta, "units")
            except:
                pass
            return "break"
        
        left_canvas.bind("<MouseWheel>", _scroll_left)
        left_canvas.bind("<Button-4>", _scroll_left)
        left_canvas.bind("<Button-5>", _scroll_left)
        
        # Columna derecha - Top por tamaaÃƒâ€šÃ‚Â±o
        right_col = tk.Frame(main_container)
        right_col.pack(side="right", fill="both", expand=True, padx=(7, 0))
        
        rc = self._card(right_col, lang.get_text("dash_top_size"), "trophy")
        rc.pack(fill="both", expand=True)
        
        # a GUARDAR REFERENCIA
        self._top_size_card = rc
        
        # Scroll para la columna derecha
        right_canvas = tk.Canvas(rc, bd=0, highlightthickness=0)
        right_scrollbar = tk.Scrollbar(rc, orient="vertical", command=right_canvas.yview, width=6)
        self.top_size_frame = tk.Frame(right_canvas)
        
        self.top_size_frame.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )
        
        right_canvas.create_window((0, 0), window=self.top_size_frame, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        self._top_size_canvas = right_canvas
        self._top_size_scrollbar = right_scrollbar
        
        right_scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=8)
        right_canvas.pack(side="left", fill="both", expand=True, padx=(8, 2), pady=8)
        
        def _scroll_right(event):
            try:
                if right_canvas.winfo_exists():
                    delta = -1 if event.num == 4 else 1 if event.num == 5 else int(-1 * (event.delta / 120))
                    right_canvas.yview_scroll(delta, "units")
            except:
                pass
            return "break"
        
        right_canvas.bind("<MouseWheel>", _scroll_right)
        right_canvas.bind("<Button-4>", _scroll_right)
        right_canvas.bind("<Button-5>", _scroll_right)

        # Estado inicial para evitar pantalla vacia al abrir.
        self.after(0, lambda: self._update_metrics_tables(self._selected_files))

    def _mini_card(self, parent, title, value, color, icon=None):
        """Mini tarjeta para resaÃƒâ€šÃ‚Âºmenes con icono"""
        card = tk.Frame(parent, bd=0, highlightthickness=1, relief="solid")
        
        # Header con icono
        header_frame = tk.Frame(card)
        header_frame.pack(padx=10, pady=(8, 2), fill="x")
        
        if icon:
            icon_lbl = tk.Label(header_frame, image=icon)
            icon_lbl.image = icon
            icon_lbl.pack(side="left", padx=(0, 5))
        
        title_lbl = tk.Label(  # a GUARDAR REFERENCIA
            header_frame, text=title,
            font=("Segoe UI", 8), anchor="w"
        )
        title_lbl.pack(side="left")
        
        value_lbl = tk.Label(
            card, text=value,
            font=("Segoe UI", 16, "bold"), anchor="w",
            fg=color
        )
        value_lbl.pack(padx=10, pady=(0, 8), fill="x")
        
        card._value_lbl = value_lbl
        card._title_lbl = title_lbl  # a NUEVA REFERENCIA
        card._color = color
        return card

    # WIDGET HELPERS

    def _card(self, parent, title, ico_key):
        outer = tk.Frame(parent, bd=0, highlightthickness=1)
        if title:
            hdr = tk.Frame(outer, height=32)
            hdr.pack(fill="x")
            hdr.pack_propagate(False)
            inner_h = tk.Frame(hdr)
            inner_h.pack(side="left", padx=10, fill="y")
            ico = self._icon(ico_key) if ico_key else None
            if ico:
                li = tk.Label(inner_h, image=ico)
                li.image = ico
                li.pack(side="left", padx=(0, 5))
            
            title_lbl = tk.Label(inner_h, text=title,  #  GUARDAR REFERENCIA
                        font=("Segoe UI", 9, "bold"), anchor="w")
            title_lbl.pack(side="left")
            
            sep = tk.Frame(outer, height=1)
            sep.pack(fill="x")
            outer._hdr = hdr
            outer._sep = sep
            outer._inner_h = inner_h
            outer._title_lbl = title_lbl  # a NUEVA REFERENCIA
        return outer

    def _text_widget(self, parent, height=None):
        wrap_frame = tk.Frame(parent, bd=0)
        wrap_frame.pack(fill="both", expand=True, padx=0, pady=0)

        sb = tk.Scrollbar(wrap_frame, orient="vertical", width=8,
                          relief="flat", bd=0, elementborderwidth=0)
        sb.pack(side="right", fill="y", padx=(0, 2), pady=2)

        kw = dict(font=("Consolas", 9), bd=0, highlightthickness=0,
                  wrap="word", state="disabled", yscrollcommand=sb.set,
                  relief="flat")
        if height:
            kw["height"] = height

        txt = tk.Text(wrap_frame, **kw)
        txt.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        sb.config(command=txt.yview)
        txt._sb = sb

        def _scroll_y(event):
            try:
                if txt.winfo_exists() and txt.winfo_ismapped():
                    delta = int(-1 * (event.delta / 120)) if hasattr(event, 'delta') else (-1 if event.num == 4 else 1)
                    txt.yview_scroll(delta, "units")
            except:
                pass
            return "break"

        txt.bind("<MouseWheel>", _scroll_y)
        txt.bind("<Button-4>", _scroll_y)
        txt.bind("<Button-5>", _scroll_y)

        return txt

    def _page_header(self, parent, title, btn_text, ico_key, cmd):
        bar = tk.Frame(parent, height=46)
        bar.pack(fill="x", padx=14, pady=(12, 6))
        bar.pack_propagate(False)
        
        # a GUARDAR REFERENCIA AL LABEL DEL titulo
        title_lbl = tk.Label(bar, text=title, font=("Segoe UI", 11, "bold"), anchor="w")
        title_lbl.pack(side="left", fill="y")
        
        # Crear boton sin icono inicialmente
        btn = tk.Button(bar, text=f"  {btn_text}",
                        compound="left",
                        command=cmd, font=("Segoe UI", 9), cursor="hand2",
                        bd=0, relief="flat", padx=12, pady=5)
        btn.pack(side="right", pady=6)
        
        # Guardar referencia al boton y la clave del icono para recargarlo despuaÃƒâ€šÃ‚Â©s
        btn._ico_key = ico_key
        
        # Cargar icono con el tema actual
        ico = self._icon(ico_key)
        if ico:
            btn.configure(image=ico)
            btn.image = ico  # critico: mantener referencia a la imagen
        
        self._style_btn(btn)
        
        # Guardar referencia del boton para poder actualizarlo en apply_theme
        if not hasattr(self, '_header_buttons'):
            self._header_buttons = []
        self._header_buttons.append(btn)
        
        # a NUEVO: Guardar referencia del titulo tambien
        if not hasattr(self, '_header_titles'):
            self._header_titles = []
        self._header_titles.append(title_lbl)
        
        # NUEVO: Guardar LA PAGINA en este header
        bar._page_type = None  # Lo asignaremos desde _build_todos_page y _build_dupes_page
        
        return bar

    # TABS

    def _show_page(self, idx):
        for i, p in enumerate(self._pages):
            if i == idx:
                p.pack(fill="both", expand=True)
            else:
                p.pack_forget()
        self._active_tab = idx
        self._update_tab_colors()

    def _switch_tab(self, idx):
        self._show_page(idx)
        if idx == 3:
            # Garantiza refresh al entrar en Top Archivos.
            self._update_metrics_tables(self._selected_files)

    def _update_tab_colors(self):
        t = self.theme_manager.get_theme()
        for i, btn in enumerate(self._tab_btns):
            if i == self._active_tab:
                btn.configure(bg=t["bg"], fg=t["accent"],
                               font=("Segoe UI", 9, "bold"))
            else:
                btn.configure(bg=t["secondary_bg"], fg=t["fg"],
                               font=("Segoe UI", 9))

    def _tab_hover_on(self, btn):
        if btn != self._tab_btns[self._active_tab]:
            btn.configure(bg=self.theme_manager.get_theme()["border"])

    def _tab_hover_off(self, btn):
        if btn in self._tab_btns and \
                self._tab_btns.index(btn) != self._active_tab:
            btn.configure(bg=self.theme_manager.get_theme()["secondary_bg"])

    # THEMING

    def apply_theme(self):
        self.apply_base_theme()
        theme_key = self.theme_manager.current_theme
        if theme_key == self._last_theme_key:
            return
        self._last_theme_key = theme_key

        t       = self.theme_manager.get_theme()
        bg      = t["bg"]
        sec_bg  = t["secondary_bg"]
        fg      = t["fg"]
        border  = t["border"]
        tree_bg = t["tree_bg"]
        tree_fg = t["tree_fg"]
        accent  = t["accent"]
        btn_bg  = t["button_bg"]
        btn_fg  = t["button_fg"]

        self._load_icons(bg=sec_bg)

        self.configure(bg=border)
        self._tab_bar.configure(bg=sec_bg)
        self._pages_frame.configure(bg=bg)
        for p in self._pages:
            p.configure(bg=bg)

        self._update_tab_colors()
        self._theme_recursive(self._pages_frame, t)

        # Tags de color
        if hasattr(self, 'duplicates_text'):
            for txt in [self.duplicates_text]:
                txt.configure(bg=tree_bg, fg=tree_fg)
                
                txt.tag_configure("error", foreground="#e74c3c", font=("Consolas", 9, "bold"))
                txt.tag_configure("warning", foreground="#f39c12", font=("Consolas", 9, "bold"))
                txt.tag_configure("todo", foreground="#3498db", font=("Consolas", 9, "bold"))
                txt.tag_configure("fixme", foreground="#e67e22", font=("Consolas", 9, "bold"))
                txt.tag_configure("duplicate", foreground="#9b59b6", font=("Consolas", 9, "bold"))
                txt.tag_configure("code", foreground="#2ecc71", font=("Consolas", 8))
                txt.tag_configure("line_num", foreground="#7f8c8d", font=("Consolas", 8))
                txt.tag_configure("file", foreground=accent, font=("Consolas", 9, "bold"))
                txt.tag_configure("header", foreground=accent, font=("Consolas", 10, "bold"))
                txt.tag_configure("success", foreground="#27ae60", font=("Consolas", 9, "bold"))
                
                if hasattr(txt, "_sb"):
                    txt._sb.configure(
                        bg=sec_bg,
                        troughcolor=bg,
                        activebackground=accent,
                        highlightthickness=0,
                        bd=0, relief="flat",
                        elementborderwidth=0,
                    )

        if hasattr(self, "todos_tree"):
            style = ttk.Style(self)
            style.configure(
                "Todos.Treeview",
                background=tree_bg,
                fieldbackground=tree_bg,
                foreground=tree_fg,
                borderwidth=0,
                rowheight=24,
                font=("Segoe UI", 9),
            )
            style.configure(
                "Todos.Treeview.Heading",
                background=sec_bg,
                foreground=fg,
                relief="flat",
                font=("Segoe UI", 9, "bold"),
            )
            self.todos_tree.configure(style="Todos.Treeview")
            self.todos_tree.tag_configure("ERR", foreground="#e74c3c")
            self.todos_tree.tag_configure("TODO", foreground="#3498db")
            self.todos_tree.tag_configure("FIXME", foreground="#f39c12")
            self.todos_tree.tag_configure("BUG", foreground="#e67e22")
            self._todos_tree_sb.configure(
                bg=sec_bg,
                troughcolor=bg,
                activebackground=accent,
                highlightthickness=0,
                bd=0,
                relief="flat",
                elementborderwidth=0,
            )

        if hasattr(self, "_top_lines_scrollbar"):
            for sb in [self._top_lines_scrollbar, self._top_size_scrollbar]:
                sb.configure(
                    bg=sec_bg,
                    troughcolor=bg,
                    activebackground=accent,
                    highlightthickness=0,
                    bd=0,
                    relief="flat",
                    elementborderwidth=0,
                    width=6,
                )
            self._top_lines_canvas.configure(bg=tree_bg)
            self._top_size_canvas.configure(bg=tree_bg)
            self.top_lines_frame.configure(bg=tree_bg)
            self.top_size_frame.configure(bg=tree_bg)

        # Tarjetas de stats
        if hasattr(self, 'card_files'):
            for card in [self.card_files, self.card_lines, self.card_size]:
                card.configure(bg=sec_bg, highlightbackground=border, highlightcolor=border)
                for child in card.winfo_children():
                    # Solo aplicar fg a Labels, no a Frames
                    if isinstance(child, tk.Label):
                        child.configure(bg=sec_bg, fg=fg)
                    elif isinstance(child, tk.Frame):
                        child.configure(bg=sec_bg)
                        # Aplicar a los hijos del Frame (header_frame)
                        for subchild in child.winfo_children():
                            if isinstance(subchild, tk.Label):
                                subchild.configure(bg=sec_bg, fg=fg)
                card._value_lbl.configure(fg=accent)

        # Botones - SOLO configurar colores, NO tocar imaÃƒâ€šÃ‚Â¡genes
        for w in self._iter_widgets(self._pages_frame):
            if isinstance(w, tk.Button):
                try:
                    w.configure(bg=btn_bg, fg=btn_fg,
                                activebackground=t["button_hover"],
                                activeforeground=btn_fg)
                except:
                    pass

        # a AGREGAR ESTA SECCIaÃƒÂ¢Ã¢â€šÂ¬Ã…â€œN NUEVA:
        # Mini tarjetas de TODOs y Duplicados
        if hasattr(self, 'todos_card_errors'):
            for card in [self.todos_card_errors, self.todos_card_todos, self.todos_card_fixmes]:
                card.configure(bg=sec_bg, highlightbackground=border, highlightcolor=border)
                for child in card.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=sec_bg, fg=fg)
                    elif isinstance(child, tk.Frame):
                        child.configure(bg=sec_bg)
                        for subchild in child.winfo_children():
                            if isinstance(subchild, tk.Label):
                                subchild.configure(bg=sec_bg, fg=fg)
                # Mantener el color del valor
                card._value_lbl.configure(fg=card._color)

        if hasattr(self, 'dupes_card'):
            for card in [self.dupes_card, self.dupes_lines_card]:
                card.configure(bg=sec_bg, highlightbackground=border, highlightcolor=border)
                for child in card.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=sec_bg, fg=fg)
                    elif isinstance(child, tk.Frame):
                        child.configure(bg=sec_bg)
                        for subchild in child.winfo_children():
                            if isinstance(subchild, tk.Label):
                                subchild.configure(bg=sec_bg, fg=fg)
                # Mantener el color del valor
                card._value_lbl.configure(fg=card._color)

        # Recargar iconos de botones de headers con el nuevo tema
        if hasattr(self, '_header_buttons'):
            for btn in self._header_buttons:
                if hasattr(btn, '_ico_key') and btn.winfo_exists():
                    ico = self._icon(btn._ico_key)
                    if ico:
                        btn.configure(image=ico)
                        btn.image = ico

    def _theme_recursive(self, widget, t):
        bg     = t["bg"]
        sec_bg = t["secondary_bg"]
        fg     = t["fg"]
        border = t["border"]

        try:
            cls = type(widget).__name__
            if cls == "Frame":
                if hasattr(widget, "_sep"):
                    widget.configure(bg=sec_bg,
                                     highlightbackground=border,
                                     highlightthickness=1)
                    widget._sep.configure(bg=border)
                    if hasattr(widget, "_hdr"):
                        widget._hdr.configure(bg=sec_bg)
                    if hasattr(widget, "_inner_h"):
                        self._set_bg_deep(widget._inner_h, sec_bg, fg)
                else:
                    widget.configure(bg=bg)
            elif cls == "Label":
                try:
                    pbg = widget.master.cget("bg")
                except Exception:
                    pbg = bg
                widget.configure(bg=pbg, fg=fg)
            elif cls == "Canvas":
                widget.configure(bg=bg)
        except Exception:
            pass

        for child in widget.winfo_children():
            self._theme_recursive(child, t)

    def _set_bg_deep(self, widget, bg, fg):
        try:
            widget.configure(bg=bg)
            if isinstance(widget, tk.Label):
                widget.configure(fg=fg)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._set_bg_deep(child, bg, fg)

    def _build_top_header(self, parent, value_title, t):
        header = tk.Frame(parent, bg=t["secondary_bg"], height=26)
        header.pack(fill="x", pady=(0, 2))
        tk.Label(
            header, text="#", width=3, anchor="e",
            font=("Segoe UI", 8, "bold"), bg=t["secondary_bg"], fg=t["fg"]
        ).pack(side="left", padx=(6, 4))
        tk.Label(
            header, text=value_title, width=12, anchor="e",
            font=("Segoe UI", 8, "bold"), bg=t["secondary_bg"], fg=t["fg"]
        ).pack(side="left", padx=(0, 8))
        tk.Label(
            header, text="Archivo", anchor="w",
            font=("Segoe UI", 8, "bold"), bg=t["secondary_bg"], fg=t["fg"]
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

    def _ellipsize_middle(self, text, max_chars=44):
        if len(text) <= max_chars:
            return text
        head = max(8, int(max_chars * 0.58))
        tail = max(8, max_chars - head - 1)
        return f"{text[:head]}aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¦{text[-tail:]}"

    def _iter_widgets(self, widget):
        yield widget
        for child in widget.winfo_children():
            yield from self._iter_widgets(child)

    def _style_btn(self, btn):
        def on_enter(e):
            try:
                btn.configure(bg=self.theme_manager.get_theme()["button_hover"])
            except:
                pass
        def on_leave(e):
            try:
                btn.configure(bg=self.theme_manager.get_theme()["button_bg"])
            except:
                pass
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # OVERLAY HELPERS

    def _show_overlay(self, overlay, text_widget):
        parent = text_widget.master
        overlay.place(in_=parent, relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()
        overlay.start()

    def _hide_overlay(self, overlay, text_widget):
        overlay.stop()
        overlay.place_forget()

    # DATOS aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â PaÃƒâ€¦Ã‚Â¡BLICO
    
    def update_dashboard(self, selected_files):
        self._dbg(f"update_dashboard input={len(selected_files or [])}")
        if not selected_files:
            self._selected_files = []
            self._update_metrics_tables(self._selected_files)
            self._dbg("Sin seleccion, mostrando placeholder en Top Archivos")
            return

        filtered_files = [
            fp for fp in selected_files
            if self._is_allowed_selected_file(fp)
        ]
        self._dbg(f"filtrados={len(filtered_files)}")
        if filtered_files:
            self._selected_files = filtered_files
        else:
            fallback_files = []
            for fp in selected_files:
                cleaned = str(fp or "").strip().strip("\"'`")
                cleaned = os.path.normpath(cleaned)
                if os.path.isfile(cleaned):
                    fallback_files.append(cleaned)
            self._selected_files = fallback_files
        self._dbg(f"usados={len(self._selected_files)}")

        stats = self.project_stats.calculate_stats(self._selected_files)
        self.card_files._value_lbl.configure(text=str(stats.get("total_files", 0)))
        self.card_lines._value_lbl.configure(text=f"{stats.get('total_lines', 0):,}")
        self.card_size._value_lbl.configure(text=self._format_size(stats.get("total_size", 0)))
        self._update_files_chart(stats)
        self._update_lines_chart(stats)
        self._update_language_table(stats)
        self._update_metrics_tables(self._selected_files)

    def _is_allowed_selected_file(self, filepath):
        try:
            fp = str(filepath or "").strip().strip("\"'`")
            fp = os.path.normpath(fp)
            if not fp or not os.path.isfile(fp):
                return False
            ext = os.path.splitext(fp)[1].lower()
            if ext in self._IGNORED_EXTS:
                return False
            normalized = fp.replace("\\", "/")
            parts = {p.lower() for p in normalized.split("/") if p}
            return not any(p in self._IGNORED_DIRS for p in parts)
        except Exception:
            return False

    # GRAFICAS Y TABLAS

    def _update_files_chart(self, stats):
        for w in self.files_chart_frame.winfo_children():
            w.destroy()
        if not stats.get("by_extension"):
            return
        t  = self.theme_manager.get_theme()
        sx = sorted(stats["by_extension"].items(),
                    key=lambda x: x[1]["count"], reverse=True)[:8]
        labels = [e for e, _ in sx]
        values = [d["count"] for _, d in sx]

        fig = Figure(figsize=(3.2, 2.5), dpi=85)
        fig.patch.set_facecolor(t["secondary_bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(t["secondary_bg"])
        colors = self._palette(len(values), t["accent"])
        ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90,
               colors=colors,
               textprops={"color": t["fg"], "fontsize": 7})
        ax.axis("equal")
        fig.tight_layout(pad=0.3)
        self._embed_chart(fig, self.files_chart_frame, t)

    def _update_lines_chart(self, stats):
        for w in self.lines_chart_frame.winfo_children():
            w.destroy()
        if not stats.get("by_extension"):
            return
        t = self.theme_manager.get_theme()
        ld = self.project_stats.get_language_distribution(stats)
        sl = sorted(ld.items(), key=lambda x: x[1]["lines"], reverse=True)[:8]
        labels = [lang for lang, _ in sl]
        values = [d["lines"] for _, d in sl]

        fig = Figure(figsize=(3.2, 2.5), dpi=85)
        fig.patch.set_facecolor(t["secondary_bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(t["secondary_bg"])
        colors = self._palette(len(values), t["accent"])
        ax.barh(labels, values, color=colors, height=0.5)
        ax.invert_yaxis()
        ax.set_xlabel(self.language_manager.get_text("dash_lines_count"), color=t["fg"], fontsize=7)
        ax.tick_params(colors=t["fg"], labelsize=7)
        for sp in ax.spines.values():
            sp.set_edgecolor(t["border"])
        fig.tight_layout(pad=0.3)
        self._embed_chart(fig, self.lines_chart_frame, t)

    def _embed_chart(self, fig, frame, t):
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        w = canvas.get_tk_widget()
        w.configure(bg=t["secondary_bg"], highlightthickness=0)
        w.pack(fill="both", expand=True)

    def _update_language_table(self, stats):
        """Tabla de lenguajes COMPACTA y CORRECTA."""
        lang = self.language_manager
        for w in self.lang_table_frame.winfo_children():
            w.destroy()
        
        if not stats.get("by_extension"):
            tk.Label(self.lang_table_frame, 
                    text="Sin datos",
                    font=("Segoe UI", 9)).pack(pady=20)
            return
        
        t = self.theme_manager.get_theme()
        ld = self.project_stats.get_language_distribution(stats)
        sl = sorted(ld.items(), key=lambda x: x[1]["lines"], reverse=True)[:15]
        
        if not sl:
            tk.Label(self.lang_table_frame, 
                    text="Sin datos",
                    font=("Segoe UI", 9)).pack(pady=20)
            return
        
        # Header compacto con 4 columnas
        header = tk.Frame(self.lang_table_frame, bg=t["secondary_bg"])
        header.pack(fill="x", pady=(0, 1))
        
        tk.Label(header, text=lang.get_text("dash_lang"), font=("Segoe UI", 8, "bold"), 
                width=8, anchor="w", bg=t["secondary_bg"], fg=t["fg"]).pack(side="left", padx=(6, 2), pady=4)
        tk.Label(header, text=lang.get_text("dash_files_count"), font=("Segoe UI", 8, "bold"), 
                width=8, anchor="e", bg=t["secondary_bg"], fg=t["fg"]).pack(side="left", padx=2, pady=4)
        tk.Label(header, text=lang.get_text("dash_lines_count"), font=("Segoe UI", 8, "bold"), 
                width=8, anchor="e", bg=t["secondary_bg"], fg=t["fg"]).pack(side="left", padx=2, pady=4)
        tk.Label(header, text=lang.get_text("dash_size_label"), font=("Segoe UI", 8, "bold"), 
                width=8, anchor="e", bg=t["secondary_bg"], fg=t["fg"]).pack(side="left", padx=(2, 6), pady=4)
        
        # Rows compactas con 4 columnas
        for i, (lang, data) in enumerate(sl):
            bg_color = t["tree_bg"] if i % 2 == 0 else t["secondary_bg"]
            row = tk.Frame(self.lang_table_frame, bg=bg_color)
            row.pack(fill="x", pady=0)
            
            # Icono + nombre
            lang_cell = tk.Frame(row, bg=bg_color)
            lang_cell.pack(side="left")
            
            icon = self._lang_icons.get(lang)
            if icon:
                icon_lbl = tk.Label(lang_cell, image=icon, bg=bg_color)
                icon_lbl.image = icon
                icon_lbl.pack(side="left", padx=(6, 3), pady=3)
            
            tk.Label(lang_cell, text=lang[:10], font=("Segoe UI", 8), bg=bg_color, fg=t["tree_fg"],
                    anchor="w", width=6).pack(side="left", pady=3)
            
            # Cantidad de archivos
            tk.Label(row, text=str(data['count']), font=("Segoe UI", 8), bg=bg_color, fg=t["tree_fg"],
                    width=8, anchor="e").pack(side="left", padx=2, pady=3)
            
            # LaÃƒâ€šÃ‚Â­neas
            tk.Label(row, text=f"{data['lines']:,}", font=("Segoe UI", 8, "bold"), bg=bg_color, fg=t["accent"],
                    width=8, anchor="e").pack(side="left", padx=2, pady=3)
            
            # TamaaÃƒâ€šÃ‚Â±o
            size_bytes = data.get("size", 0)
            tk.Label(row, text=self._format_size(size_bytes), font=("Segoe UI", 8), bg=bg_color, fg=t["tree_fg"],
                    width=8, anchor="e").pack(side="left", padx=(2, 6), pady=3)

    def _update_metrics_tables(self, selected_files):
        """Actualizar top archivos con visual mas compacta."""
        t = self.theme_manager.get_theme()
        files = list(selected_files or [])
        self._dbg(f"_update_metrics_tables selected={len(files)}")

        for w in self.top_lines_frame.winfo_children():
            w.destroy()
        for w in self.top_size_frame.winfo_children():
            w.destroy()

        try:
            top_lines = self.project_stats.get_top_files_by_lines(files)
        except Exception as e:
            self._dbg(f"top_lines error: {e}")
            top_lines = []
        self._dbg(f"top_lines={len(top_lines)}")

        if not top_lines:
            tk.Label(
                self.top_lines_frame, text=self.language_manager.get_text("dash_no_data"),
                font=("Segoe UI", 9), fg=t["fg"], bg=t["tree_bg"]
            ).pack(pady=20)
        else:
            self._build_top_header(self.top_lines_frame, "Lineas", t)
            max_lines = max(fi["lines"] for fi in top_lines) or 1
            for i, fi in enumerate(top_lines, 1):
                bg_color = t["tree_bg"] if i % 2 == 0 else t["secondary_bg"]
                row = tk.Frame(self.top_lines_frame, bg=bg_color, height=30)
                row.pack(fill="x", pady=1)
                tk.Label(row, text=f"{i}.", font=("Segoe UI", 9), bg=bg_color, fg=t["tree_fg"], width=3, anchor="e").pack(side="left", padx=(8, 4), pady=4)
                tk.Label(row, text=f"{fi['lines']:,} lin", font=("Segoe UI", 9, "bold"), bg=bg_color, fg=t["accent"], width=12, anchor="e").pack(side="left", padx=(0, 8), pady=4)
                bar_width = int((fi["lines"] / max_lines) * 190)
                bar_container = tk.Frame(row, width=190, height=10, bg=t["border"])
                bar_container.pack(side="left", padx=(0, 8), pady=4)
                bar_container.pack_propagate(False)
                if bar_width > 0:
                    tk.Frame(bar_container, width=bar_width, height=10, bg=t["accent"]).place(x=0, y=0)
                rel = self.file_manager.get_relative_path(fi["path"])
                tk.Label(row, text=self._ellipsize_middle(rel), font=("Segoe UI", 9), bg=bg_color, fg=t["tree_fg"], anchor="w").pack(side="left", fill="x", expand=True, padx=(0, 8), pady=4)

        try:
            top_size = self.project_stats.get_top_files_by_size(files)
        except Exception as e:
            self._dbg(f"top_size error: {e}")
            top_size = []
        self._dbg(f"top_size={len(top_size)}")

        if not top_size:
            tk.Label(
                self.top_size_frame, text=self.language_manager.get_text("dash_no_data"),
                font=("Segoe UI", 9), fg=t["fg"], bg=t["tree_bg"]
            ).pack(pady=20)
        else:
            self._build_top_header(self.top_size_frame, "TamaÃƒÆ’Ã‚Â±o", t)
            max_size = max(fi["size"] for fi in top_size) or 1
            for i, fi in enumerate(top_size, 1):
                bg_color = t["tree_bg"] if i % 2 == 0 else t["secondary_bg"]
                row = tk.Frame(self.top_size_frame, bg=bg_color, height=30)
                row.pack(fill="x", pady=1)
                tk.Label(row, text=f"{i}.", font=("Segoe UI", 9), bg=bg_color, fg=t["tree_fg"], width=3, anchor="e").pack(side="left", padx=(8, 4), pady=4)
                tk.Label(row, text=fi["size_formatted"], font=("Segoe UI", 9, "bold"), bg=bg_color, fg=t["accent"], width=12, anchor="e").pack(side="left", padx=(0, 8), pady=4)
                bar_width = int((fi["size"] / max_size) * 190)
                bar_container = tk.Frame(row, width=190, height=10, bg=t["border"])
                bar_container.pack(side="left", padx=(0, 8), pady=4)
                bar_container.pack_propagate(False)
                if bar_width > 0:
                    tk.Frame(bar_container, width=bar_width, height=10, bg=t["accent"]).place(x=0, y=0)
                rel = self.file_manager.get_relative_path(fi["path"])
                tk.Label(row, text=self._ellipsize_middle(rel), font=("Segoe UI", 9), bg=bg_color, fg=t["tree_fg"], anchor="w").pack(side="left", fill="x", expand=True, padx=(0, 8), pady=4)

    def _scan_todos_async(self):
        if self._loading:
            return
        self._loading = True
        self._show_overlay(self._todos_overlay, self._todos_results_host)
        threading.Thread(target=self._scan_todos_worker, daemon=True).start()

    def _scan_todos_worker(self):
        import time
        import ast
        
        try:
            if not self._selected_files:
                issues = []
                summary = {"errors": 0, "todos": 0, "fixmes": 0, "bugs": 0}
                empty_message = "aqui, no hay archivos seleccionados para analizar"
            else:
                start_time = time.time()
                total_files = len(self._selected_files)
                
                findings = {}
                syntax_errors = {}
                
                for i, fp in enumerate(self._selected_files):
                    try:
                        partial = self.code_analyzer.find_todos_in_files([fp])
                        if partial:
                            findings.update(partial)
                        
                        # Errores de sintaxis Python
                        if fp.endswith('.py'):
                            try:
                                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                                    ast.parse(f.read())
                            except SyntaxError as e:
                                if fp not in syntax_errors:
                                    syntax_errors[fp] = []
                                syntax_errors[fp].append({
                                    'line': e.lineno,
                                    'msg': str(e.msg),
                                    'text': e.text.strip() if e.text else ''
                                })
                    except:
                        pass
                    
                    if i % 5 == 0 or i == total_files - 1:
                        elapsed = time.time() - start_time
                        pct = int((i + 1) / total_files * 100) if total_files else 100
                        rate = (i + 1) / elapsed if elapsed > 0 else 0
                        remaining = (total_files - i - 1) / rate if rate > 0 else 0
                        
                        status_msg = f"{i + 1}/{total_files} archivos  a {pct}%  a  {remaining:.1f}s"
                        self.after(0, lambda msg=status_msg: self._todos_overlay.set_sub(msg))
                        self.after(0, lambda p=pct: self._todos_overlay.set_bar(p))
                
                issues = []
                errors_count = 0
                
                # Errores de sintaxis
                if syntax_errors:
                    for fp, errors in sorted(syntax_errors.items()):
                        for err in errors:
                            errors_count += 1
                            issues.append({
                                "kind": "Error",
                                "kind_tag": "ERR",
                                "file_abs": fp,
                                "file_rel": self.file_manager.get_relative_path(fp),
                                "line": int(err.get("line") or 1),
                                "message": err.get("msg", "Error de sintaxis"),
                                "preview": err.get("text", ""),
                            })
                
                # TODOs
                todo_count = 0
                fixme_count = 0
                bug_count = 0
                if findings:
                    for fp, items in sorted(findings.items()):
                        for item in items:
                            typ = item.get("type", "BUG")
                            if typ == "TODO":
                                todo_count += 1
                            elif typ == "FIXME":
                                fixme_count += 1
                            else:
                                bug_count += 1
                            issues.append({
                                "kind": typ,
                                "kind_tag": typ if typ in ("TODO", "FIXME", "BUG") else "BUG",
                                "file_abs": fp,
                                "file_rel": self.file_manager.get_relative_path(fp),
                                "line": int(item.get("line") or 1),
                                "message": item.get("text", ""),
                                "preview": "",
                            })

                issues.sort(key=lambda r: (r["file_rel"].lower(), r["line"], r["kind"]))
                summary = {"errors": errors_count, "todos": todo_count, "fixmes": fixme_count, "bugs": bug_count}
                empty_message = "No se encontraron errores, TODOs, FIXMEs ni BUGs"
                
        except Exception as e:
            issues = []
            summary = {"errors": 0, "todos": 0, "fixmes": 0, "bugs": 0}
            empty_message = f"aÃƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ Error: {e}"
        finally:
            self.after(0, lambda: self._finish_todos(issues, summary, empty_message))

    def _finish_todos(self, issues, summary, empty_message):
        self._hide_overlay(self._todos_overlay, self._todos_results_host)
        self._render_todos_issues(issues, summary, empty_message)
        self._loading = False

    def _render_todos_issues(self, issues, summary, empty_message):
        self._todo_issue_rows = issues or []
        self._todo_issue_map = {}

        self.todos_card_errors._value_lbl.configure(text=str(summary.get("errors", 0)))
        self.todos_card_todos._value_lbl.configure(text=str(summary.get("todos", 0)))
        self.todos_card_fixmes._value_lbl.configure(text=str(summary.get("fixmes", 0)))

        for iid in self.todos_tree.get_children():
            self.todos_tree.delete(iid)

        if not self._todo_issue_rows:
            self._todos_hint.configure(text=empty_message)
            self._todos_go_btn.configure(state="disabled")
            self._todos_open_btn.configure(state="disabled")
            return

        self._todos_hint.configure(
            text=f"Errores: {summary.get('errors', 0)}  aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢  TODOs: {summary.get('todos', 0)}  aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢  FIXMEs: {summary.get('fixmes', 0)}  aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢  BUGs: {summary.get('bugs', 0)}"
        )

        for row in self._todo_issue_rows:
            iid = self.todos_tree.insert(
                "",
                "end",
                values=(row["kind"], row["file_rel"], row["line"], row["message"]),
                tags=(row["kind_tag"],),
            )
            self._todo_issue_map[iid] = row

        first = self.todos_tree.get_children()
        if first:
            self.todos_tree.selection_set(first[0])
            self.todos_tree.focus(first[0])
        self._on_todo_row_select()

    def _on_todo_row_select(self, _event=None):
        sel = self.todos_tree.selection()
        state = "normal" if sel else "disabled"
        self._todos_go_btn.configure(state=state)
        self._todos_open_btn.configure(state=state)

    def _open_selected_issue(self, use_open_with=False):
        sel = self.todos_tree.selection()
        if not sel:
            return
        row = self._todo_issue_map.get(sel[0])
        if not row:
            return
        self._open_issue_location(row, use_open_with=use_open_with)

    def _normalize_issue_path(self, row):
        raw = str(row.get("file_abs") or "").strip()
        raw = raw.replace("\ufeff", "").replace("\u200b", "")
        quote_chars = "\"'`aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚ÂaÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¹Ã…â€œaÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢"
        while raw and raw[0] in quote_chars:
            raw = raw[1:]
        while raw and raw[-1] in quote_chars:
            raw = raw[:-1]
        if raw:
            candidate = os.path.normpath(os.path.expandvars(os.path.expanduser(raw)))
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)

        file_rel = str(row.get("file_rel") or "").strip().strip("\"'")
        root_path = getattr(self.file_manager, "root_path", "") or ""
        if file_rel and root_path:
            file_rel = file_rel.lstrip("\\/")
            candidate = os.path.normpath(os.path.join(root_path, file_rel))
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)

        return ""

    def _open_issue_location(self, row, use_open_with=False):
        file_path = self._normalize_issue_path(row)
        line = int(row.get("line") or 1)
        if not file_path:
            self._todos_hint.configure(
                text=f"No se pudo abrir: archivo no encontrado ({row.get('file_rel', 'ruta desconocida')})"
            )
            return

        try:
            if os.name == "nt":
                if use_open_with:
                    subprocess.Popen(
                        ["rundll32.exe", "shell32.dll,OpenAs_RunDLL", file_path],
                        close_fds=True
                    )
                    self._todos_hint.configure(text=f"{self.language_manager.get_text('dash_open_with')} {row['file_rel']}")
                else:
                    # "Ir": abre la ubicacicon del archivo sin depender de asociaciones de app.
                    subprocess.Popen(["explorer.exe", "/select,", file_path], close_fds=True)
                    self._todos_hint.configure(text=f"Ubicacicon abierta: {row['file_rel']}")
            else:
                os.startfile(file_path)
                self._todos_hint.configure(text=f"Archivo abierto: {row['file_rel']}")
            try:
                self.clipboard_clear()
                self.clipboard_append(str(line))
            except Exception:
                pass
            self._todos_hint.configure(
                text=f"{self._todos_hint.cget('text')} la linea {line} copiada al portapapeles."
            )
        except Exception as e:
            self._todos_hint.configure(text=f"No se pudo abrir el archivo: {e}")

    def _scan_dupes_async(self):
        if self._loading:
            return
        if not self._selected_files:
            self._write_colored(self.duplicates_text, 
                              [("aqui, Selecciona archivos para analizar", "warning")])
            return
        
        self._loading = True
        self._show_overlay(self._dupes_overlay, self.duplicates_text)
        threading.Thread(target=self._scan_dupes_worker, daemon=True).start()

    def _scan_dupes_worker(self):
        import time
        
        try:
            code_exts = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', 
                        '.cs', '.php', '.rb', '.go', '.rs', '.kt', '.swift'}
            code_files = [f for f in self._selected_files 
                         if os.path.isfile(f) and os.path.splitext(f)[1] in code_exts]
            
            if not code_files:
                result = [("aqui, No hay archivos de codigo seleccionados", "warning")]
            else:
                start_time = time.time()
                total_files = len(code_files)
                
                file_hashes = {}
                for i, fp in enumerate(code_files):
                    if i % 5 == 0 or i == total_files - 1:
                        pct = int((i + 1) / total_files * 50)
                        elapsed = time.time() - start_time
                        rate = (i + 1) / elapsed if elapsed > 0 else 0
                        remaining = (total_files - i - 1) / rate if rate > 0 else 0
                        
                        status_msg = f"Indexando {i + 1}/{total_files}  aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢  {pct}%  aÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢  {remaining:.1f}s"
                        self.after(0, lambda msg=status_msg: self._dupes_overlay.set_sub(msg))
                        self.after(0, lambda p=pct: self._dupes_overlay.set_bar(p))
                    
                    try:
                        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                            file_hashes[fp] = f.readlines()
                    except:
                        pass
                
                duplicates = []
                files_list = list(file_hashes.keys())
                total_comparisons = len(files_list) * (len(files_list) - 1) // 2
                comparisons_done = 0
                MIN_LINES = 8  # Aumentado para ignorar duplicados triviales
                
                for i, file1 in enumerate(files_list):
                    for file2 in files_list[i+1:]:
                        comparisons_done += 1
                        
                        if comparisons_done % 20 == 0:
                            pct = 50 + int(comparisons_done / total_comparisons * 50)
                            elapsed = time.time() - start_time
                            rate = comparisons_done / elapsed if elapsed > 0 else 0
                            remaining = (total_comparisons - comparisons_done) / rate if rate > 0 else 0
                            
                            status_msg = f"{self.language_manager.get_text('dash_comparing')} {comparisons_done}/{total_comparisons}  a {pct}%  a  {remaining:.1f}s"
                            self.after(0, lambda msg=status_msg: self._dupes_overlay.set_sub(msg))
                            self.after(0, lambda p=pct: self._dupes_overlay.set_bar(p))
                        
                        blocks = self._find_duplicate_blocks(file_hashes[file1], file_hashes[file2], MIN_LINES)
                        
                        if blocks:
                            duplicates.append({
                                'file1': file1,
                                'file2': file2,
                                'blocks': blocks
                            })
                
                result = []
                if not duplicates:
                    result = [(" No se encontrco ccodigo duplicado significativo (maximo 8 lineas)", "success")]
                else:
                    result.append(("aÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢Ãƒâ€šÃ‚Â" * 80, "header"))
                    result.append((f"ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€šÃ‚Â CaÃƒÂ¢Ã¢â€šÂ¬Ã…â€œDIGO DUPLICADO ({len(duplicates)} casos)", "duplicate"))
                    result.append(("aÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢Ãƒâ€šÃ‚Â" * 80, "header"))
                    result.append(("", None))
                    
                    for idx, dup in enumerate(duplicates, 1):
                        f1 = self.file_manager.get_relative_path(dup["file1"])
                        f2 = self.file_manager.get_relative_path(dup["file2"])
                        
                        result.append((f"{'aÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬' * 80}", "line_num"))
                        result.append((f"Caso #{idx}", "header"))
                        result.append((f"ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒÂ¢Ã¢â€šÂ¬Ã…Â¾ {f1}", "file"))
                        result.append((f"ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒÂ¢Ã¢â€šÂ¬Ã…Â¾ {f2}", "file"))
                        result.append(("", None))
                        
                        for block in dup["blocks"]:
                            result.append((f"{block['lines']} laÃƒâ€šÃ‚Â­neas duplicadas (L{block['start1']}-{block['end1']} aÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â L{block['start2']}-{block['end2']})", "warning"))
                            result.append(("", None))
                            
                            with open(dup["file1"], 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                for line_num in range(block['start1'] - 1, min(block['end1'], block['start1'] + 6)):
                                    line_content = lines[line_num].rstrip()
                                    result.append((f"    {line_num + 1:4d} aÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ {line_content}", "code"))
                            
                            if block['lines'] > 6:
                                result.append((f"    ... y {block['lines'] - 6} laÃƒâ€šÃ‚Â­neas mÃƒÆ’Ã‚Â¡s", "line_num"))
                            
                            result.append(("", None))
                        
                        result.append(("", None))
                
        except Exception as e:
            result = [(f"aÃƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ Error: {e}", "error")]
        finally:
            self.after(0, lambda: self._finish_dupes(result))

    def _find_duplicate_blocks(self, lines1, lines2, min_lines=8):
        blocks = []
        i = 0
        
        # Ignorar laÃƒâ€šÃ‚Â­neas comunes triviales
        trivial_patterns = ['import ', 'from ', '{', '}', '(', ')', ';', '//', '#', '/*', '*/', '"""', "'''"]
        
        while i < len(lines1):
            j = 0
            while j < len(lines2):
                match_len = 0
                while (i + match_len < len(lines1) and 
                       j + match_len < len(lines2)):
                    line1 = lines1[i + match_len].strip()
                    line2 = lines2[j + match_len].strip()
                    
                    # Ignorar laÃƒâ€šÃ‚Â­neas vacaÃƒâ€šÃ‚Â­as y triviales
                    if (line1 == line2 and line1 != "" and 
                        not any(pattern in line1 for pattern in trivial_patterns)):
                        match_len += 1
                    else:
                        break
                
                if match_len >= min_lines:
                    blocks.append({
                        'start1': i + 1,
                        'end1': i + match_len,
                        'start2': j + 1,
                        'end2': j + match_len,
                        'lines': match_len
                    })
                    i += match_len
                    j += match_len
                else:
                    j += 1
            i += 1
        
        return blocks

    def _finish_dupes(self, result):
        self._hide_overlay(self._dupes_overlay, self.duplicates_text)
        self._write_colored(self.duplicates_text, result)
        self._loading = False

    # UTILS

    @staticmethod
    def _write_colored(widget, content_list):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        
        for text, tag in content_list:
            if tag:
                widget.insert(tk.END, text + "\n", tag)
            else:
                widget.insert(tk.END, text + "\n")
        
        widget.configure(state="disabled")

    @staticmethod
    def _format_size(n: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
            n /= 1024
        return f"{n:.1f} TB"

    @staticmethod
    def _palette(n, accent):
        try:
            h = accent.lstrip("#")
            r0, g0, b0 = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            out = []
            for i in range(n):
                f = 0.45 + 0.55*(i/max(n-1,1))
                out.append("#{:02x}{:02x}{:02x}".format(
                    min(255,int(r0*f+160*(1-f))),
                    min(255,int(g0*f+90*(1-f))),
                    min(255,int(b0*f+210*(1-f))),
                ))
            return out
        except:
            return ["#4488cc"]*n
        
    @staticmethod
    def _mix_colors(c1: str, c2: str, ratio: float = 0.5) -> str:
        """Mezcla dos colores hexadecimales."""
        try:
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return c1

    @staticmethod
    def _dim(color, factor):
        try:
            h = color.lstrip("#")
            return "#{:02x}{:02x}{:02x}".format(
                min(255,max(0,int(int(h[0:2],16)*factor))),
                min(255,max(0,int(int(h[2:4],16)*factor))),
                min(255,max(0,int(int(h[4:6],16)*factor))),
            )
        except:
            return color


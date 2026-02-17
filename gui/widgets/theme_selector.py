import tkinter as tk
import os
from gui.components import CustomToplevel
from utils.theme_manager import ThemeManager  # ← importar directo, sin duplicar
from utils.helpers import resource_path

class ThemeSelector(CustomToplevel):
    """
    Selector de tema con preview visual de colores reales.
    Importa ThemeManager directamente para no duplicar la definiciÃ³n de temas.
    """

    def __init__(self, parent, theme_manager, language_manager, on_theme_change):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title=language_manager.get_text("theme_window_title"),
            size="560x500",
            min_size=(440, 380),
            max_size=(760, 680),
        )

        self.language_manager = language_manager
        self.on_theme_change  = on_theme_change
        self._config_manager  = getattr(theme_manager, "config_manager", None)
        self._icons           = {}
        self._icon_refs       = []
        self._theme_cards     = {}
        self._title_icon_label = None

        self._load_icons()
        self._setup_title_icon()
        self._build_ui()
        self.apply_theme()
        self.language_manager.subscribe(self.update_ui_language)
        
    def update_ui_language(self):
        lang = self.language_manager
        try:
            self.title_label.configure(text=lang.get_text("theme_window_title"))
            self._sub_label.configure(text=lang.get_text("theme_subtitle"))
            self._footer_label.configure(
                text=f"{lang.get_text('theme_active')}: {self.theme_manager.current_theme}"
            )
            self._close_btn.configure(text=f"  {lang.get_text('search_close')}")
            self._refresh_animation_labels()
        except Exception:
            pass

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # ICONOS â€” cargados UNA vez, nunca recargados
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _load_icons(self):
        try:
            from PIL import Image, ImageTk
            icon_dir = resource_path("assets/icons")
            t        = self.theme_manager.get_theme()

            def _rgb(h):
                h = h.lstrip("#")
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

            def load(name, size=(16, 16), bg=None, keep_alpha=False):
                path = os.path.join(icon_dir, name)
                if not os.path.exists(path):
                    return None
                img    = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                if keep_alpha:
                    return ImageTk.PhotoImage(img, master=self)
                bg_hex = bg or t["secondary_bg"]
                base   = Image.new("RGBA", img.size, _rgb(bg_hex) + (255,))
                base.paste(img, mask=img.split()[3])
                return ImageTk.PhotoImage(base.convert("RGB"), master=self)

            self._icons = {
                "theme": load("theme.png", (16, 16), keep_alpha=True),
                "check": load("check.png",     (13, 13)),
                "close": load("close.png",     (14, 14)),
                "sun":   load("sun.png",        (14, 14)),
                "moon":  load("moon.png",       (14, 14)),
            }
            self._icon_refs = [v for v in self._icons.values() if v is not None]
        except Exception:
            self._icons     = {}
            self._icon_refs = []

    def _icon(self, name):
        return self._icons.get(name)

    def _setup_title_icon(self):
        ico = self._icon("theme")
        if ico:
            if self._title_icon_label and self._title_icon_label.winfo_exists():
                self._title_icon_label.configure(image=ico)
                self._title_icon_label.image = ico
            else:
                self._title_icon_label = self.add_title_icon(ico)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # UI
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _build_ui(self):
        # Sub-barra
        self._sub_bar = tk.Frame(self.content_frame, height=32)
        self._sub_bar.pack(fill="x")
        self._sub_bar.pack_propagate(False)

        # REEMPLAZAR POR:
        lang = self.language_manager

        self._sub_label = tk.Label(
            self._sub_bar,
            text=lang.get_text("theme_subtitle"),
            font=("Segoe UI", 8),
            anchor="w",
        )

        self._sub_label.pack(side="left", padx=16, fill="y")

        self._sep_sub = tk.Frame(self.content_frame, height=1)
        self._sep_sub.pack(fill="x")

        self._anim_panel = tk.Frame(self.content_frame)
        self._anim_panel.pack(fill="x", padx=12, pady=(10, 0))

        self._anim_title = tk.Label(
            self._anim_panel,
            text="Animaciones",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self._anim_title.pack(fill="x", padx=8, pady=(8, 2))

        self._anim_bar_row = tk.Frame(self._anim_panel)
        self._anim_bar_row.pack(fill="x", padx=8, pady=(0, 8))
        self._anim_bar_label = tk.Label(self._anim_bar_row, anchor="w", font=("Segoe UI", 9))
        self._anim_bar_label.pack(side="left", fill="x", expand=True)
        self._anim_bar_btn = tk.Button(
            self._anim_bar_row,
            command=lambda: self._toggle_anim_option("animated_toolbar_background"),
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=10,
            pady=4,
            width=10,
        )
        self._anim_bar_btn.pack(side="right")

        self._sep_anim = tk.Frame(self.content_frame, height=1)
        self._sep_anim.pack(fill="x", padx=12)

        # Canvas scrollable sin scrollbar visible
        outer = tk.Frame(self.content_frame)
        outer.pack(fill="both", expand=True, padx=12, pady=10)

        self._canvas = tk.Canvas(outer, bd=0, highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        self._cards_frame = tk.Frame(self._canvas)
        self._cwin = self._canvas.create_window((0, 0), window=self._cards_frame, anchor="nw")

        self._cards_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cwin, width=e.width))

        for w in (self._canvas, self._cards_frame):
            w.bind("<MouseWheel>", self._scroll)
            w.bind("<Button-4>",   self._scroll)
            w.bind("<Button-5>",   self._scroll)

        self._populate_cards()

        # Footer
        self._sep_footer = tk.Frame(self.content_frame, height=1)
        self._sep_footer.pack(fill="x", side="bottom")

        self._footer = tk.Frame(self.content_frame, height=44)
        self._footer.pack(fill="x", side="bottom")
        self._footer.pack_propagate(False)

        fi = tk.Frame(self._footer)
        fi.pack(fill="both", expand=True, padx=14, pady=8)

        self._footer_label = tk.Label(fi, text="", font=("Segoe UI", 8), anchor="w")
        self._footer_label.pack(side="left")

        ico_x = self._icon("close")
        lang = self.language_manager  # â† AGREGAR ESTA LÃNEA SI NO EXISTE
        self._close_btn = tk.Button(
            fi, text=f"  {lang.get_text('search_close')}",
            image=ico_x, compound="left" if ico_x else "none",
            command=self.destroy,
            font=("Segoe UI", 9), cursor="hand2",
            bd=0, relief="flat", padx=12, pady=4,
        )
        if ico_x:
            self._close_btn.image = ico_x
        self._close_btn.pack(side="right")
        self._btn_hover(self._close_btn, primary=False)
        self._refresh_animation_labels()

    def _scroll(self, event):
        try:
            if   event.num == 4: d = -1
            elif event.num == 5: d =  1
            else:                d = int(-1 * (event.delta / 120))
            self._canvas.yview_scroll(d, "units")
        except Exception:
            pass
        return "break"

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # TARJETAS
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _populate_cards(self):
        for w in self._cards_frame.winfo_children():
            w.destroy()
        self._theme_cards.clear()

        # Usamos ThemeManager.THEMES directamente â€” sin duplicar
        themes      = ThemeManager.THEMES
        current_key = self.theme_manager.current_theme
        col = row = 0

        for key, data in themes.items():
            card = self._make_card(key, data, is_active=(key == current_key))
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self._theme_cards[key] = card

            for w in self._iter_all(card):
                w.bind("<MouseWheel>", self._scroll)
                w.bind("<Button-4>",   self._scroll)
                w.bind("<Button-5>",   self._scroll)

            col += 1
            if col >= 2:
                col = 0
                row += 1

        self._cards_frame.columnconfigure(0, weight=1)
        self._cards_frame.columnconfigure(1, weight=1)

    def _make_card(self, theme_key, theme_data, is_active):
        lang = self.language_manager
        """
        Tarjeta con preview que muestra los colores REALES del tema:
        - Franja superior = secondary_bg (barra de tÃ­tulo)
        - Ãrea izquierda = tree_bg (panel lateral)  
        - Ãrea derecha = bg (Ã¡rea principal)
        - Franja de acento = accent
        - Fila seleccionada = tree_selected_bg
        Todo marcado con _preview=True para que el theming no lo toque.
        """
        t_now = self.theme_manager.get_theme()

        # â”€â”€ Colores REALES del tema destino â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        p_bg      = theme_data["bg"]
        p_sec     = theme_data["secondary_bg"]
        p_fg      = theme_data["fg"]
        p_accent  = theme_data["accent"]
        p_border  = theme_data["border"]
        p_tree_bg = theme_data["tree_bg"]
        p_tree_fg = theme_data["tree_fg"]
        p_sel_bg  = theme_data["tree_selected_bg"]
        p_sel_fg  = theme_data["tree_selected_fg"]
        p_btn_bg  = theme_data["button_bg"]
        p_btn_fg  = theme_data["button_fg"]

        # Colores del tema ACTIVO (para la secciÃ³n info/botones)
        n_sec    = t_now["secondary_bg"]
        n_fg     = t_now["fg"]
        n_border = t_now["border"]
        n_btn_bg = t_now["button_bg"]
        n_btn_fg = t_now["button_fg"]

        # â”€â”€ Card container â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        card = tk.Frame(
            self._cards_frame,
            bd=0,
            highlightthickness=2,
            highlightbackground=p_accent if is_active else n_border,
            cursor="hand2",
        )
        card._theme_key  = theme_key
        card._theme_data = theme_data
        card._is_active  = is_active
        card._accent     = p_accent

        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # PREVIEW â€” colores 100% fijos, todos marcados con _preview=True
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        preview = tk.Frame(card, height=72, bg=p_bg,
                           highlightthickness=0)
        preview._preview = True
        preview.pack(fill="x")
        preview.pack_propagate(False)

        # â”€â”€â”€ Columna izquierda: simula panel lateral (tree_bg) â”€â”€â”€â”€â”€â”€â”€â”€
        left_col = tk.Frame(preview, bg=p_tree_bg, width=52)
        left_col._preview = True
        left_col.pack(side="left", fill="y")
        left_col.pack_propagate(False)

        # Barra de tÃ­tulo del panel izquierdo
        left_header = tk.Frame(left_col, bg=p_sec, height=12)
        left_header._preview = True
        left_header.pack(fill="x")

        # Filas simuladas del Ã¡rbol
        tree_rows = [
            (p_tree_bg, p_tree_fg),
            (p_sel_bg,  p_sel_fg),
            (p_tree_bg, p_tree_fg),
            (p_tree_bg, p_tree_fg),
        ]
        for i, (rbg, rfg) in enumerate(tree_rows):
            row_f = tk.Frame(left_col, bg=rbg, height=11)
            row_f._preview = True
            row_f.pack(fill="x", pady=(1 if i > 0 else 0))
            # LÃ­nea de texto simulada
            indent = 8 + (4 if i > 0 else 0)
            tk.Frame(row_f, bg=rfg, width=22, height=3).place(x=indent, y=4)

        # â”€â”€â”€ Columna derecha: simula Ã¡rea de contenido (bg) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        right_col = tk.Frame(preview, bg=p_bg)
        right_col._preview = True
        right_col.pack(side="left", fill="both", expand=True)

        # Barra de tÃ­tulo del Ã¡rea principal
        right_header = tk.Frame(right_col, bg=p_sec, height=12)
        right_header._preview = True
        right_header.pack(fill="x")

        # Punto de acento en la barra (simula tab activo)
        accent_tab = tk.Frame(right_header, bg=p_accent, width=18, height=12)
        accent_tab._preview = True
        accent_tab.pack(side="left", padx=(4, 0))

        # BotÃ³n simulado
        btn_sim = tk.Frame(right_header, bg=p_btn_bg, width=20, height=7)
        btn_sim._preview = True
        btn_sim.place(in_=right_header, relx=1.0, rely=0.5, anchor="e", x=-4)

        # LÃ­neas de contenido simuladas
        content_area = tk.Frame(right_col, bg=p_bg)
        content_area._preview = True
        content_area.pack(fill="both", expand=True, padx=4, pady=3)

        line_colors = [p_accent, p_fg, p_fg, p_tree_fg]
        line_widths  = [0.55,     0.8,  0.6,  0.45]
        for lc, lw in zip(line_colors, line_widths):
            lf = tk.Frame(content_area, bg=lc, height=3)
            lf._preview = True
            lf.pack(fill="x", pady=1)
            # anchura relativa simulada con un frame interno
            lf.pack_propagate(False)

        # Marcar recursivamente todos los hijos del preview
        self._mark_preview(preview)

        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # SECCIÃ“N INFO â€” colores del tema activo, se actualiza normalmente
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

        # Separador entre preview e info
        sep = tk.Frame(card, bg=n_border, height=1)
        sep._preview = False
        sep._is_sep  = True
        sep.pack(fill="x")

        info = tk.Frame(card, bg=n_sec)
        info._preview = False
        info.pack(fill="x", padx=10, pady=(5, 7))

        name_row = tk.Frame(info, bg=n_sec)
        name_row._preview = False
        name_row.pack(fill="x")

        # Icono sol/luna segÃºn luminancia del bg del tema
        luma    = self._luminance(p_bg)
        ico_key = "sun" if luma > 0.35 else "moon"
        ico     = self._icon(ico_key)
        if ico:
            lbl_i = tk.Label(name_row, image=ico, bg=n_sec)
            lbl_i.image   = ico
            lbl_i._preview = False
            lbl_i.pack(side="left", padx=(0, 5))

        name_lbl = tk.Label(
            name_row,
            text=theme_data.get("name", theme_key),
            font=("Segoe UI", 9, "bold"),
            bg=n_sec, fg=n_fg, anchor="w",
        )
        name_lbl._preview = False
        name_lbl.pack(side="left", fill="x", expand=True)

        if is_active:
            badge = tk.Label(
                name_row,
                text=lang.get_text("theme_badge_active"),
                font=("Segoe UI", 8, "bold"),
                bg=n_sec, fg=p_accent, padx=4,
            )
            badge._preview  = False
            badge.pack(side="right")
            card._badge     = badge
            card._apply_btn = None
        else:
            btn = tk.Button(
                name_row,
                text=lang.get_text("theme_btn_apply"),
                font=("Segoe UI", 8),
                bg=n_btn_bg, fg=n_btn_fg,
                activebackground=t_now["button_hover"],
                activeforeground=n_btn_fg,
                cursor="hand2",
                bd=0, relief="flat",
                padx=8, pady=2,
                command=lambda k=theme_key: self._select_theme(k),
            )
            btn._preview = False
            btn.pack(side="right")
            btn.bind("<Button-1>",        lambda e: "break")
            btn.bind("<ButtonRelease-1>", lambda e, k=theme_key: self._select_theme(k))
            self._btn_hover(btn, primary=True)
            card._apply_btn = btn
            card._badge     = None

        # Hover borde tarjeta
        def _enter(e, c=card):
            if not c._is_active:
                c.configure(highlightbackground=c._accent)
        def _leave(e, c=card):
            if not c._is_active:
                c.configure(highlightbackground=self.theme_manager.get_theme()["border"])

        card.bind("<Enter>", _enter)
        card.bind("<Leave>", _leave)
        for w in self._iter_all(info):
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

        return card

    def _mark_preview(self, widget):
        """Marca recursivamente todos los widgets con _preview=True."""
        widget._preview = True
        for child in widget.winfo_children():
            self._mark_preview(child)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # ACCIÃ“N
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _select_theme(self, theme_key):
        if theme_key == self.theme_manager.current_theme:
            return
        self.theme_manager.set_theme(theme_key)
        self.on_theme_change()
        self._populate_cards()
        self._apply_ui_theme()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # THEMING â€” nunca toca widgets con _preview=True
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def apply_theme(self):
        # Recargar iconos para que respeten el color del tema activo.
        self._load_icons()
        self._setup_title_icon()
        if hasattr(self, "_close_btn"):
            ico_x = self._icon("close")
            self._close_btn.configure(
                image=ico_x,
                compound="left" if ico_x else "none"
            )
            if ico_x:
                self._close_btn.image = ico_x
        self.apply_base_theme()
        self._apply_ui_theme()

    def _apply_ui_theme(self):
        t      = self.theme_manager.get_theme()
        bg     = t["bg"]
        sec    = t["secondary_bg"]
        fg     = t["fg"]
        border = t["border"]

        if hasattr(self, "_sub_bar"):
            self._sub_bar.configure(bg=sec)
            self._sub_label.configure(bg=sec, fg=self._mix(fg, sec, 0.35))
            self._sep_sub.configure(bg=border)

        if hasattr(self, "_canvas"):
            self._canvas.configure(bg=bg)
            self._cards_frame.configure(bg=bg)

        if hasattr(self, "_anim_panel"):
            self._anim_panel.configure(bg=sec, highlightthickness=1, highlightbackground=border)
            self._anim_title.configure(bg=sec, fg=fg)
            self._anim_bar_row.configure(bg=sec)
            self._anim_bar_label.configure(bg=sec, fg=fg)
            self._sep_anim.configure(bg=border)
            self._style_toggle_button(self._anim_bar_btn, self._read_anim_option("animated_toolbar_background"))

        if hasattr(self, "_footer"):
            self._sep_footer.configure(bg=border)
            self._footer.configure(bg=sec)
            children = self._footer.winfo_children()
            if children:
                children[0].configure(bg=sec)
            lang = self.language_manager  # ðŸ‘ˆ agregas esto antes

            self._footer_label.configure(
                bg=sec,
                fg=self._mix(fg, sec, 0.35),
                text=f"{lang.get_text('theme_active')}: {self.theme_manager.current_theme}",
            )
            self._close_btn.configure(
                bg=sec, fg=fg,
                activebackground=border, activeforeground=fg,
            )

        self._apply_cards_theme()

    def _style_toggle_button(self, btn, enabled):
        t = self.theme_manager.get_theme()
        if enabled:
            btn.configure(
                bg=t.get("success", t["button_bg"]),
                fg="#ffffff",
                activebackground=t.get("success", t["button_bg"]),
                activeforeground="#ffffff",
            )
        else:
            btn.configure(
                bg=t["button_bg"],
                fg=t["button_fg"],
                activebackground=t["button_hover"],
                activeforeground=t["button_fg"],
            )

    def _texts_for_toggles(self):
        lang = self.language_manager
        return {
            "title": lang.get_text("theme_anim_title"),
            "bar": lang.get_text("theme_anim_bar"),
            "on": lang.get_text("theme_anim_enabled"),
            "off": lang.get_text("theme_anim_disabled"),
        }

    def _read_anim_option(self, key):
        if not self._config_manager:
            return True
        return bool(self._config_manager.get(key, True))

    def _set_anim_option(self, key, enabled):
        if self._config_manager:
            self._config_manager.set(key, bool(enabled))

    def _toggle_anim_option(self, key):
        enabled = not self._read_anim_option(key)
        self._set_anim_option(key, enabled)
        self._refresh_animation_labels()
        self.on_theme_change()
        notify = getattr(self.theme_manager, "_notify_observers", None)
        if callable(notify):
            notify()

    def _refresh_animation_labels(self):
        if not hasattr(self, "_anim_title"):
            return
        texts = self._texts_for_toggles()
        bar_on = self._read_anim_option("animated_toolbar_background")
        self._anim_title.configure(text=texts["title"])
        self._anim_bar_label.configure(text=texts["bar"])
        self._anim_bar_btn.configure(text=texts["on"] if bar_on else texts["off"])
        self._style_toggle_button(self._anim_bar_btn, bar_on)

    def _apply_cards_theme(self):
        t      = self.theme_manager.get_theme()
        sec    = t["secondary_bg"]
        fg     = t["fg"]
        border = t["border"]
        btn_bg = t["button_bg"]
        btn_fg = t["button_fg"]
        hover  = t["button_hover"]

        for key, card in self._theme_cards.items():
            active = (key == self.theme_manager.current_theme)
            card._is_active = active
            try:
                card.configure(highlightbackground=card._accent if active else border)
            except Exception:
                pass

            for child in card.winfo_children():
                if getattr(child, "_preview", False):
                    continue
                self._theme_info_recursive(child, sec, fg, btn_bg, btn_fg, hover, card._accent, border)

    def _theme_info_recursive(self, widget, sec, fg, btn_bg, btn_fg, hover, accent, border=None):
        if getattr(widget, "_preview", False):
            return
        try:
            if isinstance(widget, tk.Frame):
                # Separadores reciben el color de borde, no secondary_bg
                if getattr(widget, "_is_sep", False) and border:
                    widget.configure(bg=border)
                else:
                    widget.configure(bg=sec)
            elif isinstance(widget, tk.Label):
                cur_fg = widget.cget("fg")
                widget.configure(bg=sec, fg=accent if cur_fg == accent else fg)
            elif isinstance(widget, tk.Button):
                widget.configure(bg=btn_bg, fg=btn_fg,
                                  activebackground=hover, activeforeground=btn_fg)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._theme_info_recursive(child, sec, fg, btn_bg, btn_fg, hover, accent, border)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # HELPERS
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _btn_hover(self, btn, primary=True):
        def on_enter(e):
            t = self.theme_manager.get_theme()
            btn.configure(bg=t["button_hover"] if primary else t["border"])
        def on_leave(e):
            t = self.theme_manager.get_theme()
            btn.configure(bg=t["button_bg"] if primary else t["secondary_bg"])
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _iter_all(self, widget):
        yield widget
        for child in widget.winfo_children():
            yield from self._iter_all(child)

    @staticmethod
    def _luminance(hex_color):
        try:
            h = hex_color.lstrip("#")
            r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
            return 0.2126*r + 0.7152*g + 0.0722*b
        except Exception:
            return 0.0

    @staticmethod
    def _mix(c1, c2, ratio=0.5):
        try:
            def p(c):
                c = c.lstrip("#")
                return int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
            r1,g1,b1 = p(c1)
            r2,g2,b2 = p(c2)
            r = int(r1*(1-ratio) + r2*ratio)
            g = int(g1*(1-ratio) + g2*ratio)
            b = int(b1*(1-ratio) + b2*ratio)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return c1

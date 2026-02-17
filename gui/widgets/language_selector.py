import tkinter as tk
import os
from gui.components import CustomToplevel
from utils.helpers import resource_path

class LanguageSelector(CustomToplevel):
    """
    Selector de idioma â€” diseÃ±o premium consistente con ThemeSelector.
    Sin decoraciones nativas, sin emojis, iconos desde assets/icons/.
    """

    def __init__(self, parent, language_manager, theme_manager, on_language_change):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title=language_manager.get_text("lang_window_title"),
            size="420x438",
            min_size=(340, 260),
            max_size=(600, 500),
        )

        self.language_manager  = language_manager
        self.on_language_change = on_language_change
        self._icons             = {}
        self._icon_refs         = []
        self._lang_cards        = {}

        self._load_icons()
        self._setup_title_icon()
        self._build_ui()
        self.apply_theme()
        self.language_manager.subscribe(self.update_ui_language)
        
    def update_ui_language(self):
        lang = self.language_manager
        try:
            self.title_label.configure(text=lang.get_text("lang_window_title"))
            self._sub_label.configure(text=lang.get_text("lang_subtitle"))
            self._footer_label.configure(
                text=f"{lang.get_text('lang_active')}: {lang.current_language}"
            )
            self._close_btn.configure(text=f"  {lang.get_text('search_close')}")
            self._populate_cards()
        except Exception:
            pass

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # ICONOS â€” cargados UNA vez
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _load_icons(self):
        try:
            from PIL import Image, ImageTk
            icon_dir = resource_path("assets/icons")
            flag_dir = resource_path("assets/flags")  # â† NUEVA carpeta para banderas
            t        = self.theme_manager.get_theme()

            def _rgb(h):
                h = h.lstrip("#")
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

            def load(name, size=(16, 16), bg=None):
                path = os.path.join(icon_dir, name)
                if not os.path.exists(path):
                    return None
                img    = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                bg_hex = bg or t["secondary_bg"]
                base   = Image.new("RGBA", img.size, _rgb(bg_hex) + (255,))
                base.paste(img, mask=img.split()[3])
                return ImageTk.PhotoImage(base.convert("RGB"))
            
            # âœ… NUEVA FUNCIÃ“N: Cargar banderas
            def load_flag(lang_code, size=(24, 24)):
                """Carga bandera PNG desde assets/flags/{lang_code}.png"""
                path = os.path.join(flag_dir, f"{lang_code}.png")
                if not os.path.exists(path):
                    return None
                img = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                # Sin fondo, las banderas tienen sus colores propios
                return ImageTk.PhotoImage(img)

            self._icons = {
                "language": load("language.png",  (16, 16)),
                "check":    load("check.png",     (13, 13)),
                "close":    load("close.png",     (14, 14)),
                "apply":    load("settings.png",  (13, 13), t["button_bg"]),
            }
            
            # âœ… NUEVO: Cargar banderas para cada idioma
            self._flags = {}
            for lang_code, _, _ in self.language_manager.get_available_languages():
                flag_img = load_flag(lang_code)
                if flag_img:
                    self._flags[lang_code] = flag_img
            
            self._icon_refs = [v for v in self._icons.values() if v is not None]
            self._icon_refs.extend(self._flags.values())  # â† Guardar referencias
            
        except Exception:
            self._icons = {}
            self._flags = {}
            self._icon_refs = []

    def _icon(self, name):
        return self._icons.get(name)

    def _setup_title_icon(self):
        ico = self._icon("language")
        if ico:
            self.add_title_icon(ico)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # UI
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _build_ui(self):
        # Sub-barra descriptiva
        self._sub_bar = tk.Frame(self.content_frame, height=32)
        self._sub_bar.pack(fill="x")
        self._sub_bar.pack_propagate(False)

        # DESPUÃ‰S (âœ…):
        lang = self.language_manager  # â† Agregar si no existe
        self._sub_label = tk.Label(
            self._sub_bar,
            text=lang.get_text("lang_subtitle"),  # âœ…
            font=("Segoe UI", 8),
            anchor="w",
        )
        self._sub_label.pack(side="left", padx=16, fill="y")

        self._sep_sub = tk.Frame(self.content_frame, height=1)
        self._sep_sub.pack(fill="x")

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
        
        lang = self.language_manager  # â† DeberÃ­a estar arriba ya
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
        self._lang_cards.clear()

        available = self.language_manager.get_available_languages()
        current   = self.language_manager.current_language

        for lang_code, lang_name, flag in available:
            card = self._make_card(lang_code, lang_name, flag,
                                   is_active=(lang_code == current))
            card.pack(fill="x", padx=2, pady=4)
            self._lang_cards[lang_code] = card

            for w in self._iter_all(card):
                w.bind("<MouseWheel>", self._scroll)
                w.bind("<Button-4>",   self._scroll)
                w.bind("<Button-5>",   self._scroll)

    def _make_card(self, lang_code, lang_name, flag, is_active):
        """
        Tarjeta de idioma con:
        - Franja de acento a la izquierda
        - Bandera (texto) + nombre del idioma
        - Badge activo o botÃ³n Aplicar
        Sin imÃ¡genes en botones para evitar error pyimage.
        """
        t_now    = self.theme_manager.get_theme()
        n_sec    = t_now["secondary_bg"]
        n_fg     = t_now["fg"]
        n_border = t_now["border"]
        n_accent = t_now["accent"]
        n_btn_bg = t_now["button_bg"]
        n_btn_fg = t_now["button_fg"]

        # â”€â”€ Card container â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        card = tk.Frame(
            self._cards_frame,
            bd=0,
            highlightthickness=2,
            highlightbackground=n_accent if is_active else n_border,
            cursor="hand2",
        )
        card._lang_code = lang_code
        card._is_active = is_active

        # â”€â”€ Franja vertical de acento (izquierda) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        accent_bar = tk.Frame(card, width=4, bg=n_accent)
        accent_bar._is_sep = True
        accent_bar.pack(side="left", fill="y")
        accent_bar.pack_propagate(False)

        # â”€â”€ Contenido principal â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        body = tk.Frame(card, bg=n_sec)
        body.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=8)

        # Fila: bandera + nombre
        name_row = tk.Frame(body, bg=n_sec)
        name_row.pack(fill="x")

        # Intentar cargar bandera PNG, fallback a emoji
        flag_img = self._flags.get(lang_code)
        if flag_img:
            flag_lbl = tk.Label(name_row, image=flag_img, bg=n_sec)
            flag_lbl.image = flag_img  # â† Mantener referencia
            flag_lbl.pack(side="left", padx=(0, 8))
        else:
            # Fallback a emoji si no hay PNG
            flag_lbl = tk.Label(
                name_row,
                text=flag,
                font=("Segoe UI", 13),
                bg=n_sec, fg=n_fg,
            )
            flag_lbl.pack(side="left", padx=(0, 8))

        name_lbl = tk.Label(
            name_row,
            text=lang_name,
            font=("Segoe UI", 10, "bold"),
            bg=n_sec, fg=n_fg,
            anchor="w",
        )
        name_lbl.pack(side="left", fill="x", expand=True)
        
        lang = self.language_manager  
        
        # Badge activo O botÃ³n Aplicar
        if is_active:
            badge = tk.Label(
                name_row,
                text=lang.get_text("lang_badge_active"),
                font=("Segoe UI", 8, "bold"),
                bg=n_sec, fg=n_accent,
                padx=4,
            )
            badge.pack(side="right")
            card._badge     = badge
            card._apply_btn = None
        else:
            btn = tk.Button(
                    name_row,
                    text=lang.get_text("lang_btn_apply"),
                font=("Segoe UI", 8),
                bg=n_btn_bg, fg=n_btn_fg,
                activebackground=t_now["button_hover"],
                activeforeground=n_btn_fg,
                cursor="hand2",
                bd=0, relief="flat",
                padx=8, pady=2,
                command=lambda k=lang_code: self._select_language(k),
            )
            btn.pack(side="right")
            btn.bind("<Button-1>",        lambda e: "break")
            btn.bind("<ButtonRelease-1>", lambda e, k=lang_code: self._select_language(k))
            self._btn_hover(btn, primary=True)
            card._apply_btn = btn
            card._badge     = None

        # Subtext: cÃ³digo del idioma
        code_lbl = tk.Label(
            body,
            text=lang_code.upper(),
            font=("Segoe UI", 7),
            bg=n_sec,
            fg=self._mix(n_fg, n_sec, 0.45),
            anchor="w",
        )
        code_lbl.pack(fill="x", pady=(1, 0))

        # Hover borde
        def _enter(e, c=card, a=n_accent):
            if not c._is_active:
                c.configure(highlightbackground=a)
        def _leave(e, c=card, b=n_border):
            if not c._is_active:
                c.configure(highlightbackground=self.theme_manager.get_theme()["border"])

        card.bind("<Enter>", _enter)
        card.bind("<Leave>", _leave)
        for w in self._iter_all(body):
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

        return card

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # ACCIÃ“N
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _select_language(self, lang_code):
        if lang_code == self.language_manager.current_language:
            return
        self.language_manager.set_language(lang_code)
        self.on_language_change()
        self._populate_cards()
        self._apply_ui_theme()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # THEMING
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def apply_theme(self):
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

        if hasattr(self, "_footer"):
            self._sep_footer.configure(bg=border)
            self._footer.configure(bg=sec)
            children = self._footer.winfo_children()
            if children:
                children[0].configure(bg=sec)
            
            lang = self.language_manager
            self._footer_label.configure(
                bg=sec,
                fg=self._mix(fg, sec, 0.35),
                text=f"{lang.get_text('lang_active')}: {lang.current_language}",  # âœ…
            )
            self._close_btn.configure(
                bg=sec, fg=fg,
                activebackground=border, activeforeground=fg,
            )

        self._apply_cards_theme()

    def _apply_cards_theme(self):
        t      = self.theme_manager.get_theme()
        sec    = t["secondary_bg"]
        fg     = t["fg"]
        border = t["border"]
        accent = t["accent"]
        btn_bg = t["button_bg"]
        btn_fg = t["button_fg"]
        hover  = t["button_hover"]

        for code, card in self._lang_cards.items():
            active = (code == self.language_manager.current_language)
            card._is_active = active
            try:
                card.configure(highlightbackground=accent if active else border)
            except Exception:
                pass

            for child in card.winfo_children():
                self._theme_card_recursive(child, sec, fg, border, accent, btn_bg, btn_fg, hover)

    def _theme_card_recursive(self, widget, sec, fg, border, accent, btn_bg, btn_fg, hover):
        try:
            if isinstance(widget, tk.Frame):
                # Franja de acento lateral
                if getattr(widget, "_is_sep", False):
                    widget.configure(bg=accent)
                else:
                    widget.configure(bg=sec)
            elif isinstance(widget, tk.Label):
                cur_fg = widget.cget("fg")
                if cur_fg == accent:
                    widget.configure(bg=sec)
                else:
                    # Respetar el color sutil del cÃ³digo de idioma
                    widget.configure(bg=sec, fg=fg)
            elif isinstance(widget, tk.Button):
                widget.configure(
                    bg=btn_bg, fg=btn_fg,
                    activebackground=hover, activeforeground=btn_fg,
                )
        except Exception:
            pass
        for child in widget.winfo_children():
            self._theme_card_recursive(child, sec, fg, border, accent, btn_bg, btn_fg, hover)

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

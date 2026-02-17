import tkinter as tk
import os
from gui.components import CustomToplevel


class ShortcutsWindow(CustomToplevel):
    """
    Ventana de atajos de teclado.
    """

    KEY_ICONS = {
        "Ctrl":              "ctrl.png",
        "Alt":               "alt.png",
        "Shift":             "shift.png",
        "Enter":             "enter.png",
        "Escape":            "escape.png",
        "Tab":               "tab.png",
        "Space":             "space.png",
        "F5":                "f5.png",
        "+":                 "plus.png",
        "\u2212":            "minus.png",
        "-":                 "minus.png",
        "0":                 "0.png",
        "C":                 "c.png",
        "D":                 "d.png",
        "E":                 "e.png",
        "F":                 "f.png",
        "O":                 "o.png",
        "P":                 "p.png",
        "Q":                 "q.png",
        "Scroll":            "scroll.png",
        "Double\u2011Click": "doubleclick.png",
        "Right\u2011Click":  "rightclick.png",
    }

    KEY_SIZE = (56, 42)  # Aumentado de 48x36 para mejor visibilidad

    def __init__(self, parent, theme_manager, language_manager):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title=language_manager.get_text("menu_shortcuts"),
            size="400x650",
            min_size=(510, 650),
            max_size=(510, 760),
            use_custom_decorations=False
        )
        self.language_manager = language_manager
        self._photos = []  # Lista global de PhotoImages

        self._load_title_icon()
        self._build_ui()
        self.apply_theme()
        self.language_manager.subscribe(self.update_ui_language)

    def _load_title_icon(self):
        try:
            from PIL import Image, ImageTk
            t = self.theme_manager.get_theme()
            path = os.path.join("assets", "icons", "keyboard.png")
            if not os.path.exists(path):
                return
            img = Image.open(path).convert("RGBA").resize(
                (16, 16), Image.Resampling.LANCZOS)
            bg = t["secondary_bg"].lstrip("#")
            rgb = tuple(int(bg[i:i+2], 16) for i in (0, 2, 4))
            base = Image.new("RGBA", (16, 16), rgb + (255,))
            base.paste(img, mask=img.split()[3])
            self._title_ico = ImageTk.PhotoImage(base.convert("RGB"))
            self.add_title_icon(self._title_ico)
        except Exception:
            pass

    def _build_ui(self):
        lang = self.language_manager
        cf = self.content_frame

        hdr = tk.Frame(cf)
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        self._hdr = hdr  # Guardar referencia
        self._h_title = tk.Label(hdr,
            text=lang.get_text("menu_shortcuts"),
            font=("Segoe UI", 13, "bold"), anchor="w")
        self._h_title.pack(fill="x")
        self._h_sub = tk.Label(hdr,
            text=lang.get_text("shortcuts_subtitle"),
            font=("Segoe UI", 9), anchor="w")
        self._h_sub.pack(fill="x", pady=(2, 0))
        
        # Bindear scroll al header también
        for w in (hdr, self._h_title, self._h_sub):
            w.bind("<MouseWheel>", self._scroll)
            w.bind("<Button-4>", self._scroll)
            w.bind("<Button-5>", self._scroll)

        self._sep_top = tk.Frame(cf, height=1)
        self._sep_top.pack(fill="x", padx=20, pady=(10, 0))

        outer = tk.Frame(cf)
        outer.pack(fill="both", expand=True, padx=16, pady=(6, 0))
        self._outer = outer  # Guardar referencia

        self._vsb = tk.Scrollbar(outer, orient="vertical", width=6,
                                  relief="flat", bd=0, elementborderwidth=0)
        self._vsb.pack(side="right", fill="y")

        self._canvas = tk.Canvas(outer, bd=0, highlightthickness=0,
                                  yscrollcommand=self._vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._vsb.config(command=self._canvas.yview)

        self._sf = tk.Frame(self._canvas)
        self._cwin = self._canvas.create_window(
            (0, 0), window=self._sf, anchor="nw")
        self._sf.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cwin, width=e.width))

        for w in (self._canvas, self._sf):
            w.bind("<MouseWheel>", self._scroll)
            w.bind("<Button-4>", self._scroll)
            w.bind("<Button-5>", self._scroll)
        
        # ✅ CRÍTICO: Bindear scroll a la ventana completa y al content_frame
        self.bind_all("<MouseWheel>", self._scroll)
        self.bind_all("<Button-4>", self._scroll)
        self.bind_all("<Button-5>", self._scroll)
        cf.bind("<MouseWheel>", self._scroll)
        cf.bind("<Button-4>", self._scroll)
        cf.bind("<Button-5>", self._scroll)

        self._sep_bot = tk.Frame(cf, height=1)
        self._sep_bot.pack(fill="x", padx=20, pady=(6, 0))

        btn_row = tk.Frame(cf)
        btn_row.pack(fill="x", padx=20, pady=(6, 14))
        self._btn_row = btn_row  # Guardar referencia para apply_theme
        self._close_btn = tk.Button(btn_row,
            text=lang.get_text("search_close"),
            command=self.destroy,
            font=("Segoe UI", 9), cursor="hand2",
            bd=0, relief="flat", padx=18, pady=5)
        self._close_btn.pack(side="right")

        self._populate()

    def _get_sections(self):
        lang = self.language_manager
        return [
            (lang.get_text("shortcuts_section_general"), [
                (["Ctrl", "O"], lang.get_text("tooltip_open")),
                (["Ctrl", "Q"], lang.get_text("shortcuts_exit")),
                (["F5"], lang.get_text("shortcuts_refresh")),
            ]),
            (lang.get_text("shortcuts_section_selection"), [
                (["E"], lang.get_text("shortcuts_mark")),
                (["Space"], lang.get_text("shortcuts_mark")),
                (["Ctrl", "C"], lang.get_text("tooltip_copy")),
                (["Ctrl", "D"], lang.get_text("shortcuts_clear")),
            ]),
            (lang.get_text("shortcuts_section_navigation"), [
                (["Ctrl", "F"], lang.get_text("tooltip_search")),
                (["Ctrl", "P"], lang.get_text("tooltip_preview")),
                (["Double\u2011Click"], lang.get_text("shortcuts_mark_file")),
                (["Right\u2011Click"], lang.get_text("shortcuts_context")),
            ]),
            (lang.get_text("shortcuts_section_zoom"), [
                (["Ctrl", "+"], lang.get_text("tooltip_zoom_in")),
                (["Ctrl", "\u2212"], lang.get_text("tooltip_zoom_out")),
                (["Ctrl", "0"], lang.get_text("tooltip_zoom_reset")),
                (["Ctrl", "Scroll"], lang.get_text("shortcuts_zoom_scroll")),
            ]),
            (lang.get_text("shortcuts_section_tools"), [
                (["Ctrl", "F"], lang.get_text("menu_search_files")),
            ]),
        ]

    def _populate(self):
        for w in self._sf.winfo_children():
            w.destroy()
        
        self._photos.clear()
        
        t = self.theme_manager.get_theme()
        for sec_title, rows in self._get_sections():
            self._add_section(sec_title, rows, t)
        
        self._sf.update_idletasks()

    def _add_section(self, title, rows, t):
        bg = t["bg"]
        sec_bg = t["secondary_bg"]
        fg = t["fg"]
        border = t["border"]
        acc = t["accent"]

        hdr = tk.Frame(self._sf, bg=bg)
        hdr.pack(fill="x", pady=(16, 4), padx=12)
        title_label = tk.Label(hdr, text=title.upper(),
                 font=("Segoe UI", 10, "bold"),
                 bg=bg, fg=acc, anchor="w")
        title_label.pack(side="left")
        separator = tk.Frame(hdr, bg=border, height=1)
        separator.pack(side="left", fill="x", expand=True, padx=(10, 6), pady=8)
        
        # Bindear scroll al header de sección
        for w in (hdr, title_label, separator):
            w.bind("<MouseWheel>", self._scroll)
            w.bind("<Button-4>", self._scroll)
            w.bind("<Button-5>", self._scroll)

        for i, (keys, desc) in enumerate(rows):
            # ✅ Todas las filas color piel (bg) sin alternar
            row_bg = bg
            row = tk.Frame(self._sf, bg=row_bg)
            row.pack(fill="x", padx=10, pady=3)

            keys_col = tk.Frame(row, bg=row_bg)
            keys_col.pack(side="left", padx=(14, 18), pady=10)
            # NO usar pack_propagate(False) aquí - causa colapso de altura

            self._render_keys(keys_col, keys, t, row_bg)

            desc_label = tk.Label(row, text=desc,
                     font=("Segoe UI", 11),
                     bg=row_bg, fg=fg, anchor="w")
            desc_label.pack(side="left", fill="x", expand=True, pady=10)

            # Bindear scroll a TODOS los widgets de la fila
            for w in (row, keys_col, desc_label):
                w.bind("<MouseWheel>", self._scroll)
                w.bind("<Button-4>", self._scroll)
                w.bind("<Button-5>", self._scroll)

    def _render_keys(self, parent, keys, t, row_bg):
        """Renderiza las teclas con sus iconos PNG usando Canvas - CON LOGS"""
        from PIL import Image, ImageTk
        
        bg = t["bg"]
        sec_bg = t["secondary_bg"]
        border = t["border"]
        fg = t["fg"]

        # ✅ badge_bg debe ser IGUAL a row_bg, no invertido
        badge_bg = row_bg  
        bg_hex = badge_bg.lstrip("#")
        rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))

        print(f"\n{'='*60}")
        print(f"🔍 Renderizando teclas: {keys}")
        print(f"📐 KEY_SIZE configurado: {self.KEY_SIZE}")
        print(f"🎨 Badge BG: {badge_bg}, RGB: {rgb}")

        for i, key in enumerate(keys):
            if i > 0:
                tk.Label(parent, text="+",
                        font=("Segoe UI", 12, "bold"),
                        bg=row_bg, fg=fg).pack(side="left", padx=6)

            filename = self.KEY_ICONS.get(key)
            print(f"\n🔑 Tecla: {key}")
            print(f"   Archivo: {filename}")
            
            if filename:
                path = os.path.join("assets", "keys", filename)
                print(f"   Path: {path}")
                print(f"   Existe: {os.path.exists(path)}")
                
                if os.path.exists(path):
                    try:
                        # Cargar imagen original
                        img_original = Image.open(path)
                        print(f"   📸 Imagen cargada - Modo: {img_original.mode}, Tamaño: {img_original.size}")
                        
                        # Si está en RGB, convertir a RGBA para consistencia
                        if img_original.mode == 'RGB':
                            img_original = img_original.convert("RGBA")
                        
                        # Redimensionar (SIN modificar colores ni transparencia)
                        img_resized = img_original.resize(self.KEY_SIZE, Image.Resampling.LANCZOS)
                        print(f"   📏 Imagen redimensionada a: {img_resized.size}")
                        
                        # Convertir directamente a PhotoImage
                        photo = ImageTk.PhotoImage(img_resized)
                        print(f"   ✅ PhotoImage creado - Tamaño: {photo.width()}x{photo.height()}")
                        
                        # Canvas con fondo del badge
                        canvas = tk.Canvas(parent,
                                         width=self.KEY_SIZE[0],
                                         height=self.KEY_SIZE[1],
                                         bg=badge_bg,
                                         highlightthickness=0,
                                         bd=0,
                                         relief="flat")
                        canvas.pack(side="left", padx=3)
                        
                        # Crear imagen en canvas
                        img_id = canvas.create_image(
                            self.KEY_SIZE[0] // 2,
                            self.KEY_SIZE[1] // 2,
                            image=photo,
                            anchor="center"
                        )
                        print(f"   🖼️  Imagen en canvas (ID: {img_id})")
                        
                        # Guardar referencias
                        self._photos.append(photo)
                        canvas._photo_ref = photo
                        print(f"   ✅ Referencias guardadas (total: {len(self._photos)})")
                        
                        # Eventos de scroll
                        canvas.bind("<MouseWheel>", self._scroll)
                        canvas.bind("<Button-4>", self._scroll)
                        canvas.bind("<Button-5>", self._scroll)
                        
                        continue
                        
                    except Exception as e:
                        print(f"   ❌ ERROR: {e}")
                        import traceback
                        traceback.print_exc()
            else:
                print(f"   ⚠️  Sin archivo de icono")
            
            # Fallback: badge de texto
            print(f"   📝 Usando fallback de texto")
            fallback = tk.Label(parent,
                    text=key.replace("\u2011", "-"),
                    font=("Segoe UI", 10, "bold"),
                    bg=badge_bg, fg=fg,
                    padx=10, pady=8,
                    relief="flat", bd=1,
                    highlightthickness=1,
                    highlightbackground=border)
            fallback.pack(side="left", padx=3)
            fallback.update_idletasks()
            print(f"   📝 Fallback tamaño: {fallback.winfo_width()}x{fallback.winfo_height()}")
        
        print(f"{'='*60}\n")

    def _scroll(self, event):
        try:
            if not self._canvas.winfo_exists():
                return
            # Linux: event.num 4/5
            if event.num == 4:
                self._canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self._canvas.yview_scroll(1, "units")
            # Windows/Mac: event.delta
            else:
                delta = event.delta
                # En Windows, delta es ±120 por cada "click" de rueda
                # Dividir entre 120 y negar para dirección correcta
                self._canvas.yview_scroll(-1 * (delta // 120), "units")
        except Exception:
            pass
        return "break"

    def apply_theme(self):
        self.apply_base_theme()
        t = self.theme_manager.get_theme()
        bg = t["bg"]
        sec_bg = t["secondary_bg"]
        fg = t["fg"]
        border = t["border"]
        btn_bg = t["button_bg"]
        btn_fg = t["button_fg"]
        hover = t.get("button_hover", btn_bg)
        acc = t["accent"]
        
        try:
            self.content_frame.configure(bg=bg)
            self._hdr.configure(bg=bg)  # Header frame
            self._h_title.configure(bg=bg, fg=fg)
            self._h_sub.configure(bg=bg, fg=fg)  # Cambiado de border a fg para mejor contraste
            self._sep_top.configure(bg=border)
            self._sep_bot.configure(bg=border)
            self._outer.configure(bg=bg)  # Outer frame
            self._canvas.configure(bg=bg)
            self._sf.configure(bg=bg)
            self._btn_row.configure(bg=bg)  # Button row frame
            self._vsb.configure(bg=sec_bg, troughcolor=bg,
                                activebackground=acc,
                                highlightthickness=0, bd=0,
                                relief="flat", elementborderwidth=0)
            self._close_btn.configure(bg=btn_bg, fg=btn_fg,
                                      activebackground=hover,
                                      activeforeground=btn_fg)
            
            self._populate()
            
        except Exception as e:
            print(f"Error aplicando tema: {e}")

    def update_ui_language(self):
        lang = self.language_manager
        try:
            self.title_label.configure(text=lang.get_text("menu_shortcuts"))
            self._h_title.configure(text=lang.get_text("menu_shortcuts"))
            self._h_sub.configure(text=lang.get_text("shortcuts_subtitle"))
            self._close_btn.configure(text=lang.get_text("search_close"))
            self._populate()
        except Exception:
            pass
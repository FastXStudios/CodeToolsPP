import tkinter as tk
import os
from gui.components import CustomToplevel
from utils.helpers import resource_path

class AboutWindow(CustomToplevel):
    """Ventana 'Acerca de' con diseño moderno y visual."""

    VERSION = "1.0.0"
    AUTHOR = "Fast X Studios - Byron Vera"
    GITHUB = "github.com/FastXStudios/CodeToolsPP"
    EMAIL = "byronvera113@gmail.com"

    def __init__(self, parent, theme_manager, language_manager):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title=language_manager.get_text("menu_about"),
            size="650x700",
            min_size=(550, 650),
            max_size=(850, 900)
        )
        self.language_manager = language_manager
        self._photos = []
        self._title_icon_label = None

        self._load_title_icon()
        self._build_ui()
        self.apply_theme()
        self.language_manager.subscribe(self.update_ui_language)

    def _load_title_icon(self):
        try:
            from PIL import Image, ImageTk
            t = self.theme_manager.get_theme()
            path = resource_path(os.path.join("assets", "icons", "about.png"))
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA").resize((16, 16), Image.Resampling.LANCZOS)
                bg = t["secondary_bg"].lstrip("#")
                rgb = tuple(int(bg[i:i+2], 16) for i in (0, 2, 4))
                base = Image.new("RGBA", (16, 16), rgb + (255,))
                base.paste(img, mask=img.split()[3])
                self._title_ico = ImageTk.PhotoImage(base.convert("RGB"))
                if self._title_icon_label and self._title_icon_label.winfo_exists():
                    self._title_icon_label.configure(image=self._title_ico)
                    self._title_icon_label.image = self._title_ico
                else:
                    self._title_icon_label = self.add_title_icon(self._title_ico)
        except Exception:
            pass

    def _build_ui(self):
        lang = self.language_manager
        cf = self.content_frame

        outer = tk.Frame(cf)
        outer.pack(fill="both", expand=True, padx=0, pady=0)

        self._scrollbar = tk.Scrollbar(outer, orient="vertical", width=8)
        self._scrollbar.pack(side="right", fill="y")

        self._canvas = tk.Canvas(outer, bd=0, highlightthickness=0,
                                yscrollcommand=self._scrollbar.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.config(command=self._canvas.yview)

        self._scrollable = tk.Frame(self._canvas)
        self._canvas_window = self._canvas.create_window((0, 0),
            window=self._scrollable, anchor="nw")

        self._scrollable.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._canvas_window, width=e.width))

        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

        self._build_header()
        self._build_features_grid()
        self._build_info_section()

        tk.Frame(self._scrollable, height=20).pack()

        self._sep_bottom = tk.Frame(cf, height=1)
        self._sep_bottom.pack(fill="x", side="bottom")

        btn_container = tk.Frame(cf)
        btn_container.pack(side="bottom", pady=14)

        self._close_btn = tk.Button(
            btn_container,
            text=lang.get_text("search_close"),
            command=self.destroy,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            bd=0, relief="flat",
            padx=32, pady=9
        )
        self._close_btn.pack()

    def _build_header(self):
        lang = self.language_manager
        header = tk.Frame(self._scrollable)
        header.pack(fill="x", pady=(28, 20))

        icon_frame = tk.Frame(header)
        icon_frame.pack()

        self._app_icon_lbl = tk.Label(icon_frame)
        self._app_icon_lbl.pack()
        self._load_app_icon()

        self._app_name_lbl = tk.Label(
            header,
            text="Code Tools ++",
            font=("Segoe UI", 24, "bold")
        )
        self._app_name_lbl.pack(pady=(14, 4))

        version_frame = tk.Frame(header)
        version_frame.pack()

        self._version_badge = tk.Label(
            version_frame,
            text=f"v{self.VERSION}",
            font=("Segoe UI", 9, "bold"),
            padx=12, pady=4
        )
        self._version_badge.pack()

        self._tagline = tk.Label(
            header,
            text=lang.get_text("about_app_tagline"),
            font=("Segoe UI", 10),
            wraplength=550
        )
        self._tagline.pack(pady=(12, 0))

    def _build_features_grid(self):
        lang = self.language_manager
        
        self._features_title_frame = tk.Frame(self._scrollable)
        self._features_title_frame.pack(fill="x", padx=40, pady=(24, 16))

        self._features_title_label = tk.Label(
            self._features_title_frame,
            text=lang.get_text("about_section_features"),
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        )
        self._features_title_label.pack(side="left")

        grid = tk.Frame(self._scrollable)
        grid.pack(fill="x", padx=35, pady=(0, 20))

        # Features con keys de traducción
        self.features_data = [
            ("about_feature_files.png", "about_feature_files", "about_feature_files_desc"),
            ("about_feature_dashboard.png", "about_feature_dashboard", "about_feature_dashboard_desc"),
            ("about_feature_search.png", "about_feature_search", "about_feature_search_desc"),
            ("about_feature_export.png", "about_feature_export", "about_feature_export_desc"),
            ("ai.gif", "about_feature_ai", "about_feature_ai_desc"),
            ("limpmax.gif", "about_feature_limpmax", "about_feature_limpmax_desc"),
            ("markdown.png", "about_feature_readme", "about_feature_readme_desc"),
            ("about_feature_themes.png", "about_feature_themes", "about_feature_themes_desc"),
            ("todo.png", "about_feature_todos", "about_feature_todos_desc"),
            ("about_feature_duplicates.png", "about_feature_duplicates", "about_feature_duplicates_desc"),
            ("language.png", "about_feature_i18n", "about_feature_i18n_desc"),
        ]

        self._feature_cards = []
        self._feature_titles = []
        self._feature_descs = []
        row_frame = None

        for i, (icon_name, title_key, desc_key) in enumerate(self.features_data):
            if i % 3 == 0:
                row_frame = tk.Frame(grid)
                row_frame.pack(fill="x", pady=6)

            card, title_lbl, desc_lbl = self._create_feature_card(
                row_frame, icon_name, title_key, desc_key
            )
            card.pack(side="left", padx=6, fill="both", expand=True)
            self._feature_cards.append(card)
            self._feature_titles.append(title_lbl)
            self._feature_descs.append(desc_lbl)

    def _create_feature_card(self, parent, icon_name, title_key, desc_key):
        lang = self.language_manager
        
        card = tk.Frame(parent, relief="flat", bd=1, height=140)
        card.pack_propagate(False)

        content = tk.Frame(card)
        content.place(relx=0.5, rely=0.5, anchor="center")

        icon = self._load_icon(icon_name, 32)
        if icon:
            icon_lbl = tk.Label(content, image=icon)
            icon_lbl.pack(pady=(0, 8))
            self._photos.append(icon)
            icon_lbl._photo_ref = icon
        else:
            placeholder = tk.Frame(content, width=32, height=32)
            placeholder.pack(pady=(0, 8))
            placeholder.pack_propagate(False)

        title_lbl = tk.Label(
            content,
            text=lang.get_text(title_key),
            font=("Segoe UI", 10, "bold"),
            justify="center"
        )
        title_lbl.pack(pady=(0, 4))

        desc_lbl = tk.Label(
            content,
            text=lang.get_text(desc_key),
            font=("Segoe UI", 8),
            justify="center"
        )
        desc_lbl.pack(pady=(0, 0))

        return card, title_lbl, desc_lbl

    def _build_info_section(self):
        lang = self.language_manager
        
        self._info_title_frame = tk.Frame(self._scrollable)
        self._info_title_frame.pack(fill="x", padx=40, pady=(8, 16))

        self._info_title_label = tk.Label(
            self._info_title_frame,
            text=lang.get_text("about_section_info"),
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        )
        self._info_title_label.pack(side="left")

        cols = tk.Frame(self._scrollable)
        cols.pack(fill="x", padx=40)

        left = tk.Frame(cols)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._info_box_left, self._info_left_labels = self._create_info_box(
            left, "about_info_details.png", "about_info_details", [
                ("about_info_version", self.VERSION),
                ("about_info_developer", self.AUTHOR),
                ("about_info_python", "3.12+"),
                ("about_info_framework", "Tkinter"),
            ]
        )

        right = tk.Frame(cols)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._info_box_right, self._info_right_labels = self._create_info_box(
            right, "about_info_contact.png", "about_info_contact", [
                ("about_info_github", self.GITHUB.split("/")[-1]),
                ("about_info_email", self.EMAIL),
                ("about_info_license", "MIT License"),
                ("about_info_languages", "ES · EN · ZH · RU"),
            ]
        )

    def _create_info_box(self, parent, icon_name, title_key, items):
        lang = self.language_manager
        
        box = tk.Frame(parent, relief="flat", bd=1)
        box.pack(fill="both", expand=True)

        header = tk.Frame(box)
        header.pack(fill="x", padx=16, pady=(14, 10))

        icon = self._load_icon(icon_name, 18)
        if icon:
            icon_lbl = tk.Label(header, image=icon)
            icon_lbl.pack(side="left", padx=(0, 8))
            self._photos.append(icon)
            icon_lbl._photo_ref = icon
        else:
            placeholder = tk.Frame(header, width=18, height=18)
            placeholder.pack(side="left", padx=(0, 8))
            placeholder.pack_propagate(False)

        title_label = tk.Label(
            header,
            text=lang.get_text(title_key),
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        )
        title_label.pack(side="left")

        items_frame = tk.Frame(box)
        items_frame.pack(fill="x", padx=16, pady=(0, 14))

        label_widgets = []
        for label_key, value in items:
            row = tk.Frame(items_frame)
            row.pack(fill="x", pady=3)

            label_widget = tk.Label(
                row,
                text=f"{lang.get_text(label_key)}:",
                font=("Segoe UI", 9, "bold"),
                anchor="w",
                width=12
            )
            label_widget.pack(side="left")
            label_widgets.append((label_widget, label_key))

            value_widget = tk.Label(
                row,
                text=value,
                font=("Segoe UI", 9),
                anchor="w"
            )
            value_widget.pack(side="left", fill="x", expand=True)

        return box, (title_label, title_key, label_widgets)

    def _load_app_icon(self):
        try:
            from PIL import Image, ImageTk
            t = self.theme_manager.get_theme()

            search_paths = [
                resource_path("icon.ico"),
                resource_path("assets/icons/dashboard.png"),
                resource_path("assets/icons/file.png"),
            ]

            for path in search_paths:
                if os.path.exists(path):
                    img = Image.open(path).convert("RGBA").resize(
                        (80, 80), Image.Resampling.LANCZOS
                    )
                    bg_hex = t["bg"].lstrip("#")
                    rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
                    base = Image.new("RGBA", (80, 80), rgb + (255,))
                    base.paste(img, mask=img.split()[3])
                    self._app_icon_img = ImageTk.PhotoImage(base.convert("RGB"))
                    self._app_icon_lbl.configure(image=self._app_icon_img)
                    self._photos.append(self._app_icon_img)
                    return
            
            self._create_icon_placeholder(self._app_icon_lbl, 80)
            
        except Exception as e:
            print(f"Error cargando icono principal: {e}")
            self._create_icon_placeholder(self._app_icon_lbl, 80)

    def _load_icon(self, name, size):
        try:
            from PIL import Image, ImageTk
            t = self.theme_manager.get_theme()

            path = resource_path(os.path.join("assets", "icons", name))
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA").resize(
                    (size, size), Image.Resampling.LANCZOS
                )
                bg_hex = t["bg"].lstrip("#")
                rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
                base = Image.new("RGBA", (size, size), rgb + (255,))
                base.paste(img, mask=img.split()[3])
                return ImageTk.PhotoImage(base.convert("RGB"))
        except Exception as e:
            print(f"Error cargando icono {name}: {e}")
        
        return None

    def _create_icon_placeholder(self, label, size):
        try:
            from PIL import Image, ImageDraw, ImageTk
            t = self.theme_manager.get_theme()
            
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            acc = t.get("accent", "#007AFF").lstrip("#")
            rgb = tuple(int(acc[i:i+2], 16) for i in (0, 2, 4))
            
            draw.ellipse([2, 2, size-2, size-2], fill=rgb + (180,))
            
            photo = ImageTk.PhotoImage(img)
            label.configure(image=photo)
            self._photos.append(photo)
        except Exception as e:
            print(f"Error creando placeholder: {e}")

    def _on_mousewheel(self, event):
        try:
            if not self._canvas.winfo_exists():
                return

            if event.num == 4:
                self._canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self._canvas.yview_scroll(1, "units")
            else:
                self._canvas.yview_scroll(-1 * (event.delta // 120), "units")
        except:
            pass
        return "break"

    def apply_theme(self):
        self._load_title_icon()
        self.apply_base_theme()
        t = self.theme_manager.get_theme()
        bg = t["bg"]
        sec_bg = t["secondary_bg"]
        fg = t["fg"]
        border = t["border"]
        acc = t["accent"]
        btn_bg = t["button_bg"]
        btn_fg = t["button_fg"]

        try:
            self.content_frame.configure(bg=bg)
            self._canvas.configure(bg=bg)
            self._scrollable.configure(bg=bg)

            self._scrollbar.configure(
                bg=sec_bg, troughcolor=bg,
                activebackground=acc,
                highlightthickness=0, bd=0
            )

            self._sep_bottom.configure(bg=border)

            for widget in [self._app_icon_lbl, self._app_name_lbl,
                          self._tagline]:
                try:
                    widget.configure(bg=bg, fg=fg)
                except:
                    pass

            self._app_name_lbl.configure(fg=acc)

            self._version_badge.configure(bg=acc, fg="#ffffff")

            for card in self._feature_cards:
                card.configure(bg=sec_bg, highlightbackground=border, highlightthickness=1)
                self._apply_bg_recursive(card, sec_bg, fg)

            for box in [self._info_box_left, self._info_box_right]:
                box.configure(bg=sec_bg, highlightbackground=border, highlightthickness=1)
                self._apply_bg_recursive(box, sec_bg, fg)

            self._close_btn.configure(
                bg=btn_bg, fg=btn_fg,
                activebackground=t.get("button_hover", btn_bg),
                activeforeground=btn_fg
            )

            self._apply_bg_recursive(self._scrollable, bg, fg)

        except Exception as e:
            print(f"Error aplicando tema: {e}")

    def _apply_bg_recursive(self, widget, bg, fg=None):
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg)
            elif isinstance(widget, tk.Label):
                widget.configure(bg=bg)
                if fg:
                    try:
                        if not widget.cget("image"):
                            widget.configure(fg=fg)
                    except:
                        widget.configure(fg=fg)
        except:
            pass

        try:
            for child in widget.winfo_children():
                self._apply_bg_recursive(child, bg, fg)
        except:
            pass

    def update_ui_language(self):
        lang = self.language_manager
        try:
            # Título de la ventana
            self.title_label.configure(text=lang.get_text("menu_about"))
            
            # Tagline
            self._tagline.configure(text=lang.get_text("about_app_tagline"))
            
            # Título de características
            self._features_title_label.configure(text=lang.get_text("about_section_features"))
            
            # Actualizar títulos y descripciones de tarjetas
            for i, (title_lbl, desc_lbl) in enumerate(zip(self._feature_titles, self._feature_descs)):
                _, title_key, desc_key = self.features_data[i]
                title_lbl.configure(text=lang.get_text(title_key))
                desc_lbl.configure(text=lang.get_text(desc_key))
            
            # Título de información
            self._info_title_label.configure(text=lang.get_text("about_section_info"))
            
            # Actualizar info boxes
            for box_labels in [self._info_left_labels, self._info_right_labels]:
                title_label, title_key, label_widgets = box_labels
                title_label.configure(text=lang.get_text(title_key))
                for label_widget, label_key in label_widgets:
                    label_widget.configure(text=f"{lang.get_text(label_key)}:")
            
            # Botón cerrar
            self._close_btn.configure(text=lang.get_text("search_close"))
            
        except Exception as e:
            print(f"Error actualizando idioma: {e}")

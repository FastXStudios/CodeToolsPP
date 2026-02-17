import tkinter as tk


class ExportMenu:
    """Menu de exportacion con estilo personalizado."""

    def __init__(self, parent, theme_manager, language_manager, icon_manager, on_option_selected):
        self.parent = parent
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        self.icon_manager = icon_manager
        self.on_option_selected = on_option_selected
        self.menu_window = None

        # Evita que tkinter libere referencias a imagenes
        self._icon_refs = {}

    def show(self, button_widget):
        """Muestra el menu debajo del boton indicado."""
        if self.menu_window and self.menu_window.winfo_exists():
            self.menu_window.destroy()

        t = self.theme_manager.get_theme()
        lang = self.language_manager

        self.menu_window = tk.Toplevel(self.parent)
        self.menu_window.withdraw()
        self.menu_window.overrideredirect(True)
        self.menu_window.configure(bg=t["border"])

        main_frame = tk.Frame(self.menu_window, bg=t["secondary_bg"], bd=0)
        main_frame.pack(fill="both", expand=True, padx=1, pady=1)

        header = tk.Frame(main_frame, bg=t["secondary_bg"])
        header.pack(fill="x")

        header_label = tk.Label(
            header,
            text=f"  {lang.get_text('btn_export')}",
            font=("Segoe UI", 9, "bold"),
            bg=t["secondary_bg"],
            fg=t["fg"],
            anchor="w",
        )
        header_label.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        close_btn = tk.Label(
            header,
            text="  x  ",
            font=("Segoe UI", 12),
            bg=t["secondary_bg"],
            fg=t["fg"],
            cursor="hand2",
        )
        close_btn.pack(side="right", padx=4)
        close_btn.bind("<Button-1>", lambda e: self.menu_window.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg=t.get("warning", "#e74c3c"), fg="#ffffff"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg=t["secondary_bg"], fg=t["fg"]))

        tk.Frame(main_frame, bg=t["border"], height=1).pack(fill="x")

        options = [
            ("with_content", "copycontent.png", lang.get_text("export_with_content")),
            ("paths_only", "rut.png", lang.get_text("export_paths_only")),
            ("tree_structure", "tree.png", lang.get_text("export_tree_structure")),
            ("for_llm", "LLM.png", lang.get_text("export_for_llm")),
            ("save_file", "save.png", lang.get_text("export_save_file")),
        ]

        list_frame = tk.Frame(main_frame, bg=t["tree_bg"])
        list_frame.pack(fill="both", expand=True)

        for index, option in enumerate(options):
            if index == 4:
                tk.Frame(list_frame, bg=t["border"], height=1).pack(fill="x")
            self._create_option_item(list_frame, option, index, t)

        self.menu_window.update_idletasks()

        try:
            if button_widget and button_widget.winfo_exists():
                x = button_widget.winfo_rootx()
                y = button_widget.winfo_rooty() + button_widget.winfo_height() + 2
            else:
                x = self.parent.winfo_pointerx()
                y = self.parent.winfo_pointery()
        except Exception:
            x = self.parent.winfo_pointerx()
            y = self.parent.winfo_pointery()

        width = 320
        height = main_frame.winfo_reqheight() + 10
        self.menu_window.geometry(f"{width}x{height}+{x}+{y}")
        self.menu_window.deiconify()
        self.menu_window.lift()
        self.menu_window.focus_set()

        self.menu_window.after(100, self._check_focus)

    def _create_option_item(self, parent, option, index, theme):
        action, icon_name, label_text = option
        item_bg = theme["tree_bg"] if index % 2 == 0 else theme["bg"]
        hover_bg = theme["tree_selected_bg"]

        item = tk.Frame(parent, bg=item_bg, cursor="hand2")
        item.pack(fill="x", pady=1)

        icon = self.icon_manager.load_icon(icon_name, (16, 16))
        if icon:
            self._icon_refs[f"{action}_{index}"] = icon
            icon_lbl = tk.Label(item, image=icon, bg=item_bg, cursor="hand2")
            icon_lbl.pack(side="left", padx=(10, 8), pady=9)
        else:
            icon_lbl = None

        text_lbl = tk.Label(
            item,
            text=label_text,
            font=("Segoe UI", 9),
            bg=item_bg,
            fg=theme["fg"],
            anchor="w",
            cursor="hand2",
        )
        text_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=9)

        widgets = [item, text_lbl]
        if icon_lbl:
            widgets.append(icon_lbl)

        def on_enter(_event):
            for w in widgets:
                try:
                    w.configure(bg=hover_bg)
                    if w == text_lbl:
                        w.configure(fg=theme.get("tree_selected_fg", "#ffffff"))
                except Exception:
                    pass

        def on_leave(_event):
            for w in widgets:
                try:
                    w.configure(bg=item_bg)
                    if w == text_lbl:
                        w.configure(fg=theme["fg"])
                except Exception:
                    pass

        def on_click(_event):
            self.on_option_selected(action)
            if self.menu_window and self.menu_window.winfo_exists():
                self.menu_window.destroy()

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

    def _check_focus(self):
        """Cierra el menu si pierde foco."""
        try:
            if self.menu_window and self.menu_window.winfo_exists():
                if not self.menu_window.focus_displayof():
                    self.menu_window.destroy()
                else:
                    self.menu_window.after(100, self._check_focus)
        except Exception:
            pass

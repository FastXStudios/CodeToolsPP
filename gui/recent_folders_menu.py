import tkinter as tk
import os


class RecentFoldersMenu:
    """Menú profesional de carpetas recientes"""
    
    def __init__(self, parent, theme_manager, language_manager, icon_manager, config_manager, on_folder_selected):
        self.parent = parent
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        self.icon_manager = icon_manager
        self.config_manager = config_manager
        self.on_folder_selected = on_folder_selected
        
        self.menu_window = None
    
    def show(self, button_widget):
        """Muestra el menú debajo del botón especificado"""
        if self.menu_window and self.menu_window.winfo_exists():
            self.menu_window.destroy()
        
        lang = self.language_manager
        recent = self.config_manager.get_recent_folders()
        t = self.theme_manager.get_theme()
        
        # ═══════════════════════════════════════════════════════════
        # CREAR VENTANA PERSONALIZADA
        # ═══════════════════════════════════════════════════════════
        self.menu_window = tk.Toplevel(self.parent)
        self.menu_window.withdraw()
        self.menu_window.overrideredirect(True)
        self.menu_window.configure(bg=t['border'])
        
        # Frame principal
        main_frame = tk.Frame(self.menu_window, bg=t['secondary_bg'], bd=0)
        main_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # ═══════════════════════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════════════════════
        header = tk.Frame(main_frame, bg=t['secondary_bg'])
        header.pack(fill="x")
        
        header_label = tk.Label(
            header,
            text=f"  {lang.get_text('menu_recent_folders')}",
            font=("Segoe UI", 9, "bold"),
            bg=t['secondary_bg'],
            fg=t['fg'],
            anchor="w"
        )
        header_label.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        
        # Botón cerrar
        close_btn = tk.Label(
            header,
            text="  ×  ",
            font=("Segoe UI", 12),
            bg=t['secondary_bg'],
            fg=t['fg'],
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=4)
        close_btn.bind("<Button-1>", lambda e: self.menu_window.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg=t.get('warning', '#e74c3c'), fg='#ffffff'))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg=t['secondary_bg'], fg=t['fg']))
        
        # Separador
        tk.Frame(main_frame, bg=t['border'], height=1).pack(fill="x")
        
        # ═══════════════════════════════════════════════════════════
        # BOTÓN LIMPIAR HISTORIAL - AL INICIO
        # ═══════════════════════════════════════════════════════════
        footer = tk.Frame(main_frame, bg=t['secondary_bg'])
        footer.pack(fill="x")
        
        # ✅ Intentar cargar icono con múltiples fallbacks
        clear_icon = None
        try:
            # OPCIÓN 1: Intentar con get_icon
            clear_icon = self.icon_manager.get_icon("clear.png", (16, 16))
        except:
            try:
                # OPCIÓN 2: Cargar directamente desde archivo
                from PIL import Image, ImageTk
                import os
                icon_path = os.path.join("assets", "icons", "clear.png")
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    img = img.resize((16, 16), Image.Resampling.LANCZOS)
                    clear_icon = ImageTk.PhotoImage(img)
            except:
                # OPCIÓN 3: Usar emoji como fallback
                pass
        
        # Frame para botón con icono + texto
        btn_frame = tk.Frame(footer, bg=t['secondary_bg'], cursor="hand2")
        btn_frame.pack(side="left", padx=12, pady=10)
        
        if clear_icon:
            # Con icono
            icon_label = tk.Label(btn_frame, image=clear_icon, bg=t['secondary_bg'], cursor="hand2")
            icon_label.image = clear_icon
            icon_label.pack(side="left", padx=(0, 6))
        
        text_label = tk.Label(
            btn_frame,
            text=lang.get_text('clear_history'),
            font=("Segoe UI", 9),
            bg=t['secondary_bg'],
            fg=t['fg'],
            cursor="hand2"
        )
        text_label.pack(side="left")
        
        # Hacer todo clickeable
        def on_clear_click(e):
            self._clear_history()
        
        all_clear_widgets = [btn_frame, text_label]
        if clear_icon:
            all_clear_widgets.append(icon_label)
            icon_label.bind("<Button-1>", on_clear_click)
        
        btn_frame.bind("<Button-1>", on_clear_click)
        text_label.bind("<Button-1>", on_clear_click)
        
        # Hover effect
        def on_enter(e):
            for w in all_clear_widgets:
                try:
                    w.configure(bg=t.get('warning', '#e74c3c'))
                    if w == text_label:
                        w.configure(fg='#ffffff')
                except:
                    pass
        
        def on_leave(e):
            for w in all_clear_widgets:
                try:
                    w.configure(bg=t['secondary_bg'])
                    if w == text_label:
                        w.configure(fg=t['fg'])
                except:
                    pass
        
        for w in all_clear_widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
        
        # Separador
        tk.Frame(main_frame, bg=t['border'], height=1).pack(fill="x")
        
        # ═══════════════════════════════════════════════════════════
        # LISTA DE CARPETAS - SIN SCROLLBAR, SOLO RUEDA DEL MOUSE
        # ═══════════════════════════════════════════════════════════
        valid_recent = [f for f in recent if os.path.exists(f)]
        
        if not valid_recent:
            # Estado vacío
            empty = tk.Frame(main_frame, bg=t['tree_bg'])
            empty.pack(fill="both", expand=True)
            
            tk.Label(
                empty,
                text=lang.get_text('menu_empty'),
                font=("Segoe UI", 9),
                bg=t['tree_bg'],
                fg=t['fg']
            ).pack(expand=True, pady=40)
        else:
            # Canvas con scroll SOLO con rueda del mouse
            list_height = min(300, len(valid_recent) * 52)
            canvas = tk.Canvas(
                main_frame, 
                bg=t['tree_bg'], 
                highlightthickness=0, 
                height=list_height
            )
            canvas.pack(fill="both", expand=True)
            
            scrollable = tk.Frame(canvas, bg=t['tree_bg'])
            canvas.create_window((0, 0), window=scrollable, anchor="nw")
            
            # Actualizar scroll region cuando cambie el tamaño
            scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
            # ✅ SCROLL CON RUEDA DEL MOUSE (sin scrollbar visible)
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            self.menu_window.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))
            
            # Items
            for i, folder in enumerate(valid_recent):
                self._create_folder_item(scrollable, folder, i, t)
        
        # ═══════════════════════════════════════════════════════════
        # POSICIONAR Y MOSTRAR
        # ═══════════════════════════════════════════════════════════
        self.menu_window.update_idletasks()
        
        try:
            if button_widget and button_widget.winfo_exists():
                x = button_widget.winfo_rootx()
                y = button_widget.winfo_rooty() + button_widget.winfo_height() + 2
            else:
                x = self.parent.winfo_pointerx()
                y = self.parent.winfo_pointery()
        except:
            x = self.parent.winfo_pointerx()
            y = self.parent.winfo_pointery()
        
        # Calcular altura automáticamente
        width = 420
        height = main_frame.winfo_reqheight() + 10
        
        self.menu_window.geometry(f"{width}x{height}+{x}+{y}")
        self.menu_window.deiconify()
        self.menu_window.lift()
        self.menu_window.focus_set()
        
        # Cerrar al hacer clic fuera
        self.menu_window.after(100, self._check_focus)
    
    def _create_folder_item(self, parent, folder, index, theme):
        """Crea un item de carpeta en la lista"""
        # Frame del item
        item_bg = theme['tree_bg'] if index % 2 == 0 else theme['bg']
        item = tk.Frame(parent, bg=item_bg, cursor="hand2")
        item.pack(fill="x", pady=1)
        
        # Icono carpeta
        try:
            ico = self.icon_manager.get_folder_icon("folder", False, (16, 16))
            if ico:
                lbl_ico = tk.Label(item, image=ico, bg=item_bg)
                lbl_ico.image = ico
                lbl_ico.pack(side="left", padx=(10, 8), pady=10)
        except:
            pass
        
        # Textos
        text_frame = tk.Frame(item, bg=item_bg)
        text_frame.pack(side="left", fill="x", expand=True, pady=8)
        
        # Nombre de carpeta
        name = os.path.basename(folder)
        name_lbl = tk.Label(
            text_frame,
            text=name,
            font=("Segoe UI", 9, "bold"),
            bg=item_bg,
            fg=theme['fg'],
            anchor="w"
        )
        name_lbl.pack(fill="x", padx=(0, 10))
        
        # Ruta completa
        path_lbl = tk.Label(
            text_frame,
            text=folder,
            font=("Segoe UI", 8),
            bg=item_bg,
            fg=theme['tree_fg'],
            anchor="w"
        )
        path_lbl.pack(fill="x", padx=(0, 10))
        
        # Hover effect
        hover_bg = theme['tree_selected_bg']
        all_widgets = [item, text_frame, name_lbl, path_lbl]
        
        def on_enter(e):
            for w in all_widgets:
                try: 
                    w.configure(bg=hover_bg)
                    if w == name_lbl or w == path_lbl:
                        w.configure(fg=theme.get('tree_selected_fg', '#ffffff'))
                except: 
                    pass
        
        def on_leave(e):
            for w in all_widgets:
                try:
                    w.configure(bg=item_bg)
                    if w == name_lbl:
                        w.configure(fg=theme['fg'])
                    elif w == path_lbl:
                        w.configure(fg=theme['tree_fg'])
                except: 
                    pass
        
        def on_click(e):
            self.on_folder_selected(folder)
            self.menu_window.destroy()
        
        for w in all_widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)
    
    def _clear_history(self):
        """Limpia el historial de carpetas recientes"""
        self.config_manager.config["recent_folders"] = []
        self.config_manager.save()
        self.menu_window.destroy()
        
        # Mostrar mensaje
        from tkinter import messagebox
        messagebox.showinfo(
            self.language_manager.get_text('msg_success'),
            self.language_manager.get_text('history_cleared')
        )
    
    def _check_focus(self):
        """Cierra el menú si pierde el foco"""
        try:
            if self.menu_window and self.menu_window.winfo_exists():
                if not self.menu_window.focus_displayof():
                    self.menu_window.destroy()
                else:
                    self.menu_window.after(100, self._check_focus)
        except:
            pass
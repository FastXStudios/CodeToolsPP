import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class TreeView(ttk.Treeview):
    """TreeView mejorado con iconos y selección inteligente"""

    IGNORED_DIRS = {
        "node_modules", "venv", ".venv", "env", ".env",
        "__pycache__", ".git", ".svn", ".hg", "dist", "build",
    }
    IGNORED_ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}
    
    def __init__(self, parent, file_manager, selection_manager, icon_manager, alert_manager, theme_manager, language_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.file_manager = file_manager
        self.selection_manager = selection_manager
        self.icon_manager = icon_manager
        self.alert_manager = alert_manager
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        
        # Configuración
        self.configure(columns=("abspath",), show="tree")
        self.column("#0", width=500)
        
        # Tags para estilos con colores más visibles
        self.tag_configure("selected", background="#2ecc71", foreground="#ffffff")
        self.tag_configure("folder", font=("Helvetica", 10, "bold"))
        self.tag_configure("file", font=("Helvetica", 10))
        
        # Bindings
        self.bind("<<TreeviewOpen>>", self._on_open)
        self.bind("<<TreeviewClose>>", self._on_close)  # ← AGREGAR ESTA LÍNEA
        self.bind("<KeyPress-e>", self._toggle_selection_key)
        self.bind("<KeyPress-E>", self._toggle_selection_key)
        self.bind("<space>", self._toggle_selection_key)
        self.bind("<Double-Button-1>", self._on_double_click)
        
        # Menú contextual
        self._create_context_menu()
        self.bind("<Button-3>", self._show_context_menu)
        
        self.apply_theme()
    
    def apply_theme(self):
        """Aplica el tema actual"""
        theme = self.theme_manager.get_theme()
        
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background=theme['tree_bg'],
            foreground=theme['tree_fg'],
            fieldbackground=theme['tree_bg'],
            font=("Helvetica", 10),
            rowheight=25
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#2ecc71")],
            foreground=[("selected", "#ffffff")]
        )
        
        # Configurar tag selected con colores del tema
        self.tag_configure("selected", background="#2ecc71", foreground="#ffffff")
        
        self.configure(style="Custom.Treeview")
    
    def load_directory(self, path):
        """Carga un directorio en el árbol"""
        self.delete(*self.get_children())
        self.file_manager.set_root(path)
        self._insert_node("", path, path)
    
    def _insert_node(self, parent, text, abspath):
        is_dir = os.path.isdir(abspath)
        basename = os.path.basename(abspath) or abspath

        # Icono base (carpeta o archivo)
        if is_dir:
            base_icon = self.icon_manager.get_folder_icon(basename, False, size=(18, 18))
        else:
            base_icon = self.icon_manager.get_file_icon(basename, size=(18, 18))

        # Checkbox PNG
        is_selected = self.selection_manager.is_selected(abspath)
        if is_selected:
            checkbox_icon = self.icon_manager.load_icon('checkbox-checked.png', size=(16, 16))
        else:
            checkbox_icon = self.icon_manager.load_icon('checkbox-unchecked.png', size=(16, 16))

        # 🔥 Combinar imágenes
        combined_icon = self._combine_icons(checkbox_icon, base_icon)

        tags = ["folder" if is_dir else "file"]
        if is_selected:
            tags.append("selected")

        node = self.insert(
            parent, "end",
            text=basename,   # ❌ SIN emojis
            image=combined_icon,
            open=False,
            values=(abspath,),
            tags=tuple(tags)
        )

        # Guardar referencia
        if not hasattr(self, '_node_images'):
            self._node_images = {}
        self._node_images[node] = combined_icon

        if is_dir:
            self.insert(node, "end", text="", values=("__dummy__",))

        return node
    def _combine_icons(self, checkbox_icon, base_icon):
        """Combina checkbox + icono base en una sola imagen"""
        from PIL import Image, ImageTk

        img1 = checkbox_icon._PhotoImage__photo.zoom(1)
        img2 = base_icon._PhotoImage__photo.zoom(1)

        width = img1.width() + img2.width()
        height = max(img1.height(), img2.height())

        combined = Image.new("RGBA", (width, height))

        checkbox_pil = ImageTk.getimage(checkbox_icon)
        base_pil = ImageTk.getimage(base_icon)

        combined.paste(checkbox_pil, (0, 0), checkbox_pil)
        combined.paste(base_pil, (img1.width(), 0), base_pil)

        return ImageTk.PhotoImage(combined)

    
    def _on_open(self, event):
        """Maneja la apertura de carpetas (carga perezosa)"""
        node = self.focus()
        if not node:
            return
        
        values = self.item(node, "values")
        if not values:
            return
        
        abspath = values[0]
        if not os.path.isdir(abspath):
            return
        
        # Verificar si ya está cargado
        children = self.get_children(node)
        if len(children) == 1 and self.item(children[0], "values") == ("__dummy__",):
            # Eliminar dummy y cargar contenido real
            self.delete(children[0])
            self._load_directory_contents(node, abspath)
        
        # SIEMPRE actualizar icono de carpeta abierta
        self._update_folder_icon(node, abspath, True)

    def _on_close(self, event):
        """Maneja el cierre de carpetas"""
        node = self.focus()
        if not node:
            return
        
        values = self.item(node, "values")
        if not values:
            return
        
        abspath = values[0]
        if not os.path.isdir(abspath):
            return
        
        # Actualizar icono de carpeta cerrada
        self._update_folder_icon(node, abspath, False)

    def _load_directory_contents(self, parent_node, dirpath):
        """Carga el contenido de un directorio"""
        try:
            items = self.file_manager.list_directory(dirpath)
            for item in items:
                self._insert_node(parent_node, item['name'], item['path'])
        except Exception as e:
            print(f"Error loading directory {dirpath}: {e}")

    def _update_folder_icon(self, node, path, is_open):
        basename = os.path.basename(path)

        is_selected = self.selection_manager.is_selected(path)

        # Icono base carpeta (open / close)
        base_icon = self.icon_manager.get_folder_icon(
            basename, is_open, size=(18, 18)
        )

        # Checkbox PNG
        if is_selected:
            checkbox_icon = self.icon_manager.load_icon(
                'checkbox-checked.png', size=(16, 16)
            )
        else:
            checkbox_icon = self.icon_manager.load_icon(
                'checkbox-unchecked.png', size=(16, 16)
            )

        # Combinar imágenes
        combined_icon = self._combine_icons(checkbox_icon, base_icon)

        tags = ["folder"]
        if is_selected:
            tags.append("selected")

        # 🔥 SIN EMOJIS
        self.item(node, text=basename, image=combined_icon, tags=tuple(tags))

        if not hasattr(self, '_node_images'):
            self._node_images = {}
        self._node_images[node] = combined_icon

        print(f"Icono actualizado: {basename} ({'abierto' if is_open else 'cerrado'})")

    
    def _toggle_selection_key(self, event):
        """Maneja la tecla E o espacio para marcar/desmarcar"""
        node = self.focus()
        if not node:
            return
        
        values = self.item(node, "values")
        if not values or values[0] == "__dummy__":
            return
        
        abspath = values[0]
        self.toggle_selection(node, abspath)
    
    def toggle_selection(self, node, abspath):
        """Marca/desmarca un item"""
        is_dir = os.path.isdir(abspath)
        basename = os.path.basename(abspath)
        
        # Verificar alerta para carpetas especiales
        if is_dir and self.icon_manager.is_warning_folder(basename):
            if self.alert_manager.should_warn(basename):
                if not self.alert_manager.show_warning(basename):
                    return  # Usuario canceló
        
        # Toggle selección
        current_state = self.selection_manager.is_selected(abspath)
        new_state = not current_state
        
        if new_state:
            self.selection_manager.select_item(abspath)
            if is_dir:
                # Seleccionar recursivamente, alertando también por subcarpetas sensibles.
                self._select_folder_with_warnings(abspath)
        else:
            self.selection_manager.deselect_item(abspath)
            if is_dir:
                # Deseleccionar todo el contenido
                self.selection_manager.deselect_all_in_folder(abspath)
        
        # Actualizar visualización
        self._update_node_display(node, abspath, new_state)
        
        # Si es carpeta, actualizar hijos si están cargados
        if is_dir:
            self._refresh_loaded_subtree(node)
        
        return new_state

    def _select_folder_with_warnings(self, folder_path):
        """Selecciona carpeta recursivamente, pidiendo confirmación en subcarpetas sensibles."""
        if not os.path.isdir(folder_path):
            return

        warned_decisions = {}
        root_norm = os.path.normcase(os.path.normpath(folder_path))
        skipped_dirs = set()
        skipped_files = set()

        try:
            for current_root, dirs, files in os.walk(folder_path):
                current_norm = os.path.normcase(os.path.normpath(current_root))
                current_name = os.path.basename(current_root).lower()

                # Nunca incluir automáticamente carpetas pesadas/sistema cuando se marca carpeta padre.
                if current_norm != root_norm and current_name in self.IGNORED_DIRS:
                    skipped_dirs.add(current_name)
                    dirs[:] = []
                    continue

                # Si el root actual es sensible (y no es la carpeta raíz que el usuario seleccionó),
                # pedir confirmación; si cancela, podar subárbol completo.
                if current_norm != root_norm and self.icon_manager.is_warning_folder(current_name):
                    if current_name in warned_decisions:
                        allow_current = warned_decisions[current_name]
                    elif self.alert_manager.should_warn(current_name):
                        allow_current = self.alert_manager.show_warning(current_name)
                        warned_decisions[current_name] = allow_current
                    else:
                        allow_current = True
                        warned_decisions[current_name] = True

                    if not allow_current:
                        dirs[:] = []
                        continue

                self.selection_manager.select_item(current_root)

                # Decidir por adelantado qué subdirectorios se recorren.
                pruned_dirs = []
                for d in dirs:
                    folder_name = d.lower()
                    if folder_name in self.IGNORED_DIRS:
                        skipped_dirs.add(folder_name)
                        continue
                    if self.icon_manager.is_warning_folder(folder_name):
                        if folder_name in warned_decisions:
                            allow_subdir = warned_decisions[folder_name]
                        elif self.alert_manager.should_warn(folder_name):
                            allow_subdir = self.alert_manager.show_warning(folder_name)
                            warned_decisions[folder_name] = allow_subdir
                        else:
                            allow_subdir = True
                            warned_decisions[folder_name] = True

                        if not allow_subdir:
                            continue

                    pruned_dirs.append(d)

                dirs[:] = pruned_dirs

                for file_name in files:
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext in self.IGNORED_ARCHIVE_EXTS:
                        skipped_files.add(ext)
                        continue
                    self.selection_manager.select_item(os.path.join(current_root, file_name))

            if skipped_dirs or skipped_files:
                parts = []
                if skipped_dirs:
                    parts.append("Carpetas omitidas: " + ", ".join(sorted(skipped_dirs)))
                if skipped_files:
                    parts.append("Archivos omitidos: " + ", ".join(sorted(skipped_files)))
                messagebox.showwarning(
                    "Selección filtrada",
                    "Se omitieron elementos recomendados para no analizar:\n\n" + "\n".join(parts)
                )
        except Exception as e:
            print(f"Error selecting folder contents with warnings: {e}")
    
    def _update_node_display(self, node, abspath, is_selected):
        is_dir = os.path.isdir(abspath)
        basename = os.path.basename(abspath)

        # Base icon
        if is_dir:
            is_open = self.item(node, "open")
            base_icon = self.icon_manager.get_folder_icon(basename, is_open, size=(18, 18))
        else:
            base_icon = self.icon_manager.get_file_icon(basename, size=(18, 18))

        # Checkbox icon
        if is_selected:
            checkbox_icon = self.icon_manager.load_icon('checkbox-checked.png', size=(16, 16))
        else:
            checkbox_icon = self.icon_manager.load_icon('checkbox-unchecked.png', size=(16, 16))

        combined_icon = self._combine_icons(checkbox_icon, base_icon)

        tags = ["folder" if is_dir else "file"]
        if is_selected:
            tags.append("selected")

        self.item(node, text=basename, image=combined_icon, tags=tuple(tags))

        if not hasattr(self, '_node_images'):
            self._node_images = {}
        self._node_images[node] = combined_icon

    
    def _update_children_display(self, parent_node, is_selected):
        """Actualiza la visualización de todos los hijos recursivamente"""
        children = self.get_children(parent_node)
        for child in children:
            values = self.item(child, "values")
            if values and values[0] != "__dummy__":
                child_path = values[0]
                self._update_node_display(child, child_path, is_selected)
                
                # Recursivo para subcarpetas
                if os.path.isdir(child_path):
                    self._update_children_display(child, is_selected)

    def _refresh_loaded_subtree(self, parent_node):
        """Sincroniza visual de nodos cargados según estado real de selección."""
        children = self.get_children(parent_node)
        for child in children:
            values = self.item(child, "values")
            if values and values[0] != "__dummy__":
                child_path = values[0]
                is_selected = self.selection_manager.is_selected(child_path)
                self._update_node_display(child, child_path, is_selected)
                if os.path.isdir(child_path):
                    self._refresh_loaded_subtree(child)
    
    def refresh_tree(self):
        """Refresca el árbol manteniendo selecciones"""
        # Guardar estado de expansión y selecciones
        expanded_nodes = self._get_expanded_nodes()
        
        # Recargar desde la raíz
        if self.file_manager.root_path:
            self.load_directory(self.file_manager.root_path)
            
            # Restaurar expansión
            self._restore_expanded_nodes(expanded_nodes)
    
    def _get_expanded_nodes(self, node=""):
        """Obtiene lista de nodos expandidos"""
        expanded = []
        children = self.get_children(node)
        
        for child in children:
            if self.item(child, "open"):
                values = self.item(child, "values")
                if values and values[0] != "__dummy__":
                    expanded.append(values[0])
                    expanded.extend(self._get_expanded_nodes(child))
        
        return expanded
    
    def _restore_expanded_nodes(self, expanded_paths, node=""):
        """Restaura los nodos que estaban expandidos"""
        children = self.get_children(node)
        
        for child in children:
            values = self.item(child, "values")
            if values and values[0] in expanded_paths:
                self.item(child, open=True)
                # Trigger carga si no está cargado
                self._on_open(None)
                self._restore_expanded_nodes(expanded_paths, child)
    
    def _on_double_click(self, event):
        """Maneja doble click"""
        node = self.focus()
        if not node:
            return
        
        values = self.item(node, "values")
        if not values or values[0] == "__dummy__":
            return
        
        abspath = values[0]
        
        # Si es archivo, marcar/desmarcar
        if os.path.isfile(abspath):
            self.toggle_selection(node, abspath)
    
    def _create_context_menu(self):
        """Crea el menú contextual"""
        lang = self.language_manager
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(
            label=f"✓ {lang.get_text('context_mark')}", 
            command=self._context_toggle
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label=f"📋 {lang.get_text('context_copy_path')}", 
            command=self._context_copy_path
        )
        self.context_menu.add_command(
            label=f"📂 {lang.get_text('context_open_location')}", 
            command=self._context_open_location
        )
    
    def _show_context_menu(self, event):
        """Muestra el menú contextual"""
        # Seleccionar el item bajo el cursor
        item = self.identify_row(event.y)
        if item:
            self.focus(item)
            self.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _context_toggle(self):
        """Toggle desde menú contextual"""
        node = self.focus()
        if node:
            values = self.item(node, "values")
            if values and values[0] != "__dummy__":
                self.toggle_selection(node, values[0])
    
    def _context_copy_path(self):
        """Copia la ruta del item"""
        node = self.focus()
        if node:
            values = self.item(node, "values")
            if values and values[0] != "__dummy__":
                import pyperclip
                pyperclip.copy(values[0])
    
    def _context_open_location(self):
        """Abre la ubicación del archivo"""
        node = self.focus()
        if node:
            values = self.item(node, "values")
            if values and values[0] != "__dummy__":
                import subprocess
                import platform
                
                path = values[0]
                if os.path.isfile(path):
                    path = os.path.dirname(path)
                
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", path])
                else:  # Linux
                    subprocess.Popen(["xdg-open", path])
    
    def get_all_file_paths(self, node=""):
        """Obtiene todas las rutas de archivos en el árbol"""
        paths = []
        children = self.get_children(node) if node else self.get_children()
        
        for child in children:
            values = self.item(child, "values")
            if values and values[0] != "__dummy__":
                path = values[0]
                if os.path.isfile(path):
                    paths.append(path)
                elif os.path.isdir(path):
                    # Recursivo
                    paths.extend(self.get_all_file_paths(child))
        
        return paths
    
    def update_ui_language(self):
        """Actualiza los textos del menú contextual"""
        lang = self.language_manager
        self.context_menu.delete(0, tk.END)
        self.context_menu.add_command(
            label=f"✓ {lang.get_text('context_mark')}", 
            command=self._context_toggle
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label=f"📋 {lang.get_text('context_copy_path')}", 
            command=self._context_copy_path
        )
        self.context_menu.add_command(
            label=f"📂 {lang.get_text('context_open_location')}", 
            command=self._context_open_location
        )

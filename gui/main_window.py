import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from datetime import datetime

from utils import ThemeManager, ConfigManager, FileIconManager, AlertManager, LanguageManager
from core import FileManager, SelectionManager, CodeAnalyzer, ExportManager, ProjectStats
from gui.widgets import CustomToolbar, StatusBar, ThemeSelector, LanguageSelector
from gui.tree_view import TreeView
from gui.preview_window import PreviewWindow
from gui.search_dialog import SearchDialog
from gui.dashboard_window import DashboardWindow
from gui.readme_generator_dialog import ReadmeGeneratorDialog
from gui.limpmax_window import LimpMaxWindow
from utils.helpers import format_file_size
from gui.recent_folders_menu import RecentFoldersMenu
from gui.export_menu import ExportMenu
from gui.shortcuts_window import ShortcutsWindow
from gui.about_window import AboutWindow

def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
            return os.path.join(base_path, relative_path)
        except Exception:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            return os.path.join(base_path, relative_path)

class MainWindow:
    """Ventana principal de la aplicación"""
    
    def __init__(self, root, preloaded=None):
        self.root = root
        self.root.title("Code Tools ++")
        preloaded = preloaded or {}
        
        # Managers
        self.config_manager = preloaded.get("config_manager") or ConfigManager()
        self.theme_manager = preloaded.get("theme_manager") or ThemeManager(self.config_manager)
        self.language_manager = preloaded.get("language_manager") or LanguageManager(self.config_manager)
        self.icon_manager = preloaded.get("icon_manager") or FileIconManager()
        self.alert_manager = preloaded.get("alert_manager") or AlertManager()
        self.file_manager = preloaded.get("file_manager") or FileManager()
        self.selection_manager = preloaded.get("selection_manager") or SelectionManager()
        self.code_analyzer = preloaded.get("code_analyzer") or CodeAnalyzer()
        self.project_stats = preloaded.get("project_stats") or ProjectStats()
        self.export_manager = preloaded.get("export_manager") or ExportManager(self.file_manager)
        from core.ai_manager import AIManager
        
        # Estado del zoom
        self.zoom_level = 1.0
        self.base_font_size = 9
        
        # Configurar ventana
        geometry = self.config_manager.get("window_geometry", "1200x800")
        self.root.geometry(geometry)
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Agregar ícono
        try:
            icon_path = resource_path("icon.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"No se pudo cargar el ícono: {e}")

        
        # Crear interfaz
        self._create_widgets()
        self._create_menu()
        self._setup_shortcuts()
        self.apply_theme()
        self.update_ui_language()
        
        # Cargar última carpeta
        last_folder = self.config_manager.get("last_folder")
        if last_folder and os.path.exists(last_folder):
            self.load_folder(last_folder)
        
        # Timer para actualizar stats
        self._update_stats_timer()
        self.ai_manager = AIManager(self.config_manager)
        

    
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Toolbar superior
        self.toolbar = CustomToolbar(self.main_frame, self.theme_manager, self.icon_manager, self.language_manager)
        self.toolbar.pack(fill="x", pady=(5, 0))
        
        self._setup_toolbar()
        
        # Frame contenedor para tree
        content_frame = tk.Frame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tree view con scrollbars
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(side="left", fill="both", expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")
        
        # TreeView
        self.tree = TreeView(
            tree_frame,
            self.file_manager,
            self.selection_manager,
            self.icon_manager,
            self.alert_manager,
            self.theme_manager,
            self.language_manager,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        self.tree.pack(side="left", fill="both", expand=True)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Status bar
        self.status_bar = StatusBar(self.main_frame, self.theme_manager, self.language_manager)
        self.status_bar.pack(fill="x", side="bottom")
        
        # Preview window (inicialmente oculta)
        self.preview_window = PreviewWindow(
            self.root,
            self.theme_manager,
            self.file_manager,
            self.language_manager
        )
    
    def _setup_toolbar(self):
        """Configura los botones del toolbar"""
        lang = self.language_manager
        
        self.toolbar.add_button(
            "select_folder",
            lang.get_text('btn_open'),
            self._select_folder_dialog,
            icon_name="folder_open.png",
            tooltip=lang.get_text('tooltip_open')
        )
        
        # ✅ **CARPETAS RECIENTES - Botón con texto + badge**
        self.toolbar.add_button(
            "recent_folders",
            lang.get_text('btn_recent'),
            self._show_recent_menu,
            icon_name="recent.png",
            tooltip=lang.get_text('tooltip_recent'),
            icon_only=False
        )
        
        # ✅ **Agregar badge DESPUÉS (usando root.after en vez de after_idle)**
        recent = self.config_manager.get_recent_folders()
        count = len([f for f in recent if os.path.exists(f)])
        if count > 0:
            self.root.after(200, lambda: self._add_recent_badge(count))
        
        self.toolbar.add_separator()
        
        self.toolbar.add_button(
            "search",
            lang.get_text('btn_search'),
            self._open_search,
            icon_name="search.png",
            tooltip=lang.get_text('tooltip_search')
        )
        
        self.toolbar.add_button(
            "preview",
            lang.get_text('btn_preview'),
            self._toggle_preview,
            icon_name="preview.png",
            tooltip=lang.get_text('tooltip_preview')
        )
        
        self.toolbar.add_separator()
        
        self.toolbar.add_button(
            "copy",
            lang.get_text('btn_copy'),
            self._copy_selected,
            icon_name="copy.png",
            tooltip=lang.get_text('tooltip_copy')
        )
        
        self.toolbar.add_button(
            "clear_selection",
            lang.get_text('btn_clear'),
            self._clear_selection,
            icon_name="clear.png",
            tooltip=lang.get_text('tooltip_clear')
        )
        
        self.toolbar.add_button(
            "export",
            lang.get_text('btn_export'),
            self._export_menu,
            icon_name="about_feature_export.png",
            tooltip=lang.get_text('tooltip_export')
        )
        
        self.toolbar.add_separator()
        
        # ✅ NUEVO: Botón de IA
        self.toolbar.add_button(
            "ai_chat",
            lang.get_text('btn_ai'),  # ✅ Usa traducción
            self._open_ai_chat,
            icon_name="ai.gif",
            tooltip=lang.get_text('tooltip_ai')  # ✅ Usa traducción
        )
        
        self.toolbar.add_separator()
        
        self.toolbar.add_button(
            "dashboard",
            lang.get_text('btn_dashboard'),
            self._open_dashboard,
            icon_name="dashboard.png",
            tooltip=lang.get_text('tooltip_dashboard')
        )
        
        self.toolbar.add_button(
            "readme",
            lang.get_text('btn_readme'),
            self._generate_readme,
            icon_name="markdown.png",
            tooltip=lang.get_text('tooltip_readme')
        )
        
        
        self.toolbar.add_button(
            "todos",
            lang.get_text('btn_todos'),
            self._scan_todos,
            icon_name="todo.png",
            tooltip=lang.get_text('tooltip_todos')
        )

        self.toolbar.add_button(
            "limpmax",
            lang.get_text('btn_limpmax'),
            self._open_limpmax,
            icon_name="limpmax.gif",
            tooltip=lang.get_text('tooltip_limpmax')
        )
        
        self.toolbar.add_separator()
        
        self.toolbar.add_zoom_group(
            zoom_out_cmd   = self._zoom_out,
            zoom_reset_cmd = self._zoom_reset,
            zoom_in_cmd    = self._zoom_in,
            initial_text   = "100%",
            tooltip_out    = lang.get_text('tooltip_zoom_out'),
            tooltip_reset  = lang.get_text('tooltip_zoom_reset'),
            tooltip_in     = lang.get_text('tooltip_zoom_in'),
        )

        self.toolbar.add_separator()
        
        self.toolbar.add_button(
            "theme",
            lang.get_text('btn_theme'),
            self._open_theme_selector,
            icon_name="theme.png",
            tooltip=lang.get_text('tooltip_theme')
        )
        
        self.toolbar.add_button(
            "language",
            lang.get_text('btn_language'),
            self._open_language_selector,
            icon_name="language.png",
            tooltip=lang.get_text('tooltip_language')
        )
        
        self.toolbar.add_button(
            "shortcuts",
            lang.get_text('btn_shortcuts'),
            self._show_shortcuts,
            icon_name="keyboard.png",
            tooltip=lang.get_text('tooltip_shortcuts')
        )

        self.toolbar.add_button(
            "about",
            lang.get_text('btn_about'),
            self._show_about,
            icon_name="about.png",
            tooltip=lang.get_text('tooltip_about')
        )
        
        
    def _update_recent_badge(self):
        """Actualiza el badge del botón de recientes"""
        recent = self.config_manager.get_recent_folders()
        count = len([f for f in recent if os.path.exists(f)])
        
        btn = self.toolbar.buttons.get("recent_folders")
        if btn and btn.winfo_exists():
            # Eliminar badge anterior
            if hasattr(btn, '_badge') and btn._badge:
                try:
                    btn._badge.destroy()
                except:
                    pass
            
            # Crear nuevo badge si hay carpetas
            if count > 0:
                self._add_recent_badge(count)

    def _create_menu(self):
        """Crea la barra de menú"""
        lang = self.language_manager
        
        menubar = tk.Menu(self.root)
        # self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=lang.get_text('menu_file'), menu=file_menu)
        file_menu.add_command(
            label=lang.get_text('menu_open_folder'),
            command=self._select_folder_dialog,
            accelerator="Ctrl+O"
        )
        file_menu.add_separator()
        
        # Carpetas recientes
        recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label=lang.get_text('menu_recent_folders'), menu=recent_menu)
        self._populate_recent_menu(recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(
            label=lang.get_text('menu_exit'),
            command=self._on_closing,
            accelerator="Ctrl+Q"
        )
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=lang.get_text('menu_view'), menu=view_menu)
        view_menu.add_command(
            label=lang.get_text('menu_refresh'),
            command=self._refresh_tree,
            accelerator="F5"
        )
        view_menu.add_command(
            label=lang.get_text('menu_preview'),
            command=self._toggle_preview,
            accelerator="Ctrl+P"
        )
        view_menu.add_separator()
        view_menu.add_command(
            label=lang.get_text('menu_dashboard'),
            command=self._open_dashboard
        )
        
        # Menú Selección
        selection_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=lang.get_text('menu_selection'), menu=selection_menu)
        selection_menu.add_command(
            label=lang.get_text('menu_clear_selection'),
            command=self._clear_selection,
            accelerator="Ctrl+D"
        )
        selection_menu.add_separator()
        selection_menu.add_command(
            label=lang.get_text('menu_copy_selected'),
            command=self._copy_selected,
            accelerator="Ctrl+C"
        )
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=lang.get_text('menu_tools'), menu=tools_menu)
        tools_menu.add_command(
            label=lang.get_text('menu_search_files'),
            command=self._open_search,
            accelerator="Ctrl+F"
        )
        tools_menu.add_command(
            label=lang.get_text('menu_generate_readme'),
            command=self._generate_readme
        )
        tools_menu.add_command(
            label="💬 Chat con IA",  # O agrega traducción
            command=self._open_ai_chat,
            accelerator="Ctrl+I"
        )
        tools_menu.add_separator()
        tools_menu.add_command(
            label=lang.get_text('menu_scan_todos'),
            command=self._scan_todos
        )
        tools_menu.add_command(
            label=lang.get_text('menu_limpmax'),
            command=self._open_limpmax
        )
        
        # Menú Temas
        themes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=lang.get_text('menu_themes'), menu=themes_menu)
        
        for theme_key in self.theme_manager.get_theme_names():
            theme_data = self.theme_manager.get_theme(theme_key)
            themes_menu.add_command(
                label=theme_data['name'],
                command=lambda tk=theme_key: self._set_theme(tk)
            )
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=lang.get_text('menu_help'), menu=help_menu)
        help_menu.add_command(
            label=lang.get_text('menu_shortcuts'),
            command=self._show_shortcuts
        )
        help_menu.add_command(
            label=lang.get_text('menu_about'),
            command=self._show_about
        )
        
        # Guardar referencia para actualizar
        self.menubar = menubar
        self.file_menu = file_menu
        self.view_menu = view_menu
        self.selection_menu = selection_menu
        self.tools_menu = tools_menu
        self.themes_menu = themes_menu
        self.help_menu = help_menu
    
    def _setup_shortcuts(self):
        """Configura los atajos de teclado"""
        # Atajos existentes
        self.root.bind("<Control-o>", lambda e: self._select_folder_dialog())
        self.root.bind("<Control-O>", lambda e: self._select_folder_dialog())
        self.root.bind("<F5>", lambda e: self._refresh_tree())
        self.root.bind("<Control-f>", lambda e: self._open_search())
        self.root.bind("<Control-F>", lambda e: self._open_search())
        self.root.bind("<Control-p>", lambda e: self._toggle_preview())
        self.root.bind("<Control-P>", lambda e: self._toggle_preview())
        self.root.bind("<Control-c>", lambda e: self._copy_selected())
        self.root.bind("<Control-C>", lambda e: self._copy_selected())
        self.root.bind("<Control-d>", lambda e: self._clear_selection())
        self.root.bind("<Control-D>", lambda e: self._clear_selection())
        self.root.bind("<Control-q>", lambda e: self._on_closing())
        self.root.bind("<Control-Q>", lambda e: self._on_closing())
        
        # Zoom shortcuts
        self.root.bind("<Control-plus>", lambda e: self._zoom_in())
        self.root.bind("<Control-equal>", lambda e: self._zoom_in())  # For keyboards without numpad
        self.root.bind("<Control-minus>", lambda e: self._zoom_out())
        self.root.bind("<Control-0>", lambda e: self._zoom_reset())
        self.root.bind("<Control-MouseWheel>", self._on_mousewheel_zoom)
        
        # AI Chat shortcut
        self.root.bind("<Control-i>", lambda e: self._open_ai_chat())
        self.root.bind("<Control-I>", lambda e: self._open_ai_chat())
    
    def _on_mousewheel_zoom(self, event):
        """Maneja zoom con Ctrl + rueda del mouse"""
        if event.delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()

    def _zoom_in(self):
        """Aumenta el zoom"""
        if self.zoom_level < 2.5:
            self.zoom_level += 0.1
            self._apply_zoom()
            self._update_zoom_button_text()

    def _zoom_out(self):
        """Disminuye el zoom"""
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.1
            self._apply_zoom()
            self._update_zoom_button_text()

    def _zoom_reset(self):
        """Restablece el zoom"""
        self.zoom_level = 1.0
        self._apply_zoom()
        self._update_zoom_button_text()

    def _apply_zoom(self):
        """Aplica el nivel de zoom actual"""
        new_size = int(self.base_font_size * self.zoom_level)
        
        # SOLO modificar el estilo - NO el widget directamente
        style = ttk.Style()
        style.configure("Custom.Treeview", 
                    font=("Helvetica", new_size),
                    rowheight=int(25 * self.zoom_level))
        
        # Actualizar tags también
        self.tree.tag_configure("folder", font=("Helvetica", new_size, "bold"))
        self.tree.tag_configure("file", font=("Helvetica", new_size))
        self.tree.tag_configure("selected", font=("Helvetica", new_size))
        
        # Forzar redibujado
        self.tree.update_idletasks()
        
        print(f"✓ Zoom aplicado: {new_size}px ({int(self.zoom_level * 100)}%)")

    def _update_zoom_button_text(self):
        """Actualiza el texto del botón de zoom"""
        if hasattr(self.toolbar, 'buttons') and 'zoom_reset' in self.toolbar.buttons:
            percentage = int(self.zoom_level * 100)
            self.toolbar.buttons['zoom_reset'].config(text=f"{percentage}%")
    
    def _populate_recent_menu(self, menu):
        """Puebla el menú de carpetas recientes"""
        lang = self.language_manager
        recent = self.config_manager.get_recent_folders()
        
        if not recent:
            menu.add_command(label=lang.get_text('menu_empty'), state="disabled")
            return
        
        for folder in recent:
            if os.path.exists(folder):
                menu.add_command(
                    label=folder,
                    command=lambda f=folder: self.load_folder(f)
                )
    
    def _select_folder_dialog(self):
        """Diálogo para seleccionar carpeta"""
        lang = self.language_manager
        folder = filedialog.askdirectory(
            title=lang.get_text('dialog_select_folder'),
            initialdir=self.file_manager.root_path or os.path.expanduser("~")
        )
        
        if folder:
            self.load_folder(folder)
    
    def _show_recent_menu(self):
        """Muestra menú de carpetas recientes"""
        btn = self.toolbar.buttons.get("recent_folders")

        # Cerrar menu de exportar si esta abierto
        self._close_export_menu()

        # ✅ Guardar referencia al menú actual
        self._recent_menu = RecentFoldersMenu(
            parent=self.root,
            theme_manager=self.theme_manager,
            language_manager=self.language_manager,
            icon_manager=self.icon_manager,
            config_manager=self.config_manager,
            on_folder_selected=self.load_folder
        )
        self._recent_menu.show(btn)

    def _add_recent_badge(self, count):
        """Agrega badge visual al botón de recientes"""
        btn = self.toolbar.buttons.get("recent_folders")
        if not btn or not btn.winfo_exists():
            self.root.after(100, lambda: self._add_recent_badge(count))
            return
        
        if btn.winfo_width() <= 1:
            self.root.after(50, lambda: self._add_recent_badge(count))
            return
        
        if hasattr(btn, '_badge'):
            try:
                btn._badge.destroy()
            except:
                pass
        
        btn.update_idletasks()
        
        badge = tk.Label(
            btn,
            text=str(count),
            font=("Segoe UI", 8, "bold"),
            bg="#e74c3c",
            fg="#ffffff",
            padx=3,
            pady=0,
            borderwidth=0,
            relief="flat"
        )
        # ✅ CENTRADO VERTICALMENTE, a la derecha del texto
        badge.place(relx=1.0, rely=0.5, anchor="e", x=3, y=0)  
        badge.lift()
        btn._badge = badge

    def _clear_recent_folders(self):
        """Limpia el historial de carpetas recientes"""
        self.config_manager.config["recent_folders"] = []
        self.config_manager.save()
        messagebox.showinfo(
            self.language_manager.get_text('msg_success'),
            "Historial limpiado" if self.language_manager.current_language == "es" 
            else "History cleared"
        )
    
    def load_folder(self, folder_path):
        """Carga una carpeta en el árbol"""
        lang = self.language_manager
        self.config_manager.add_recent_folder(folder_path)
        self._update_recent_badge()  # ← AGREGAR
        if not os.path.exists(folder_path):
            messagebox.showerror(
                lang.get_text('msg_error'),
                f"{lang.get_text('dialog_folder_not_exist')}:\n{folder_path}"
            )
            return
        
        self.status_bar.set_message(f"{lang.get_text('status_loading')} {folder_path}...")
        self.root.update()
        
        # Cargar en tree
        self.tree.load_directory(folder_path)
        
        # Guardar en config
        self.config_manager.set("last_folder", folder_path)
        self.config_manager.add_recent_folder(folder_path)
        
        # Actualizar título
        self.root.title(f"Code Tools ++ - {os.path.basename(folder_path)}")
        
        self.status_bar.set_message(
            f"{lang.get_text('msg_folder_loaded')}: {os.path.basename(folder_path)}"
        )
        
        # Actualizar stats
        self._update_stats()
    
    def _refresh_tree(self):
        """Refresca el árbol manteniendo selecciones"""
        lang = self.language_manager
        
        if not self.file_manager.root_path:
            return
        
        self.status_bar.set_message(lang.get_text('status_refreshing'))
        self.tree.refresh_tree()
        self.status_bar.set_message(lang.get_text('status_refreshed'), 2000)
        self._update_stats()
    
    def _toggle_preview(self):
        """Muestra/oculta ventana de preview"""
        self.preview_window.toggle()
        self._update_preview()
    
    def _update_preview(self):
        """Actualiza la ventana de preview"""
        selected = self.selection_manager.get_selected_files()
        self.preview_window.update_preview(selected)
    
    def _open_search(self):
        lang = self.language_manager
        
        if not self.file_manager.root_path:
            messagebox.showwarning(
                lang.get_text('msg_warning'),
                lang.get_text('msg_no_folder')
            )
            return
        
        # *** AGREGAR VERIFICACIÓN ***
        if hasattr(self, 'search_dialog') and self.search_dialog and self.search_dialog.winfo_exists():
            self.search_dialog.lift()
            self.search_dialog.focus_set()
            return
        
        self.search_dialog = SearchDialog(
            self.root,
            self.tree,
            self.file_manager,
            self.theme_manager,
            self.language_manager
        )
    
    def _open_dashboard(self):
        """Abre ventana de dashboard"""
        # Verificar si ya existe
        if hasattr(self, 'dashboard_window') and self.dashboard_window and self.dashboard_window.winfo_exists():
            self.dashboard_window.lift()
            self.dashboard_window.focus_set()
            return
        
        # Si no existe, crearla
        dashboard = DashboardWindow(
            self.root,
            self.theme_manager,
            self.file_manager,
            self.code_analyzer,
            self.project_stats,
            self.language_manager
        )
        
        # Guardar referencia
        self.dashboard_window = dashboard
        
        # *** CAMBIAR A ESTO ***
        selected = self.selection_manager.get_selected_files()  # ← ESTE ES EL CORRECTO
        if selected:
            dashboard.update_dashboard(selected)
        
        dashboard.deiconify()
    
    def _generate_readme(self):
        lang = self.language_manager
        
        if not self.file_manager.root_path:
            messagebox.showwarning(
                lang.get_text('msg_warning'),
                lang.get_text('msg_no_folder')
            )
            return
        
        # *** AGREGAR ESTO ***
        if hasattr(self, 'readme_dialog') and self.readme_dialog and self.readme_dialog.winfo_exists():
            self.readme_dialog.lift()
            self.readme_dialog.focus_set()
            return
        
        self.readme_dialog = ReadmeGeneratorDialog(
            self.root,
            self.theme_manager,
            self.file_manager,
            self.project_stats,
            self.language_manager
        )
    
    def _copy_selected(self):
        """Copia archivos seleccionados al portapapeles"""
        lang = self.language_manager
        selected = self.selection_manager.get_selected_files()
        
        if not selected:
            messagebox.showwarning(
                lang.get_text('msg_warning'),
                lang.get_text('msg_no_selection')
            )
            return
        
        # Exportar con contenido
        self.export_manager.export_to_clipboard(selected, use_relative_paths=True)
        
        self.status_bar.set_message(
            f"{len(selected)} {lang.get_text('status_copied')}",
            3000
        )
        messagebox.showinfo(
            lang.get_text('msg_success'),
            f"{len(selected)} {lang.get_text('msg_copied')}"
        )
    
    def _export_menu(self):
        """Muestra menú de opciones de exportación"""
        lang = self.language_manager
        selected = self.selection_manager.get_selected_files()

        if not selected:
            messagebox.showwarning(
                lang.get_text('msg_warning'),
                lang.get_text('msg_no_selection')
            )
            return

        # Cerrar menu de recientes si esta abierto
        if hasattr(self, '_recent_menu') and self._recent_menu:
            try:
                if self._recent_menu.menu_window and self._recent_menu.menu_window.winfo_exists():
                    self._recent_menu.menu_window.destroy()
            except:
                pass

        btn = self.toolbar.buttons.get("export")
        self._export_selected_cache = selected
        self._export_menu_popup = ExportMenu(
            parent=self.root,
            theme_manager=self.theme_manager,
            language_manager=self.language_manager,
            icon_manager=self.icon_manager,
            on_option_selected=self._on_export_option_selected
        )
        self._export_menu_popup.show(btn)

    def _on_export_option_selected(self, action):
        """Ejecuta la accion elegida en el menu de exportar."""
        files = getattr(self, "_export_selected_cache", None) or self.selection_manager.get_selected_files()
        if not files:
            return

        actions = {
            "with_content": self._export_with_content,
            "paths_only": self._export_paths_only,
            "tree_structure": self._export_tree_structure,
            "for_llm": self._export_for_llm,
            "save_file": self._export_to_file,
        }
        callback = actions.get(action)
        if callback:
            callback(files)

    def _close_export_menu(self):
        if hasattr(self, '_export_menu_popup') and self._export_menu_popup:
            try:
                if self._export_menu_popup.menu_window and self._export_menu_popup.menu_window.winfo_exists():
                    self._export_menu_popup.menu_window.destroy()
            except:
                pass
    
    def _export_with_content(self, files):
        """Exporta con contenido"""
        self.export_manager.export_to_clipboard(files, use_relative_paths=True)
        self.status_bar.set_message(
            self.language_manager.get_text('status_copied'),
            3000
        )
    
    def _export_paths_only(self, files):
        """Exporta solo rutas"""
        self.export_manager.export_paths_only(files, use_relative_paths=True)
        self.status_bar.set_message(
            self.language_manager.get_text('status_copied'),
            3000
        )
    
    def _export_tree_structure(self, files):
        """Exporta estructura de árbol"""
        self.export_manager.export_with_tree_structure(files)
        self.status_bar.set_message(
            self.language_manager.get_text('status_copied'),
            3000
        )
    
    def _export_for_llm(self, files):
        """Exporta para LLM"""
        self.export_manager.export_for_llm(files)
        self.status_bar.set_message(
            self.language_manager.get_text('status_copied'),
            3000
        )
    
    def _export_to_file(self, files):
        """Exporta a archivo"""
        lang = self.language_manager
        default_name = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        initial_dir = self.file_manager.root_path or os.path.expanduser("~")
        filepath = filedialog.asksaveasfilename(
            title=lang.get_text('export_save_file'),
            defaultextension=".md",
            initialdir=initial_dir,
            initialfile=default_name,
            filetypes=[
                ("Markdown", "*.md"),
                ("Text", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if filepath:
            success = self.export_manager.export_to_file(files, filepath, 'markdown')
            if success:
                messagebox.showinfo(
                    lang.get_text('msg_success'),
                    f"{lang.get_text('msg_exported')}:\n{filepath}"
                )
            else:
                messagebox.showerror(
                    lang.get_text('msg_error'),
                    lang.get_text('msg_cannot_export')
                )
    
    def _clear_selection(self):
        """Limpia todas las selecciones"""
        self.selection_manager.clear_selection()
        self._refresh_tree()
        self.status_bar.set_message(
            self.language_manager.get_text('status_cleared'),
            2000
        )
    
    def _scan_todos(self):
        """Abre el Dashboard directamente en la pestaña de TODOs."""
        lang = self.language_manager
        if not self.file_manager.root_path:
            messagebox.showwarning(
                lang.get_text('msg_warning'),
                lang.get_text('msg_no_folder')
            )
            return

        if hasattr(self, 'dashboard_window') and self.dashboard_window \
                and self.dashboard_window.winfo_exists():
            self.dashboard_window.lift()
            self.dashboard_window.focus_set()
            self.dashboard_window._switch_tab(1)
            return

        dashboard = DashboardWindow(
            self.root,
            self.theme_manager,
            self.file_manager,
            self.code_analyzer,
            self.project_stats,
            self.language_manager
        )
        self.dashboard_window = dashboard

        selected = self.selection_manager.get_selected_files()
        if selected:
            dashboard.update_dashboard(selected)

        dashboard._switch_tab(1)
    
    def _scan_duplicates(self):
        """Abre el Dashboard directamente en la pestaña de Duplicados."""
        lang = self.language_manager
        if not self.file_manager.root_path:
            messagebox.showwarning(
                lang.get_text('msg_warning'),
                lang.get_text('msg_no_folder')
            )
            return

        if hasattr(self, 'dashboard_window') and self.dashboard_window \
                and self.dashboard_window.winfo_exists():
            self.dashboard_window.lift()
            self.dashboard_window.focus_set()
            self.dashboard_window._switch_tab(2)
            return

        dashboard = DashboardWindow(
            self.root,
            self.theme_manager,
            self.file_manager,
            self.code_analyzer,
            self.project_stats,
            self.language_manager
        )
        self.dashboard_window = dashboard

        selected = self.selection_manager.get_selected_files()
        if selected:
            dashboard.update_dashboard(selected)

        dashboard._switch_tab(2)

    def _open_limpmax(self):
        if hasattr(self, 'limpmax_window') and self.limpmax_window and self.limpmax_window.winfo_exists():
            self.limpmax_window.lift()
            self.limpmax_window.focus_set()
            return
        self.limpmax_window = LimpMaxWindow(
            self.root,
            self.theme_manager,
            self.language_manager
        )
    
    def _open_theme_selector(self):
        """Abre selector de temas"""
        if hasattr(self, '_theme_selector') and self._theme_selector and self._theme_selector.winfo_exists():
            self._theme_selector.lift()
            self._theme_selector.focus_set()
            return
        self._theme_selector = ThemeSelector(
            self.root,
            self.theme_manager,
            self.language_manager,
            self.apply_theme
        )

    def _open_language_selector(self):
        if hasattr(self, '_lang_selector') and self._lang_selector and self._lang_selector.winfo_exists():
            self._lang_selector.lift()
            self._lang_selector.focus_set()
            return
        self._lang_selector = LanguageSelector(
            self.root,
            self.language_manager,
            self.theme_manager,
            self.update_ui_language
        )
    
    def _set_theme(self, theme_key):
        """Cambia el tema"""
        self.theme_manager.set_theme(theme_key)
        self.apply_theme()
    
    def apply_theme(self):
        """Aplica el tema actual a toda la interfaz"""
        theme = self.theme_manager.get_theme()
        
        # Ventana principal
        self.root.configure(bg=theme['bg'])
        self.main_frame.configure(bg=theme['bg'])
        
        # Toolbar y status bar
        self.toolbar.apply_theme()
        self.status_bar.apply_theme()
        
        # Tree view
        self.tree.apply_theme()
        
        # Preview window
        if hasattr(self, 'preview_window'):
            self.preview_window.apply_theme()
    
    def update_ui_language(self):
        """Actualiza todos los textos de la interfaz"""
        lang = self.language_manager
        
        # ✅ AGREGAR AL INICIO: Cerrar menú de recientes si está abierto
        if hasattr(self, '_recent_menu') and self._recent_menu:
            try:
                if self._recent_menu.menu_window and self._recent_menu.menu_window.winfo_exists():
                    self._recent_menu.menu_window.destroy()
            except:
                pass

        self._close_export_menu()
        
        # Recrear menú
        self._create_menu()
        
        # Recrear toolbar usando reset() seguro
        self.toolbar.reset()
        self._setup_toolbar()
        self.toolbar.apply_theme()
        
        # Actualizar status bar
        self.status_bar.update_ui_language()
        
        # Actualizar tree
        self.tree.update_ui_language()
        
        # Refrescar interfaz
        self.root.update_idletasks()
    
    def _update_stats(self):
        """Actualiza las estadísticas en la barra de estado"""
        if not self.file_manager.root_path:
            return
        
        # Obtener todos los archivos visibles en el árbol
        all_files = self.tree.get_all_file_paths()
        
        # Archivos seleccionados
        selected_files = self.selection_manager.get_selected_files()
        
        # Calcular stats de seleccionados
        if selected_files:
            stats = self.project_stats.calculate_stats(selected_files)
            
            self.status_bar.update_all({
                'total_files': len(all_files),
                'selected_files': len(selected_files),
                'total_lines': stats['total_lines'],
                'size_formatted': format_file_size(stats['total_size'])
            })
        else:
            self.status_bar.update_all({
                'total_files': len(all_files),
                'selected_files': 0,
                'total_lines': 0,
                'size_formatted': '0 B'
            })
        
        # *** CAMBIAR ESTA LÍNEA ***
        # Antes era:
        # if self.preview_window.winfo_viewable():
        
        # Ahora:
        if hasattr(self, 'preview_window') and self.preview_window and self.preview_window.winfo_exists() and self.preview_window.winfo_viewable():
            self._update_preview()
    
    def _update_stats_timer(self):
        """Timer para actualizar stats periódicamente"""
        # *** AGREGAR VERIFICACIÓN ***
        if hasattr(self, 'file_manager') and self.file_manager:
            self._update_stats()
        
        # Programar siguiente actualización
        self.root.after(2000, self._update_stats_timer)
    
    def _show_shortcuts(self):
        """Abre ventana de atajos de teclado."""
        if hasattr(self, '_shortcuts_window') and self._shortcuts_window \
                and self._shortcuts_window.winfo_exists():
            self._shortcuts_window.lift()
            self._shortcuts_window.focus_set()
            return
        self._shortcuts_window = ShortcutsWindow(
            self.root,
            self.theme_manager,
            self.language_manager
        )
    
    def _show_about(self):
        """Abre ventana Acerca de."""
        if hasattr(self, '_about_window') and self._about_window \
                and self._about_window.winfo_exists():
            self._about_window.lift()
            self._about_window.focus_set()
            return
        self._about_window = AboutWindow(
            self.root,
            self.theme_manager,
            self.language_manager
        )
    
    def _open_ai_chat(self):
        """Abre ventana de chat con IA"""
        from gui.ai_window import AIWindow
        
        lang = self.language_manager
        
        # Verificar si ya existe la ventana
        if hasattr(self, 'ai_window') and self.ai_window and self.ai_window.winfo_exists():
            self.ai_window.lift()
            self.ai_window.focus_set()
            return
        
        # Crear nueva ventana
        self.ai_window = AIWindow(
            parent=self.root,
            theme_manager=self.theme_manager,
            language_manager=self.language_manager,
            ai_manager=self.ai_manager,
            file_manager=self.file_manager,
            selection_manager=self.selection_manager
        )
    
    def _on_closing(self):
        """Maneja el cierre de la aplicación"""
        # Guardar geometría
        geometry = self.root.geometry()
        self.config_manager.set("window_geometry", geometry)
        
        # Cerrar
        self.root.destroy()

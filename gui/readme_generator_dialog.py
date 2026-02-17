import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import re
import unicodedata
import markdown2
import tkinterweb
from gui.components import CustomToplevel
from utils.helpers import resource_path
# Silenciar errores de tkinterweb
import io
import contextlib

@contextlib.contextmanager
def suppress_tkinterweb_errors():
    """Suprime los mensajes de error de tkinterweb"""
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    try:
        yield
    finally:
        sys.stderr = old_stderr

class ReadmeGeneratorDialog(CustomToplevel):
    """Generador automÃ¡tico de README.md - VersiÃ³n Profesional"""
    
    def __init__(self, parent, theme_manager, file_manager, project_stats, language_manager):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title=language_manager.get_text("readme_title"),
            size="1000x750",
            min_size=(900, 650),
            max_size=(1400, 900)
        )
        
        self.file_manager = file_manager
        self.project_stats = project_stats
        self.language_manager = language_manager
        
        # Estado
        self._preview_mode = "markdown"
        
        # Sobrescribir botÃ³n cerrar
        self.close_button.bind("<Button-1>", lambda e: self.destroy())
        
        self._icons = {}
        self._load_icons()
        self._create_widgets()
        self.apply_theme()
        self.language_manager.subscribe(self.update_ui_language)
        
    def update_ui_language(self):
        """Actualiza todos los textos del diÃ¡logo"""
        lang = self.language_manager
        try:
            # TÃ­tulo
            self.title_label.configure(text=lang.get_text("readme_title"))
            
            # ACTUALIZAR LABELS
            if hasattr(self, 'lbl_project_name'):
                self.lbl_project_name.configure(text=lang.get_text("readme_project_name"))
            
            if hasattr(self, 'lbl_description'):
                self.lbl_description.configure(text=lang.get_text("readme_description"))
            
            if hasattr(self, 'lbl_author_github'):
                self.lbl_author_github.configure(text=lang.get_text("readme_author_github"))
            
            if hasattr(self, 'lbl_license'):
                self.lbl_license.configure(text=lang.get_text("readme_license"))
            
            if hasattr(self, 'lbl_sections'):
                self.lbl_sections.configure(text=lang.get_text("readme_sections"))
            
            if hasattr(self, 'lbl_structure_opts'):
                self.lbl_structure_opts.configure(text=lang.get_text("readme_structure_options"))
            
            if hasattr(self, 'lbl_depth'):
                self.lbl_depth.configure(text=lang.get_text("readme_depth"))
            
            if hasattr(self, 'lbl_threshold'):
                self.lbl_threshold.configure(text=f"  {lang.get_text('readme_threshold')}")
            
            if hasattr(self, 'lbl_files_label'):
                self.lbl_files_label.configure(text=lang.get_text("readme_files_label"))
            
            # ACTUALIZAR CHECKBOXES
            if hasattr(self, 'chk_badges'):
                self.chk_badges.configure(text=lang.get_text("readme_badges"))
            
            if hasattr(self, 'chk_toc'):
                self.chk_toc.configure(text=lang.get_text("readme_toc"))
            
            if hasattr(self, 'chk_structure'):
                self.chk_structure.configure(text=lang.get_text("readme_structure"))
            
            if hasattr(self, 'chk_stats'):
                self.chk_stats.configure(text=lang.get_text("readme_stats"))
            
            if hasattr(self, 'chk_installation'):
                self.chk_installation.configure(text=lang.get_text("readme_installation"))
            
            if hasattr(self, 'chk_usage'):
                self.chk_usage.configure(text=lang.get_text("readme_usage"))
            
            if hasattr(self, 'chk_contributing'):
                self.chk_contributing.configure(text=lang.get_text("readme_contributing"))
            
            if hasattr(self, 'chk_license_section'):
                self.chk_license_section.configure(text=lang.get_text("readme_license_section"))
            
            if hasattr(self, 'chk_contact'):
                self.chk_contact.configure(text=lang.get_text("readme_contact"))
            
            if hasattr(self, 'chk_collapse_large'):
                self.chk_collapse_large.configure(text=lang.get_text("readme_collapse_large"))
            
            # ACTUALIZAR BOTONES
            if hasattr(self, 'btn_generate'):
                self.btn_generate.configure(text=f"  {lang.get_text('readme_generate_btn')}")
            
            if hasattr(self, 'btn_md_mode'):
                self.btn_md_mode.configure(text=f"  {lang.get_text('readme_markdown_view')}")
            
            if hasattr(self, 'btn_render_mode'):
                self.btn_render_mode.configure(text=f"  {lang.get_text('readme_rendered_view')}")
            
            if hasattr(self, 'btn_save'):
                self.btn_save.configure(text=f"  {lang.get_text('readme_save_btn')}")
            
            if hasattr(self, 'btn_copy'):
                self.btn_copy.configure(text=f"  {lang.get_text('readme_copy')}")
            
            # ACTUALIZAR CARDS
            if hasattr(self, 'config_card') and hasattr(self.config_card, '_title_lbl'):
                self.config_card._title_lbl.configure(text=lang.get_text("readme_configuration"))
            
            if hasattr(self, 'preview_card') and hasattr(self.preview_card, '_title_lbl'):
                self.preview_card._title_lbl.configure(text=lang.get_text("readme_preview"))

            # Regenerar markdown para reflejar idioma en tiempo real
            if hasattr(self, "preview_text"):
                self._generate_preview()
            
        except Exception as e:
            print(f"Error updating readme language: {e}")
    
    def _load_icons(self):
        """Carga los iconos necesarios con fondo del botÃ³n"""
        try:
            from PIL import Image, ImageTk
            icon_dir = resource_path("assets/icons")
            t = self.theme_manager.get_theme()
            btn_bg = t["button_bg"]
            sec_bg = t["secondary_bg"]
            
            def _rgb(h):
                h = h.lstrip("#")
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            
            def load(name, size=(16, 16), bg_color=None):
                path = os.path.join(icon_dir, name)
                if not os.path.exists(path):
                    return None
                img = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                
                if bg_color:
                    bg_img = Image.new("RGBA", img.size, _rgb(bg_color) + (255,))
                    bg_img.paste(img, mask=img.split()[3])
                    return ImageTk.PhotoImage(bg_img.convert("RGB"))
                else:
                    return ImageTk.PhotoImage(img)
            
            self._icons = {
                "markdown": load("markdown.png", (20, 20), sec_bg),
                "settings": load("settings.png", (16, 16), sec_bg),
                "save": load("save.png", (16, 16), btn_bg),
                "copy": load("copy.png", (16, 16), btn_bg),
                "refresh": load("refresh.png", (16, 16), btn_bg),
                "preview": load("preview.png", (16, 16), btn_bg),
                "code": load("code.png", (16, 16), btn_bg),
                "close": load("close.png", (16, 16), sec_bg),
            }
        except Exception as e:
            print(f"Error cargando iconos: {e}")
            self._icons = {}
    
    def _create_widgets(self):
        """Crea la interfaz moderna"""
        lang = self.language_manager
        
        if self._icons.get("markdown"):
            self.add_title_icon(self._icons["markdown"])
        
        content_frame = tk.Frame(self.content_frame)
        content_frame.pack(fill="both", expand=True, padx=14, pady=14)
        
        left_col = tk.Frame(content_frame)
        left_col.pack(side="left", fill="both", expand=False, padx=(0, 7))
        left_col.configure(width=380)
        left_col.pack_propagate(False)
        
        right_col = tk.Frame(content_frame)
        right_col.pack(side="right", fill="both", expand=True, padx=(7, 0))
        
        # LEFT COLUMN - Config card
        self.config_card = self._card(left_col, lang.get_text("readme_configuration"), "settings")
        self.config_card.pack(fill="both", expand=True)

        canvas_config = tk.Canvas(self.config_card, bd=0, highlightthickness=0)
        scrollbar_config = tk.Scrollbar(self.config_card, orient="vertical", command=canvas_config.yview, width=8)
        scrollable_config = tk.Frame(canvas_config)

        def _scroll_config(event):
            try:
                if canvas_config.winfo_exists():
                    delta = -1 if event.num == 4 else 1 if event.num == 5 else int(-1 * (event.delta / 120))
                    canvas_config.yview_scroll(delta, "units")
            except:
                pass
            return "break"

        def _bind_scroll_recursive(widget):
            widget.bind("<MouseWheel>", _scroll_config)
            widget.bind("<Button-4>", _scroll_config)
            widget.bind("<Button-5>", _scroll_config)
            for child in widget.winfo_children():
                _bind_scroll_recursive(child)

        def _on_configure(event):
            canvas_config.configure(scrollregion=canvas_config.bbox("all"))
            _bind_scroll_recursive(scrollable_config)

        scrollable_config.bind("<Configure>", _on_configure)
        canvas_config.create_window((0, 0), window=scrollable_config, anchor="nw")
        canvas_config.configure(yscrollcommand=scrollbar_config.set)

        scrollbar_config.pack(side="right", fill="y", padx=(0, 2), pady=2)
        canvas_config.pack(side="left", fill="both", expand=True, padx=2, pady=2)

        self._canvas_config = canvas_config
        self._scrollbar_config = scrollbar_config

        config_content = tk.Frame(scrollable_config)
        config_content.pack(fill="x", padx=12, pady=12)
        
        # Project name
        self.lbl_project_name = tk.Label(config_content, text=lang.get_text("readme_project_name"), font=("Segoe UI", 9, "bold"))
        self.lbl_project_name.pack(anchor="w", pady=(0, 4))
        
        self.project_name_entry = tk.Entry(config_content, font=("Segoe UI", 10))
        self.project_name_entry.pack(fill="x", pady=(0, 12))

        if self.file_manager.root_path:
            default_name = os.path.basename(self.file_manager.root_path)
            self.project_name_entry.insert(0, default_name)

        # Description
        self.lbl_description = tk.Label(config_content, text=lang.get_text("readme_description"), font=("Segoe UI", 9, "bold"))
        self.lbl_description.pack(anchor="w", pady=(0, 4))

        desc_frame = tk.Frame(config_content, bd=1, relief="solid")
        desc_frame.pack(fill="x", pady=(0, 12))
        self._desc_frame = desc_frame

        self.description_text = tk.Text(desc_frame, height=3, font=("Segoe UI", 9), bd=0, relief="flat")
        self.description_text.pack(fill="x", padx=4, pady=4)

        # Author / GitHub
        self.lbl_author_github = tk.Label(config_content, text=lang.get_text("readme_author_github"), font=("Segoe UI", 9, "bold"))
        self.lbl_author_github.pack(anchor="w", pady=(0, 4))

        author_frame = tk.Frame(config_content)
        author_frame.pack(fill="x", pady=(0, 6))

        self.author_entry = tk.Entry(author_frame, font=("Segoe UI", 9))
        self.author_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.author_entry.insert(0, lang.get_text("readme_default_author"))

        self.github_entry = tk.Entry(author_frame, font=("Segoe UI", 9))
        self.github_entry.pack(side="left", fill="x", expand=True)
        self.github_entry.insert(0, lang.get_text("readme_default_github"))

        # License
        self.lbl_license = tk.Label(config_content, text=lang.get_text("readme_license"), font=("Segoe UI", 9, "bold"))
        self.lbl_license.pack(anchor="w", pady=(12, 4))

        license_frame = tk.Frame(config_content)
        license_frame.pack(fill="x", pady=(0, 12))

        self.license_var = tk.StringVar(value="MIT")
        licenses = ["MIT", "Apache 2.0", "GPL v3", "BSD 3-Clause", "Unlicense", "Otra"]

        for lic in licenses[:3]:
            tk.Radiobutton(
                license_frame, text=lic, variable=self.license_var,
                value=lic, font=("Segoe UI", 8)
            ).pack(side="left", padx=(0, 8))

        # Sections
        self.lbl_sections = tk.Label(config_content, text=lang.get_text("readme_sections"), font=("Segoe UI", 9, "bold"))
        self.lbl_sections.pack(anchor="w", pady=(0, 4))

        sections_frame = tk.Frame(config_content)
        sections_frame.pack(fill="x", pady=(0, 12))

        self.include_badges = tk.BooleanVar(value=True)
        self.chk_badges = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_badges"),
            variable=self.include_badges, font=("Segoe UI", 9)
        )
        self.chk_badges.pack(anchor="w", pady=2)

        self.include_toc = tk.BooleanVar(value=True)
        self.chk_toc = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_toc"),
            variable=self.include_toc, font=("Segoe UI", 9)
        )
        self.chk_toc.pack(anchor="w", pady=2)

        self.include_structure = tk.BooleanVar(value=True)
        self.chk_structure = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_structure"),
            variable=self.include_structure, font=("Segoe UI", 9)
        )
        self.chk_structure.pack(anchor="w", pady=2)

        self.include_stats = tk.BooleanVar(value=True)
        self.chk_stats = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_stats"),
            variable=self.include_stats, font=("Segoe UI", 9)
        )
        self.chk_stats.pack(anchor="w", pady=2)

        self.include_installation = tk.BooleanVar(value=True)
        self.chk_installation = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_installation"),
            variable=self.include_installation, font=("Segoe UI", 9)
        )
        self.chk_installation.pack(anchor="w", pady=2)

        self.include_usage = tk.BooleanVar(value=True)
        self.chk_usage = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_usage"),
            variable=self.include_usage, font=("Segoe UI", 9)
        )
        self.chk_usage.pack(anchor="w", pady=2)

        self.include_contributing = tk.BooleanVar(value=True)
        self.chk_contributing = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_contributing"),
            variable=self.include_contributing, font=("Segoe UI", 9)
        )
        self.chk_contributing.pack(anchor="w", pady=2)

        self.include_license_section = tk.BooleanVar(value=True)
        self.chk_license_section = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_license_section"),
            variable=self.include_license_section, font=("Segoe UI", 9)
        )
        self.chk_license_section.pack(anchor="w", pady=2)

        self.include_contact = tk.BooleanVar(value=True)
        self.chk_contact = tk.Checkbutton(
            sections_frame, text=lang.get_text("readme_contact"),
            variable=self.include_contact, font=("Segoe UI", 9)
        )
        self.chk_contact.pack(anchor="w", pady=2)

        # Structure options
        self.lbl_structure_opts = tk.Label(config_content, text=lang.get_text("readme_structure_options"), font=("Segoe UI", 9, "bold"))
        self.lbl_structure_opts.pack(anchor="w", pady=(0, 4))

        structure_opts = tk.Frame(config_content)
        structure_opts.pack(fill="x", pady=(0, 12))

        depth_frame = tk.Frame(structure_opts)
        depth_frame.pack(fill="x", pady=(0, 6))

        self.lbl_depth = tk.Label(depth_frame, text=lang.get_text("readme_depth"), font=("Segoe UI", 9))
        self.lbl_depth.pack(side="left", padx=(0, 6))

        self.depth_var = tk.IntVar(value=3)
        depth_spin = tk.Spinbox(
            depth_frame, from_=1, to=10, textvariable=self.depth_var,
            width=5, font=("Segoe UI", 9)
        )
        depth_spin.pack(side="left")

        self.collapse_large_dirs = tk.BooleanVar(value=True)
        self.chk_collapse_large = tk.Checkbutton(
            structure_opts, text=lang.get_text("readme_collapse_large"),
            variable=self.collapse_large_dirs, font=("Segoe UI", 9)
        )
        self.chk_collapse_large.pack(anchor="w", pady=2)

        self.collapse_threshold = tk.IntVar(value=10)
        threshold_frame = tk.Frame(structure_opts)
        threshold_frame.pack(fill="x", pady=(0, 12))

        self.lbl_threshold = tk.Label(threshold_frame, text=f"  {lang.get_text('readme_threshold')}", font=("Segoe UI", 8))
        self.lbl_threshold.pack(side="left", padx=(0, 4))
        
        threshold_spin = tk.Spinbox(
            threshold_frame, from_=5, to=50, textvariable=self.collapse_threshold,
            width=5, font=("Segoe UI", 8)
        )
        threshold_spin.pack(side="left")
        
        self.lbl_files_label = tk.Label(threshold_frame, text=lang.get_text("readme_files_label"), font=("Segoe UI", 8))
        self.lbl_files_label.pack(side="left", padx=(4, 0))

        # Generate button
        btn_frame = tk.Frame(config_content)
        btn_frame.pack(fill="x", pady=(12, 0))
        
        self.btn_generate = self._create_button(btn_frame, f"  {lang.get_text('readme_generate_btn')}", "refresh", self._generate_preview, full_width=False)
        self.btn_generate.pack(anchor="center")
        
        # RIGHT COLUMN - Preview card
        self.preview_card = self._card(right_col, lang.get_text("readme_preview"), "markdown")
        self.preview_card.pack(fill="both", expand=True)
        
        toggle_frame = tk.Frame(self.preview_card)
        toggle_frame.pack(fill="x", padx=8, pady=6)
        
        self.btn_md_mode = self._create_button(toggle_frame, f"  {lang.get_text('readme_markdown_view')}", "code", lambda: self._set_preview_mode("markdown"))
        self.btn_md_mode.pack(side="left", padx=(0, 4))
        
        self.btn_render_mode = self._create_button(toggle_frame, f"  {lang.get_text('readme_rendered_view')}", "preview", lambda: self._set_preview_mode("rendered"))
        self.btn_render_mode.pack(side="left")
        
        preview_content = tk.Frame(self.preview_card)
        preview_content.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.markdown_frame = tk.Frame(preview_content, bd=0)
        text_frame = tk.Frame(self.markdown_frame, bd=0)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", width=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)
        
        self.preview_text = tk.Text(
            text_frame,
            font=("Consolas", 9),
            wrap="word",
            bd=0,
            relief="flat",
            yscrollcommand=scrollbar.set
        )
        self.preview_text.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.config(command=self.preview_text.yview)
        self._scrollbar = scrollbar
        
        self.rendered_frame = tk.Frame(preview_content, bd=0)
        
        try:
            from tkinterweb import HtmlFrame
            self.html_view = HtmlFrame(self.rendered_frame, messages_enabled=False)
            self.html_view.pack(fill="both", expand=True, padx=2, pady=2)
            self._has_html_view = True
        except ImportError:
            render_text_frame = tk.Frame(self.rendered_frame, bd=0)
            render_text_frame.pack(fill="both", expand=True)
            
            render_scrollbar = tk.Scrollbar(render_text_frame, orient="vertical", width=8)
            render_scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)
            
            self.html_view = tk.Text(
                render_text_frame,
                font=("Segoe UI", 10),
                wrap="word",
                bd=0,
                relief="flat",
                yscrollcommand=render_scrollbar.set
            )
            self.html_view.pack(side="left", fill="both", expand=True, padx=2, pady=2)
            render_scrollbar.config(command=self.html_view.yview)
            self._has_html_view = False
        
        self.markdown_frame.pack(fill="both", expand=True)
        
        # Bottom buttons
        sep2 = tk.Frame(self.content_frame, height=1)
        sep2.pack(fill="x")
        self._sep2 = sep2

        bottom_bar = tk.Frame(self.content_frame, height=50)
        bottom_bar.pack(fill="x", padx=14, pady=10)
        
        self.btn_save = self._create_button(bottom_bar, f"  {lang.get_text('readme_save_btn')}", "save", self._save_readme)
        self.btn_save.pack(side="left", padx=(0, 6))
        
        self.btn_copy = self._create_button(bottom_bar, f"  {lang.get_text('readme_copy')}", "copy", self._copy_to_clipboard)
        self.btn_copy.pack(side="left")
        
        self.after(100, self._generate_preview)
    
    def _set_preview_mode(self, mode):
        """Cambia entre vista markdown y renderizada"""
        self._preview_mode = mode
        
        if mode == "markdown":
            self.rendered_frame.pack_forget()
            self.markdown_frame.pack(fill="both", expand=True)
        else:
            self.markdown_frame.pack_forget()
            self.rendered_frame.pack(fill="both", expand=True)
            self._render_preview()
    
    def _render_preview(self):
        """Renderiza el markdown con formato bÃ¡sico"""
        content = self.preview_text.get("1.0", tk.END)
        
        if self._has_html_view:
            try:
                emoji_map = {
                    'ðŸ“‹': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f4cb.png" alt="ðŸ“‹" style="width:18px;height:18px;vertical-align:middle;">',
                    'ðŸš€': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f680.png" alt="ðŸš€" style="width:18px;height:18px;vertical-align:middle;">',
                    'ðŸ“': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f4c1.png" alt="ðŸ“" style="width:18px;height:18px;vertical-align:middle;">',
                    'ðŸ“Š': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f4ca.png" alt="ðŸ“Š" style="width:18px;height:18px;vertical-align:middle;">',
                    'ðŸ”§': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f527.png" alt="ðŸ”§" style="width:18px;height:18px;vertical-align:middle;">',
                    'ðŸ’»': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f4bb.png" alt="ðŸ’»" style="width:18px;height:18px;vertical-align:middle;">',
                    'ðŸ¤': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f91d.png" alt="ðŸ¤" style="width:18px;height:18px;vertical-align:middle;">',
                    'ðŸ“': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f4dd.png" alt="ðŸ“" style="width:18px;height:18px;vertical-align:middle;">',
                    'ðŸ“§': '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f4e7.png" alt="ðŸ“§" style="width:18px;height:18px;vertical-align:middle;">',
                }
                
                processed_content = content
                for emoji, img_tag in emoji_map.items():
                    processed_content = processed_content.replace(emoji, img_tag)
                
                html = markdown2.markdown(processed_content, extras=["fenced-code-blocks", "tables"])
                t = self.theme_manager.get_theme()
                styled_html = f"""
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                            background-color: {t['tree_bg']};
                            color: {t['tree_fg']};
                            padding: 16px;
                            line-height: 1.6;
                        }}
                        h1, h2, h3 {{ 
                            color: {t['accent']}; 
                            border-bottom: 2px solid {t['border']};
                            padding-bottom: 8px;
                            margin-top: 24px;
                        }}
                        h1 {{ font-size: 2em; }}
                        h2 {{ font-size: 1.5em; }}
                        h3 {{ font-size: 1.2em; }}
                        code {{
                            background-color: {t['secondary_bg']};
                            padding: 2px 6px;
                            border-radius: 3px;
                            font-family: 'Consolas', 'Courier New', monospace;
                        }}
                        pre {{
                            background-color: {t['secondary_bg']};
                            padding: 12px;
                            border-radius: 6px;
                            overflow-x: auto;
                            border: 1px solid {t['border']};
                        }}
                        pre code {{
                            background: none;
                            padding: 0;
                        }}
                        a {{ 
                            color: {t['accent']}; 
                            text-decoration: none; 
                        }}
                        a:hover {{ text-decoration: underline; }}
                        img {{
                            max-width: 100%;
                            height: auto;
                            display: inline-block;
                            vertical-align: middle;
                            margin: 2px;
                        }}
                        ul, ol {{
                            padding-left: 20px;
                        }}
                        li {{
                            margin: 4px 0;
                        }}
                        hr {{
                            border: none;
                            border-top: 2px solid {t['border']};
                            margin: 20px 0;
                        }}
                        blockquote {{
                            border-left: 4px solid {t['accent']};
                            padding-left: 16px;
                            margin: 16px 0;
                            color: {t['tree_fg']};
                            opacity: 0.8;
                        }}
                    </style>
                </head>
                <body>{html}</body>
                </html>
                """
                with suppress_tkinterweb_errors():
                    self.html_view.load_html(styled_html)
            except:
                pass
        else:
            self.html_view.configure(state="normal")
            self.html_view.delete("1.0", tk.END)
            
            t = self.theme_manager.get_theme()
            
            self.html_view.tag_configure("h1", font=("Segoe UI", 18, "bold"), foreground=t["accent"])
            self.html_view.tag_configure("h2", font=("Segoe UI", 14, "bold"), foreground=t["accent"])
            self.html_view.tag_configure("h3", font=("Segoe UI", 12, "bold"), foreground=t["accent"])
            self.html_view.tag_configure("code", font=("Consolas", 9), background=t["secondary_bg"])
            self.html_view.tag_configure("link", foreground=t["accent"], underline=True)
            self.html_view.tag_configure("bold", font=("Segoe UI", 10, "bold"))
            self.html_view.tag_configure("list", lmargin1=20, lmargin2=30)
            
            lines = content.split('\n')
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue
                
                if in_code_block:
                    self.html_view.insert(tk.END, line + "\n", "code")
                elif line.startswith('# '):
                    self.html_view.insert(tk.END, line[2:] + "\n\n", "h1")
                elif line.startswith('## '):
                    self.html_view.insert(tk.END, line[3:] + "\n\n", "h2")
                elif line.startswith('### '):
                    self.html_view.insert(tk.END, line[4:] + "\n\n", "h3")
                elif line.strip().startswith('- '):
                    self.html_view.insert(tk.END, "  â€¢ " + line.strip()[2:] + "\n", "list")
                elif '**' in line:
                    parts = line.split('**')
                    for i, part in enumerate(parts):
                        if i % 2 == 1:
                            self.html_view.insert(tk.END, part, "bold")
                        else:
                            self.html_view.insert(tk.END, part)
                    self.html_view.insert(tk.END, "\n")
                elif line.strip().startswith('!['):
                    try:
                        alt_text = line[line.find('![')+2:line.find(']')]
                        self.html_view.insert(tk.END, f"[{alt_text}] ", "link")
                    except:
                        pass
                else:
                    self.html_view.insert(tk.END, line + "\n")
            
            self.html_view.configure(state="disabled")
    
    def _card(self, parent, title, icon_key):
        """Crea una tarjeta con tÃ­tulo e icono"""
        outer = tk.Frame(parent, bd=0, highlightthickness=1, relief="solid")
        
        if title:
            hdr = tk.Frame(outer, height=36)
            hdr.pack(fill="x")
            hdr.pack_propagate(False)
            
            inner_h = tk.Frame(hdr)
            inner_h.pack(side="left", padx=12, fill="y")
            
            ico = self._icons.get(icon_key)
            if ico:
                li = tk.Label(inner_h, image=ico, bd=0)
                li.image = ico
                li.pack(side="left", padx=(0, 6))
            
            title_lbl = tk.Label(inner_h, text=title, font=("Segoe UI", 10, "bold"))
            title_lbl.pack(side="left")
            
            sep = tk.Frame(outer, height=1)
            sep.pack(fill="x")
            
            outer._hdr = hdr
            outer._sep = sep
            outer._inner_h = inner_h
            outer._title_lbl = title_lbl
        
        return outer
    
    def _create_button(self, parent, text, icon_key, command, full_width=False):
        """Crea un botÃ³n con icono"""
        ico = self._icons.get(icon_key)
        
        btn = tk.Button(
            parent,
            text=text,
            image=ico if ico else None,
            compound="left" if ico else "none",
            command=command,
            font=("Segoe UI", 9),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=14,
            pady=7
        )
        
        if ico:
            btn.image = ico
            btn._icon_key = icon_key
        
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
        
        if not hasattr(self, '_action_buttons'):
            self._action_buttons = []
        self._action_buttons.append(btn)
        
        return btn
    
    def apply_theme(self):
        """Aplica el tema actual"""
        self.apply_base_theme()
        t = self.theme_manager.get_theme()
        
        self._load_icons()
        
        if hasattr(self, '_action_buttons'):
            for btn in self._action_buttons:
                if hasattr(btn, '_icon_key') and btn.winfo_exists():
                    ico = self._icons.get(btn._icon_key)
                    if ico:
                        btn.configure(image=ico)
                        btn.image = ico
        
        self._apply_theme_recursive(self, t)
    
    def _apply_theme_recursive(self, widget, t):
        """Aplica tema recursivamente"""
        bg = t["bg"]
        sec_bg = t["secondary_bg"]
        fg = t["fg"]
        border = t["border"]
        tree_bg = t["tree_bg"]
        tree_fg = t["tree_fg"]
        btn_bg = t["button_bg"]
        btn_fg = t["button_fg"]
        accent = t["accent"]
        
        try:
            cls = type(widget).__name__
            
            if cls == "Frame":
                if hasattr(widget, "_sep"):
                    widget.configure(bg=sec_bg, highlightbackground=border)
                    widget._sep.configure(bg=border)
                    if hasattr(widget, "_hdr"):
                        widget._hdr.configure(bg=sec_bg)
                    if hasattr(widget, "_inner_h"):
                        self._set_bg_deep(widget._inner_h, sec_bg, fg)
                elif widget == getattr(self, '_desc_frame', None):
                    widget.configure(bg=border, highlightbackground=border)
                else:
                    widget.configure(bg=bg)
            
            elif cls == "Label":
                try:
                    pbg = widget.master.cget("bg")
                except:
                    pbg = bg
                widget.configure(bg=pbg, fg=fg)
            
            elif cls == "Button":
                widget.configure(
                    bg=btn_bg,
                    fg=btn_fg,
                    activebackground=t["button_hover"],
                    activeforeground=btn_fg
                )
            
            elif cls in ("Entry", "Text"):
                widget.configure(
                    bg=tree_bg,
                    fg=tree_fg,
                    insertbackground=fg
                )
            
            elif cls == "Spinbox":
                widget.configure(
                    bg=tree_bg,
                    fg=tree_fg,
                    insertbackground=fg,
                    buttonbackground=btn_bg,
                    readonlybackground=tree_bg
                )
            
            elif cls == "Checkbutton":
                try:
                    pbg = widget.master.cget("bg")
                except:
                    pbg = bg
                widget.configure(
                    bg=pbg,
                    fg=fg,
                    selectcolor=tree_bg,
                    activebackground=pbg,
                    activeforeground=fg
                )
            
            elif cls == "Radiobutton":
                try:
                    pbg = widget.master.cget("bg")
                except:
                    pbg = bg
                widget.configure(
                    bg=pbg,
                    fg=fg,
                    selectcolor=accent,
                    activebackground=pbg,
                    activeforeground=fg
                )
            
            elif cls == "Scrollbar":
                widget.configure(
                    bg=sec_bg,
                    troughcolor=bg,
                    activebackground=accent,
                    highlightthickness=0,
                    bd=0,
                    relief="flat",
                    elementborderwidth=0
                )
            
            elif cls == "Canvas":
                widget.configure(bg=bg)
        
        except Exception:
            pass
        
        for child in widget.winfo_children():
            self._apply_theme_recursive(child, t)
    
    def _set_bg_deep(self, widget, bg, fg):
        """Aplica colores profundamente"""
        try:
            widget.configure(bg=bg)
            if isinstance(widget, tk.Label):
                widget.configure(fg=fg)
        except:
            pass
        for child in widget.winfo_children():
            self._set_bg_deep(child, bg, fg)
    
    def _generate_preview(self):
        """Genera el preview del README"""
        lang = self.language_manager
        project_name = self.project_name_entry.get() or lang.get_text("readme_default_project")
        description = self.description_text.get("1.0", tk.END).strip() or "Descripción del proyecto"
        author = self.author_entry.get() or "Tu Nombre"
        github = self.github_entry.get() or "@tu_usuario"
        license_type = self.license_var.get()
        description = description if description else lang.get_text("readme_default_description")
        author = author if author else lang.get_text("readme_default_author")
        github = github if github else lang.get_text("readme_default_github")
        
        readme = []
        heading_about = lang.get_text("readme_heading_about")
        heading_structure = lang.get_text("readme_heading_structure")
        heading_stats = lang.get_text("readme_heading_stats")
        heading_installation = lang.get_text("readme_heading_installation")
        heading_usage = lang.get_text("readme_heading_usage")
        heading_contributing = lang.get_text("readme_heading_contributing")
        heading_license = lang.get_text("readme_heading_license")
        heading_contact = lang.get_text("readme_heading_contact")
        
        # Header
        readme.append(f"# {project_name}\n")
        readme.append(f"{description}\n")
        
        # Badges
        if self.include_badges.get():
            repo_slug = f"usuario/{project_name.lower().replace(' ', '-')}"
            # Forzar formato PNG agregando extensiÃ³n
            readme.append(f"![{lang.get_text('readme_badge_status')}](https://img.shields.io/badge/status-active-success.png)")
            readme.append(f"![{lang.get_text('readme_badge_license')}](https://img.shields.io/badge/license-{license_type.replace(' ', '_')}-blue.png)")
            readme.append(f"![{lang.get_text('readme_badge_stars')}](https://img.shields.io/github/stars/{repo_slug}.png)")
            readme.append("")
        
        # TOC
        if self.include_toc.get():
            readme.append(f"## {lang.get_text('readme_heading_toc')}")
            readme.append(f"- [{heading_about}](#{self._anchor_for_heading(heading_about)})")
            if self.include_structure.get():
                readme.append(f"- [{heading_structure}](#{self._anchor_for_heading(heading_structure)})")
            if self.include_stats.get():
                readme.append(f"- [{heading_stats}](#{self._anchor_for_heading(heading_stats)})")
            if self.include_installation.get():
                readme.append("- [Instalación](#instalación)")
            if self.include_usage.get():
                readme.append(f"- [{heading_usage}](#{self._anchor_for_heading(heading_usage)})")
            if self.include_contributing.get():
                readme.append(f"- [{heading_contributing}](#{self._anchor_for_heading(heading_contributing)})")
            if self.include_license_section.get():
                readme.append(f"- [{heading_license}](#{self._anchor_for_heading(heading_license)})")
            if self.include_contact.get():
                readme.append(f"- [{heading_contact}](#{self._anchor_for_heading(heading_contact)})")
            readme.append("")
        
        # About
        readme.append(f"## {heading_about}")
        readme.append(f"{description}\n")
        
        # Structure
        if self.include_structure.get() and self.file_manager.root_path:
            readme.append(f"## {heading_structure}")
            readme.append("```")
            readme.append(self._generate_tree_structure())
            readme.append("```\n")
        
        # Stats
        if self.include_stats.get() and self.file_manager.root_path:
            readme.append(f"## {heading_stats}")
            stats = self._get_project_stats()
            readme.append(stats)
            readme.append("")
        
        # Installation
        if self.include_installation.get():
            readme.append("## Instalación")
            readme.append("```bash")
            readme.append(f"# {lang.get_text('readme_install_clone_repo')}")
            readme.append(f"git clone https://github.com/usuario/{project_name.lower().replace(' ', '-')}.git")
            readme.append("")
            readme.append(f"# {lang.get_text('readme_install_enter_directory')}")
            readme.append(f"cd {project_name.lower().replace(' ', '-')}")
            readme.append("")
            readme.append(f"# {lang.get_text('readme_install_dependencies')}")
            
            if self._has_file("requirements.txt"):
                readme.append("pip install -r requirements.txt")
            elif self._has_file("package.json"):
                readme.append("npm install")
            else:
                readme.append("# [Agregar comando de instalación]")
            
            readme.append("```\n")
        
        # Usage
        if self.include_usage.get():
            readme.append(f"## {heading_usage}")
            readme.append("```bash")
            
            if self._has_file("main.py"):
                readme.append("python main.py")
            elif self._has_file("index.js"):
                readme.append("npm start")
            else:
                readme.append(f"# [{lang.get_text('readme_usage_add_instructions')}]")
            
            readme.append("```\n")
        
        # Contributing
        if self.include_contributing.get():
            readme.append(f"## {heading_contributing}")
            readme.append(lang.get_text("readme_contrib_intro"))
            readme.append(f"1. {lang.get_text('readme_contrib_step_1')}")
            readme.append(f"2. {lang.get_text('readme_contrib_step_2')}")
            readme.append(f"3. {lang.get_text('readme_contrib_step_3')}")
            readme.append(f"4. {lang.get_text('readme_contrib_step_4')}")
            readme.append(f"5. {lang.get_text('readme_contrib_step_5')}\n")
        
        # License
        if self.include_license_section.get():
            readme.append(f"## {heading_license}")
            readme.append(f"Distribuido bajo la licencia {license_type}. Ver `LICENSE` para más información.\n")
        
        # Contact
        if self.include_contact.get():
            readme.append(f"## {heading_contact}")
            readme.append(f"{author} - [{github}](https://twitter.com/{github.lstrip('@')})")
            readme.append(
                f"{lang.get_text('readme_contact_project_label')}: "
                f"[https://github.com/usuario/{project_name.lower().replace(' ', '-')}](https://github.com/usuario/{project_name.lower().replace(' ', '-')})"
            )
        
        # Show
        content = "\n".join(readme)
        content = self._translate_legacy_readme_content(content, license_type)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, content)
        
        # Update rendered view if active
        if self._preview_mode == "rendered":
            self._render_preview()
    
    def _anchor_for_heading(self, text):
        """Genera ancla markdown simple a partir del titulo."""
        normalized = unicodedata.normalize("NFKD", text.lower())
        without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        cleaned = re.sub(r"[^\w\s-]", "", without_accents)
        return re.sub(r"\s+", "-", cleaned.strip())

    def _translate_legacy_readme_content(self, content, license_type):
        """Traduce texto legado hardcodeado del README al idioma actual."""
        lang = self.language_manager
        replacements = {
            "## Tabla de Contenidos": f"## {lang.get_text('readme_heading_toc')}",
            "## Sobre el Proyecto": f"## {lang.get_text('readme_heading_about')}",
            "## Estructura del Proyecto": f"## {lang.get_text('readme_heading_structure')}",
            "## Estadisticas": f"## {lang.get_text('readme_heading_stats')}",
            "## Instalación": f"## {lang.get_text('readme_heading_installation')}",
            "## InstalaciÃ³n": f"## {lang.get_text('readme_heading_installation')}",
            "- [Instalación](#instalación)": f"- [{lang.get_text('readme_heading_installation')}](#{self._anchor_for_heading(lang.get_text('readme_heading_installation'))})",
            "- [InstalaciÃ³n](#instalaciÃ³n)": f"- [{lang.get_text('readme_heading_installation')}](#{self._anchor_for_heading(lang.get_text('readme_heading_installation'))})",
            "# Clonar el repositorio": f"# {lang.get_text('readme_install_clone_repo')}",
            "# Entrar al directorio": f"# {lang.get_text('readme_install_enter_directory')}",
            "# Instalar dependencias": f"# {lang.get_text('readme_install_dependencies')}",
            "# [Agregar comando de instalación]": f"# [{lang.get_text('readme_install_add_command')}]",
            "# [Agregar comando de instalaciÃ³n]": f"# [{lang.get_text('readme_install_add_command')}]",
        }

        legacy_license_line = f"Distribuido bajo la licencia {license_type}. Ver `LICENSE` para más información."
        legacy_license_line_mojibake = f"Distribuido bajo la licencia {license_type}. Ver `LICENSE` para mÃ¡s informaciÃ³n."
        localized_license = lang.get_text("readme_license_line").format(license=license_type)
        content = content.replace(legacy_license_line, localized_license)
        content = content.replace(legacy_license_line_mojibake, localized_license)

        for old_text, new_text in replacements.items():
            content = content.replace(old_text, new_text)
        return content

    def _generate_tree_structure(self):
        """Genera estructura de Ã¡rbol con colapso inteligente"""
        if not self.file_manager.root_path:
            return self.language_manager.get_text("readme_tree_no_folder")
        
        max_depth = self.depth_var.get()
        tree_lines = []
        tree_lines.append(os.path.basename(self.file_manager.root_path) + "/")
        
        self._build_tree(self.file_manager.root_path, "", tree_lines, 0, max_depth)
        
        return "\n".join(tree_lines)
    
    def _build_tree(self, path, prefix, lines, depth, max_depth):
        """Construye Ã¡rbol con colapso inteligente"""
        if depth >= max_depth:
            return
        
        # Directorios a ignorar
        ignored_dirs = {
            'node_modules', 'venv', '.venv', 'env', '.env',
            '__pycache__', '.git', '.svn',
            'dist', 'build', 'target', 'bin', 'obj',
            '.idea', '.vscode', 'coverage',
            'site-packages', 'Lib', 'Scripts'
        }
        
        try:
            items = sorted(os.listdir(path))
            # Filtrar items ignorados
            items = [item for item in items 
                    if not item.startswith('.') 
                    and item not in ignored_dirs]
            
            # Contar archivos en subdirectorios
            if self.collapse_large_dirs.get():
                threshold = self.collapse_threshold.get()
                processed_items = []
                
                for item in items:
                    fullpath = os.path.join(path, item)
                    if os.path.isdir(fullpath):
                        try:
                            subfiles = [f for f in os.listdir(fullpath) 
                                    if not f.startswith('.') 
                                    and f not in ignored_dirs]
                            if len(subfiles) > threshold:
                                # Marcar para colapsar
                                processed_items.append((item, len(subfiles), True))
                            else:
                                processed_items.append((item, 0, False))
                        except:
                            processed_items.append((item, 0, False))
                    else:
                        processed_items.append((item, 0, False))
            else:
                processed_items = [(item, 0, False) for item in items]
            
            for i, (item, count, collapse) in enumerate(processed_items):
                is_last = i == len(processed_items) - 1
                fullpath = os.path.join(path, item)
                
                connector = "└── " if is_last else "├── "
                
                if collapse:
                    lines.append(f"{prefix}{connector}{item}/ ({count} {self.language_manager.get_text('readme_files_label')})")
                else:
                    lines.append(f"{prefix}{connector}{item}")
                    
                    if os.path.isdir(fullpath) and not collapse:
                        extension = "    " if is_last else "│   "
                        self._build_tree(fullpath, prefix + extension, lines, depth + 1, max_depth)
        except PermissionError:
            pass
    
    def _get_project_stats(self):
        """Obtiene estadÃ­sticas"""
        all_files = []
        
        # Directorios a ignorar
        ignored_dirs = {
            'node_modules', 'venv', '.venv', 'env', '.env',
            '__pycache__', '.git', '.svn', '.hg',
            'dist', 'build', '.next', '.nuxt',
            'target', 'bin', 'obj',
            '.idea', '.vscode', '.vs',
            'coverage', '.pytest_cache', '.mypy_cache',
            'site-packages', 'Lib', 'lib', 'Scripts',
            '.egg-info', 'eggs'
        }
        
        for root, dirs, files in os.walk(self.file_manager.root_path):
            # Filtrar directorios ignorados
            dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith('.')]
            
            # Ignorar si estamos dentro de un directorio ignorado
            path_parts = os.path.normpath(root).split(os.sep)
            if any(part in ignored_dirs or part.startswith('.') for part in path_parts):
                continue
            
            for file in files:
                # Ignorar archivos temporales y compilados
                if file.startswith('.') or file.endswith(('.pyc', '.pyo', '.so', '.dll', '.exe', '.o', '.a')):
                    continue
                
                all_files.append(os.path.join(root, file))
        
        stats = self.project_stats.calculate_stats(all_files)
        
        output = []
        output.append(f"- **{self.language_manager.get_text('readme_stats_total_files')}**: {stats['total_files']}")
        output.append(f"- **{self.language_manager.get_text('readme_stats_total_lines')}**: {stats['total_lines']:,}")
        
        from utils.helpers import format_file_size
        output.append(f"- **{self.language_manager.get_text('readme_stats_total_size')}**: {format_file_size(stats['total_size'])}")
        
        lang_dist = self.project_stats.get_language_distribution(stats)
        sorted_langs = sorted(lang_dist.items(), key=lambda x: x[1]['lines'], reverse=True)[:5]
        
        if sorted_langs:
            output.append("")
            output.append(f"**{self.language_manager.get_text('readme_stats_top_languages')}:**")
            for lang, data in sorted_langs:
                percentage = (data['lines'] / stats['total_lines'] * 100) if stats['total_lines'] > 0 else 0
                output.append(f"- {lang}: {data['lines']:,} {self.language_manager.get_text('readme_stats_lines_label')} ({percentage:.1f}%)")
        
        return "\n".join(output)
    
    def _has_file(self, filename):
        """Verifica si existe un archivo"""
        if not self.file_manager.root_path:
            return False
        return os.path.exists(os.path.join(self.file_manager.root_path, filename))
    
    def _save_readme(self):
        """Guarda el README"""
        content = self.preview_text.get("1.0", tk.END)
        
        if self.file_manager.root_path:
            initial_dir = self.file_manager.root_path
        else:
            initial_dir = os.path.expanduser("~")
        
        filepath = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            initialfile="README.md",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All Files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo(
                    self.language_manager.get_text("msg_success"),
                    f"{self.language_manager.get_text('readme_save_success_prefix')}:\n{filepath}"
                )
            except Exception as e:
                messagebox.showerror(
                    self.language_manager.get_text("msg_error"),
                    f"{self.language_manager.get_text('readme_save_error_prefix')}:\n{e}"
                )
    
    def _copy_to_clipboard(self):
        """Copia al portapapeles"""
        try:
            import pyperclip
            content = self.preview_text.get("1.0", tk.END)
            pyperclip.copy(content)
            messagebox.showinfo(
                self.language_manager.get_text("msg_success"),
                self.language_manager.get_text("readme_copy_success")
            )
        except ImportError:
            self.clipboard_clear()
            self.clipboard_append(self.preview_text.get("1.0", tk.END))
            messagebox.showinfo(
                self.language_manager.get_text("msg_success"),
                self.language_manager.get_text("readme_copy_success")
            )

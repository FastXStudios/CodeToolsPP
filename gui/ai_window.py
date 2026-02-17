"""
Ventana de Chat con IA para Code Tools++
Interfaz profesional para interactuar con modelos de IA
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import json
import re
import keyword
from collections import deque
from urllib import request as urllib_request
from gui.components import CustomToplevel
from utils.helpers import resource_path
from PIL import Image, ImageTk


class AIWindow(CustomToplevel):
    """Ventana de chat profesional con IA - DiseÃ±o moderno y limpio"""
    
    # Archivo para persistencia
    HISTORY_FILE = ".ai_chat_history.json"
    
    def __init__(self, parent, theme_manager, language_manager, ai_manager, 
                 file_manager, selection_manager):
        title = language_manager.get_text("ai_chat_title")
        
        # âœ… PRIMERO: Cargar modelo ANTES de crear UI
        self._early_load_history(ai_manager)
        
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title=title,
            size="1100x750",
            min_size=(900, 600),
            max_size=(1600, 1000)
        )
        self.language_manager = language_manager
        self.ai_manager = ai_manager
        self.file_manager = file_manager
        self.selection_manager = selection_manager
        
        self._icons = {}
        self._model_logos = {}
        self._gif_frames = {}
        self._gif_durations = {}
        self._gif_animation_ids = {}
        
        self.chat_history = []
        self._is_thinking = False
        self._chat_request_in_flight = False
        self._emoji_images = {}
        self._model_selector_open = False
        self._model_selector_window = None
        self._add_model_dialog_open = False
        self._add_model_dialog_window = None
        self.context_mode = "smart"
        
        self._load_icons()
        self._build_ui()
        self.apply_theme()
        
        # Suscripciones
        self.theme_manager.subscribe(self.apply_theme)
        self.language_manager.subscribe(self._update_translations)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        # Restaurar mensajes despues de crear UI
        self._restore_chat_from_history()

    def _early_load_history(self, ai_manager):
        """Carga temprana solo para restaurar modelo"""
        # âœ… Inicializar valores por defecto PRIMERO
        self._pending_history = []
        self._saved_token_count = "0 tokens"  # âœ… Siempre inicializar
        
        try:
            if os.path.exists(self.HISTORY_FILE):
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    
                    # âœ… Restaurar modelo DIRECTAMENTE
                    saved_model = history_data.get("current_model")
                    if saved_model and saved_model in ai_manager.models:
                        ai_manager.current_model = saved_model
                        ai_manager.config_manager.set("ai_current_model", saved_model)
                        print(f"âœ… Modelo restaurado: {saved_model}")
                    
                    # Guardar mensajes para despuÃ©s
                    self._pending_history = history_data.get("messages", [])
                    self.context_mode = history_data.get("context_mode", "smart")
                    self._saved_token_count = history_data.get("last_token_count", "0 tokens")
        except Exception as e:
            print(f"Error: {e}")
    
    def _restore_chat_from_history(self):
        """Restaura mensajes DESPUÃ‰S de crear UI"""
        if hasattr(self, '_pending_history') and self._pending_history:
            self.chat_history = []
            for msg in self._pending_history:
                self._add_message(
                    msg.get("text", ""),
                    msg.get("is_user", False),
                    show_model=not msg.get("is_user", False),
                    persist=False
                )
            print(f"âœ… {len(self._pending_history)} mensajes restaurados")
            

    
    def _on_close(self):
        """Guardar historial antes de cerrar"""
        self._save_history()
        self.destroy()
    
    # LÃNEA 48-75: Mejorar persistencia del historial:
    def _save_history(self):
        """Guarda historial con TODOS los detalles"""
        try:
            history_data = {
                "messages": [
                    {"text": msg["text"], "is_user": msg["is_user"]}
                    for msg in self.chat_history
                ],
                "context_mode": self.context_mode,
                "current_model": self.ai_manager.current_model,
                # âœ… Guardar tambiÃ©n stats de tokens
                "last_token_count": self._token_label.cget("text") if hasattr(self, '_token_label') else "0 tokens"
            }
            
            with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            
            print(f"âœ… Historial guardado: {len(history_data['messages'])} mensajes")
        except Exception as e:
            print(f"âŒ Error guardando historial: {e}")
    
    # LÃNEA 77-95: Mejorar carga del historial:
    def _load_history(self):
        """Carga historial completo"""
        try:
            if os.path.exists(self.HISTORY_FILE):
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    
                    self._pending_history = history_data.get("messages", [])
                    self.context_mode = history_data.get("context_mode", "smart")
                    
                    # âœ… Restaurar modelo guardado
                    saved_model = history_data.get("current_model")
                    if saved_model and saved_model in self.ai_manager.models:
                        self.ai_manager.set_current_model(saved_model)
                    
                    # âœ… Restaurar contador de tokens
                    last_tokens = history_data.get("last_token_count", "0 tokens")
                    
                    print(f"Historial cargado: {len(self._pending_history)} mensajes, modelo: {saved_model}")
                    return last_tokens
        except Exception as e:
            print(f"Error cargando historial: {e}")
            self.chat_history = []
            return "0 tokens"
    
    def _update_translations(self):
        """Actualiza traducciones cuando cambia el idioma"""
        # Actualizar tÃ­tulo de ventana
        self.title(self.language_manager.get_text("ai_chat_title"))
        
        # Actualizar textos de botones y labels
        try:
            # Botones de toolbar
            if hasattr(self, '_action_buttons_data'):
                for i, (icon_name, text_key, command) in enumerate(self._action_buttons_data):
                    if i < len(self._action_buttons):
                        btn = self._action_buttons[i]
                        text = self.language_manager.get_text(text_key)
                        btn.configure(text=f" {text}")
            
            # BotÃ³n enviar
            if hasattr(self, '_send_btn'):
                self._send_btn.configure(
                    text=" " + self.language_manager.get_text("ai_send")
                )
            
            # BotÃ³n limpiar
            if hasattr(self, '_clear_btn'):
                self._clear_btn.configure(
                    text=" " + self.language_manager.get_text("ai_clear")
                )
            
            # BotÃ³n modelos
            if hasattr(self, '_models_btn'):
                self._models_btn.configure(
                    text=" " + self.language_manager.get_text("ai_select_model")
                )
            
            # Label de contexto
            if hasattr(self, '_context_label'):
                if self.context_mode == "smart":
                    context_text = "Contexto: Inteligente" if self.language_manager.current_language == "es" else "Context: Smart"
                else:
                    context_text = "Contexto: Completo" if self.language_manager.current_language == "es" else "Context: Full"
                self._context_label.configure(text=context_text)
            
            # Placeholder del input
            if hasattr(self, '_has_placeholder') and self._has_placeholder:
                self._input_text.delete("1.0", "end")
                placeholder = self.language_manager.get_text('ai_placeholder')
                self._input_text.insert("1.0", placeholder)
        
        except Exception as e:
            print(f"Error actualizando traducciones: {e}")
    
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # ICONOS Y GIFS
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    
    def _load_icons(self):
        """Carga iconos PNG y GIFs animados"""
        try:
            from PIL import Image, ImageTk
            icon_dir = resource_path("assets/icons")
            t = self.theme_manager.get_theme()
            
            def _rgb(h):
                h = h.lstrip("#")
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            
            def load_png(name, size=(16, 16), bg=None):
                path = os.path.join(icon_dir, name)
                if not os.path.exists(path):
                    return None
                img = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                bg_hex = bg or t["secondary_bg"]
                base = Image.new("RGBA", img.size, _rgb(bg_hex) + (255,))
                base.paste(img, mask=img.split()[3])
                return ImageTk.PhotoImage(base.convert("RGB"))
            
            # Iconos para la interfaz
            self._icons = {
                "send": load_png("send.png", (18, 18), t["button_bg"]),
                "clear": load_png("trash.png", (18, 18)),
                "settings": load_png("settings.png", (18, 18)),
                "scan": load_png("scan.png", (18, 18)),
                "code": load_png("code.png", (18, 18)),
                "document": load_png("document.png", (18, 18)),
                "performance": load_png("performance.png", (18, 18)),
                "help": load_png("help.png", (18, 18)),
                "user": load_png("user.png", (24, 24)),
                "ai": load_png("ai.gif", (24, 24)),
            }
            
            # Cargar GIFs de modelos
            models = self.ai_manager.get_available_models()
            for model in models:
                self._ensure_model_logo_loaded(model.get("key", ""))
            
        except Exception as e:
            print(f"Error cargando iconos: {e}")
            self._icons = {}
    
    def _load_gif(self, model_key: str, gif_path: str, size=(28, 28)):
        """Carga un GIF animado"""
        try:
            if not os.path.exists(gif_path):
                return
            
            gif = Image.open(gif_path)
            frames = []
            durations = []
            
            try:
                while True:
                    frame = gif.copy().convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                    frame = self._strip_logo_matte(frame)
                    photo = ImageTk.PhotoImage(frame)
                    frames.append(photo)
                    duration = gif.info.get('duration', 100)
                    durations.append(duration)
                    gif.seek(len(frames))
            except EOFError:
                pass
            
            if frames:
                self._gif_frames[model_key] = frames
                self._gif_durations[model_key] = durations
                self._model_logos[model_key] = frames[0]
        except Exception as e:
            print(f"Error cargando GIF {gif_path}: {e}")

    def _load_static_logo(self, model_key: str, image_path: str, size=(28, 28)):
        """Carga logo estático (PNG/JPG/WebP/etc)."""
        try:
            if not os.path.exists(image_path):
                return False
            img = Image.open(image_path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
            img = self._strip_logo_matte(img)
            photo = ImageTk.PhotoImage(img)
            self._model_logos[model_key] = photo
            self._gif_frames.pop(model_key, None)
            self._gif_durations.pop(model_key, None)
            return True
        except Exception as e:
            print(f"Error cargando logo {image_path}: {e}")
            return False

    def _ensure_model_logo_loaded(self, model_key: str, size=(28, 28)):
        """Carga logo del modelo si aún no está en memoria."""
        if not model_key:
            return False
        if model_key in self._model_logos:
            return True

        model_config = self.ai_manager.models.get(model_key, {})
        logo_name = model_config.get("logo", "ai.gif")
        if not logo_name:
            return False

        logo_path = logo_name if os.path.isabs(logo_name) else resource_path(os.path.join("assets", "logos", logo_name))
        ext = os.path.splitext(logo_path)[1].lower()
        if ext == ".gif":
            self._load_gif(model_key, logo_path, size=size)
            return model_key in self._model_logos
        return self._load_static_logo(model_key, logo_path, size=size)

    def _cancel_model_logo_animations(self):
        """Cancela animaciones activas de logos para evitar frames viejos."""
        for anim_id in list(self._gif_animation_ids.keys()):
            try:
                self.after_cancel(self._gif_animation_ids[anim_id])
                del self._gif_animation_ids[anim_id]
            except Exception:
                pass

    def _strip_logo_matte(self, frame: Image.Image):
        """Elimina fondo sólido de borde en logos (ej. GIF con matte blanco)."""
        try:
            if frame.mode != "RGBA":
                frame = frame.convert("RGBA")

            w, h = frame.size
            if w < 3 or h < 3:
                return frame

            px = frame.load()
            edge_samples = []
            step_x = max(1, w // 16)
            step_y = max(1, h // 16)

            for x in range(0, w, step_x):
                edge_samples.append(px[x, 0][:3])
                edge_samples.append(px[x, h - 1][:3])
            for y in range(0, h, step_y):
                edge_samples.append(px[0, y][:3])
                edge_samples.append(px[w - 1, y][:3])

            if not edge_samples:
                return frame

            r = sum(c[0] for c in edge_samples) // len(edge_samples)
            g = sum(c[1] for c in edge_samples) // len(edge_samples)
            b = sum(c[2] for c in edge_samples) // len(edge_samples)
            if (r + g + b) // 3 < 165:
                return frame

            tol = 24
            q = deque()
            visited = set()

            def near_bg(xx, yy):
                pr, pg, pb, pa = px[xx, yy]
                if pa == 0:
                    return True
                return abs(pr - r) <= tol and abs(pg - g) <= tol and abs(pb - b) <= tol

            for x in range(w):
                q.append((x, 0))
                q.append((x, h - 1))
            for y in range(h):
                q.append((0, y))
                q.append((w - 1, y))

            while q:
                x, y = q.popleft()
                if (x, y) in visited:
                    continue
                visited.add((x, y))
                if x < 0 or y < 0 or x >= w or y >= h:
                    continue
                if not near_bg(x, y):
                    continue

                pr, pg, pb, pa = px[x, y]
                px[x, y] = (pr, pg, pb, 0)

                q.append((x + 1, y))
                q.append((x - 1, y))
                q.append((x, y + 1))
                q.append((x, y - 1))

            return frame
        except Exception:
            return frame
    
    def _animate_gif(self, label, model_key: str, frame_index: int = 0):
        """Anima un GIF"""
        if model_key not in self._gif_frames or not label.winfo_exists():
            return
        
        frames = self._gif_frames[model_key]
        durations = self._gif_durations[model_key]
        
        if not frames:
            return
        
        try:
            label.configure(image=frames[frame_index])
        except:
            return
        
        next_frame = (frame_index + 1) % len(frames)
        duration = durations[frame_index]
        
        anim_id = self.after(duration, lambda: self._animate_gif(label, model_key, next_frame))
        self._gif_animation_ids[f"{model_key}_{id(label)}"] = anim_id
    
    # UI CONSTRUCCIÓN

    def _build_ui(self):
        """Construye la interfaz moderna"""
        t = self.theme_manager.get_theme()
        p = self._chat_palette(t)
        
        # TOP BAR - InformaciÃ³n del modelo y estada­sticas
        top_bar = tk.Frame(self.content_frame, height=60, bg=p["panel_bg"])
        top_bar.pack(fill="x", pady=(0, 1))
        top_bar.pack_propagate(False)
        self._top_bar = top_bar
        
        # Contenedor interno con padding
        top_inner = tk.Frame(top_bar, bg=p["panel_bg"])
        top_inner.pack(fill="both", expand=True, padx=16, pady=10)
        
        # LEFT: Modelo actual con logo
        left_section = tk.Frame(top_inner, bg=p["panel_bg"])
        left_section.pack(side="left", fill="y")
        
        current_model = self.ai_manager.current_model
        if current_model and current_model in self._model_logos:
            self._model_logo_label = tk.Label(
                left_section,
                image=self._model_logos[current_model]
            )
            self._model_logo_label.pack(side="left", padx=(0, 12))
            
            if current_model in self._gif_frames:
                self._animate_gif(self._model_logo_label, current_model)
        
        model_info_frame = tk.Frame(left_section, bg=p["panel_bg"])
        model_info_frame.pack(side="left", fill="y", anchor="w")
        
        if current_model:
            model_config = self.ai_manager.models.get(current_model, {})
            
            self._model_name_label = tk.Label(
                model_info_frame,
                text=model_config.get("name", "IA"),
                font=("Segoe UI", 11, "bold")
            )
            self._model_name_label.pack(anchor="w")
            
            model_id = model_config.get("model_id", "")
            if model_id:
                self._model_id_label = tk.Label(
                    model_info_frame,
                    text=model_id,
                    font=("Segoe UI", 8)
                )
                self._model_id_label.pack(anchor="w")
        
        # RIGHT: EstadÃ­sticas y controles
        right_section = tk.Frame(top_inner, bg=p["panel_bg"])
        right_section.pack(side="right", fill="y")
        
        # Stats frame
        self._stats_frame = tk.Frame(right_section, bg=p["panel_bg"])
        self._stats_frame.pack(side="left", padx=(0, 16))

        # En la parte donde creas _token_label:
        self._token_label = tk.Label(
            self._stats_frame,
            text=self._saved_token_count,  # âœ… Usa el valor guardado
            font=("Segoe UI", 9)
        )
        self._token_label.pack(anchor="e")

        
        # Texto inicial del contexto segÃºn idioma
        if self.context_mode == "smart":
            context_text = "Contexto: Inteligente" if self.language_manager.current_language == "es" else "Context: Smart"
        else:
            context_text = "Contexto: Completo" if self.language_manager.current_language == "es" else "Context: Full"
        
        self._context_label = tk.Label(
            self._stats_frame,
            text=context_text,
            font=("Segoe UI", 8)
        )
        self._context_label.pack(anchor="e")
        
        # Context mode toggle
        context_btn_frame = tk.Frame(right_section, bg=p["panel_bg"])
        context_btn_frame.pack(side="left", padx=(0, 8))
        
        self._context_btn = tk.Button(
            context_btn_frame,
            text="Smart" if self.context_mode == "smart" else "Full",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=12,
            pady=4,
            width=6,
            command=self._toggle_context_mode
        )
        self._context_btn.pack()
        
        # BOTÃ“N DE MODELOS CON ICONO Y TEXTO
        if "settings" in self._icons:
            self._models_btn = tk.Button(
                right_section,
                image=self._icons["settings"],
                text=" " + self.language_manager.get_text("ai_select_model"),
                compound="left",
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
                bd=0,
                relief="flat",
                padx=12,
                pady=6,
                command=self._show_model_selector
            )
            self._models_btn.pack(side="left")
            self._bind_hover(self._models_btn, action=True)
        
        # Separador
        sep1 = tk.Frame(self.content_frame, height=1, bg=p["line"])
        sep1.pack(fill="x")
        self._sep1 = sep1
        
        # MAIN CONTENT - Chat area con scroll
        main_container = tk.Frame(self.content_frame, bg=p["chat_bg"])
        main_container.pack(fill="both", expand=True)
        self._main_container = main_container
        
        # Canvas + Scrollbar
        self._chat_canvas = tk.Canvas(
            main_container,
            bd=0,
            highlightthickness=0,
            bg=p["chat_bg"]
        )
        
        self._scrollbar = tk.Scrollbar(
            main_container,
            orient="vertical",
            command=self._chat_canvas.yview,
            width=8
        )
        
        self._chat_canvas.configure(yscrollcommand=self._scrollbar.set)
        
        self._scrollbar.pack(side="right", fill="y")
        self._chat_canvas.pack(side="left", fill="both", expand=True)
        
        # Frame de mensajes
        self._messages_frame = tk.Frame(self._chat_canvas, bg=p["chat_bg"])
        self._messages_content = tk.Frame(self._messages_frame, bg=p["chat_bg"])
        self._messages_content.pack(side="top", fill="x", anchor="n")
        self._canvas_window = self._chat_canvas.create_window(
            (0, 0),
            window=self._messages_frame,
            anchor="nw",
            tags="messages_frame"
        )
        
        # Configurar scroll
        self._messages_frame.bind("<Configure>", self._on_frame_configure)
        self._messages_content.bind("<Configure>", self._on_frame_configure, add="+")
        self._chat_canvas.bind("<Configure>", self._on_canvas_configure, add="+")
        self._setup_chat_scroll_bindings()
        # Separador
        sep2 = tk.Frame(self.content_frame, height=1, bg=p["line"])
        sep2.pack(fill="x")
        self._sep2 = sep2
        
        # TOOLBAR - Acciones rÃ¡pidas
        toolbar = tk.Frame(self.content_frame, height=50, bg=p["panel_bg"])
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)
        self._toolbar = toolbar
        
        toolbar_inner = tk.Frame(toolbar, bg=p["panel_bg"])
        toolbar_inner.pack(fill="both", expand=True, padx=12, pady=8)
        
        # Botones de acciÃ³n
        self._action_buttons_data = [
            ("scan", "ai_analyze", self._analyze_selected),
            ("code", "ai_fix_errors", self._fix_errors),
            ("document", "ai_document", self._generate_docs),
            ("performance", "ai_optimize", self._optimize_code),
            ("help", "ai_explain", self._explain_code),
        ]
        
        self._action_buttons = []
        for icon_name, text_key, command in self._action_buttons_data:
            icon = self._icons.get(icon_name) or self._icons.get("scan")
            text = self.language_manager.get_text(text_key)
            
            btn = tk.Button(
                toolbar_inner,
                text=f" {text}",
                image=icon if icon else None,
                compound="left" if icon else "none",
                font=("Segoe UI", 9),
                cursor="hand2",
                bd=0,
                relief="flat",
                padx=14,
                pady=6,
                command=command
            )
            btn.pack(side="left", padx=(0, 6))
            self._bind_hover(btn, action=True)
            self._action_buttons.append(btn)
        
        # Separador
        sep3 = tk.Frame(self.content_frame, height=1, bg=p["line"])
        sep3.pack(fill="x")
        self._sep3 = sep3
        
        # INPUT AREA - Mensaje y botones
        input_container = tk.Frame(self.content_frame, bg=p["panel_bg"])
        input_container.pack(fill="x", side="bottom", padx=16, pady=12)
        self._input_container = input_container
        
        # Input frame con borde
        self._input_outer = tk.Frame(input_container, bd=1, relief="flat")
        self._input_outer.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        self._input_text = tk.Text(
            self._input_outer,
            height=3,
            font=("Segoe UI", 10),
            bd=0,
            wrap="word",
            relief="flat",
            padx=12,
            pady=10
        )
        self._input_text.pack(fill="both", expand=True)
        self._input_text.bind("<Shift-Return>", lambda e: "break")
        self._input_text.bind("<Return>", self._on_enter_press)
        self._input_text.bind("<FocusIn>", self._on_input_focus_in)
        self._input_text.bind("<FocusOut>", self._on_input_focus_out)
        
        # Placeholder
        self._show_placeholder()
        
        # Botones verticales
        buttons_frame = tk.Frame(input_container, bg=p["panel_bg"])
        buttons_frame.pack(side="right", fill="y")
        
        # Send button
        if "send" in self._icons:
            self._send_btn = tk.Button(
                buttons_frame,
                image=self._icons["send"],
                text=" " + self.language_manager.get_text("ai_send"),
                compound="left",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                bd=0,
                relief="flat",
                padx=16,
                pady=10,
                command=self._send_message
            )
            self._send_btn.pack(fill="x", pady=(0, 6))
            self._bind_hover(self._send_btn, primary=True)
        
        # Clear button
        if "clear" in self._icons:
            self._clear_btn = tk.Button(
                buttons_frame,
                image=self._icons["clear"],
                text=" " + self.language_manager.get_text("ai_clear"),
                compound="left",
                font=("Segoe UI", 9),
                cursor="hand2",
                bd=1,
                relief="solid",
                padx=16,
                pady=8,
                command=self._clear_chat
            )
            self._clear_btn.pack(fill="x")
            self._bind_hover(self._clear_btn, action=True)
    
    def _on_frame_configure(self, event=None):
        """Actualiza el scroll region"""
        content_h = self._messages_content.winfo_reqheight() if hasattr(self, "_messages_content") else self._messages_frame.winfo_reqheight()
        target_h = max(content_h, self._chat_canvas.winfo_height())
        self._chat_canvas.itemconfig(self._canvas_window, height=target_h)
        bbox = self._chat_canvas.bbox(self._canvas_window)
        if bbox:
            self._chat_canvas.configure(scrollregion=bbox)

    def _on_canvas_configure(self, event):
        """Ajusta el ancho del frame de mensajes"""
        canvas_width = event.width
        content_h = self._messages_content.winfo_reqheight() if hasattr(self, "_messages_content") else self._messages_frame.winfo_reqheight()
        target_h = max(content_h, self._chat_canvas.winfo_height())
        self._chat_canvas.itemconfig(self._canvas_window, width=canvas_width, height=target_h)
        bbox = self._chat_canvas.bbox(self._canvas_window)
        if bbox:
            self._chat_canvas.configure(scrollregion=bbox)


    def _setup_chat_scroll_bindings(self):
        """Vincula el scroll del mouse para toda el area del chat."""
        self._bind_scroll_tree(self._chat_canvas)
        self._bind_scroll_tree(self._messages_frame)
        self._bind_scroll_tree(self._messages_content)

    def _bind_scroll_events(self, widget):
        """Aplica binds de scroll sin usar bind_all para evitar conflictos."""
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_mousewheel, add="+")
        widget.bind("<Button-5>", self._on_mousewheel, add="+")

    def _bind_scroll_tree(self, widget):
        """Aplica binds de scroll al arbol completo de widgets."""
        self._bind_scroll_events(widget)
        for child in widget.winfo_children():
            self._bind_scroll_tree(child)

    def _scroll_to_bottom(self):
        """Hace autoscroll solo cuando llega un mensaje nuevo."""
        self._chat_canvas.update_idletasks()
        content_h = self._messages_content.winfo_reqheight() if hasattr(self, "_messages_content") else self._messages_frame.winfo_reqheight()
        viewport_h = self._chat_canvas.winfo_height()
        if content_h > viewport_h:
            self._chat_canvas.yview_moveto(1.0)
        else:
            self._chat_canvas.yview_moveto(0.0)

    def _on_mousewheel(self, event):
        """Scroll mejorado"""
        try:
            if hasattr(event, 'delta'):
                delta = int(-1 * (event.delta / 120))
                if delta == 0:
                    delta = -1 if event.delta > 0 else 1
                self._chat_canvas.yview_scroll(delta, "units")
            elif event.num == 4:
                self._chat_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self._chat_canvas.yview_scroll(1, "units")
            return "break"
        except:
            pass
    
    def _toggle_context_mode(self):
        """Cambia entre smart y full context"""
        if self.context_mode == "smart":
            self.context_mode = "full"
            self._context_btn.configure(text="Full")
            context_text = "Contexto: Completo" if self.language_manager.current_language == "es" else "Context: Full"
            self._context_label.configure(text=context_text)
        else:
            self.context_mode = "smart"
            self._context_btn.configure(text="Smart")
            context_text = "Contexto: Inteligente" if self.language_manager.current_language == "es" else "Context: Smart"
            self._context_label.configure(text=context_text)
        self._save_history()
    
    # MENSAJES DEL CHAT
    
    def _add_message_to_ui(self, text: str, is_user: bool, show_model: bool = False):
        """Agrega mensaje con FORMATO MEJORADO"""
        t = self.theme_manager.get_theme()
        p = self._chat_palette(t)
        
        msg_container = tk.Frame(self._messages_content, bg=p["chat_bg"])
        self._mark_custom_style(msg_container)
        
        if is_user:
            msg_container.pack(anchor="e", padx=16, pady=8)
            # Usuario - igual que antes
            msg_frame = tk.Frame(msg_container, bg=p["chat_bg"])
            msg_frame.pack(side="right", anchor="e")
            self._mark_custom_style(msg_frame)
            
            if "user" in self._icons:
                avatar = tk.Label(msg_frame, image=self._icons["user"], bg=p["chat_bg"])
                avatar.pack(side="right", padx=(10, 0))
                self._mark_custom_style(avatar)
            
            bubble = tk.Frame(
                msg_frame,
                bg=p["user_bubble"],
                bd=1,
                relief="flat",
                highlightthickness=1,
                highlightbackground=p["user_border"]
            )
            bubble.pack(side="right", padx=(0, 8))
            self._mark_custom_style(bubble)
            
            content = tk.Label(
                bubble,
                text=text,
                font=("Segoe UI", 10),
                justify="left",
                wraplength=640,
                anchor="w",
                padx=16,
                pady=11,
                bg=p["user_bubble"],
                fg=p["user_text"]
            )
            content.pack()
            self._mark_custom_style(content)
        else:
            msg_container.pack(anchor="w", padx=16, pady=8)
            # IA - CON FORMATO MEJORADO
            msg_frame = tk.Frame(msg_container, bg=p["chat_bg"])
            msg_frame.pack(side="left", anchor="w")
            self._mark_custom_style(msg_frame)
            
            # Avatar
            current_model = self.ai_manager.current_model
            if show_model and current_model and current_model in self._model_logos:
                avatar = tk.Label(msg_frame, image=self._model_logos[current_model], bg=p["chat_bg"])
                avatar.pack(side="left", padx=(0, 10), anchor="n")
                self._mark_custom_style(avatar)
                if current_model in self._gif_frames:
                    self._animate_gif(avatar, current_model)
            elif "ai" in self._icons:
                avatar = tk.Label(msg_frame, image=self._icons["ai"], bg=p["chat_bg"])
                avatar.pack(side="left", padx=(0, 10), anchor="n")
                self._mark_custom_style(avatar)
            
            # âœ… Contenido con markdown
            bubble = tk.Frame(
                msg_frame,
                bg=p["assistant_bubble"],
                bd=1,
                relief="flat",
                highlightthickness=1,
                highlightbackground=p["assistant_border"]
            )
            bubble.pack(side="left", padx=(2, 0))
            self._mark_custom_style(bubble)
            
            self._render_markdown_message(bubble, text, t)

        self._bind_scroll_tree(msg_container)
        msg_container.lift()

        self._messages_frame.update_idletasks()
        self._messages_content.update_idletasks()
        self._on_frame_configure()
        self._scroll_to_bottom()

        return msg_container

    def _render_markdown_message(self, parent, text, theme):
        """Renderiza texto con markdown y codigo resaltado."""
        code_pattern = re.compile(r"```([\w+-]*)[ \t]*\n(.*?)```", re.DOTALL)
        cursor = 0

        for match in code_pattern.finditer(text):
            start, end = match.span()
            plain = text[cursor:start]
            if plain.strip():
                self._add_text_block(parent, plain, theme)

            lang = (match.group(1) or "code").strip()
            code = match.group(2)
            self._add_code_block(parent, code, lang, theme)
            cursor = end

        remaining = text[cursor:]
        if remaining.strip():
            self._add_text_block(parent, remaining, theme)

    def _add_code_block(self, parent, code, lang, theme):
        """Agrega bloque de codigo con boton de copiar."""
        p = self._chat_palette(theme)
        code_frame = tk.Frame(
            parent,
            bg=p["code_bg"],
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=p["code_border"]
        )
        code_frame.pack(fill="x", padx=10, pady=8)
        self._mark_custom_style(code_frame)

        header = tk.Frame(code_frame, bg=p["code_header_bg"])
        header.pack(fill="x")
        self._mark_custom_style(header)

        lang_label = tk.Label(
            header,
            text=lang or "code",
            font=("Segoe UI Semibold", 9),
            bg=p["code_header_bg"],
            fg=p["text_muted"],
            padx=10,
            pady=4
        )
        lang_label.pack(side="left")
        self._mark_custom_style(lang_label)

        copied_text = "Copiado" if self.language_manager.current_language == "es" else "Copied"
        copy_text = "Copiar" if self.language_manager.current_language == "es" else "Copy"
        copy_btn = tk.Button(
            header,
            image=self._icons.get("code"),
            text=f" {copy_text}",
            compound="left",
            font=("Segoe UI Semibold", 9),
            bg=p["code_button_bg"],
            fg=p["code_button_fg"],
            activebackground=p["code_button_hover"],
            activeforeground=p["code_button_fg"],
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=10,
            pady=3,
            command=lambda: self._copy_code(code, copy_btn, copied_text, copy_text)
        )
        copy_btn.pack(side="right", padx=6, pady=4)
        self._mark_custom_style(copy_btn)

        code_text = tk.Text(
            code_frame,
            font=("Consolas", 10),
            bg=p["code_bg"],
            fg=p["code_fg"],
            insertbackground=p["code_fg"],
            wrap="none",
            relief="flat",
            padx=12,
            pady=10,
            height=min(20, code.count('\n') + 1)
        )
        code_text.insert("1.0", code)
        self._apply_syntax_highlighting(code_text, code, (lang or "code").lower(), p)
        code_text.configure(state="disabled")
        code_text.pack(fill="both", expand=True)
        self._bind_scroll_events(code_text)

        if code.strip() and max(len(line) for line in code.split('\n') if line) > 80:
            scrollbar = tk.Scrollbar(
                code_frame,
                orient="horizontal",
                command=code_text.xview,
                bg=p["panel_bg"],
                troughcolor=p["code_bg"],
                activebackground=p["code_button_hover"]
            )
            code_text.configure(xscrollcommand=scrollbar.set)
            scrollbar.pack(fill="x")
            self._mark_custom_style(scrollbar)

    def _add_text_block(self, parent, text, theme):
        """Agrega bloque de texto normal."""
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)

        clean_text = text.strip()
        if not clean_text:
            return
        clean_text = re.sub(r'^\s{0,3}#{1,6}\s*', '', clean_text, flags=re.MULTILINE)
        clean_text = self._normalize_emoji_text(clean_text)
        block_bg = parent.cget("bg")

        text_widget = tk.Text(
            parent,
            height=1,
            wrap="word",
            bd=0,
            relief="flat",
            bg=block_bg,
            fg=theme["fg"],
            insertbackground=theme["fg"],
            font=("Segoe UI", 10),
            padx=14,
            pady=7,
            highlightthickness=0,
            cursor="arrow"
        )
        text_widget.tag_configure("plain", font=("Segoe UI", 10))
        text_widget.tag_configure("emoji_fallback", font=("Segoe UI Emoji", 10))

        image_refs = []
        for token, is_emoji in self._tokenize_for_emoji(clean_text):
            if is_emoji:
                emoji_image = self._get_emoji_image(token, size=18)
                if emoji_image:
                    text_widget.image_create("end", image=emoji_image)
                    image_refs.append(emoji_image)
                else:
                    text_widget.insert("end", token, ("emoji_fallback",))
            else:
                text_widget.insert("end", token, ("plain",))

        text_widget.pack(fill="x")
        self._schedule_fit_text_widget_height(text_widget)
        text_widget.bind(
            "<Configure>",
            lambda e, w=text_widget: self._schedule_fit_text_widget_height(w),
            add="+",
        )
        text_widget.configure(state="disabled")
        text_widget._emoji_refs = image_refs
        self._mark_custom_style(text_widget)
        self._bind_scroll_events(text_widget)

    def _schedule_fit_text_widget_height(self, text_widget):
        """Programa ajuste de altura cuando el ancho real ya este aplicado."""
        try:
            if getattr(text_widget, "_fit_after_id", None):
                text_widget.after_cancel(text_widget._fit_after_id)
        except Exception:
            pass

        def _run():
            try:
                self._fit_text_widget_height(text_widget)
            finally:
                text_widget._fit_after_id = None

        try:
            text_widget._fit_after_id = text_widget.after_idle(_run)
        except Exception:
            self._fit_text_widget_height(text_widget)

    def _fit_text_widget_height(self, text_widget, max_lines=28):
        """Ajusta altura visual para evitar texto cortado."""
        try:
            text_widget.configure(state="normal")
            text_widget.update_idletasks()
            display_lines = int(text_widget.count("1.0", "end-1c", "displaylines")[0])
        except Exception:
            content = text_widget.get("1.0", "end-1c")
            display_lines = max(1, len(content.splitlines()))
        text_widget.configure(height=max(1, min(max_lines, display_lines)), state="disabled")

    def _contains_emoji(self, text):
        """Detecta si el texto contiene emojis Unicode."""
        for ch in text:
            cp = ord(ch)
            if (
                0x1F300 <= cp <= 0x1FAFF
                or 0x2600 <= cp <= 0x27BF
                or 0xFE00 <= cp <= 0xFE0F
            ):
                return True
        return False

    def _normalize_emoji_text(self, text):
        """Convierte emoticonos/kaomojis comunes a emojis Unicode."""
        replacements = [
            (r"(?<!\w):\)(?!\w)", "🙂"),
            (r"(?<!\w):-\)(?!\w)", "🙂"),
            (r"(?<!\w):D(?!\w)", "😄"),
            (r"(?<!\w):-D(?!\w)", "😄"),
            (r"(?<!\w)XD(?!\w)", "😆"),
            (r"(?<!\w)xD(?!\w)", "😆"),
            (r"(?<!\w):\((?!\w)", "🙁"),
            (r"(?<!\w):'\((?!\w)", "😢"),
            (r"(?<!\w):P(?!\w)", "😛"),
            (r"(?<!\w):p(?!\w)", "😛"),
            (r"(?<!\w);\)(?!\w)", "😉"),
            (r"(?<!\w):\|(?!\w)", "😐"),
            (r"(?<!\w):o(?!\w)", "😮"),
            (r"(?<!\w):O(?!\w)", "😮"),
            (r"(?<!\w)<3(?!\w)", "❤️"),
            (r"(?<!\w)</3(?!\w)", "💔"),
            (r"¯\\_\(ツ\)_/¯", "🤷"),
            (r"\^_\^", "😊"),
        ]

        normalized = text
        for pattern, emoji in replacements:
            normalized = re.sub(pattern, emoji, normalized)
        return normalized

    def _tokenize_for_emoji(self, text):
        """Tokeniza texto separando secuencias emoji para render en imagen."""
        tokens = []
        i = 0
        n = len(text)

        while i < n:
            ch = text[i]
            if not self._is_emoji_char(ch):
                start = i
                i += 1
                while i < n and not self._is_emoji_char(text[i]):
                    i += 1
                tokens.append((text[start:i], False))
                continue

            seq = [ch]
            i += 1

            # Variantes/modificadores inmediatos
            while i < n and (text[i] == "\ufe0f" or 0x1F3FB <= ord(text[i]) <= 0x1F3FF):
                seq.append(text[i])
                i += 1

            # Secuencias ZWJ
            while i + 1 < n and text[i] == "\u200d" and self._is_emoji_char(text[i + 1]):
                seq.append(text[i])      # ZWJ
                seq.append(text[i + 1])  # siguiente emoji
                i += 2
                while i < n and (text[i] == "\ufe0f" or 0x1F3FB <= ord(text[i]) <= 0x1F3FF):
                    seq.append(text[i])
                    i += 1

            tokens.append(("".join(seq), True))

        return tokens

    def _is_emoji_char(self, ch):
        cp = ord(ch)
        return (
            0x1F300 <= cp <= 0x1FAFF
            or 0x2600 <= cp <= 0x27BF
            or 0x1F1E6 <= cp <= 0x1F1FF
        )

    def _emoji_cache_key(self, emoji):
        return "-".join(f"{ord(c):x}" for c in emoji)

    def _twemoji_code(self, emoji):
        # Twemoji usa secuencia hex separada por '-'
        return "-".join(f"{ord(c):x}" for c in emoji)

    def _get_emoji_image(self, emoji, size=18):
        """Obtiene imagen emoji (cache local + descarga Twemoji)."""
        key = f"{self._emoji_cache_key(emoji)}_{size}"
        if key in self._emoji_images:
            return self._emoji_images[key]

        cache_dir = os.path.join("assets", "emojis", "twemoji")
        os.makedirs(cache_dir, exist_ok=True)

        code = self._twemoji_code(emoji)
        local_file = os.path.join(cache_dir, f"{code}.png")

        if not os.path.exists(local_file):
            url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{code}.png"
            try:
                urllib_request.urlretrieve(url, local_file)
            except Exception:
                return None

        try:
            img = Image.open(local_file).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._emoji_images[key] = photo
            return photo
        except Exception:
            return None

    def _copy_code(self, code, button=None, copied_text=None, default_text=None):
        """Copia codigo al clipboard con feedback."""
        try:
            self.clipboard_clear()
            self.clipboard_append(code)
            if button and copied_text and default_text:
                button.configure(text=f" {copied_text}")
                self.after(1200, lambda: button.winfo_exists() and button.configure(text=f" {default_text}"))
        except Exception as e:
            print(f"Error copiando codigo: {e}")

    def _apply_syntax_highlighting(self, text_widget, code, lang, palette):
        """Aplica resaltado simple de sintaxis en el bloque de codigo."""
        # Paleta de resaltado (oscura, legible en tema actual).
        colors = {
            "keyword": "#c792ea",
            "builtin": "#82aaff",
            "string": "#c3e88d",
            "number": "#f78c6c",
            "comment": "#637777",
            "operator": "#89ddff",
            "function": "#ffcb6b",
        }

        for tag, fg in colors.items():
            text_widget.tag_configure(tag, foreground=fg)

        # Comentarios
        self._tag_regex(text_widget, r"#.*$", "comment")

        # Strings (simples y dobles)
        self._tag_regex(text_widget, r"'(?:\\.|[^'\\])*'", "string")
        self._tag_regex(text_widget, r'"(?:\\.|[^"\\])*"', "string")

        # Numeros
        self._tag_regex(text_widget, r"\b\d+(?:\.\d+)?\b", "number")

        # Operadores y simbolos relevantes
        self._tag_regex(text_widget, r"==|!=|<=|>=|:=|->|=>|\+|\-|\*|/|%|=|<|>|\(|\)|\[|\]|\{|\}|:|,|\.", "operator")

        # Nombres de funcion (algo(...))
        self._tag_regex(text_widget, r"\b[A-Za-z_]\w*(?=\s*\()", "function")

        # Keywords segun lenguaje
        keywords = self._keywords_for_language(lang)
        if keywords:
            kw_pattern = r"\b(?:" + "|".join(re.escape(k) for k in sorted(keywords, key=len, reverse=True)) + r")\b"
            self._tag_regex(text_widget, kw_pattern, "keyword")

        # Builtins Python frecuentes
        if lang in ("py", "python"):
            builtins = {
                "print", "len", "range", "str", "int", "float", "dict", "list",
                "set", "tuple", "type", "isinstance", "enumerate", "zip", "map",
                "filter", "sum", "min", "max", "any", "all", "open"
            }
            bi_pattern = r"\b(?:" + "|".join(sorted(builtins)) + r")\b"
            self._tag_regex(text_widget, bi_pattern, "builtin")

    def _tag_regex(self, text_widget, pattern, tag):
        """Aplica un tag a todas las coincidencias regex en el widget Text."""
        content = text_widget.get("1.0", "end-1c")
        for match in re.finditer(pattern, content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            text_widget.tag_add(tag, start, end)

    def _keywords_for_language(self, lang):
        """Retorna keywords segun lenguaje."""
        if lang in ("py", "python"):
            return set(keyword.kwlist)
        if lang in ("js", "javascript", "ts", "typescript"):
            return {
                "const", "let", "var", "function", "return", "if", "else", "for",
                "while", "break", "continue", "switch", "case", "default", "class",
                "extends", "new", "try", "catch", "finally", "throw", "import",
                "from", "export", "async", "await", "true", "false", "null",
                "undefined", "this", "super", "typeof", "instanceof"
            }
        if lang in ("json",):
            return {"true", "false", "null"}
        if lang in ("bash", "sh", "shell", "zsh", "powershell", "ps1"):
            return {
                "if", "then", "fi", "for", "do", "done", "while", "case", "esac",
                "function", "return", "echo", "export"
            }
        return set()
    
    def _add_message(self, text: str, is_user: bool, show_model: bool = False, persist: bool = True):
        """Agrega un mensaje al chat y al historial."""
        frame = self._add_message_to_ui(text, is_user, show_model)
        
        self.chat_history.append({
            "text": text,
            "is_user": is_user,
            "frame": frame
        })

        if persist:
            self._save_history()
        
        return frame
    
    def _show_thinking(self):
        """Muestra indicador de pensamiento"""
        if self._is_thinking:
            return
        
        self._is_thinking = True
        self._set_chat_busy(True)
        thinking_text = self.language_manager.get_text('ai_thinking')
        self._thinking_frame = self._add_message_to_ui(thinking_text, is_user=False, show_model=True)
    
    def _hide_thinking(self):
        """Oculta indicador de pensamiento"""
        if self._is_thinking and hasattr(self, '_thinking_frame'):
            try:
                self._thinking_frame.destroy()
            except:
                pass
            self._is_thinking = False
            self._set_chat_busy(False)

    def _set_chat_busy(self, busy: bool):
        """Bloquea UI de envio mientras la IA responde."""
        state = "disabled" if busy else "normal"
        try:
            if hasattr(self, "_send_btn"):
                self._send_btn.configure(state=state)
            if hasattr(self, "_input_text"):
                self._input_text.configure(state=state)
            if hasattr(self, "_clear_btn"):
                self._clear_btn.configure(state=state)
        except Exception:
            pass
    
    # INPUT HANDLING
    
    def _show_placeholder(self):
        """Muestra placeholder"""
        placeholder = self.language_manager.get_text('ai_placeholder')
        self._input_text.insert("1.0", placeholder)
        self._input_text.config(fg="#888888")
        self._has_placeholder = True
    
    def _hide_placeholder(self):
        """Oculta placeholder"""
        if hasattr(self, '_has_placeholder') and self._has_placeholder:
            self._input_text.delete("1.0", "end")
            t = self.theme_manager.get_theme()
            self._input_text.config(fg=t["tree_fg"])
            self._has_placeholder = False
    
    def _on_input_focus_in(self, event):
        """Focus en input"""
        self._hide_placeholder()
        t = self.theme_manager.get_theme()
        self._input_outer.configure(highlightbackground=t["accent"], highlightthickness=2)
    
    def _on_input_focus_out(self, event):
        """Focus out de input"""
        if not self._input_text.get("1.0", "end-1c").strip():
            self._show_placeholder()
        t = self.theme_manager.get_theme()
        self._input_outer.configure(highlightthickness=1)
    
    def _on_enter_press(self, event):
        """Enviar con Enter"""
        self._send_message()
        return "break"
    
    def _get_input_text(self) -> str:
        """Obtiene texto del input"""
        text = self._input_text.get("1.0", "end-1c").strip()
        if hasattr(self, '_has_placeholder') and self._has_placeholder:
            return ""
        return text
    
    def _clear_input(self):
        """Limpia el input"""
        self._input_text.delete("1.0", "end")
        self._has_placeholder = False
        t = self.theme_manager.get_theme()
        self._input_text.config(fg=t["tree_fg"])
        # NO poner _show_placeholder() aquÃ­
    
    # CONTEXTO INTELIGENTE
    
    def _prepare_smart_context(self, selected_files):
        """Contexto inteligente con metadata"""
        if not selected_files:
            return ""
        
        context_parts = [f"Selected files ({len(selected_files)}):"]
        
        for filepath in selected_files:
            try:
                file_info = self.file_manager.get_file_info(filepath)
                if file_info:
                    name = os.path.basename(filepath)
                    ext = os.path.splitext(name)[1]
                    lines = file_info.get('lines', 0)
                    size = file_info.get('size', 0)
                    
                    context_parts.append(
                        f"- {name} ({ext}, {lines} lines, {size} bytes)"
                    )
            except:
                context_parts.append(f"- {os.path.basename(filepath)}")
        
        return "\n".join(context_parts)
    
    def _prepare_full_context(self, selected_files):
        """Contexto completo con contenido"""
        context_result = self.ai_manager.prepare_context(selected_files, self.file_manager)
        if isinstance(context_result, tuple):
            return context_result[0]
        return context_result
    
    def _update_token_display(self, usage: dict):
        """Actualiza el display de tokens"""
        if usage:
            total = usage.get("total_tokens", 0)
            prompt = usage.get("prompt_tokens", 0)
            completion = usage.get("completion_tokens", 0)
            
            self._token_label.configure(
                text=f"{total:,} tokens ({prompt:,}↑ + {completion:,}↓)"
            )
            self._save_history()
    
    # ACCIONES
    
    def _send_message(self):
        """EnvÃ­a mensaje a la IA"""
        if self._chat_request_in_flight or self._is_thinking:
            return

        text = self._get_input_text()
        if not text:
            return
        
        self._add_message(text, is_user=True)
        self._clear_input()  # â† Esto es suficiente
        
        selected_files = self.selection_manager.get_selected_files()
        
        context = ""
        if selected_files:
            if self.context_mode == "smart":
                context = self._prepare_smart_context(selected_files)
            else:
                context = self._prepare_full_context(selected_files)
        self._chat_request_in_flight = True
        self._show_thinking()

        def callback(result):
            self.after(0, lambda: self._handle_response(result))

        self.ai_manager.send_request_async(text, context, callback=callback)

    def _handle_response(self, result: dict):
        """Maneja respuesta de la IA"""
        self._hide_thinking()

        if result.get("success"):
            content = result.get("content", "")
            self._add_message(content, is_user=False, show_model=True)

            usage = result.get("usage", {})
            if usage:
                self._update_token_display(usage)
        else:
            error = result.get("error", "Unknown error")
            self._add_message(f"Error: {error}", is_user=False, show_model=True)

        self._chat_request_in_flight = False
    
    def _analyze_selected(self):
        """Analiza archivos seleccionados"""
        selected_files = self.selection_manager.get_selected_files()
        
        if not selected_files:
            messagebox.showwarning(
                self.language_manager.get_text('msg_warning'),
                self.language_manager.get_text('ai_no_files')
            )
            return
        
        analyze_text = self.language_manager.get_text('ai_analyze')
        self._add_message(f"{analyze_text} ({len(selected_files)} files)...", is_user=True)
        self._show_thinking()
        
        def callback(result):
            self.after(0, lambda: self._handle_response(result))
        
        import threading
        def worker():
            result = self.ai_manager.analyze_code(selected_files, self.file_manager)
            callback(result)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _fix_errors(self):
        """Corregir errores"""
        selected_files = self.selection_manager.get_selected_files()
        if not selected_files:
            messagebox.showwarning(
                self.language_manager.get_text('msg_warning'),
                self.language_manager.get_text('ai_no_files')
            )
            return
        
        fix_text = self.language_manager.get_text('ai_fix_errors')
        self._add_message(f"{fix_text}...", is_user=True)
        self._show_thinking()
        
        def callback(result):
            self.after(0, lambda: self._handle_response(result))
        
        import threading
        def worker():
            result = self.ai_manager.fix_code(selected_files, self.file_manager)
            callback(result)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _generate_docs(self):
        """Generar documentaciÃ³n"""
        selected_files = self.selection_manager.get_selected_files()
        if not selected_files:
            messagebox.showwarning(
                self.language_manager.get_text('msg_warning'),
                self.language_manager.get_text('ai_no_files')
            )
            return
        
        doc_text = self.language_manager.get_text('ai_document')
        self._add_message(f"{doc_text}...", is_user=True)
        self._show_thinking()
        
        def callback(result):
            self.after(0, lambda: self._handle_response(result))
        
        import threading
        def worker():
            result = self.ai_manager.generate_documentation(selected_files, self.file_manager)
            callback(result)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _optimize_code(self):
        """Optimizar cÃ³digo"""
        selected_files = self.selection_manager.get_selected_files()
        if not selected_files:
            messagebox.showwarning(
                self.language_manager.get_text('msg_warning'),
                self.language_manager.get_text('ai_no_files')
            )
            return
        
        optimize_text = self.language_manager.get_text('ai_optimize')
        self._add_message(f"{optimize_text}...", is_user=True)
        self._show_thinking()
        
        def callback(result):
            self.after(0, lambda: self._handle_response(result))
        
        import threading
        def worker():
            result = self.ai_manager.optimize_code(selected_files, self.file_manager)
            callback(result)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _explain_code(self):
        """Explicar cÃ³digo"""
        selected_files = self.selection_manager.get_selected_files()
        if not selected_files:
            messagebox.showwarning(
                self.language_manager.get_text('msg_warning'),
                self.language_manager.get_text('ai_no_files')
            )
            return
        
        explain_text = self.language_manager.get_text('ai_explain')
        self._add_message(f"{explain_text}...", is_user=True)
        self._show_thinking()
        
        def callback(result):
            self.after(0, lambda: self._handle_response(result))
        
        import threading
        def worker():
            result = self.ai_manager.explain_code(selected_files, self.file_manager)
            callback(result)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _clear_chat(self):
        """Limpia el chat"""
        for item in self.chat_history:
            try:
                frame = item.get("frame")
                if frame is not None:
                    frame.destroy()
            except:
                pass
        
        self.chat_history = []
        self._token_label.configure(text="0 tokens")
        self._save_history()
    
    def _show_model_selector(self):
        """Muestra selector de modelos con CustomToplevel"""
        if self._model_selector_window and self._model_selector_window.winfo_exists():
            try:
                self._model_selector_window.lift()
                self._model_selector_window.focus_force()
            except Exception:
                pass
            return

        if self._model_selector_open and (not self._model_selector_window or not self._model_selector_window.winfo_exists()):
            self._model_selector_open = False

        if getattr(self, "_model_selector_open", False):
            return

        self._model_selector_open = True
        
        models = self.ai_manager.get_available_models()
        
        if not models:
            self._add_message("No models available", is_user=False)
            self._model_selector_open = False
            return
        
        # Crear ventana personalizada
        selector = CustomToplevel(
            parent=self,
            theme_manager=self.theme_manager,
            title=self.language_manager.get_text('ai_select_model'),
            size="600x500",
            min_size=(500, 400)
        )
        self._model_selector_window = selector
        
        def on_close():
            self._model_selector_open = False
            self._model_selector_window = None
            try:
                selector.destroy()
            except Exception:
                pass

        def on_destroy(_event=None):
            self._model_selector_open = False
            self._model_selector_window = None

        selector.protocol("WM_DELETE_WINDOW", on_close)
        selector.bind("<Destroy>", on_destroy, add="+")

        t = self.theme_manager.get_theme()
        
        # TÃ­tulo
        title_label = tk.Label(
            selector.content_frame,
            text=self.language_manager.get_text('ai_select_model'),
            font=("Segoe UI", 16, "bold"),
            bg=t["secondary_bg"],
            fg=t["fg"]
        )
        title_label.pack(pady=(20, 10))
        
        # SubtÃ­tulo
        subtitle = tk.Label(
            selector.content_frame,
            text=self.language_manager.get_text("ai_select_model_subtitle"),
            font=("Segoe UI", 9),
            bg=t["secondary_bg"],
            fg=t["tree_fg"]
        )
        subtitle.pack(pady=(0, 20))
        
        # Frame con scroll para modelos
        list_frame = tk.Frame(selector.content_frame, bg=t["secondary_bg"])
        list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Crear botones para cada modelo
        for model in models:
            key = model.get('key', '')
            name = model.get('name', 'Unknown')
            model_id = model.get('model_id', '')
            is_custom = model.get('is_custom', False)
            self._ensure_model_logo_loaded(key)
            
            is_current = (key == self.ai_manager.current_model)
            
            # Frame del modelo
            model_frame = tk.Frame(
                list_frame,
                bg=t["tree_bg"] if is_current else t["bg"],
                relief="solid",
                bd=2 if is_current else 1,
                cursor="hand2",
                highlightbackground=t["accent"] if is_current else t["border"],
                highlightthickness=2 if is_current else 0
            )
            model_frame.pack(fill="x", pady=8)
            
            # Contenido interno
            inner_frame = tk.Frame(model_frame, bg=t["tree_bg"] if is_current else t["bg"])
            inner_frame.pack(fill="both", padx=15, pady=12)
            
            # Logo del modelo
            left_side = tk.Frame(inner_frame, bg=t["tree_bg"] if is_current else t["bg"])
            left_side.pack(side="left", fill="y")
            
            logo_label = None
            logo_image = self._model_logos.get(key) or self._icons.get("ai")
            if logo_image:
                logo_label = tk.Label(
                    left_side,
                    image=logo_image,
                    bg=t["tree_bg"] if is_current else t["bg"]
                )
                logo_label.image = logo_image
                logo_label.pack(side="left", padx=(0, 15))
            
            # Info del modelo
            info_frame = tk.Frame(inner_frame, bg=t["tree_bg"] if is_current else t["bg"])
            info_frame.pack(side="left", fill="both", expand=True)
            
            name_label = tk.Label(
                info_frame,
                text=name,
                font=("Segoe UI", 12, "bold"),
                bg=t["tree_bg"] if is_current else t["bg"],
                fg=t["accent"] if is_current else t["fg"],
                anchor="w"
            )
            name_label.pack(anchor="w", fill="x")
            
            if model_id:
                id_label = tk.Label(
                    info_frame,
                    text=model_id,
                    font=("Segoe UI", 9),
                    bg=t["tree_bg"] if is_current else t["bg"],
                    fg=t["tree_fg"],
                    anchor="w"
                )
                id_label.pack(anchor="w", fill="x", pady=(2, 0))
            
            # Badge de activo
            if is_current:
                badge_label = tk.Label(
                    inner_frame,
                    text=self.language_manager.get_text("ai_model_active_badge"),
                    font=("Segoe UI", 10, "bold"),
                    bg=t["accent"],
                    fg="#FFFFFF",
                    padx=15,
                    pady=8,
                    relief="flat"
                )
                badge_label.pack(side="right", padx=(10, 0))
            
            # BotÃ³n eliminar para modelos custom
            if is_custom:
                delete_btn = tk.Label(
                    inner_frame,
                    image=self._icons.get("clear"),  # Icono de basura
                    bg=t["tree_bg"] if is_current else t["bg"],
                    cursor="hand2",
                    padx=8
                )
                delete_btn.pack(side="right", padx=(5, 0))
                
                def delete_model(k=key, n=name):
                    # Crear variable para evitar acceso despuÃ©s de destroy
                    try:
                        # Quitar topmost temporalmente
                        selector.attributes('-topmost', False)
                        selector.update()
                        
                        # Mostrar diÃ¡logo de confirmaciÃ³n
                        result = messagebox.askyesno(
                            self.language_manager.get_text("ai_confirm"),
                            self.language_manager.get_text("ai_delete_model_confirm").format(name=n),
                            parent=self
                        )
                        
                        if result:
                            # Eliminar modelo
                            self.ai_manager.remove_custom_model(k)
                            
                            # Cerrar ventana actual
                            self._model_selector_open = False
                            try:
                                selector.destroy()
                            except:
                                pass
                            
                            # Reabrir despuÃ©s de un delay
                            self.after(150, self._show_model_selector)
                        else:
                            # Restaurar topmost si cancelÃ³
                            try:
                                selector.attributes('-topmost', True)
                            except:
                                pass
                    except Exception as e:
                        print(f"Error deleting model: {e}")
                        # Asegurar que la ventana se cierre
                        self._model_selector_open = False
                        try:
                            selector.destroy()
                        except:
                            pass
                
                delete_btn.bind("<Button-1>", lambda e, k=key, n=name: delete_model(k, n))
            
            # Bind click a todos los widgets (pero NO al delete_btn)
            def select_model(k=key):
                self._select_model(k)
                self._model_selector_open = False
                selector.destroy()
            
            clickable_widgets = [model_frame, inner_frame, left_side, info_frame, name_label]
            if logo_label is not None:
                clickable_widgets.append(logo_label)
            
            for widget in clickable_widgets:
                widget.bind("<Button-1>", lambda e, k=key: select_model(k))
            
            # Hover effect
            def on_enter(e, frame=model_frame, is_curr=is_current):
                if not is_curr:
                    frame.configure(bg=t["border"])
            
            def on_leave(e, frame=model_frame, is_curr=is_current):
                if not is_curr:
                    frame.configure(bg=t["bg"])
            
            model_frame.bind("<Enter>", on_enter)
            model_frame.bind("<Leave>", on_leave)
        
        # Separador
        sep = tk.Frame(selector.content_frame, height=2, bg=t["border"])
        sep.pack(fill="x", padx=30, pady=10)
        
        # BotOn agregar modelo
        def open_add_model_dialog():
            on_close()
            self.after(10, self._add_custom_model)

        add_btn = tk.Button(
            selector.content_frame,
            image=self._icons.get("settings"),  # o cualquier icono apropiado
            text=" " + self.language_manager.get_text('ai_add_custom_model'),
            compound="left",
            font=("Segoe UI", 11, "bold"),
            bg=t["button_bg"],
            fg=t["button_fg"],
            activebackground=t["button_hover"],
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=25,
            pady=12,
            command=open_add_model_dialog
        )
        add_btn.pack(pady=20)
        
        # Aplicar tema al selector
        selector.apply_base_theme()
    
    def _select_model(self, model_key: str):
        """Cambia el modelo con notificaciÃ³n visual"""
        if self.ai_manager.set_current_model(model_key):
            model_config = self.ai_manager.models.get(model_key, {})
            model_name = model_config.get('name', model_key)
            self._ensure_model_logo_loaded(model_key)
            
            # Mensaje de cambio
            changed_text = self.language_manager.get_text('ai_model_changed')
            self._add_message(f"{changed_text} {model_name}", is_user=False, show_model=True)
            
            # Actualizar UI del top bar
            if hasattr(self, '_model_name_label'):
                self._model_name_label.configure(text=model_name)
            
            if hasattr(self, '_model_id_label'):
                model_id = model_config.get("model_id", "")
                self._model_id_label.configure(text=model_id if model_id else "")
            
            # Actualizar logo con animaciÃ³n
            if hasattr(self, '_model_logo_label'):
                self._cancel_model_logo_animations()
                logo_image = self._model_logos.get(model_key) or self._icons.get("ai")
                if logo_image:
                    self._model_logo_label.configure(image=logo_image)
                    self._model_logo_label.image = logo_image
                if model_key in self._gif_frames:
                    # Iniciar nueva animaciÃ³n
                    self._animate_gif(self._model_logo_label, model_key)

            self._save_history()
    
    def _add_custom_model(self):
        """Agregar modelo custom con selector de logo"""
        if self._add_model_dialog_window and self._add_model_dialog_window.winfo_exists():
            try:
                self._add_model_dialog_window.lift()
                self._add_model_dialog_window.focus_force()
            except Exception:
                pass
            return

        if self._add_model_dialog_open and (not self._add_model_dialog_window or not self._add_model_dialog_window.winfo_exists()):
            self._add_model_dialog_open = False
            self._add_model_dialog_window = None

        if getattr(self, "_add_model_dialog_open", False):
            return
        
        self._add_model_dialog_open = True
        
        dialog = CustomToplevel(
            parent=self,
            theme_manager=self.theme_manager,
            title=self.language_manager.get_text('ai_add_custom_model'),
            size="550x750",
            min_size=(500, 700)
        )
        self._add_model_dialog_window = dialog

        def on_dialog_close():
            self._add_model_dialog_open = False
            self._add_model_dialog_window = None
            try:
                self.language_manager.unsubscribe(update_dialog_texts)
            except Exception:
                pass
            dialog.destroy()

        def on_dialog_destroy(_event=None):
            self._add_model_dialog_open = False
            self._add_model_dialog_window = None
            try:
                self.language_manager.unsubscribe(update_dialog_texts)
            except Exception:
                pass

        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        dialog.bind("<Destroy>", on_dialog_destroy, add="+")
        try:
            dialog.lift()
            dialog.focus_force()
        except Exception:
            pass
        
        t = self.theme_manager.get_theme()
        
        # TÃ­tulo
        title_label = tk.Label(
            dialog.content_frame,
            text=self.language_manager.get_text('ai_add_custom_model'),
            font=("Segoe UI", 16, "bold"),
            bg=t["secondary_bg"],
            fg=t["fg"]
        )
        title_label.pack(pady=(20, 10))
        
        # SubtÃ­tulo
        subtitle = tk.Label(
            dialog.content_frame,
            text=self.language_manager.get_text("ai_add_model_subtitle"),
            font=("Segoe UI", 9),
            bg=t["secondary_bg"],
            fg=t["tree_fg"]
        )
        subtitle.pack(pady=(0, 25))
        
        # Frame de formulario
        form_frame = tk.Frame(dialog.content_frame, bg=t["secondary_bg"])
        form_frame.pack(fill="both", expand=True, padx=40)
        
        entries = {}
        field_labels = {}
        
        # Campos del formulario
        fields = [
            (self.language_manager.get_text("ai_model_name_label"), "name", self.language_manager.get_text("ai_model_name_placeholder")),
            (self.language_manager.get_text("ai_model_id_label"), "model_id", self.language_manager.get_text("ai_model_id_placeholder")),
            (self.language_manager.get_text("ai_api_key_label"), "api_key", ""),
            (self.language_manager.get_text("ai_description_label"), "description", self.language_manager.get_text("ai_description_placeholder")),
        ]
        
        for label_text, key, placeholder in fields:
            label = tk.Label(
                form_frame,
                text=label_text,
                font=("Segoe UI", 10, "bold"),
                bg=t["secondary_bg"],
                fg=t["fg"],
                anchor="w"
            )
            label.pack(anchor="w", pady=(10, 5))
            field_labels[key] = label
            
            entry = tk.Entry(
                form_frame,
                font=("Segoe UI", 10),
                bg=t["tree_bg"],
                fg=t["tree_fg"],
                insertbackground=t["fg"],
                relief="flat",
                bd=1,
                highlightthickness=1,
                highlightbackground=t["border"],
                highlightcolor=t["accent"]
            )
            entry.pack(fill="x", ipady=8)
            
            if placeholder:
                entry.insert(0, placeholder)
                entry.config(fg=t["tree_fg"])
            
            entries[key] = entry
        
        # MÃ¡ximo de tokens
        max_tokens_label = tk.Label(
            form_frame,
            text=self.language_manager.get_text("ai_max_tokens_label"),
            font=("Segoe UI", 10, "bold"),
            bg=t["secondary_bg"],
            fg=t["fg"],
            anchor="w"
        )
        max_tokens_label.pack(anchor="w", pady=(10, 5))
        
        max_tokens_spinbox = tk.Spinbox(
            form_frame,
            from_=1000,
            to=200000,
            increment=1000,
            font=("Segoe UI", 10),
            bg=t["tree_bg"],
            fg=t["tree_fg"],
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        max_tokens_spinbox.delete(0, "end")
        max_tokens_spinbox.insert(0, "8000")
        max_tokens_spinbox.pack(fill="x", ipady=8)
        entries["max_tokens"] = max_tokens_spinbox
        
        # NUEVO: Campo para logo
        logo_label = tk.Label(
            form_frame,
            text=self.language_manager.get_text("ai_custom_logo_label"),
            font=("Segoe UI", 10, "bold"),
            bg=t["secondary_bg"],
            fg=t["fg"],
            anchor="w"
        )
        logo_label.pack(anchor="w", pady=(10, 5))
        
        logo_frame = tk.Frame(form_frame, bg=t["secondary_bg"])
        logo_frame.pack(fill="x")
        
        logo_path_var = tk.StringVar()
        
        logo_entry = tk.Entry(
            logo_frame,
            textvariable=logo_path_var,
            font=("Segoe UI", 10),
            bg=t["tree_bg"],
            fg=t["tree_fg"],
            state="readonly",
            relief="flat",
            bd=1
        )
        logo_entry.pack(side="left", fill="x", expand=True, ipady=8)
        
        def select_logo():
            from tkinter import filedialog
            filepath = filedialog.askopenfilename(
                title=self.language_manager.get_text("ai_select_logo_title"),
                filetypes=[(self.language_manager.get_text("ai_image_filetypes"), "*.png *.gif")]
            )
            if filepath:
                logo_path_var.set(filepath)
                
        logo_btn = tk.Button(
            logo_frame,
            image=self._icons.get("document"),
            text=" " + self.language_manager.get_text("ai_browse"),
            compound="left",
            font=("Segoe UI", 9),
            bg=t["button_bg"],
            fg=t["button_fg"],
            cursor="hand2",
            bd=0,
            padx=12,
            pady=6,
            command=select_logo
        )
        logo_btn.pack(side="right", padx=(5, 0))
        
        # Botones Guardar / Cancelar
        button_frame = tk.Frame(dialog.content_frame, bg=t["secondary_bg"])
        button_frame.pack(pady=25)
        
        def on_save():
            try:
                model_data = {
                    "name": entries["name"].get().strip(),
                    "model_id": entries["model_id"].get().strip(),
                    "api_key": entries["api_key"].get().strip(),
                    "description": entries["description"].get().strip(),
                    "max_tokens": int(entries["max_tokens"].get()),
                    "logo_path": logo_path_var.get() or None
                }
                
                if not model_data["name"] or not model_data["model_id"]:
                    messagebox.showerror(
                        self.language_manager.get_text("msg_error"),
                        self.language_manager.get_text("ai_name_model_required")
                    )
                    return
                
                key = f"custom_{model_data['name'].lower().replace(' ', '_')}"
                
                self.ai_manager.add_custom_model(
                    key=key,
                    name=model_data["name"],
                    model_id=model_data["model_id"],
                    api_key=model_data["api_key"],
                    description=model_data.get("description", ""),
                    max_tokens=model_data.get("max_tokens", 8000),
                    logo_path=model_data.get("logo_path")
                )
                
                self._add_model_dialog_open = False
                dialog.destroy()
                self._select_model(key)
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        save_btn = tk.Button(
            button_frame,
            text=self.language_manager.get_text("ai_add"),
            font=("Segoe UI", 11, "bold"),
            bg=t["button_bg"],
            fg=t["button_fg"],
            activebackground=t["button_hover"],
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=30,
            pady=10,
            command=on_save
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text=self.language_manager.get_text("ai_cancel"),
            font=("Segoe UI", 10),
            bg=t["bg"],
            fg=t["fg"],
            activebackground=t["border"],
            cursor="hand2",
            bd=1,
            relief="solid",
            padx=25,
            pady=10,
            command=on_dialog_close
        )
        cancel_btn.pack(side="left", padx=5)

        def update_dialog_texts():
            try:
                dialog.title(self.language_manager.get_text('ai_add_custom_model'))
                title_label.configure(text=self.language_manager.get_text('ai_add_custom_model'))
                subtitle.configure(text=self.language_manager.get_text("ai_add_model_subtitle"))

                field_labels["name"].configure(text=self.language_manager.get_text("ai_model_name_label"))
                field_labels["model_id"].configure(text=self.language_manager.get_text("ai_model_id_label"))
                field_labels["api_key"].configure(text=self.language_manager.get_text("ai_api_key_label"))
                field_labels["description"].configure(text=self.language_manager.get_text("ai_description_label"))

                max_tokens_label.configure(text=self.language_manager.get_text("ai_max_tokens_label"))
                logo_label.configure(text=self.language_manager.get_text("ai_custom_logo_label"))
                logo_btn.configure(text=" " + self.language_manager.get_text("ai_browse"))
                save_btn.configure(text=self.language_manager.get_text("ai_add"))
                cancel_btn.configure(text=self.language_manager.get_text("ai_cancel"))
            except Exception:
                pass

        self.language_manager.subscribe(update_dialog_texts)
        
        dialog.apply_base_theme()

    
    # THEMING
    
    def _chat_palette(self, t):
        """Paleta visual estilo chat moderno."""
        return {
            "panel_bg": t["secondary_bg"],
            "chat_bg": t["bg"],
            "line": t["border"],
            "text_primary": t["fg"],
            "text_secondary": t["tree_fg"],
            "text_muted": t["tree_fg"],
            "user_bubble": t["button_bg"],
            "user_border": t["button_hover"],
            "user_text": t["button_fg"],
            "assistant_bubble": t["secondary_bg"],
            "assistant_border": t["border"],
            "code_bg": t["tree_bg"],
            "code_fg": t["tree_fg"],
            "code_border": t["border"],
            "code_header_bg": t["border"],
            "code_button_bg": t["button_bg"],
            "code_button_hover": t["button_hover"],
            "code_button_fg": t["button_fg"],
        }

    def _mark_custom_style(self, widget):
        """Marca widgets para no sobrescribir su estilo en theme recursivo."""
        try:
            setattr(widget, "_ai_custom_style", True)
        except Exception:
            pass

    def apply_theme(self):
        """Aplica el tema (override de CustomToplevel)"""
        self.apply_base_theme()  # Aplicar tema base de CustomToplevel
        
        # Luego aplica el tema especÃ­fico de AIWindow
        t = self.theme_manager.get_theme()
        p = self._chat_palette(t)
        
        bg = t["bg"]
        sec_bg = t["secondary_bg"]
        fg = t["fg"]
        border = t["border"]
        tree_bg = t["tree_bg"]
        tree_fg = t["tree_fg"]
        accent = t["accent"]
        btn_bg = t["button_bg"]
        btn_fg = t["button_fg"]
        btn_hover = t["button_hover"]
        
        try:
            # ... resto de tu cÃ³digo de theming existente
            # Aplicar recursivamente
            self._apply_theme_recursive(self.content_frame, t)

            if hasattr(self, "_top_bar"):
                self._top_bar.configure(bg=p["panel_bg"])
            if hasattr(self, "_toolbar"):
                self._toolbar.configure(bg=p["panel_bg"])
            if hasattr(self, "_input_container"):
                self._input_container.configure(bg=p["panel_bg"])
            if hasattr(self, "_main_container"):
                self._main_container.configure(bg=p["chat_bg"])
            if hasattr(self, "_sep1"):
                self._sep1.configure(bg=p["line"])
            if hasattr(self, "_sep2"):
                self._sep2.configure(bg=p["line"])
            if hasattr(self, "_sep3"):
                self._sep3.configure(bg=p["line"])
             
            # Canvas y scrollbar
            if hasattr(self, '_chat_canvas'):
                self._chat_canvas.configure(bg=p["chat_bg"])
                self._messages_frame.configure(bg=p["chat_bg"])
                if hasattr(self, "_messages_content"):
                    self._messages_content.configure(bg=p["chat_bg"])
            
            if hasattr(self, '_scrollbar'):
                self._scrollbar.configure(
                    bg=sec_bg,
                    troughcolor=p["chat_bg"],
                    activebackground=accent
                )
            
            # Input
            if hasattr(self, '_input_text'):
                self._input_text.configure(
                    bg=tree_bg,
                    fg=tree_fg,
                    insertbackground=fg
                )
                self._input_outer.configure(bg=tree_bg, highlightbackground=border)
            
            # Botones
            if hasattr(self, '_send_btn'):
                self._send_btn.configure(bg=btn_bg, fg=btn_fg, activebackground=btn_hover)
            
            if hasattr(self, '_clear_btn'):
                self._clear_btn.configure(bg=sec_bg, fg=fg, activebackground=border, highlightbackground=border, relief="flat", bd=0)
            
            if hasattr(self, '_context_btn'):
                self._context_btn.configure(bg=sec_bg, fg=fg, activebackground=border, highlightbackground=border, relief="flat", bd=0)
             
            if hasattr(self, '_models_btn'):
                self._models_btn.configure(bg=sec_bg, fg=fg, activebackground=border, highlightbackground=border, relief="flat", bd=0)
             
            # Action buttons
            if hasattr(self, '_action_buttons'):
                for btn in self._action_buttons:
                    btn.configure(bg=sec_bg, fg=fg, activebackground=border, highlightbackground=border, relief="flat", bd=0)
        
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def _apply_theme_recursive(self, widget, t):
        """Aplica tema recursivamente"""
        if getattr(widget, "_ai_custom_style", False):
            return

        bg = t["bg"]
        sec_bg = t["secondary_bg"]
        fg = t["fg"]
        
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=sec_bg)
            elif isinstance(widget, tk.Label):
                widget.configure(bg=sec_bg, fg=fg)
        except:
            pass
        
        for child in widget.winfo_children():
            self._apply_theme_recursive(child, t)
    
    def _bind_hover(self, btn, primary=False, action=False):
        """Hover effect"""
        def on_enter(e):
            t = self.theme_manager.get_theme()
            if primary:
                btn.configure(bg=t["button_hover"])
            else:
                btn.configure(bg=t["border"])
        
        def on_leave(e):
            t = self.theme_manager.get_theme()
            if primary:
                btn.configure(bg=t["button_bg"])
            else:
                btn.configure(bg=t["secondary_bg"])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

"""
Startup preloader for Code Tools++.
Shows a loading window while warming managers and resources.
"""

import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Callable, Dict
import random
import math

from utils.helpers import resource_path
from utils import (
    ThemeManager,
    ConfigManager,
    FileIconManager,
    AlertManager,
    LanguageManager,
)
from core import FileManager, SelectionManager, CodeAnalyzer, ExportManager, ProjectStats


class _StartupSplash(tk.Toplevel):
    """Simple startup splash with progress."""

    def __init__(self, root, theme):
        super().__init__(root)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=theme["border"])

        w, h = 520, 220
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = int((sw - w) / 2), int((sh - h) / 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        panel = tk.Frame(self, bg=theme["secondary_bg"], padx=20, pady=20)
        panel.pack(fill="both", expand=True, padx=1, pady=1)

        self._title = tk.Label(
            panel,
            text="Code Tools ++",
            bg=theme["secondary_bg"],
            fg=theme["fg"],
            font=("Segoe UI", 16, "bold"),
            anchor="w",
        )
        self._title.pack(fill="x")

        self._message = tk.Label(
            panel,
            text="Loading resources...",
            bg=theme["secondary_bg"],
            fg=theme["tree_fg"],
            font=("Segoe UI", 10),
            anchor="w",
            pady=14,
        )
        self._message.pack(fill="x")

        style = ttk.Style(self)
        style.configure(
            "Startup.Horizontal.TProgressbar",
            troughcolor=theme["border"],
            background=theme["accent"],
            bordercolor=theme["border"],
            lightcolor=theme["accent"],
            darkcolor=theme["accent"],
            thickness=8,
        )
        self._bar = ttk.Progressbar(
            panel,
            style="Startup.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=0,
            length=440,
        )
        self._bar.pack(fill="x", pady=(4, 10))

        self._percent = tk.Label(
            panel,
            text="0%",
            bg=theme["secondary_bg"],
            fg=theme["tree_fg"],
            font=("Segoe UI", 9),
            anchor="e",
        )
        self._percent.pack(fill="x")

    def update_state(self, message: str, progress: int):
        self._message.configure(text=message)
        self._bar["value"] = max(0, min(100, progress))
        self._percent.configure(text=f"{int(self._bar['value'])}%")
        self.update_idletasks()


class _WelcomeLauncher(tk.Toplevel):
    """Launcher visual with animated starfield + image start button."""

    def __init__(self, root, theme, texts):
        super().__init__(root)
        self.started = False
        self._icon_photo = None
        self._start_img_normal = None
        self._start_img_hover = None
        self._start_img_pressed = None
        self._drag_x = 0
        self._drag_y = 0
        self._after_ids = []
        self._stars = []
        self._star_streaks = []
        self._scene_t = 0.0
        self._frame_i = 0
        self._card_center = (0, 0)
        self._last_canvas_size = (0, 0)

        self._theme = theme
        self._colors = self._build_palette(theme)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=self._colors["border"])

        w, h = 820, 500
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self._target_x = int((sw - w) / 2)
        self._target_y = int((sh - h) / 2)
        self.geometry(f"{w}x{h}+{self._target_x}+{self._target_y}")

        shell = tk.Frame(self, bg=self._colors["border"], padx=1, pady=1)
        shell.pack(fill="both", expand=True)

        panel = tk.Frame(shell, bg=self._colors["bg"])
        panel.pack(fill="both", expand=True)

        top_bar = tk.Frame(panel, bg=self._colors["top_bg"], height=40)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)
        self._bind_drag(top_bar)

        title = tk.Label(
            top_bar,
            text="Code Tools ++",
            bg=self._colors["top_bg"],
            fg=self._colors["text"],
            font=("Segoe UI", 10, "bold"),
            padx=12,
        )
        title.pack(side="left")
        self._bind_drag(title)

        close_btn = tk.Button(
            top_bar,
            text="x",
            bg=self._colors["top_bg"],
            fg=self._colors["text"],
            activebackground=self._colors["close_hover"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=5,
            font=("Segoe UI", 11, "bold"),
            command=self._close,
        )
        close_btn.pack(side="right", padx=6, pady=4)
        close_btn.bind("<Enter>", lambda _e: close_btn.configure(bg=self._colors["close_hover"]))
        close_btn.bind("<Leave>", lambda _e: close_btn.configure(bg=self._colors["top_bg"]))

        self._canvas = tk.Canvas(
            panel,
            bg=self._colors["bg"],
            bd=0,
            highlightthickness=0,
            relief="flat",
        )
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<Configure>", self._on_canvas_resize)

        self._card = tk.Frame(
            self._canvas,
            bg=self._colors["card_bg"],
            bd=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self._colors["card_border"],
            padx=54,
            pady=32,
        )
        self._card_window = self._canvas.create_window(0, 0, window=self._card, anchor="center")

        icon_label = tk.Label(self._card, bg=self._colors["card_bg"])
        icon_label.pack(pady=(0, 12))
        self._load_app_icon(icon_label)

        tk.Label(
            self._card,
            text="Code Tools ++",
            bg=self._colors["card_bg"],
            fg=self._colors["text"],
            font=("Segoe UI", 28, "bold"),
        ).pack()

        tk.Label(
            self._card,
            text=texts["subtitle"],
            bg=self._colors["card_bg"],
            fg=self._colors["muted"],
            font=("Segoe UI", 11),
            pady=10,
        ).pack()

        self._build_start_control(texts["start"])

        self.bind("<Escape>", lambda _e: self._close())
        self.bind("<Destroy>", self._on_destroy, add="+")

        self._seed_stars()
        self._animate_intro()
        self._animate_scene()

    def _build_palette(self, t):
        base_bg = t.get("bg", "#111827")
        sec = t.get("secondary_bg", "#1f2937")
        border = t.get("border", "#374151")
        accent = t.get("accent", "#3b82f6")
        dark_bg = self._mix_color(base_bg, "#000000", 0.45)
        return {
            "bg": dark_bg,
            "top_bg": self._mix_color(sec, "#000000", 0.35),
            # Visual "transparency": closer to background while preserving readability.
            "card_bg": self._mix_color(sec, dark_bg, 0.55),
            "card_border": border,
            "border": border,
            "text": t.get("fg", "#e5e7eb"),
            "muted": t.get("tree_fg", "#9ca3af"),
            "accent": accent,
            "accent_soft": self._mix_color(accent, dark_bg, 0.45),
            "button_bg": t.get("button_bg", accent),
            "button_hover": t.get("button_hover", self._shift_color(accent, 18)),
            "button_fg": t.get("button_fg", "#ffffff"),
            "close_hover": "#e25363",
        }

    def _build_start_control(self, fallback_text):
        container = tk.Frame(self._card, bg=self._colors["card_bg"])
        container.pack(pady=(14, 0))

        ep_path = Path(resource_path("assets/logos/ep.png"))
        if ep_path.exists():
            try:
                from PIL import Image, ImageTk, ImageEnhance

                img = Image.open(ep_path).convert("RGBA")
                max_w, max_h = 260, 82
                scale = min(max_w / img.width, max_h / img.height, 1.0)
                size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
                base = img.resize(size, Image.Resampling.LANCZOS)
                hover = ImageEnhance.Brightness(base).enhance(1.08)
                pressed = ImageEnhance.Brightness(base).enhance(0.92)

                self._start_img_normal = ImageTk.PhotoImage(base)
                self._start_img_hover = ImageTk.PhotoImage(hover)
                self._start_img_pressed = ImageTk.PhotoImage(pressed)

                btn_canvas = tk.Canvas(
                    container,
                    width=size[0],
                    height=size[1],
                    bg=self._colors["card_bg"],
                    highlightthickness=0,
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                )
                btn_canvas.pack()

                image_id = btn_canvas.create_image(size[0] / 2, size[1] / 2, image=self._start_img_normal)
                # Ajuste fino del texto sobre la imagen del boton.
                # Cambia estos dos valores para moverlo a tu gusto.
                TEXT_OFFSET_X = -5   # negativo = izquierda, positivo = derecha
                TEXT_OFFSET_Y = -3   # negativo = arriba, positivo = abajo
                cx = (size[0] / 2) + TEXT_OFFSET_X
                cy = (size[1] / 2) + TEXT_OFFSET_Y
                text_shadow = btn_canvas.create_text(
                    cx + 1,
                    cy + 1,
                    text=fallback_text,
                    fill=self._mix_color("#000000", self._colors["card_bg"], 0.7),
                    font=("Segoe UI", 13, "bold"),
                )
                text_id = btn_canvas.create_text(
                    cx,
                    cy,
                    text=fallback_text,
                    fill=self._colors["button_fg"],
                    font=("Segoe UI", 13, "bold"),
                )

                def set_state(name):
                    if name == "hover":
                        btn_canvas.itemconfig(image_id, image=self._start_img_hover)
                    elif name == "pressed":
                        btn_canvas.itemconfig(image_id, image=self._start_img_pressed)
                    else:
                        btn_canvas.itemconfig(image_id, image=self._start_img_normal)

                def on_enter(_e):
                    set_state("hover")

                def on_leave(_e):
                    set_state("normal")

                def on_press(_e):
                    set_state("pressed")

                def on_release(_e):
                    set_state("hover")
                    self._start()

                btn_canvas.bind("<Enter>", on_enter)
                btn_canvas.bind("<Leave>", on_leave)
                btn_canvas.bind("<ButtonPress-1>", on_press)
                btn_canvas.bind("<ButtonRelease-1>", on_release)
                btn_canvas.tag_bind(text_id, "<ButtonPress-1>", on_press)
                btn_canvas.tag_bind(text_id, "<ButtonRelease-1>", on_release)
                btn_canvas.tag_bind(text_shadow, "<ButtonPress-1>", on_press)
                btn_canvas.tag_bind(text_shadow, "<ButtonRelease-1>", on_release)
                return
            except Exception:
                pass

        fallback = tk.Button(
            container,
            text=fallback_text,
            bg=self._colors["button_bg"],
            fg=self._colors["button_fg"],
            activebackground=self._colors["button_hover"],
            activeforeground=self._colors["button_fg"],
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=28,
            pady=10,
            font=("Segoe UI", 12, "bold"),
            command=self._start,
        )
        fallback.pack()
        fallback.bind("<Enter>", lambda _e: fallback.configure(bg=self._colors["button_hover"]))
        fallback.bind("<Leave>", lambda _e: fallback.configure(bg=self._colors["button_bg"]))

    def _bind_drag(self, widget):
        widget.bind("<Button-1>", self._start_drag)
        widget.bind("<B1-Motion>", self._do_drag)

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_x)
        y = self.winfo_y() + (event.y - self._drag_y)
        self.geometry(f"+{x}+{y}")

    def _on_canvas_resize(self, _event=None):
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        self._card_center = (w / 2, h / 2 + 2)
        self._canvas.coords(self._card_window, self._card_center[0], self._card_center[1])
        self._draw_background(w, h)
        if w > 10 and h > 10 and (not self._stars or self._last_canvas_size != (w, h)):
            self._seed_stars(w, h)
            self._last_canvas_size = (w, h)

    def _draw_background(self, w, h):
        self._canvas.delete("bg")
        self._canvas.create_rectangle(0, 0, w, h, fill=self._colors["bg"], outline="", tags="bg")
        self._canvas.tag_lower("bg")

    def _seed_stars(self, w=None, h=None):
        self._stars.clear()
        self._star_streaks.clear()
        self._canvas.delete("star")
        self._canvas.delete("star_streak")
        w = max(1, int(w or self._canvas.winfo_width() or self.winfo_width()))
        h = max(1, int(h or self._canvas.winfo_height() or self.winfo_height()))
        # 3 layers for smooth depth/parallax.
        layers = [
            {"count": 70, "size": (0.8, 1.3), "vx": (-0.10, 0.10), "vy": (0.08, 0.30), "mix": (0.22, 0.38)},
            {"count": 55, "size": (1.2, 1.9), "vx": (-0.16, 0.16), "vy": (0.22, 0.62), "mix": (0.34, 0.50)},
            {"count": 30, "size": (1.8, 2.8), "vx": (-0.24, 0.24), "vy": (0.36, 0.96), "mix": (0.52, 0.74)},
        ]
        for layer_idx, layer in enumerate(layers):
            for _ in range(layer["count"]):
                s = random.uniform(layer["size"][0], layer["size"][1])
                x = random.uniform(0, w)
                y = random.uniform(0, h)
                vy = random.uniform(layer["vy"][0], layer["vy"][1])
                vx = random.uniform(layer["vx"][0], layer["vx"][1])
                phase = random.uniform(0.0, 6.283)
                twinkle_speed = random.uniform(0.05, 0.13)
                # Mantener alto contraste aunque el tema sea muy gris/rosa.
                tone = random.uniform(layer["mix"][0], layer["mix"][1])
                color = self._mix_color("#dff6ff", "#ffffff", tone)
                sid = self._canvas.create_oval(x, y, x + s, y + s, fill=color, outline="", tags=f"star_l{layer_idx}")
                self._stars.append({
                    "id": sid,
                    "x": x,
                    "y": y,
                    "s": s,
                    "vx": vx,
                    "vy": vy,
                    "p": phase,
                    "ps": twinkle_speed,
                    "c": color,
                })

        # Sparse moving streaks (shooting-star-like ambience).
        for _ in range(6):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            ln = random.uniform(18, 34)
            streak_id = self._canvas.create_line(
                x, y, x - ln, y + (ln * 0.8),
                fill=self._mix_color("#b3ecff", "#ffffff", 0.7),
                width=1.2,
                capstyle="round",
                tags="star_streak",
            )
            self._star_streaks.append({
                "id": streak_id,
                "x": x,
                "y": y,
                "len": ln,
                "vx": random.uniform(1.1, 2.8),
                "vy": random.uniform(0.7, 1.9),
            })
        # Fondo: estrellas detras de la card. En el primer frame puede no existir "bg".
        try:
            if self._canvas.find_withtag("bg"):
                self._canvas.tag_raise("star", "bg")
                self._canvas.tag_raise("star_streak", "bg")
            else:
                self._canvas.tag_raise("star")
                self._canvas.tag_raise("star_streak")
            self._canvas.tag_lower("star", self._card_window)
            self._canvas.tag_lower("star_streak", self._card_window)
        except Exception:
            pass

    def _animate_scene(self):
        if not self.winfo_exists():
            return

        self._scene_t += 0.055
        self._frame_i += 1
        w = max(1, self._canvas.winfo_width())
        h = max(1, self._canvas.winfo_height())

        twinkle_bucket = self._frame_i % 3
        for idx, star in enumerate(self._stars):
            star["x"] += star["vx"]
            star["y"] += star["vy"]
            if idx % 3 == twinkle_bucket:
                star["p"] += star["ps"]

            if star["y"] > h + 6:
                star["y"] = -6
                star["x"] = random.uniform(0, w)
            if star["x"] < -6:
                star["x"] = w + 6
            elif star["x"] > w + 6:
                star["x"] = -6

            glow = 0.42 + 0.58 * ((math.sin(star["p"]) + 1.0) * 0.5)
            self._canvas.coords(star["id"], star["x"], star["y"], star["x"] + star["s"], star["y"] + star["s"])
            if idx % 3 == twinkle_bucket:
                mixed = self._mix_color(star["c"], self._colors["bg"], 0.30 + glow * 0.70)
                self._canvas.itemconfig(star["id"], fill=mixed)

        for streak in self._star_streaks:
            streak["x"] += streak["vx"]
            streak["y"] += streak["vy"]
            if streak["x"] > w + 40 or streak["y"] > h + 30:
                streak["x"] = random.uniform(-120, -20)
                streak["y"] = random.uniform(-50, h * 0.55)
                streak["len"] = random.uniform(18, 34)
                streak["vx"] = random.uniform(1.1, 2.8)
                streak["vy"] = random.uniform(0.7, 1.9)
            x = streak["x"]
            y = streak["y"]
            ln = streak["len"]
            self._canvas.coords(streak["id"], x, y, x - ln, y + (ln * 0.8))

        if self._card_center != (0, 0):
            float_y = self._card_center[1] + math.sin(self._scene_t * 0.85) * 5.0
            self._canvas.coords(self._card_window, self._card_center[0], float_y)

        self._queue_after(14, self._animate_scene)

    def _animate_intro(self):
        start_y = self._target_y + 22
        steps = 14
        for i in range(steps + 1):
            ratio = i / float(steps)
            y = int(start_y - (22 * ratio))
            alpha = max(0.0, min(1.0, ratio))
            self._queue_after(i * 18, lambda y=y, alpha=alpha: self._set_intro_state(y, alpha))

    def _set_intro_state(self, y, alpha):
        if not self.winfo_exists():
            return
        self.geometry(f"+{self._target_x}+{y}")
        try:
            self.attributes("-alpha", alpha)
        except Exception:
            pass

    def _queue_after(self, ms, callback):
        holder = {"id": None}

        def wrapped():
            aid = holder["id"]
            if aid in self._after_ids:
                self._after_ids.remove(aid)
            callback()

        holder["id"] = self.after(ms, wrapped)
        self._after_ids.append(holder["id"])

    def _on_destroy(self, _event=None):
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()

    def _load_app_icon(self, target_label):
        icon_path = Path(resource_path("icon.ico"))
        if not icon_path.exists():
            return

        try:
            self.iconbitmap(str(icon_path))
        except Exception:
            pass

        try:
            from PIL import Image, ImageTk

            img = Image.open(icon_path).convert("RGBA")
            img = img.resize((84, 84), Image.Resampling.LANCZOS)
            self._icon_photo = ImageTk.PhotoImage(img)
            target_label.configure(image=self._icon_photo)
        except Exception:
            pass

    def _start(self):
        self.started = True
        self.destroy()

    def _close(self):
        self.started = False
        self.destroy()

    def _shift_color(self, hex_color, delta):
        r, g, b = self._hex_to_rgb(hex_color)
        r = max(0, min(255, r + delta))
        g = max(0, min(255, g + delta))
        b = max(0, min(255, b + delta))
        return self._rgb_to_hex(r, g, b)

    def _mix_color(self, c1, c2, c1_ratio=0.5):
        c1_ratio = max(0.0, min(1.0, c1_ratio))
        r1, g1, b1 = self._hex_to_rgb(c1)
        r2, g2, b2 = self._hex_to_rgb(c2)
        r = int((r1 * c1_ratio) + (r2 * (1.0 - c1_ratio)))
        g = int((g1 * c1_ratio) + (g2 * (1.0 - c1_ratio)))
        b = int((b1 * c1_ratio) + (b2 * (1.0 - c1_ratio)))
        return self._rgb_to_hex(r, g, b)

    def _hex_to_rgb(self, color):
        color = color.lstrip("#")
        if len(color) != 6:
            return (32, 32, 32)
        return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))

    def _rgb_to_hex(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"


def _startup_texts(language_manager: LanguageManager) -> Dict[str, str]:
    lang = getattr(language_manager, "current_language", "en")
    if lang == "es":
        return {
            "loading": "Cargando recursos...",
            "managers": "Inicializando modulos...",
            "icons": "Precargando iconos...",
            "images": "Precargando imagenes...",
            "modules": "Optimizando ventanas...",
            "ready": "Listo. Abriendo aplicacion...",
        }
    if lang == "zh":
        return {
            "loading": "æ­£åœ¨åŠ è½½èµ„æº...",
            "managers": "æ­£åœ¨åˆå§‹åŒ–æ¨¡å—...",
            "icons": "æ­£åœ¨é¢„åŠ è½½å›¾æ ‡...",
            "images": "æ­£åœ¨é¢„åŠ è½½å›¾ç‰‡...",
            "modules": "æ­£åœ¨ä¼˜åŒ–çª—å£...",
            "ready": "å°±ç»ªã€‚æ­£åœ¨æ‰“å¼€åº”ç”¨...",
        }
    return {
        "loading": "Loading resources...",
        "managers": "Initializing modules...",
        "icons": "Preloading icons...",
        "images": "Preloading images...",
        "modules": "Optimizing windows...",
        "ready": "Ready. Opening app...",
    }


def _launcher_texts(language_manager: LanguageManager) -> Dict[str, str]:
    lang = getattr(language_manager, "current_language", "en")

    if lang == "es":
        return {
            "start": "Empezar",
            "subtitle": "Análisis y productividad para tu código"
        }

    if lang == "zh":
        return {
            "start": "开始",
            "subtitle": "为你的代码提供分析与效率"
        }

    if lang == "ru":
        return {
            "start": "Начать",
            "subtitle": "Анализ и продуктивность для вашего кода"
        }

    return {
        "start": "Start",
        "subtitle": "Analysis and productivity for your code"
    }


def _warm_icon_manager(icon_manager: FileIconManager):
    icon_names = [
        "folder_open.png", "recent.png", "search.png", "preview.png", "copy.png",
        "clear.png", "about_feature_export.png", "ai.gif", "dashboard.png",
        "markdown.png", "todo.png", "duplicate.png", "theme.png", "language.png",
        "keyboard.png", "about.png", "send.png", "trash.png", "settings.png",
        "scan.png", "code.png", "document.png", "performance.png", "help.png",
        "user.png", "file.png", "folder.png", "folder-open.png",
    ]
    sizes = [(16, 16), (18, 18), (20, 20), (24, 24)]
    for icon in icon_names:
        for size in sizes:
            try:
                icon_manager.load_icon(icon, size=size)
            except Exception:
                continue


def _warm_image_decoding(max_files: int = 420):
    try:
        from PIL import Image
    except Exception:
        return

    roots = [
        Path(resource_path("assets/icons")),
        Path(resource_path("assets/logos")),
        Path(resource_path("assets/emojis/twemoji")),
    ]

    count = 0
    for root in roots:
        if not root.exists():
            continue
        for file_path in root.rglob("*"):
            if count >= max_files:
                return
            if file_path.suffix.lower() not in {".png", ".gif", ".jpg", ".jpeg", ".webp"}:
                continue
            try:
                with Image.open(file_path) as img:
                    img.load()
                count += 1
            except Exception:
                continue


def _warm_heavy_modules():
    # Imports cost at first use, so warm them during splash.
    import gui.dashboard_window  # noqa: F401
    import gui.ai_window  # noqa: F401
    import gui.search_dialog  # noqa: F401
    import gui.readme_generator_dialog  # noqa: F401
    import gui.preview_window  # noqa: F401


def run_app_with_preload(main_window_cls: Callable):
    """
    Bootstraps the app with a startup splash and resource preloading.
    `main_window_cls` should be gui.MainWindow.
    """
    root = tk.Tk()
    root.withdraw()

    config_manager = ConfigManager()
    theme_manager = ThemeManager(config_manager)
    language_manager = LanguageManager(config_manager)

    theme = theme_manager.get_theme()
    launcher = _WelcomeLauncher(root, theme, _launcher_texts(language_manager))
    root.wait_window(launcher)
    if not launcher.started:
        root.destroy()
        return

    texts = _startup_texts(language_manager)
    splash = _StartupSplash(root, theme)
    splash.update_state(texts["loading"], 4)
    root.update()

    file_manager = FileManager()
    selection_manager = SelectionManager()
    code_analyzer = CodeAnalyzer()
    project_stats = ProjectStats()
    alert_manager = AlertManager()
    icon_manager = FileIconManager()
    export_manager = ExportManager(file_manager)

    splash.update_state(texts["managers"], 18)
    root.update()

    _warm_icon_manager(icon_manager)
    splash.update_state(texts["icons"], 50)
    root.update()

    _warm_image_decoding()
    splash.update_state(texts["images"], 74)
    root.update()

    _warm_heavy_modules()
    splash.update_state(texts["modules"], 92)
    root.update()

    preloaded = {
        "config_manager": config_manager,
        "theme_manager": theme_manager,
        "language_manager": language_manager,
        "icon_manager": icon_manager,
        "alert_manager": alert_manager,
        "file_manager": file_manager,
        "selection_manager": selection_manager,
        "code_analyzer": code_analyzer,
        "project_stats": project_stats,
        "export_manager": export_manager,
    }

    splash.update_state(texts["ready"], 100)
    root.update()
    splash.destroy()

    main_window_cls(root, preloaded=preloaded)
    try:
        root.state("zoomed")
    except Exception:
        try:
            root.attributes("-zoomed", True)
        except Exception:
            pass
    root.deiconify()
    root.mainloop()

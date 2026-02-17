import tkinter as tk
import os
from PIL import Image, ImageTk
from gui.components.animated_starfield import AnimatedStarfield
from utils.helpers import resource_path


class CustomToolbar(tk.Frame):
    """
    Toolbar profesional.
    - Botones sin fondo visible (secondary_bg)
    - Pack directo sin canvas: se adapta automáticamente al ancho disponible
    - Scroll horizontal con rueda si no caben todos los botones
    """

    def __init__(self, parent, theme_manager, icon_manager, language_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_manager    = theme_manager
        self.icon_manager     = icon_manager
        self.language_manager = language_manager
        self.buttons          = {}
        self._separators      = []
        self._icon_refs       = {}
        self._zoom_group      = None
        self._starfield       = None
        self._fx_top_starfield = None
        self._fx_bottom_starfield = None

        self.configure(relief="flat", bd=0)
        self._setup_scroll_container()

    def _setup_scroll_container(self):
        t  = self.theme_manager.get_theme()
        bg = self._toolbar_bg()
        self.configure(bg=bg)

        self._fx_top = tk.Canvas(
            self, height=6, bd=0, highlightthickness=0, bg=bg
        )
        self._fx_top.pack(fill="x", side="top")

        # Canvas para scroll horizontal cuando sea necesario
        self._canvas = tk.Canvas(
            self, height=50, bd=0,
            highlightthickness=0, bg=bg
        )
        self._canvas.pack(fill="both", expand=True)

        self._fx_bottom = tk.Canvas(
            self, height=6, bd=0, highlightthickness=0, bg=bg
        )
        self._fx_bottom.pack(fill="x", side="bottom")

        # Frame interno — se crea en after para que canvas esté renderizado
        self._inner = tk.Frame(self._canvas, bg=bg, pady=0)
        self._cwin  = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )
        self._starfield = AnimatedStarfield(
            canvas=self._canvas,
            theme_manager=self.theme_manager,
            tag_prefix="toolbar_starfield",
            layer="above",
            density=0.00045,
            min_stars=20,
            max_stars=110,
            interval_ms=30,
        )
        self._starfield.set_below(self._cwin)
        self._starfield.set_enabled(self._is_bar_animation_enabled())
        self._starfield.start()

        self._fx_top_starfield = AnimatedStarfield(
            canvas=self._fx_top,
            theme_manager=self.theme_manager,
            tag_prefix="toolbar_fx_top_starfield",
            density=0.0020,
            min_stars=16,
            max_stars=72,
            interval_ms=32,
        )
        self._fx_top_starfield.set_enabled(self._is_bar_animation_enabled())
        self._fx_top_starfield.start()

        self._fx_bottom_starfield = AnimatedStarfield(
            canvas=self._fx_bottom,
            theme_manager=self.theme_manager,
            tag_prefix="toolbar_fx_bottom_starfield",
            density=0.0020,
            min_stars=16,
            max_stars=72,
            interval_ms=32,
        )
        self._fx_bottom_starfield.set_enabled(self._is_bar_animation_enabled())
        self._fx_bottom_starfield.start()

        # Bindings
        self._inner.bind("<Configure>", self._on_content_change)
        self._canvas.bind("<Configure>", self._on_canvas_resize, add="+")

        for w in (self._canvas, self._inner):
            w.bind("<MouseWheel>", self._hscroll)
            w.bind("<Button-4>",   self._hscroll)
            w.bind("<Button-5>",   self._hscroll)

    # ──────────────────────────────────────────────────────────────────
    # SCROLL Y ADAPTACIÓN
    # ──────────────────────────────────────────────────────────────────

    def _on_content_change(self, event=None):
        """Se llama cuando cambia el tamaño del inner (botones agregados)."""
        try:
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        except Exception:
            pass
        # Diferir adapt para que winfo_width esté actualizado
        self.after(10, self._adapt)

    def _on_canvas_resize(self, event=None):
        """Se llama cuando la ventana se redimensiona."""
        try:
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        except Exception:
            pass
        self.after(10, self._adapt)

    def _adapt(self):
        """
        Expande el inner al ancho del canvas si los botones caben.
        Si no caben, deja tamaño natural y activa scroll.
        """
        try:
            cw = self._canvas.winfo_width()
            iw = self._inner.winfo_reqwidth()
            if cw < 10:
                self.after(50, self._adapt)
                return
            
            if iw <= cw:
                # Caben todos: expandir para llenar el ancho
                self._canvas.itemconfig(self._cwin, width=cw)
                self._canvas.xview_moveto(0)
            else:
                # No caben: ancho natural + SCROLL HABILITADO
                self._canvas.itemconfig(self._cwin, width=iw)
                # Configurar scrollregion para habilitar scroll
                self._canvas.configure(scrollregion=self._canvas.bbox("all"))
                
        except Exception:
            pass

    def _hscroll(self, event):
        try:
            if hasattr(event, "delta") and event.delta != 0:
                d = -1 if event.delta > 0 else 1
            else:
                d = -1 if event.num == 4 else 1
            self._canvas.xview_scroll(d, "units")
        except Exception:
            pass

    def _bs(self, w):
        """Bind scroll en widget hijo."""
        w.bind("<MouseWheel>", self._hscroll, add="+")
        w.bind("<Button-4>",   self._hscroll, add="+")
        w.bind("<Button-5>",   self._hscroll, add="+")

    # ──────────────────────────────────────────────────────────────────
    # API PÚBLICA
    # ──────────────────────────────────────────────────────────────────

    def add_button(self, name, text, command, icon_name="",
                tooltip="", icon_only=False):
        t  = self.theme_manager.get_theme()
        bg = self._toolbar_bg()
        fg = t["fg"]

        if icon_name == "ai.gif":
            ico = self._load_icon(name, icon_name, size=(27, 27), bg=bg)

        elif icon_name == "limpmax.gif":
            ico = self._load_icon(name, icon_name, size=(27, 27), bg=bg)

        else:
            ico = self._load_icon(name, icon_name, bg=bg)



        kw = dict(
            command=command,
            bg=bg, fg=fg,
            activebackground=bg,  # ← CAMBIO: Sin hover visible
            activeforeground=fg,
            relief="flat", bd=0,
            font=("Segoe UI", 10, "bold"),  # ← CAMBIO: Más grande y negrita
            cursor="hand2",
            padx=12, pady=0,
        )
        if ico:
            kw.update(image=ico, text=f" {text}", compound="left")
            btn = tk.Button(self._inner, **kw)
            btn.image = ico
        else:
            kw["text"] = text
            btn = tk.Button(self._inner, **kw)

        btn.pack(side="left", padx=2, pady=5)
        self._bs(btn)
        self._hover(btn)  # Hover sutil
        if tooltip:
            self._tooltip(btn, tooltip)

        self.buttons[name] = btn
        # 🔥 Si el icono es GIF, iniciar animación
        if name in self._icon_refs and "frames" in self._icon_refs[name]:
            frames = self._icon_refs[name]["frames"]

            def animate(index=0):
                if not btn.winfo_exists():
                    return
                btn.configure(image=frames[index])
                btn.image = frames[index]
                btn.after(100, animate, (index + 1) % len(frames))

            animate()

        return btn

    def add_separator(self):
        t   = self.theme_manager.get_theme()
        sep = tk.Frame(self._inner, width=1, bg=t["border"])
        sep.pack(side="left", fill="y", padx=5, pady=10)
        self._bs(sep)
        self._separators.append(sep)
        return sep

    def add_zoom_group(self, zoom_out_cmd, zoom_reset_cmd, zoom_in_cmd,
                    initial_text="100%",
                    tooltip_out=None, tooltip_reset=None, tooltip_in=None):
        t  = self.theme_manager.get_theme()
        bg = self._toolbar_bg()
        fg = t["fg"]

        group = tk.Frame(
            self._inner, bd=0,
            highlightthickness=1,
            highlightbackground=t["border"],
            bg=bg
        )
        group.pack(side="left", padx=4, pady=10)
        self._bs(group)

        def _zbtn(txt, cmd, key, w):
            btn = tk.Button(
                group, text=txt, command=cmd,
                bg=bg, fg=fg,
                activebackground=bg,  # ← CAMBIO: Sin hover visible
                activeforeground=fg,
                relief="flat", bd=0,
                font=("Segoe UI", 10, "bold"),  # ← CAMBIO: Más grande y negrita
                cursor="hand2",
                padx=5, pady=2, width=w
            )
            btn.pack(side="left")
            self._bs(btn)
            self._hover(btn)
            self.buttons[key] = btn
            return btn

        b_out   = _zbtn("−",          zoom_out_cmd,   "zoom_out",   2)
        b_reset = _zbtn(initial_text, zoom_reset_cmd, "zoom_reset", 5)
        b_in    = _zbtn("+",          zoom_in_cmd,    "zoom_in",    2)

        if tooltip_out:   self._tooltip(b_out,   tooltip_out)
        if tooltip_reset: self._tooltip(b_reset, tooltip_reset)
        if tooltip_in:    self._tooltip(b_in,    tooltip_in)

        self._zoom_group = group
        return group

    def reset(self):
        """Limpia botones sin destruir el canvas. Usar desde update_ui_language."""
        if self._inner and self._inner.winfo_exists():
            for child in list(self._inner.winfo_children()):
                try:
                    child.destroy()
                except Exception:
                    pass
        self.buttons.clear()
        self._separators.clear()
        self._zoom_group = None
        self._icon_refs.clear()
        try:
            self._canvas.xview_moveto(0)
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────────────
    # TEMA
    # ──────────────────────────────────────────────────────────────────

    def apply_theme(self):
        t      = self.theme_manager.get_theme()
        bg     = self._toolbar_bg()
        fg     = t["fg"]
        border = t["border"]
        hover  = t.get("button_hover", border)

        self.configure(bg=bg)
        self._fx_top.configure(bg=bg)
        self._canvas.configure(bg=bg)
        self._fx_bottom.configure(bg=bg)
        if self._inner and self._inner.winfo_exists():
            self._inner.configure(bg=bg)
        if self._starfield:
            self._starfield.update_theme()
            self._starfield.set_enabled(self._is_bar_animation_enabled())
        if self._fx_top_starfield:
            self._fx_top_starfield.update_theme()
            self._fx_top_starfield.set_enabled(self._is_bar_animation_enabled())
        if self._fx_bottom_starfield:
            self._fx_bottom_starfield.update_theme()
            self._fx_bottom_starfield.set_enabled(self._is_bar_animation_enabled())

        for key, btn in self.buttons.items():
            if not btn or not btn.winfo_exists():
                continue
            try:
                if key in self._icon_refs:
                    ico_name = self._icon_refs[key].get("name")
                    if ico_name:
                        new_ico = self._load_icon(key, ico_name, bg=bg)
                        if new_ico:
                            btn.configure(image=new_ico)
                            btn.image = new_ico
                btn.configure(bg=bg, fg=fg,
                              activebackground=hover, activeforeground=fg)
            except Exception:
                pass

        for sep in self._separators:
            try:
                if sep.winfo_exists():
                    sep.configure(bg=border)
            except Exception:
                pass

        if self._zoom_group and self._zoom_group.winfo_exists():
            self._zoom_group.configure(bg=bg, highlightbackground=border)
            for child in self._zoom_group.winfo_children():
                if isinstance(child, tk.Button) and child.winfo_exists():
                    child.configure(bg=bg, fg=fg,
                                    activebackground=hover, activeforeground=fg)

    # ──────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────

    def _load_icon(self, key, icon_name, size=(18, 18), bg=None):
        if not icon_name:
            return None

        try:
            t    = self.theme_manager.get_theme()
            bg   = bg or self._toolbar_bg()
            path = os.path.join(resource_path("assets/icons"), icon_name)

            if not os.path.exists(path):
                return None

            # 🔥 SI ES GIF → animarlo
            if icon_name.lower().endswith(".gif"):
                gif = Image.open(path)
                frames = []

                try:
                    while True:
                        frame = gif.copy().convert("RGBA").resize(
                            size, Image.Resampling.LANCZOS
                        )
                        # Mantener alpha del GIF (no aplanar a RGB) para evitar fondo negro.
                        photo = ImageTk.PhotoImage(frame)
                        frames.append(photo)

                        gif.seek(len(frames))
                except EOFError:
                    pass

                if not frames:
                    return None

                self._icon_refs[key] = {"frames": frames, "name": icon_name}
                return frames[0]


                def animate(index=0):
                    if not button.winfo_exists():
                        return
                    button.configure(image=frames[index])
                    button.image = frames[index]
                    button.after(100, animate, (index + 1) % len(frames))

                # Guardar frames
                self._icon_refs[key] = {"frames": frames, "name": icon_name}

                animate()
                return frames[0]

            # 🧱 SI NO ES GIF → comportamiento normal
            img = Image.open(path).convert("RGBA").resize(
                size, Image.Resampling.LANCZOS)

            h   = bg.lstrip("#")
            rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            base = Image.new("RGBA", img.size, rgb + (255,))
            base.paste(img, mask=img.split()[3])

            photo = ImageTk.PhotoImage(base.convert("RGB"))
            self._icon_refs[key] = {"photo": photo, "name": icon_name}
            return photo

        except Exception as e:
            print(f"[Toolbar] '{icon_name}': {e}")
            return None


    def _hover(self, btn):
        """Hover apenas perceptible - casi invisible"""
        def on_enter(e):
            try:
                t = self.theme_manager.get_theme()
                bg = t["secondary_bg"]
                # CAMBIO: Solo 3 puntos de diferencia (imperceptible)
                h = bg.lstrip("#")
                r, g, b = [int(h[i:i+2], 16) for i in (0, 2, 4)]
                r = min(255, r + 3)
                g = min(255, g + 3)
                b = min(255, b + 3)
                hover_color = f"#{r:02x}{g:02x}{b:02x}"
                btn.configure(bg=hover_color)
            except Exception:
                pass
        
        def on_leave(e):
            try:
                btn.configure(bg=self._toolbar_bg())
            except Exception:
                pass
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _tooltip(self, widget, text):
        """Tooltip que solo aparece al pasar el mouse"""
        tip = None
        show_timer = None
        
        def show(e):
            nonlocal tip, show_timer
            # Cancelar si ya hay un timer
            if show_timer:
                widget.after_cancel(show_timer)
            
            # Mostrar después de 500ms
            def _show():
                nonlocal tip
                try:
                    if tip:  # Si ya existe, destruirlo primero
                        tip.destroy()
                    
                    x = widget.winfo_rootx()
                    y = widget.winfo_rooty() + widget.winfo_height() + 4
                    tip = tk.Toplevel(widget)
                    tip.wm_overrideredirect(True)
                    tip.wm_geometry(f"+{x}+{y}")
                    t = self.theme_manager.get_theme()
                    lbl = tk.Label(tip, text=text, 
                                font=("Segoe UI", 8),
                                bg=t["secondary_bg"], 
                                fg=t["fg"],
                                relief="solid", 
                                bd=1, 
                                padx=8, 
                                pady=4)
                    lbl.pack()
                    tip.lift()
                except Exception:
                    pass
            
            show_timer = widget.after(500, _show)
        
        def hide(e):
            nonlocal tip, show_timer
            # Cancelar timer si existe
            if show_timer:
                widget.after_cancel(show_timer)
                show_timer = None
            # Destruir tooltip si existe
            try:
                if tip:
                    tip.destroy()
                    tip = None
            except Exception:
                pass
        
        # IMPORTANTE: Solo bind a Enter/Leave, NO a Button
        widget.bind("<Enter>", show, add="+")
        widget.bind("<Leave>", hide, add="+")
        # Asegurar que se oculte al hacer clic
        widget.bind("<Button-1>", hide, add="+")

    def _is_bar_animation_enabled(self):
        cfg = getattr(self.theme_manager, "config_manager", None)
        if not cfg:
            return True
        return bool(cfg.get("animated_toolbar_background", True))

    def _toolbar_bg(self):
        t = self.theme_manager.get_theme()
        return self._mix_colors(t.get("secondary_bg", "#252526"), t.get("bg", "#1e1e1e"), 0.55)

    def _mix_colors(self, c1, c2, ratio=0.5):
        ratio = max(0.0, min(1.0, ratio))
        r1, g1, b1 = self._hex_to_rgb(c1)
        r2, g2, b2 = self._hex_to_rgb(c2)
        r = int((r1 * ratio) + (r2 * (1.0 - ratio)))
        g = int((g1 * ratio) + (g2 * (1.0 - ratio)))
        b = int((b1 * ratio) + (b2 * (1.0 - ratio)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _hex_to_rgb(self, color):
        color = str(color).lstrip("#")
        if len(color) != 6:
            return (37, 37, 38)
        return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))

    def enable_button(self, name):
        if name in self.buttons:
            try:
                self.buttons[name].configure(state="normal")
            except Exception:
                pass

    def disable_button(self, name):
        if name in self.buttons:
            try:
                self.buttons[name].configure(state="disabled")
            except Exception:
                pass

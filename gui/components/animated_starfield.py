import math
import math
import random


class AnimatedStarfield:
    """
    Reusable starfield animation for any tkinter Canvas.
    Draws only moving/twinkling dots (no streak lines).
    """

    def __init__(
        self,
        canvas,
        theme_manager,
        tag_prefix="starfield",
        layer="below",
        lock_to_viewport=False,
        density=0.00032,
        min_stars=24,
        max_stars=140,
        interval_ms=22,
    ):
        self.canvas = canvas
        self.theme_manager = theme_manager
        self.tag_prefix = tag_prefix
        self.layer = layer
        self.lock_to_viewport = bool(lock_to_viewport)
        self.density = density
        self.min_stars = min_stars
        self.max_stars = max_stars
        self.interval_ms = interval_ms

        self._enabled = True
        self._stars = []
        self._after_id = None
        self._frame_i = 0
        self._size = (0, 0)
        self._below_item = None
        self._last_viewport = (0.0, 0.0)

        self.canvas.bind("<Configure>", self._on_canvas_configure, add="+")

    def set_enabled(self, enabled):
        enabled = bool(enabled)
        if self._enabled == enabled:
            return
        self._enabled = enabled
        if enabled:
            self._reseed()
            self.start()
        else:
            self.stop()
            self._clear()

    def set_below(self, item_id):
        self._below_item = item_id
        self._apply_layering()

    def set_layer(self, layer):
        self.layer = "above" if str(layer).lower() == "above" else "below"
        self._apply_layering()

    def refresh_layering(self):
        self._apply_layering()

    def force_restart(self):
        """Force reseed + start (useful when canvas gets sized after creation)."""
        self.stop()
        self._size = (max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height()))
        self._reseed()
        self.start()

    def update_theme(self):
        if not self._stars:
            return
        fg, bg = self._star_palette()
        for star in self._stars:
            star["base"] = self._mix_color(fg, bg, star["mix"])

    def start(self):
        if not self._enabled or self._after_id is not None:
            return
        if not self._stars:
            w = max(1, self.canvas.winfo_width())
            h = max(1, self.canvas.winfo_height())
            if (w, h) != self._size:
                self._size = (w, h)
            if w > 1 and h > 1:
                self._reseed()
        self._tick()

    def stop(self):
        if self._after_id is not None:
            try:
                self.canvas.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def destroy(self):
        self.stop()
        self._clear()

    def _on_canvas_configure(self, event=None):
        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())
        if (w, h) != self._size:
            self._size = (w, h)
            if self._enabled:
                self._reseed()
                self.start()

    def _reseed(self):
        self._clear()
        w, h = self._size
        if w <= 1 or h <= 1:
            return

        target_count = int(w * h * self.density)
        target_count = max(self.min_stars, min(self.max_stars, target_count))
        fg, bg = self._star_palette()
        x0, y0 = self._view_origin()

        for _ in range(target_count):
            size = random.choice((1.0, 1.2, 1.5, 1.8, 2.1))
            if self.lock_to_viewport:
                x = random.uniform(0, w)
                y = random.uniform(0, h)
                draw_x = x0 + x
                draw_y = y0 + y
            else:
                x = random.uniform(x0, x0 + w)
                y = random.uniform(y0, y0 + h)
                draw_x = x
                draw_y = y
            vx = random.uniform(-0.08, 0.08)
            vy = random.uniform(0.06, 0.42)
            phase = random.uniform(0.0, 6.283)
            tw = random.uniform(0.05, 0.14)
            mix = random.uniform(0.30, 0.78)
            base_color = self._mix_color(fg, bg, mix)
            item_id = self.canvas.create_oval(
                draw_x,
                draw_y,
                draw_x + size,
                draw_y + size,
                fill=base_color,
                outline="",
                tags=(self.tag_prefix, f"{self.tag_prefix}_dot"),
            )
            self._stars.append(
                {
                    "id": item_id,
                    "x": x,
                    "y": y,
                    "s": size,
                    "vx": vx,
                    "vy": vy,
                    "p": phase,
                    "tw": tw,
                    "mix": mix,
                    "base": base_color,
                }
            )

        self._apply_layering()

    def _apply_layering(self):
        try:
            if self.layer == "above":
                if self._below_item is not None:
                    self.canvas.tag_raise(self.tag_prefix, self._below_item)
                    self.canvas.tag_lower(self._below_item, self.tag_prefix)
                else:
                    self.canvas.tag_raise(self.tag_prefix)
            else:
                if self._below_item is not None:
                    self.canvas.tag_lower(self.tag_prefix, self._below_item)
                else:
                    self.canvas.tag_lower(self.tag_prefix)
        except Exception:
            pass

    def _tick(self):
        if not self._enabled:
            self._after_id = None
            return
        if not self.canvas.winfo_exists():
            self._after_id = None
            return

        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())
        x0, y0 = self._view_origin()
        
        # Detectar cambio de viewport (scroll)
        last_x0, last_y0 = self._last_viewport
        dy = y0 - last_y0
        
        # ✅ Si el viewport se movió mucho (ej: nuevo mensaje), reposicionar estrellas
        if self.lock_to_viewport and abs(dy) > h * 0.3:
            # Viewport se movió significativamente - reposicionar todas las estrellas
            for star in self._stars:
                # Mantener posición relativa al nuevo viewport
                star["x"] = random.uniform(0, w)
                star["y"] = random.uniform(0, h)
        
        self._last_viewport = (x0, y0)
        
        self._frame_i += 1
        bucket = self._frame_i % 3
        bg = self._star_palette()[1]

        for idx, star in enumerate(self._stars):
            # Mover estrellas con su velocidad
            star["x"] += star["vx"]
            star["y"] += star["vy"]
            
            # Actualizar fase de twinkle
            if idx % 3 == bucket:
                star["p"] += star["tw"]

            if self.lock_to_viewport:
                # ✅ Mantener estrellas dentro del viewport visible
                # Wraparound en coordenadas relativas (0 a w, 0 a h)
                if star["y"] > h + 4:
                    star["y"] = -4
                    star["x"] = random.uniform(0, w)
                elif star["y"] < -4:
                    star["y"] = h + 4
                    star["x"] = random.uniform(0, w)
                    
                if star["x"] > w + 4:
                    star["x"] = -4
                elif star["x"] < -4:
                    star["x"] = w + 4
                
                # Dibujar en coordenadas absolutas del canvas
                draw_x = x0 + star["x"]
                draw_y = y0 + star["y"]
            else:
                # Modo normal: coordenadas absolutas
                x_min = x0 - 4
                x_max = x0 + w + 4
                y_min = y0 - 4
                y_max = y0 + h + 4
                
                if star["y"] > y_max:
                    star["y"] = y_min
                    star["x"] = random.uniform(x0, x0 + w)
                elif star["y"] < y_min:
                    star["y"] = y_max
                    star["x"] = random.uniform(x0, x0 + w)
                    
                if star["x"] > x_max:
                    star["x"] = x_min
                elif star["x"] < x_min:
                    star["x"] = x_max
                    
                draw_x = star["x"]
                draw_y = star["y"]

            # Actualizar posición visual
            self.canvas.coords(
                star["id"],
                draw_x,
                draw_y,
                draw_x + star["s"],
                draw_y + star["s"],
            )

            # Actualizar color con twinkle
            if idx % 3 == bucket:
                glow = 0.42 + 0.58 * ((math.sin(star["p"]) + 1.0) * 0.5)
                tone = 0.58 + glow * 0.42
                color = self._mix_color(star["base"], bg, tone)
                self.canvas.itemconfig(star["id"], fill=color)

        # Some tkinter canvas window-items can end up above regular items
        # after geometry reflows; enforce desired layering continuously.
        self._apply_layering()
        self._after_id = self.canvas.after(self.interval_ms, self._tick)

    def _clear(self):
        self.canvas.delete(self.tag_prefix)
        self._stars.clear()

    def _star_palette(self):
        t = self.theme_manager.get_theme()
        bg = self.canvas.cget("bg") or t.get("secondary_bg", "#1b1f27")
        luma = self._luminance(bg)

        accent = t.get("accent", "#7cc4ff")
        if luma >= 0.65:
            fg = self._mix_color(accent, "#000000", 0.70)
        elif luma <= 0.28:
            fg = self._mix_color(accent, "#ffffff", 0.30)
        else:
            fg = self._mix_color(accent, "#ffffff", 0.48 if luma < 0.5 else 0.40)

        return fg, bg

    def _mix_color(self, c1, c2, c1_ratio=0.5):
        c1_ratio = max(0.0, min(1.0, c1_ratio))
        r1, g1, b1 = self._hex_to_rgb(c1)
        r2, g2, b2 = self._hex_to_rgb(c2)
        r = int((r1 * c1_ratio) + (r2 * (1.0 - c1_ratio)))
        g = int((g1 * c1_ratio) + (g2 * (1.0 - c1_ratio)))
        b = int((b1 * c1_ratio) + (b2 * (1.0 - c1_ratio)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _hex_to_rgb(self, color):
        color = str(color).lstrip("#")
        if len(color) != 6:
            return (180, 200, 230)
        return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))

    def _luminance(self, color):
        r, g, b = self._hex_to_rgb(color)
        return (0.2126 * (r / 255.0)) + (0.7152 * (g / 255.0)) + (0.0722 * (b / 255.0))

    def _view_origin(self):
        try:
            return float(self.canvas.canvasx(0)), float(self.canvas.canvasy(0))
        except Exception:
            return 0.0, 0.0

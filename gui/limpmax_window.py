import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.limpmax_processor import LimpMaxConfig, LimpMaxProcessor
from gui.components import CustomToplevel
from utils.helpers import resource_path

class LimpMaxWindow(CustomToplevel):
    def __init__(self, parent, theme_manager, language_manager):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title=language_manager.get_text("btn_limpmax"),
            size="1180x700",
            min_size=(1180, 620),
            max_size=(1280, 900),
        )
        self.language_manager = language_manager
        self.processor = LimpMaxProcessor()

        self._running = False
        self._started_at = None
        self._title_icon_label = None
        self._icon_refs = []
        self._gif_frames = []
        self._gif_index = 0
        self._gif_animation_id = None

        self._build_ui()
        self.apply_theme()
        self._on_scope_change()
        self._on_output_mode_change()
        self.theme_manager.subscribe(self.apply_theme)
        self.language_manager.subscribe(self.update_ui_language)

    def _build_ui(self):
        root = self.content_frame
        self.main = tk.Frame(root, bd=0, highlightthickness=0)
        self.main.pack(fill="both", expand=True, padx=10, pady=10)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self._build_hero_banner(self.main)

        body = tk.Frame(self.main, bd=0, highlightthickness=0)
        body.grid(row=1, column=0, sticky="nsew", pady=(10, 10))
        body.grid_columnconfigure(0, weight=47)
        body.grid_columnconfigure(1, weight=63)
        body.grid_rowconfigure(0, weight=1)

        left_col = tk.Frame(body, bd=0, highlightthickness=0)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_col.grid_columnconfigure(0, weight=1)
        left_col.grid_rowconfigure(1, weight=1)

        right_col = tk.Frame(body, bd=0, highlightthickness=0)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(1, weight=1)

        self._build_source_box(left_col)
        self._build_options_box(left_col)
        self._build_output_box(right_col)
        self._build_progress_box(right_col)
        self._build_action_row(self.main)
        self._load_icons()

    def _build_hero_banner(self, parent):
        lang = self.language_manager
        banner = tk.Frame(parent, bd=0, highlightthickness=1)
        banner.grid(row=0, column=0, sticky="ew")
        self._title_banner = banner
        banner.grid_columnconfigure(1, weight=1)

        icon_holder = tk.Frame(banner, width=42, height=42, bd=0, highlightthickness=0)
        icon_holder.grid(row=0, column=0, sticky="w", padx=12, pady=10)
        icon_holder.grid_propagate(False)
        self._banner_icon = tk.Label(icon_holder, bd=0, highlightthickness=0)
        self._banner_icon.place(relx=0.5, rely=0.5, anchor="center")

        text = tk.Frame(banner, bd=0, highlightthickness=0)
        text.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=10)
        self._banner_title = tk.Label(text, text=lang.get_text("limpmax_title"), font=("Segoe UI", 17, "bold"), anchor="w")
        self._banner_title.pack(fill="x")
        self._banner_subtitle = tk.Label(
            text, text=lang.get_text("limpmax_subtitle"), font=("Segoe UI", 10), anchor="w"
        )
        self._banner_subtitle.pack(fill="x", pady=(2, 0))

    def _build_section(self, parent, key, icon_attr):
        lang = self.language_manager
        section = tk.Frame(parent, bd=0, highlightthickness=1)
        section.pack(fill="both", expand=False, pady=(0, 10))

        header = tk.Frame(section, bd=0, highlightthickness=0)
        header.pack(fill="x", padx=10, pady=(8, 6))
        icon_wrap = tk.Frame(header, width=18, height=18, bd=0, highlightthickness=0)
        icon_wrap.pack(side="left", padx=(0, 7))
        icon_wrap.pack_propagate(False)
        icon_label = tk.Label(icon_wrap, bd=0, highlightthickness=0)
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        setattr(self, icon_attr, icon_label)

        lbl = tk.Label(header, text=lang.get_text(key), font=("Segoe UI", 12, "bold"), anchor="w")
        lbl.pack(side="left")
        body = tk.Frame(section, bd=0, highlightthickness=0)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        return section, lbl, body

    def _build_source_box(self, parent):
        section, self.lbl_source_title, body = self._build_section(parent, "limpmax_source", "_source_icon")
        self._source_box = section

        row1 = tk.Frame(body, bd=0, highlightthickness=0)
        row1.pack(fill="x")
        proj_icon_wrap = tk.Frame(row1, width=16, height=16, bd=0, highlightthickness=0)
        proj_icon_wrap.pack(side="left", padx=(0, 6))
        proj_icon_wrap.pack_propagate(False)
        self._project_icon = tk.Label(proj_icon_wrap, bd=0, highlightthickness=0)
        self._project_icon.place(relx=0.5, rely=0.5, anchor="center")

        self.project_var = tk.StringVar()
        self.project_entry = tk.Entry(row1, textvariable=self.project_var, font=("Segoe UI", 10))
        self.project_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        self.project_btn = tk.Button(row1, command=self._pick_project_folder, width=11, font=("Segoe UI", 10))
        self.project_btn.pack(side="right")

        row2 = tk.Frame(body, bd=0, highlightthickness=0)
        row2.pack(fill="x", pady=(9, 9))
        scope_icon_wrap = tk.Frame(row2, width=16, height=16, bd=0, highlightthickness=0)
        scope_icon_wrap.pack(side="left", padx=(0, 6))
        scope_icon_wrap.pack_propagate(False)
        self._scope_icon = tk.Label(scope_icon_wrap, bd=0, highlightthickness=0)
        self._scope_icon.place(relx=0.5, rely=0.5, anchor="center")

        self.scope_var = tk.StringVar(value="all")
        self.scope_all = tk.Radiobutton(
            row2, variable=self.scope_var, value="all", command=self._on_scope_change, font=("Segoe UI", 10)
        )
        self.scope_all.pack(side="left", padx=(0, 16))
        self.scope_single = tk.Radiobutton(
            row2, variable=self.scope_var, value="single", command=self._on_scope_change, font=("Segoe UI", 10)
        )
        self.scope_single.pack(side="left")

        row3 = tk.Frame(body, bd=0, highlightthickness=0)
        row3.pack(fill="x")
        file_icon_wrap = tk.Frame(row3, width=16, height=16, bd=0, highlightthickness=0)
        file_icon_wrap.pack(side="left", padx=(0, 6))
        file_icon_wrap.pack_propagate(False)
        self._file_icon = tk.Label(file_icon_wrap, bd=0, highlightthickness=0)
        self._file_icon.place(relx=0.5, rely=0.5, anchor="center")

        self.single_var = tk.StringVar()
        self.single_entry = tk.Entry(row3, textvariable=self.single_var, font=("Segoe UI", 10))
        self.single_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        self.single_btn = tk.Button(row3, command=self._pick_single_file, width=11, font=("Segoe UI", 10))
        self.single_btn.pack(side="right")

    def _build_options_box(self, parent):
        section, self.lbl_options_title, body = self._build_section(parent, "limpmax_options", "_options_icon")
        self._options_box = section

        cards = tk.Frame(body, bd=0, highlightthickness=0)
        cards.pack(fill="x")
        cards.grid_columnconfigure(0, weight=1)
        cards.grid_columnconfigure(1, weight=1)

        self._print_card = tk.Frame(cards, bd=1, relief="solid")
        self._print_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self._comment_card = tk.Frame(cards, bd=1, relief="solid")
        self._comment_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self._build_option_card(self._print_card, "limpmax_remove_prints_label", "_print_icon", "_opt_print_title")
        self._build_option_card(
            self._comment_card, "limpmax_remove_comments_label", "_comment_icon", "_opt_comment_title"
        )

        self.remove_prints_var = tk.BooleanVar(value=True)
        self.chk_prints = tk.Checkbutton(self._print_card, variable=self.remove_prints_var, font=("Segoe UI", 10), anchor="w")
        self.chk_prints.pack(fill="x", padx=8, pady=(0, 8))

        self.remove_comments_var = tk.BooleanVar(value=True)
        self.chk_comments = tk.Checkbutton(
            self._comment_card, variable=self.remove_comments_var, font=("Segoe UI", 10), anchor="w"
        )
        self.chk_comments.pack(fill="x", padx=8, pady=(0, 8))

    def _build_option_card(self, parent, text_key, icon_attr, title_attr):
        line = tk.Frame(parent, bd=0, highlightthickness=0)
        line.pack(fill="x", padx=8, pady=(8, 4))
        icon_wrap = tk.Frame(line, width=15, height=15, bd=0, highlightthickness=0)
        icon_wrap.pack(side="left", padx=(0, 6))
        icon_wrap.pack_propagate(False)
        icon_lbl = tk.Label(icon_wrap, bd=0, highlightthickness=0)
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
        setattr(self, icon_attr, icon_lbl)
        title = tk.Label(line, text=self.language_manager.get_text(text_key), font=("Segoe UI", 10, "bold"), anchor="w")
        title.pack(side="left", fill="x", expand=True)
        setattr(self, title_attr, title)

    def _build_output_box(self, parent):
        section, self.lbl_output_title, body = self._build_section(parent, "limpmax_output", "_output_icon")
        self._output_box = section

        row1 = tk.Frame(body, bd=0, highlightthickness=0)
        row1.pack(fill="x", pady=(0, 9))
        mode_icon_wrap = tk.Frame(row1, width=16, height=16, bd=0, highlightthickness=0)
        mode_icon_wrap.pack(side="left", padx=(0, 6))
        mode_icon_wrap.pack_propagate(False)
        self._mode_icon = tk.Label(mode_icon_wrap, bd=0, highlightthickness=0)
        self._mode_icon.place(relx=0.5, rely=0.5, anchor="center")

        self.output_mode_var = tk.StringVar(value="mirror")
        self.out_mirror = tk.Radiobutton(
            row1, variable=self.output_mode_var, value="mirror", command=self._on_output_mode_change, font=("Segoe UI", 10)
        )
        self.out_mirror.pack(side="left", padx=(0, 16))
        self.out_overwrite = tk.Radiobutton(
            row1, variable=self.output_mode_var, value="overwrite", command=self._on_output_mode_change, font=("Segoe UI", 10)
        )
        self.out_overwrite.pack(side="left")

        row2 = tk.Frame(body, bd=0, highlightthickness=0)
        row2.pack(fill="x")
        dir_icon_wrap = tk.Frame(row2, width=16, height=16, bd=0, highlightthickness=0)
        dir_icon_wrap.pack(side="left", padx=(0, 6))
        dir_icon_wrap.pack_propagate(False)
        self._dir_icon = tk.Label(dir_icon_wrap, bd=0, highlightthickness=0)
        self._dir_icon.place(relx=0.5, rely=0.5, anchor="center")

        self.output_var = tk.StringVar()
        self.output_entry = tk.Entry(row2, textvariable=self.output_var, font=("Segoe UI", 10))
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        self.output_btn = tk.Button(row2, command=self._pick_output_folder, width=11, font=("Segoe UI", 10))
        self.output_btn.pack(side="right")

    def _build_progress_box(self, parent):
        section, self.lbl_progress_title, body = self._build_section(parent, "limpmax_progress", "_progress_icon")
        self._progress_box = section
        section.pack(fill="both", expand=True, pady=(0, 0))
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        top_line = tk.Frame(body, bd=0, highlightthickness=0)
        top_line.pack(fill="x", pady=(0, 4))
        self.lbl_count = tk.Label(top_line, font=("Segoe UI", 10, "bold"), anchor="w")
        self.lbl_count.pack(side="left")
        self.lbl_eta = tk.Label(top_line, font=("Segoe UI", 10), anchor="e")
        self.lbl_eta.pack(side="right")

        self.progress = ttk.Progressbar(body, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 10))

        stats = tk.Frame(body, bd=0, highlightthickness=0)
        stats.pack(fill="x")
        for i in range(3):
            stats.grid_columnconfigure(i, weight=1)
        self.stat_processed = self._mini_stat(stats, "limpmax_processed", 0, 0)
        self.stat_copied = self._mini_stat(stats, "limpmax_copied", 0, 1)
        self.stat_modified = self._mini_stat(stats, "limpmax_modified", 0, 2)
        self.stat_prints = self._mini_stat(stats, "limpmax_prints_removed", 1, 0)
        self.stat_comments = self._mini_stat(stats, "limpmax_comments_removed", 1, 1)
        self.stat_unsupported = self._mini_stat(stats, "limpmax_unsupported", 1, 2)

        status_wrap = tk.Frame(body, bd=1, relief="solid")
        status_wrap.pack(fill="x", pady=(10, 0))
        self._status_container = status_wrap

        self.status_row = tk.Frame(status_wrap, bd=0, highlightthickness=0)
        self.status_row.pack(fill="x", padx=8, pady=7)
        icon_wrap = tk.Frame(self.status_row, width=15, height=15, bd=0, highlightthickness=0)
        icon_wrap.pack(side="left", padx=(0, 7))
        icon_wrap.pack_propagate(False)
        self.status_icon = tk.Label(icon_wrap, bd=0, highlightthickness=0)
        self.status_icon.place(relx=0.5, rely=0.5, anchor="center")
        self.status_label = tk.Label(self.status_row, text=self.language_manager.get_text("status_ready"), anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)

    def _mini_stat(self, parent, title_key: str, row: int, col: int):
        card = tk.Frame(parent, bd=1, relief="solid")
        card.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

        line = tk.Frame(card, bd=0, highlightthickness=0)
        line.pack(fill="x", padx=7, pady=(6, 3))
        icon_wrap = tk.Frame(line, width=14, height=14, bd=0, highlightthickness=0)
        icon_wrap.pack(side="left", padx=(0, 5))
        icon_wrap.pack_propagate(False)
        icon = tk.Label(icon_wrap, bd=0, highlightthickness=0)
        icon.place(relx=0.5, rely=0.5, anchor="center")
        title_lbl = tk.Label(line, text=self.language_manager.get_text(title_key), anchor="w", font=("Segoe UI", 9, "bold"))
        title_lbl.pack(side="left", fill="x", expand=True)

        value = tk.Label(card, text="0", anchor="w", font=("Segoe UI", 16, "bold"))
        value.pack(fill="x", padx=8, pady=(0, 7))

        card._title_key = title_key
        card._icon = icon
        card._title = title_lbl
        card._value = value
        return card

    def _build_action_row(self, parent):
        row = tk.Frame(parent, bd=0, highlightthickness=0)
        row.grid(row=2, column=0, sticky="ew")
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        self.run_btn = tk.Button(row, command=self._run, font=("Segoe UI", 11, "bold"), cursor="hand2", padx=24, pady=8)
        self.run_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.close_btn = tk.Button(row, command=self.destroy, font=("Segoe UI", 10), cursor="hand2", padx=20, pady=8)
        self.close_btn.grid(row=0, column=1, sticky="e")

    def _fmt_time(self, seconds: float) -> str:
        s = max(0, int(seconds))
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _show_warning(self, msg: str):
        self.lift()
        self.attributes("-topmost", True)
        self.focus_force()
        messagebox.showwarning(self.language_manager.get_text("msg_warning"), msg, parent=self)
        self.attributes("-topmost", False)

    def _show_error(self, msg: str):
        self.lift()
        self.attributes("-topmost", True)
        self.focus_force()
        messagebox.showerror(self.language_manager.get_text("msg_error"), msg, parent=self)
        self.attributes("-topmost", False)

    def _show_info(self, msg: str):
        self.lift()
        self.attributes("-topmost", True)
        self.focus_force()
        messagebox.showinfo(self.language_manager.get_text("msg_success"), msg, parent=self)
        self.attributes("-topmost", False)

    def _pick_project_folder(self):
        d = filedialog.askdirectory(title=self.language_manager.get_text("dialog_select_folder"))
        if d:
            self.project_var.set(d)
            self.output_var.set(self._next_available_output(d))

    def _pick_single_file(self):
        initial = self.project_var.get().strip() or os.path.expanduser("~")
        f = filedialog.askopenfilename(title=self.language_manager.get_text("limpmax_pick_file"), initialdir=initial)
        if f:
            self.single_var.set(f)
            if self.scope_var.get() == "single":
                folder = os.path.dirname(f)
                self.project_var.set(folder)
                self.output_var.set(self._next_available_output(folder))

    def _pick_output_folder(self):
        d = filedialog.askdirectory(title=self.language_manager.get_text("limpmax_pick_output"))
        if d:
            self.output_var.set(d)

    def _next_available_output(self, base_dir: str) -> str:
        base = os.path.join(base_dir, "limpmax")
        if not os.path.exists(base):
            return base
        idx = 1
        while True:
            candidate = os.path.join(base_dir, f"limpmax ({idx})")
            if not os.path.exists(candidate):
                return candidate
            idx += 1

    def _on_scope_change(self):
        is_single = self.scope_var.get() == "single"
        self.single_entry.configure(state=("normal" if is_single else "disabled"))
        self.single_btn.configure(state=("normal" if is_single else "disabled"))
        self.project_entry.configure(state=("disabled" if is_single else "normal"))
        self.project_btn.configure(state=("disabled" if is_single else "normal"))

    def _on_output_mode_change(self):
        mirror = self.output_mode_var.get() == "mirror"
        state = "normal" if mirror else "disabled"
        self.output_entry.configure(state=state)
        self.output_btn.configure(state=state)

    def _set_running(self, running: bool):
        self._running = running
        state = "disabled" if running else "normal"
        for w in [
            self.project_entry,
            self.project_btn,
            self.scope_all,
            self.scope_single,
            self.single_entry,
            self.single_btn,
            self.chk_prints,
            self.chk_comments,
            self.out_mirror,
            self.out_overwrite,
            self.output_entry,
            self.output_btn,
            self.run_btn,
        ]:
            try:
                w.configure(state=state)
            except Exception:
                pass
        if not running:
            self._on_scope_change()
            self._on_output_mode_change()

    def _build_config(self) -> LimpMaxConfig:
        project = self.project_var.get().strip()
        single = self.single_var.get().strip() or None
        output = self.output_var.get().strip() or None
        if self.scope_var.get() == "single" and single and os.path.isfile(single):
            project = os.path.dirname(single)
        return LimpMaxConfig(
            project_root=project,
            scope_mode=self.scope_var.get(),
            single_file=single,
            remove_prints=bool(self.remove_prints_var.get()),
            remove_comments=bool(self.remove_comments_var.get()),
            output_mode=self.output_mode_var.get(),
            output_dir=output,
        )

    def _validate(self, cfg: LimpMaxConfig) -> str | None:
        if cfg.scope_mode == "single":
            if not cfg.single_file or not os.path.isfile(cfg.single_file):
                return self.language_manager.get_text("limpmax_err_single")
            if not cfg.project_root or not os.path.isdir(cfg.project_root):
                cfg.project_root = os.path.dirname(cfg.single_file)
        else:
            if not cfg.project_root or not os.path.isdir(cfg.project_root):
                return self.language_manager.get_text("limpmax_err_project")

        if not cfg.remove_comments and not cfg.remove_prints:
            return self.language_manager.get_text("limpmax_err_option")

        if cfg.output_mode == "mirror":
            if not cfg.output_dir:
                return self.language_manager.get_text("limpmax_err_output")
            if os.path.abspath(cfg.output_dir) == os.path.abspath(cfg.project_root):
                return self.language_manager.get_text("limpmax_err_same_output")
        return None

    def _run(self):
        if self._running:
            return

        cfg = self._build_config()
        err = self._validate(cfg)
        if err:
            self._show_warning(err)
            return

        self.progress["value"] = 0
        self._started_at = time.time()
        self.lbl_count.configure(text="0/0")
        self.lbl_eta.configure(text=f"{self.language_manager.get_text('limpmax_eta')}: 00:00")
        self.status_label.configure(text=self.language_manager.get_text("limpmax_starting"))
        if getattr(self, "_status_run_icon", None):
            self.status_icon.configure(image=self._status_run_icon)
            self.status_icon.image = self._status_run_icon
        self._set_stat_values(
            {
                "processed_files": 0,
                "copied_files": 0,
                "modified_files": 0,
                "prints_removed": 0,
                "comments_removed": 0,
                "unsupported_files": 0,
            }
        )
        self._set_running(True)

        def _progress(payload):
            self.after(0, lambda p=payload: self._on_progress(p))

        def _worker():
            try:
                summary = self.processor.run(cfg, progress_cb=_progress)
                self.after(0, lambda: self._on_done(summary))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_progress(self, payload: dict):
        total = max(1, int(payload.get("total", 1)))
        done = int(payload.get("done", 0))
        pct = min(100.0, (done / total) * 100.0)
        self.progress["value"] = pct
        self.lbl_count.configure(text=f"{done}/{total}")
        self.lbl_eta.configure(text=f"{self.language_manager.get_text('limpmax_eta')}: {self._fmt_time(payload.get('remaining', 0.0))}")
        self._set_stat_values(payload)

    def _on_done(self, summary: dict):
        self._set_running(False)
        elapsed = self._fmt_time(summary.get("elapsed", 0.0))
        self.status_label.configure(text=f"{self.language_manager.get_text('limpmax_done')} - {self.language_manager.get_text('limpmax_time')}: {elapsed}")
        errors = summary.get("errors", [])
        if errors:
            if getattr(self, "_status_error_icon", None):
                self.status_icon.configure(image=self._status_error_icon)
                self.status_icon.image = self._status_error_icon
            self._show_error(f"{self.language_manager.get_text('dash_errors')}: {len(errors)}")
            return

        if getattr(self, "_status_ok_icon", None):
            self.status_icon.configure(image=self._status_ok_icon)
            self.status_icon.image = self._status_ok_icon
        self._show_info(self.language_manager.get_text("limpmax_done"))

    def _on_error(self, err: str):
        self._set_running(False)
        self.status_label.configure(text=f"{self.language_manager.get_text('msg_error')}: {err}")
        if getattr(self, "_status_error_icon", None):
            self.status_icon.configure(image=self._status_error_icon)
            self.status_icon.image = self._status_error_icon
        self._show_error(err)

    def _set_stat_values(self, payload: dict):
        self.stat_processed._value.configure(text=str(payload.get("processed_files", 0)))
        self.stat_copied._value.configure(text=str(payload.get("copied_files", 0)))
        self.stat_modified._value.configure(text=str(payload.get("modified_files", 0)))
        self.stat_prints._value.configure(text=str(payload.get("prints_removed", 0)))
        self.stat_comments._value.configure(text=str(payload.get("comments_removed", 0)))
        self.stat_unsupported._value.configure(text=str(payload.get("unsupported_files", 0)))

    def _load_animated_gif(self, path: str, size: tuple[int, int]):
        try:
            from PIL import Image, ImageSequence, ImageTk
            if not os.path.exists(path):
                return None
            gif = Image.open(path)
            frames = []
            for frame in ImageSequence.Iterator(gif):
                rgba = frame.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                rgba = self._strip_icon_background(rgba)
                frames.append(ImageTk.PhotoImage(rgba))
            return frames or None
        except Exception:
            return None

    def _animate_gif(self):
        if not self._gif_frames:
            return
        frame = self._gif_frames[self._gif_index]
        self._banner_icon.configure(image=frame)
        self._banner_icon.image = frame
        self._gif_index = (self._gif_index + 1) % len(self._gif_frames)
        self._gif_animation_id = self.after(100, self._animate_gif)

    def _load_icons(self):
        try:
            from PIL import Image, ImageTk
        except Exception:
            return

        self._icon_refs = []

        def _load(name: str, size: tuple[int, int]):
            path = os.path.join(resource_path("assets/icons"), name)
            if not os.path.exists(path):
                return None
            try:
                img = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                img = self._strip_icon_background(img)
                return ImageTk.PhotoImage(img)
            except Exception:
                return None

        title_ico = _load("limpmax.gif", (16, 16))
        if title_ico:
            if self._title_icon_label and self._title_icon_label.winfo_exists():
                self._title_icon_label.configure(image=title_ico)
                self._title_icon_label.image = title_ico
            else:
                self._title_icon_label = self.add_title_icon(title_ico)
            self._icon_refs.append(title_ico)

        gif_path = os.path.join(resource_path("assets/icons"), "limpmax.gif")
        self._gif_frames = self._load_animated_gif(gif_path, (30, 30)) or []
        if self._gif_frames:
            self._gif_index = 0
            self._animate_gif()
            self._icon_refs.extend(self._gif_frames)

        icons_map = [
            ("folder.png", 16, self._source_icon),
            ("settings.png", 16, self._options_icon),
            ("export.png", 16, self._output_icon),
            ("activity.png", 16, self._progress_icon),
            ("folder.png", 15, self._project_icon),
            ("target.png", 15, self._scope_icon),
            ("file.png", 15, self._file_icon),
            ("trash.png", 15, self._print_icon),
            ("message.png", 15, self._comment_icon),
            ("save.png", 15, self._mode_icon),
            ("folder.png", 15, self._dir_icon),
            ("file.png", 14, self.stat_processed._icon),
            ("copy.png", 14, self.stat_copied._icon),
            ("edit.png", 14, self.stat_modified._icon),
            ("trash.png", 14, self.stat_prints._icon),
            ("message.png", 14, self.stat_comments._icon),
            ("alert.png", 14, self.stat_unsupported._icon),
        ]
        for icon_file, size, widget in icons_map:
            icon = _load(icon_file, (size, size))
            if icon:
                widget.configure(image=icon)
                widget.image = icon
                self._icon_refs.append(icon)

        self._status_run_icon = _load("scan.png", (14, 14))
        self._status_ok_icon = _load("check.png", (14, 14))
        self._status_error_icon = _load("error.png", (14, 14))
        if self._status_run_icon:
            self.status_icon.configure(image=self._status_run_icon)
            self.status_icon.image = self._status_run_icon
        for icon in (self._status_run_icon, self._status_ok_icon, self._status_error_icon):
            if icon:
                self._icon_refs.append(icon)

    def update_ui_language(self):
        lang = self.language_manager
        self.title_label.configure(text=lang.get_text("btn_limpmax"))
        self._banner_title.configure(text=lang.get_text("limpmax_title"))
        self._banner_subtitle.configure(text=lang.get_text("limpmax_subtitle"))
        self.lbl_source_title.configure(text=lang.get_text("limpmax_source"))
        self.lbl_options_title.configure(text=lang.get_text("limpmax_options"))
        self.lbl_output_title.configure(text=lang.get_text("limpmax_output"))
        self.lbl_progress_title.configure(text=lang.get_text("limpmax_progress"))

        self.project_btn.configure(text=lang.get_text("btn_open"))
        self.scope_all.configure(text=lang.get_text("limpmax_scope_all"))
        self.scope_single.configure(text=lang.get_text("limpmax_scope_single"))
        self.single_btn.configure(text=lang.get_text("btn_search"))
        self._opt_print_title.configure(text=lang.get_text("limpmax_remove_prints_label"))
        self._opt_comment_title.configure(text=lang.get_text("limpmax_remove_comments_label"))
        self.chk_prints.configure(text=lang.get_text("limpmax_remove_prints"))
        self.chk_comments.configure(text=lang.get_text("limpmax_remove_comments"))
        self.out_mirror.configure(text=lang.get_text("limpmax_output_mirror"))
        self.out_overwrite.configure(text=lang.get_text("limpmax_output_overwrite"))
        self.output_btn.configure(text=lang.get_text("btn_open"))
        self.run_btn.configure(text=lang.get_text("dash_scan_btn"))
        self.close_btn.configure(text=lang.get_text("search_close"))

        for stat in (
            self.stat_processed,
            self.stat_copied,
            self.stat_modified,
            self.stat_prints,
            self.stat_comments,
            self.stat_unsupported,
        ):
            stat._title.configure(text=lang.get_text(stat._title_key))

        if not self._running:
            self.status_label.configure(text=lang.get_text("status_ready"))
        self._on_scope_change()
        self._on_output_mode_change()

    def _strip_icon_background(self, img):
        """
        Elimina fondos sÃ³lidos tÃ­picos (blanco/negro o color de borde) para que
        el icono se vea transparente sobre cualquier tema.
        """
        try:
            rgba = img.convert("RGBA")
            px = rgba.load()
            w, h = rgba.size
            if w <= 1 or h <= 1:
                return rgba

            corners = [
                px[0, 0],
                px[w - 1, 0],
                px[0, h - 1],
                px[w - 1, h - 1],
            ]
            # Color de fondo estimado por promedio de esquinas.
            br = sum(c[0] for c in corners) // 4
            bg = sum(c[1] for c in corners) // 4
            bb = sum(c[2] for c in corners) // 4

            def _dist(c1, c2):
                return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])

            key = (br, bg, bb)
            for y in range(h):
                for x in range(w):
                    r, g, b, a = px[x, y]
                    if a == 0:
                        continue
                    # Fondo por similitud al borde.
                    if _dist((r, g, b), key) <= 44:
                        px[x, y] = (r, g, b, 0)
                        continue
                    # Fondos casi negros / casi blancos.
                    if (r <= 24 and g <= 24 and b <= 24) or (r >= 244 and g >= 244 and b >= 244):
                        px[x, y] = (r, g, b, 0)
            return rgba
        except Exception:
            return img

    def apply_theme(self):
        self.apply_base_theme()
        t = self.theme_manager.get_theme()
        bg = t["bg"]
        sec = t["secondary_bg"]
        border = t["border"]
        fg = t["fg"]
        accent = t["accent"]
        entry_bg = t.get("entry_bg", t.get("tree_bg", sec))
        entry_fg = t.get("entry_fg", t.get("tree_fg", fg))

        self.main.configure(bg=bg)
        for frame in [self._title_banner, self._source_box, self._options_box, self._output_box, self._progress_box]:
            frame.configure(bg=sec, highlightbackground=border, highlightcolor=border)

        def _paint(widget, default_bg):
            cls = type(widget).__name__
            try:
                if cls == "Frame":
                    widget.configure(bg=default_bg)
                elif cls == "Label":
                    widget.configure(bg=widget.master.cget("bg"), fg=fg)
                elif cls in ("Radiobutton", "Checkbutton"):
                    parent_bg = widget.master.cget("bg")
                    widget.configure(bg=parent_bg, fg=fg, activebackground=parent_bg, activeforeground=fg, selectcolor=sec)
                elif cls == "Entry":
                    widget.configure(
                        bg=entry_bg,
                        fg=entry_fg,
                        insertbackground=entry_fg,
                        relief="flat",
                        highlightthickness=1,
                        highlightbackground=border,
                        highlightcolor=accent,
                    )
                elif cls == "Button":
                    if widget is self.run_btn:
                        widget.configure(bg=accent, fg="#FFFFFF", activebackground=accent, activeforeground="#FFFFFF", relief="flat", bd=0)
                    else:
                        widget.configure(
                            bg=t.get("button_bg", sec),
                            fg=t.get("button_fg", fg),
                            activebackground=t.get("button_hover", sec),
                            activeforeground=t.get("button_fg", fg),
                            relief="flat",
                            bd=0,
                        )
            except Exception:
                pass
            for child in widget.winfo_children():
                _paint(child, widget.cget("bg") if cls == "Frame" else default_bg)

        _paint(self.content_frame, bg)

        for card in [self._print_card, self._comment_card, self._status_container]:
            card.configure(bg=bg, highlightbackground=border, highlightcolor=border, bd=1, relief="solid")
            for child in card.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=bg)

        for stat in (
            self.stat_processed,
            self.stat_copied,
            self.stat_modified,
            self.stat_prints,
            self.stat_comments,
            self.stat_unsupported,
        ):
            stat.configure(bg=sec, highlightbackground=border, highlightcolor=border, bd=1, relief="solid")
            stat._title.configure(bg=sec, fg=fg)
            stat._value.configure(bg=sec, fg=accent)
            stat._icon.configure(bg=sec)

        self.status_label.configure(bg=self.status_row.cget("bg"), fg=accent, font=("Segoe UI", 10, "bold"))

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Limp.Horizontal.TProgressbar",
            troughcolor=entry_bg,
            background=accent,
            bordercolor=border,
            lightcolor=accent,
            darkcolor=accent,
            thickness=10,
        )
        self.progress.configure(style="Limp.Horizontal.TProgressbar")

        self.update_ui_language()
        self._load_icons()

    def destroy(self):
        try:
            self.theme_manager.unsubscribe(self.apply_theme)
        except Exception:
            pass
        if self._gif_animation_id:
            try:
                self.after_cancel(self._gif_animation_id)
            except Exception:
                pass
        super().destroy()

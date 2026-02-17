import os
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ProgressCallback = Callable[[dict], None]


@dataclass
class LimpMaxConfig:
    project_root: str
    scope_mode: str  # "all" | "single"
    single_file: str | None
    remove_prints: bool
    remove_comments: bool
    output_mode: str  # "overwrite" | "mirror"
    output_dir: str | None


class LimpMaxProcessor:
    IGNORED_DIRS = {
        "node_modules", "venv", ".venv", "env", ".env", "__pycache__",
        ".git", ".svn", ".hg", "dist", "build", ".idea", ".vscode",
    }

    ARCHIVE_EXTS = {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz",
    }

    BINARY_EXTS = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".bmp", ".tiff",
        ".mp3", ".mp4", ".wav", ".avi", ".mov", ".pdf", ".exe", ".dll",
        ".so", ".dylib", ".bin", ".class", ".pyc", ".pyo", ".jar",
    }

    SUPPORTED_COMMENT_STYLES = {
        ".py": ("#", None),
        ".sh": ("#", None),
        ".rb": ("#", None),
        ".yml": ("#", None),
        ".yaml": ("#", None),
        ".toml": ("#", None),
        ".ini": (";", None),
        ".c": ("//", ("/*", "*/")),
        ".h": ("//", ("/*", "*/")),
        ".cpp": ("//", ("/*", "*/")),
        ".hpp": ("//", ("/*", "*/")),
        ".cc": ("//", ("/*", "*/")),
        ".cxx": ("//", ("/*", "*/")),
        ".java": ("//", ("/*", "*/")),
        ".js": ("//", ("/*", "*/")),
        ".jsx": ("//", ("/*", "*/")),
        ".ts": ("//", ("/*", "*/")),
        ".tsx": ("//", ("/*", "*/")),
        ".cs": ("//", ("/*", "*/")),
        ".go": ("//", ("/*", "*/")),
        ".rs": ("//", ("/*", "*/")),
        ".swift": ("//", ("/*", "*/")),
        ".kt": ("//", ("/*", "*/")),
        ".kts": ("//", ("/*", "*/")),
        ".php": ("//", ("/*", "*/")),
        ".css": ("/*", ("/*", "*/")),
        ".scss": ("//", ("/*", "*/")),
        ".sql": ("--", ("/*", "*/")),
    }

    PRINT_PATTERNS_BY_EXT = {
        ".py": [r"^\s*print\s*\(.*\)\s*$"],
        ".js": [r"^\s*console\.(log|info|warn|error|debug)\s*\(.*\)\s*;?\s*$"],
        ".jsx": [r"^\s*console\.(log|info|warn|error|debug)\s*\(.*\)\s*;?\s*$"],
        ".ts": [r"^\s*console\.(log|info|warn|error|debug)\s*\(.*\)\s*;?\s*$"],
        ".tsx": [r"^\s*console\.(log|info|warn|error|debug)\s*\(.*\)\s*;?\s*$"],
        ".java": [
            r"^\s*System\.out\.print(ln)?\s*\(.*\)\s*;?\s*$",
            r"^\s*System\.err\.print(ln)?\s*\(.*\)\s*;?\s*$",
        ],
        ".c": [r"^\s*(printf|fprintf|puts)\s*\(.*\)\s*;?\s*$"],
        ".h": [r"^\s*(printf|fprintf|puts)\s*\(.*\)\s*;?\s*$"],
        ".cpp": [r"^\s*(printf|fprintf|puts)\s*\(.*\)\s*;?\s*$", r"^\s*std::cout\s*<<.*;\s*$"],
        ".hpp": [r"^\s*(printf|fprintf|puts)\s*\(.*\)\s*;?\s*$", r"^\s*std::cout\s*<<.*;\s*$"],
        ".cs": [r"^\s*Console\.Write(Line)?\s*\(.*\)\s*;?\s*$"],
        ".go": [r"^\s*fmt\.(Print|Printf|Println)\s*\(.*\)\s*$"],
        ".rs": [r"^\s*(println!|print!)\s*\(.*\)\s*;?\s*$"],
        ".php": [r"^\s*(echo|print)\s+.*;\s*$", r"^\s*var_dump\s*\(.*\)\s*;?\s*$"],
        ".swift": [r"^\s*print\s*\(.*\)\s*$"],
        ".kt": [r"^\s*println\s*\(.*\)\s*$", r"^\s*print\s*\(.*\)\s*$"],
    }

    HTML_COMMENT_EXTS = {
        ".html", ".htm", ".xml", ".vue", ".svelte",
        ".js", ".jsx", ".ts", ".tsx",
    }

    def _next_available_dir(self, desired: Path) -> Path:
        if not desired.exists():
            return desired
        base = desired.name
        parent = desired.parent
        idx = 1
        while True:
            candidate = parent / f"{base} ({idx})"
            if not candidate.exists():
                return candidate
            idx += 1

    def _is_ignored_path(self, path: Path) -> bool:
        parts = {p.lower() for p in path.parts}
        if any(p in self.IGNORED_DIRS for p in parts):
            return True
        ext = path.suffix.lower()
        return ext in self.ARCHIVE_EXTS or ext in self.BINARY_EXTS

    def _supports_comments(self, ext: str) -> bool:
        return ext in self.SUPPORTED_COMMENT_STYLES

    def _supports_prints(self, ext: str) -> bool:
        return ext in self.PRINT_PATTERNS_BY_EXT

    def _remove_print_lines(self, text: str, ext: str) -> tuple[str, int]:
        patterns = [re.compile(p) for p in self.PRINT_PATTERNS_BY_EXT.get(ext, [])]
        if not patterns:
            return text, 0
        removed = 0
        out = []
        for line in text.splitlines(keepends=True):
            candidate = line.rstrip("\r\n")
            if any(p.match(candidate) for p in patterns):
                removed += 1
                continue
            out.append(line)
        return "".join(out), removed

    def _strip_comments_stateful(self, text: str, ext: str) -> tuple[str, int]:
        line_marker, block = self.SUPPORTED_COMMENT_STYLES.get(ext, (None, None))
        if not line_marker and not block:
            return text, 0

        block_start = block[0] if block else None
        block_end = block[1] if block else None
        in_block = False
        removed = 0
        result_lines = []

        for raw_line in text.splitlines(keepends=True):
            line = raw_line
            i = 0
            out = []
            in_single = False
            in_double = False

            while i < len(line):
                ch = line[i]
                nxt = line[i : i + 2]

                if in_block:
                    if block_end and line.startswith(block_end, i):
                        in_block = False
                        i += len(block_end)
                    else:
                        if ch == "\n":
                            out.append("\n")
                        i += 1
                    continue

                if ch == "'" and not in_double:
                    in_single = not in_single
                    out.append(ch)
                    i += 1
                    continue
                if ch == '"' and not in_single:
                    escaped = i > 0 and line[i - 1] == "\\"
                    if not escaped:
                        in_double = not in_double
                    out.append(ch)
                    i += 1
                    continue

                if not in_single and not in_double:
                    if block_start and line.startswith(block_start, i):
                        in_block = True
                        removed += 1
                        i += len(block_start)
                        continue
                    if line_marker and line.startswith(line_marker, i):
                        removed += 1
                        if line.endswith("\r\n"):
                            out.append("\r\n")
                        elif line.endswith("\n"):
                            out.append("\n")
                        break

                out.append(ch)
                i += 1

            result_lines.append("".join(out))

        return "".join(result_lines), removed

    def _clean_file_content(
        self, text: str, ext: str, remove_prints: bool, remove_comments: bool
    ) -> tuple[str, dict]:
        stats = {"prints_removed": 0, "comments_removed": 0}
        new_text = text

        if remove_comments and self._supports_comments(ext):
            new_text, count = self._strip_comments_stateful(new_text, ext)
            stats["comments_removed"] = count
            if ext in self.HTML_COMMENT_EXTS:
                # Soporta comentarios HTML embebidos en templates JS/TS o archivos HTML-like.
                new_text, html_count = re.subn(r"<!--[\s\S]*?-->", "", new_text, flags=re.MULTILINE)
                stats["comments_removed"] += html_count
        elif remove_comments:
            # Fallback seguro para extensiones no mapeadas: solo líneas de comentario completas.
            keep = []
            removed = 0
            for i, line in enumerate(new_text.splitlines(keepends=True), start=1):
                stripped = line.lstrip()
                if i == 1 and (stripped.startswith("#!") or stripped.startswith("# -*-")):
                    keep.append(line)
                    continue
                if (
                    stripped.startswith("//")
                    or stripped.startswith("#")
                    or stripped.startswith(";")
                    or stripped.startswith("--")
                ):
                    removed += 1
                    continue
                keep.append(line)
            new_text = "".join(keep)
            stats["comments_removed"] += removed

        if remove_prints and self._supports_prints(ext):
            new_text, count = self._remove_print_lines(new_text, ext)
            stats["prints_removed"] = count

        return new_text, stats

    def _scan_all_files(self, root: Path, excluded_roots: set[Path] | None = None) -> list[Path]:
        files = []
        excluded_norm = {p.resolve() for p in (excluded_roots or set())}
        for current_root, dirs, names in os.walk(root):
            current = Path(current_root).resolve()
            # Evitar recorrer carpeta(s) de salida cuando estén dentro del proyecto.
            dirs[:] = [
                d for d in dirs
                if (current / d).resolve() not in excluded_norm
            ]
            for name in names:
                files.append(Path(current_root) / name)
        return files

    def run(self, cfg: LimpMaxConfig, progress_cb: ProgressCallback | None = None) -> dict:
        root = Path(cfg.project_root).resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError("Carpeta de proyecto inválida.")
        if not cfg.remove_prints and not cfg.remove_comments:
            raise ValueError("Debes activar al menos una opción de limpieza.")
        if cfg.output_mode == "mirror" and not cfg.output_dir:
            raise ValueError("Selecciona carpeta de salida.")

        start = time.time()
        single = Path(cfg.single_file).resolve() if cfg.single_file else None
        mirror_dir = Path(cfg.output_dir).resolve() if cfg.output_mode == "mirror" else None

        if mirror_dir:
            if mirror_dir == root:
                raise ValueError("La carpeta de salida debe ser distinta al proyecto.")
            # Permitido dentro del proyecto; la excluimos del escaneo para evitar recursión.
            mirror_dir = self._next_available_dir(mirror_dir)
            mirror_dir.mkdir(parents=True, exist_ok=True)

        if cfg.scope_mode == "single":
            if not single or not single.is_file():
                raise ValueError("Archivo único inválido para procesar.")
            all_files = [single]
        else:
            excluded = {mirror_dir} if mirror_dir else set()
            all_files = self._scan_all_files(root, excluded_roots=excluded)

        process_candidates: set[Path] = set()
        for fp in all_files:
            if cfg.scope_mode == "single":
                # En modo archivo único solo se trabaja con ese archivo.
                if fp != single:
                    continue
            ext = fp.suffix.lower()
            if self._is_ignored_path(fp):
                continue
            if cfg.remove_comments and self._supports_comments(ext):
                process_candidates.add(fp)
            if cfg.remove_prints and self._supports_prints(ext):
                process_candidates.add(fp)

        tasks = []
        if cfg.output_mode == "mirror":
            for fp in all_files:
                rel = fp.relative_to(root)
                dst = mirror_dir / rel
                mode = "process" if fp in process_candidates else "copy"
                tasks.append((mode, fp, dst))
        else:
            for fp in sorted(process_candidates):
                tasks.append(("process", fp, fp))

        summary = {
            "total_tasks": len(tasks),
            "processed_files": 0,
            "copied_files": 0,
            "modified_files": 0,
            "prints_removed": 0,
            "comments_removed": 0,
            "skipped_unsupported": 0,
            "unsupported_files": 0,
            "errors": [],
        }

        unsupported_set: set[Path] = set()
        for fp in all_files:
            if cfg.scope_mode == "single":
                if fp != single:
                    continue
            if self._is_ignored_path(fp):
                continue
            ext = fp.suffix.lower()
            supports_comments = (cfg.remove_comments and self._supports_comments(ext)) or (cfg.remove_comments and ext in self.HTML_COMMENT_EXTS)
            supports_prints = cfg.remove_prints and self._supports_prints(ext)
            if not supports_comments and not supports_prints:
                unsupported_set.add(fp)
        summary["unsupported_files"] = len(unsupported_set)

        def emit(idx: int):
            if not progress_cb:
                return
            elapsed = time.time() - start
            done = idx
            total = max(1, len(tasks))
            rate = done / elapsed if elapsed > 0 else 0.0
            remaining = (total - done) / rate if rate > 0 else 0.0
            payload = {
                "done": done,
                "total": total,
                "elapsed": elapsed,
                "remaining": remaining,
                **summary,
            }
            progress_cb(payload)

        emit(0)
        for i, (mode, src, dst) in enumerate(tasks, start=1):
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if mode == "copy":
                    shutil.copy2(src, dst)
                    summary["copied_files"] += 1
                else:
                    ext = src.suffix.lower()
                    if not ((cfg.remove_comments and self._supports_comments(ext)) or (cfg.remove_prints and self._supports_prints(ext))):
                        summary["skipped_unsupported"] += 1
                        if cfg.output_mode == "mirror":
                            shutil.copy2(src, dst)
                            summary["copied_files"] += 1
                        emit(i)
                        continue

                    raw = src.read_text(encoding="utf-8", errors="ignore")
                    cleaned, stats = self._clean_file_content(
                        raw, ext, cfg.remove_prints, cfg.remove_comments
                    )
                    changed = cleaned != raw
                    if changed:
                        dst.write_text(cleaned, encoding="utf-8")
                        summary["modified_files"] += 1
                    elif cfg.output_mode == "mirror":
                        shutil.copy2(src, dst)
                        summary["copied_files"] += 1
                    summary["processed_files"] += 1
                    summary["prints_removed"] += stats["prints_removed"]
                    summary["comments_removed"] += stats["comments_removed"]
            except Exception as e:
                summary["errors"].append(f"{src}: {e}")
            emit(i)

        summary["elapsed"] = time.time() - start
        return summary

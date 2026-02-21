import os
import sys


def app_base_path():
    """Base persistente de la app (junto al .exe en frozen, raíz del proyecto en dev)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def resource_path(relative_path):
    """Resuelve rutas priorizando recursos externos persistentes y luego _MEIPASS."""
    persistent_candidate = os.path.join(app_base_path(), relative_path)
    if os.path.exists(persistent_candidate):
        return persistent_candidate

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)

    return persistent_candidate

def format_file_size(size_bytes):
    """Formatea tamaño de archivo en formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def count_lines_in_file(filepath):
    """Cuenta líneas en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def is_text_file(filepath):
    """Verifica si un archivo es de texto"""
    text_extensions = {
        '.txt', '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.cs',
        '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.html', '.htm', '.css',
        '.scss', '.sass', '.less', '.json', '.xml', '.yaml', '.yml', '.toml',
        '.ini', '.csv', '.md', '.sh', '.bat', '.sql', '.r', '.m', '.h'
    }
    ext = os.path.splitext(filepath)[1].lower()
    return ext in text_extensions

def get_file_extension(filepath):
    """Obtiene la extensión de un archivo"""
    return os.path.splitext(filepath)[1].lower()

def is_hidden_file(filepath):
    """Verifica si un archivo/carpeta está oculto"""
    basename = os.path.basename(filepath)
    return basename.startswith('.')

def safe_read_file(filepath, max_size=10*1024*1024):
    """Lee un archivo de forma segura con límite de tamaño"""
    try:
        file_size = os.path.getsize(filepath)
        if file_size > max_size:
            return None, f"Archivo demasiado grande ({format_file_size(file_size)})"
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return content, None
    except Exception as e:
        return None, str(e)

def get_relative_path(filepath, base_path):
    """Obtiene la ruta relativa respecto a una base"""
    try:
        return os.path.relpath(filepath, base_path)
    except ValueError:
        return filepath

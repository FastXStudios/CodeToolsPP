import os
from utils.helpers import is_text_file, count_lines_in_file, format_file_size

class FileManager:
    """Gestiona operaciones de archivos y directorios"""
    
    def __init__(self):
        self.root_path = None
    
    def set_root(self, path):
        """Establece la raíz del proyecto"""
        self.root_path = path
    
    def list_directory(self, path, show_hidden=False):
        """Lista archivos y carpetas en un directorio"""
        try:
            items = []
            for name in sorted(os.listdir(path)):
                if not show_hidden and name.startswith('.'):
                    continue
                fullpath = os.path.join(path, name)
                items.append({
                    'name': name,
                    'path': fullpath,
                    'is_dir': os.path.isdir(fullpath),
                    'is_file': os.path.isfile(fullpath)
                })
            return items
        except PermissionError:
            return []
        except Exception as e:
            print(f"Error listing directory {path}: {e}")
            return []
    
    def get_file_info(self, filepath):
        """Obtiene información detallada de un archivo"""
        try:
            stat = os.stat(filepath)
            info = {
                'path': filepath,
                'name': os.path.basename(filepath),
                'size': stat.st_size,
                'size_formatted': format_file_size(stat.st_size),
                'is_text': is_text_file(filepath),
                'lines': 0,
                'extension': os.path.splitext(filepath)[1]
            }
            
            if info['is_text']:
                info['lines'] = count_lines_in_file(filepath)
            
            return info
        except Exception as e:
            print(f"Error getting file info {filepath}: {e}")
            return None
    
    def read_file_content(self, filepath):
        """Lee el contenido de un archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None
    
    def get_directory_stats(self, path):
        """Obtiene estadísticas de un directorio"""
        stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'total_lines': 0,
            'extensions': {}
        }
        
        try:
            for root, dirs, files in os.walk(path):
                stats['total_dirs'] += len(dirs)
                for file in files:
                    stats['total_files'] += 1
                    filepath = os.path.join(root, file)
                    try:
                        size = os.path.getsize(filepath)
                        stats['total_size'] += size
                        
                        ext = os.path.splitext(file)[1] or 'sin extensión'
                        if ext not in stats['extensions']:
                            stats['extensions'][ext] = {'count': 0, 'lines': 0}
                        stats['extensions'][ext]['count'] += 1
                        
                        if is_text_file(filepath):
                            lines = count_lines_in_file(filepath)
                            stats['total_lines'] += lines
                            stats['extensions'][ext]['lines'] += lines
                    except:
                        pass
        except Exception as e:
            print(f"Error getting directory stats: {e}")
        
        return stats
    
    def get_relative_path(self, filepath):
        """Obtiene la ruta relativa desde la raíz"""
        if self.root_path:
            try:
                return os.path.relpath(filepath, self.root_path)
            except ValueError:
                return filepath
        return filepath
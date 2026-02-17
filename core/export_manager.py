import os
import pyperclip
from utils.helpers import safe_read_file, get_relative_path

class ExportManager:
    """Gestiona la exportación de archivos seleccionados en diferentes formatos"""
    
    def __init__(self, file_manager):
        self.file_manager = file_manager
    
    def export_to_clipboard(self, filepaths, use_relative_paths=True, include_content=True):
        """Exporta archivos al portapapeles"""
        output = []
        
        for filepath in filepaths:
            if not os.path.isfile(filepath):
                continue
            
            # Obtener ruta
            if use_relative_paths and self.file_manager.root_path:
                path_to_show = get_relative_path(filepath, self.file_manager.root_path)
            else:
                path_to_show = filepath
            
            output.append(f"{'='*60}")
            output.append(f"FILE: {path_to_show}")
            output.append(f"{'='*60}")
            
            if include_content:
                content, error = safe_read_file(filepath)
                if content:
                    output.append(content)
                elif error:
                    output.append(f"[Error reading file: {error}]")
            
            output.append("")  # Línea en blanco entre archivos
        
        result = '\n'.join(output)
        pyperclip.copy(result)
        return result
    
    def export_paths_only(self, filepaths, use_relative_paths=True):
        """Exporta solo las rutas de los archivos"""
        output = []
        
        for filepath in filepaths:
            if use_relative_paths and self.file_manager.root_path:
                path_to_show = get_relative_path(filepath, self.file_manager.root_path)
            else:
                path_to_show = filepath
            output.append(path_to_show)
        
        result = '\n'.join(output)
        pyperclip.copy(result)
        return result
    
    def export_with_tree_structure(self, filepaths):
        """Exporta con estructura de árbol"""
        if not self.file_manager.root_path:
            return self.export_paths_only(filepaths)
        
        # Organizar por estructura de carpetas
        tree = {}
        for filepath in filepaths:
            if not os.path.exists(filepath):
                continue
            relpath = get_relative_path(filepath, self.file_manager.root_path)
            parts = relpath.split(os.sep)
            
            current = tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # Es archivo
                    if '__files__' not in current:
                        current['__files__'] = []
                    current['__files__'].append(part)
                else:  # Es carpeta
                    if part not in current:
                        current[part] = {}
                    current = current[part]
        
        # Generar output con formato de árbol
        output = []
        output.append(f"Project: {os.path.basename(self.file_manager.root_path)}")
        output.append("=" * 60)
        self._build_tree_string(tree, output, "", True)
        
        result = '\n'.join(output)
        pyperclip.copy(result)
        return result
    
    def _build_tree_string(self, tree, output, prefix, is_last):
        """Construye string con formato de árbol"""
        items = [(k, v) for k, v in tree.items() if k != '__files__']
        items.sort()
        
        # Agregar carpetas
        for i, (name, subtree) in enumerate(items):
            is_last_item = (i == len(items) - 1) and '__files__' not in tree
            connector = "└── " if is_last_item else "├── "
            output.append(f"{prefix}{connector}📁 {name}/")
            
            extension = "    " if is_last_item else "│   "
            self._build_tree_string(subtree, output, prefix + extension, is_last_item)
        
        # Agregar archivos
        if '__files__' in tree:
            files = sorted(tree['__files__'])
            for i, filename in enumerate(files):
                is_last_file = i == len(files) - 1
                connector = "└── " if is_last_file else "├── "
                output.append(f"{prefix}{connector}📄 {filename}")
    
    def export_for_llm(self, filepaths):
        """Exporta optimizado para LLMs (con contexto claro)"""
        output = []
        output.append("# Project Files")
        output.append("")
        
        if self.file_manager.root_path:
            output.append(f"Root: {self.file_manager.root_path}")
            output.append("")
        
        for filepath in filepaths:
            if not os.path.isfile(filepath):
                continue
            
            relpath = self.file_manager.get_relative_path(filepath)
            output.append(f"## File: `{relpath}`")
            output.append("")
            
            content, error = safe_read_file(filepath)
            if content:
                ext = os.path.splitext(filepath)[1].lstrip('.')
                output.append(f"```{ext if ext else 'text'}")
                output.append(content)
                output.append("```")
            elif error:
                output.append(f"*Error: {error}*")
            
            output.append("")
        
        result = '\n'.join(output)
        pyperclip.copy(result)
        return result
    
    def export_to_file(self, filepaths, output_path, format='markdown'):
        """Exporta a un archivo"""
        if format == 'markdown':
            content = self.export_for_llm(filepaths)
        elif format == 'tree':
            content = self.export_with_tree_structure(filepaths)
        elif format == 'paths':
            content = self.export_paths_only(filepaths)
        else:
            content = self.export_to_clipboard(filepaths)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error exporting to file: {e}")
            return False
import os
from collections import defaultdict
from utils.helpers import count_lines_in_file, is_text_file, format_file_size

class ProjectStats:
    """Calcula y mantiene estadísticas del proyecto"""
    
    # Mapeo de extensiones a nombres de lenguajes
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'React',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript React',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.md': 'Markdown',
        '.sh': 'Shell',
        '.sql': 'SQL',
        '.txt': 'Text',
        
        '.png': 'Image',
        '.jpg': 'Image',
        '.jpeg': 'Image',
        '.gif': 'Image',
        '.svg': 'SVG',
        '.ico': 'Icon',
        '.webp': 'Image',
        '.bmp': 'Image',
        '.tiff': 'Image',
    }
    
    def __init__(self):
        self.stats = {
            'total_files': 0,
            'total_folders': 0,
            'total_size': 0,
            'total_lines': 0,
            'by_extension': defaultdict(lambda: {'count': 0, 'lines': 0, 'size': 0}),
            'selected_files': 0,
            'selected_lines': 0,
            'selected_size': 0
        }
    
    def calculate_stats(self, filepaths):
        """Calcula estadísticas de una lista de archivos"""
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_size': 0,
            'by_extension': defaultdict(lambda: {'count': 0, 'lines': 0, 'size': 0})
        }
        
        for filepath in filepaths:
            if not os.path.isfile(filepath):
                continue
            
            stats['total_files'] += 1
            
            try:
                size = os.path.getsize(filepath)
                stats['total_size'] += size
                
                ext = os.path.splitext(filepath)[1] or 'sin extensión'
                stats['by_extension'][ext]['count'] += 1
                stats['by_extension'][ext]['size'] += size
                
                if is_text_file(filepath):
                    lines = count_lines_in_file(filepath)
                    stats['total_lines'] += lines
                    stats['by_extension'][ext]['lines'] += lines
            except Exception as e:
                print(f"Error calculating stats for {filepath}: {e}")
        
        return stats
    
    def get_formatted_stats(self, stats):
        """Formatea las estadísticas para mostrar"""
        formatted = []
        formatted.append(f"📊 Estadísticas del Proyecto")
        formatted.append("=" * 50)
        formatted.append(f"Total de archivos: {stats['total_files']}")
        formatted.append(f"Total de líneas: {stats['total_lines']:,}")
        formatted.append(f"Tamaño total: {format_file_size(stats['total_size'])}")
        formatted.append("")
        
        if stats['by_extension']:
            formatted.append("Por extensión:")
            # Ordenar por cantidad de archivos
            sorted_exts = sorted(
                stats['by_extension'].items(), 
                key=lambda x: x[1]['count'], 
                reverse=True
            )
            
            for ext, data in sorted_exts[:10]:  # Top 10
                formatted.append(
                    f"  {ext}: {data['count']} archivos, "
                    f"{data['lines']:,} líneas, "
                    f"{format_file_size(data['size'])}"
                )
        
        return '\n'.join(formatted)
    
    def get_language_distribution(self, stats):
        """Obtiene distribución de lenguajes"""
        distribution = {}
        for ext, data in stats['by_extension'].items():
            lang = self.LANGUAGE_MAP.get(ext, ext)
            if lang not in distribution:
                distribution[lang] = {'count': 0, 'lines': 0, 'size': 0}
            distribution[lang]['count'] += data['count']
            distribution[lang]['lines'] += data['lines']
            distribution[lang]['size'] += data['size']
        
        return distribution
    
    def compare_stats(self, stats1, stats2):
        """Compara dos conjuntos de estadísticas"""
        comparison = {
            'files_diff': stats2['total_files'] - stats1['total_files'],
            'lines_diff': stats2['total_lines'] - stats1['total_lines'],
            'size_diff': stats2['total_size'] - stats1['total_size']
        }
        return comparison
    
    def get_top_files_by_lines(self, filepaths, top_n=10):
        """Obtiene los archivos con más líneas"""
        file_lines = []
        
        for filepath in filepaths:
            if not os.path.isfile(filepath) or not is_text_file(filepath):
                continue
            
            lines = count_lines_in_file(filepath)
            file_lines.append({
                'path': filepath,
                'lines': lines,
                'name': os.path.basename(filepath)
            })
        
        file_lines.sort(key=lambda x: x['lines'], reverse=True)
        return file_lines[:top_n]
    
    def get_top_files_by_size(self, filepaths, top_n=10):
        """Obtiene los archivos más grandes"""
        file_sizes = []
        
        for filepath in filepaths:
            if not os.path.isfile(filepath):
                continue
            
            try:
                size = os.path.getsize(filepath)
                file_sizes.append({
                    'path': filepath,
                    'size': size,
                    'size_formatted': format_file_size(size),
                    'name': os.path.basename(filepath)
                })
            except:
                pass
        
        file_sizes.sort(key=lambda x: x['size'], reverse=True)
        return file_sizes[:top_n]
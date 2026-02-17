import os
import re
from collections import defaultdict
from utils.helpers import is_text_file, safe_read_file

class CodeAnalyzer:
    """Analiza código para detectar TODOs, duplicados, métricas, etc."""
    
    def __init__(self):
        self.todo_patterns = [
            r'#\s*TODO:?\s*(.+)',
            r'//\s*TODO:?\s*(.+)',
            r'/\*\s*TODO:?\s*(.+)\s*\*/',
            r'<!--\s*TODO:?\s*(.+)\s*-->',
        ]
        
        self.fixme_patterns = [
            r'#\s*FIXME:?\s*(.+)',
            r'//\s*FIXME:?\s*(.+)',
            r'/\*\s*FIXME:?\s*(.+)\s*\*/',
            r'<!--\s*FIXME:?\s*(.+)\s*-->',
        ]
        
        self.bug_patterns = [
            r'#\s*BUG:?\s*(.+)',
            r'//\s*BUG:?\s*(.+)',
            r'/\*\s*BUG:?\s*(.+)\s*\*/',
            r'<!--\s*BUG:?\s*(.+)\s*-->',
        ]
    
    def find_todos_in_file(self, filepath):
        """Encuentra TODOs, FIXMEs y BUGs en un archivo"""
        if not is_text_file(filepath):
            return []
        
        content, error = safe_read_file(filepath)
        if error:
            return []
        
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Buscar TODOs
            for pattern in self.todo_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    findings.append({
                        'type': 'TODO',
                        'line': line_num,
                        'text': match.group(1).strip(),
                        'full_line': line.strip()
                    })
            
            # Buscar FIXMEs
            for pattern in self.fixme_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    findings.append({
                        'type': 'FIXME',
                        'line': line_num,
                        'text': match.group(1).strip(),
                        'full_line': line.strip()
                    })
            
            # Buscar BUGs
            for pattern in self.bug_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    findings.append({
                        'type': 'BUG',
                        'line': line_num,
                        'text': match.group(1).strip(),
                        'full_line': line.strip()
                    })
        
        return findings
    
    def find_todos_in_files(self, filepaths):
        """Encuentra TODOs en múltiples archivos"""
        all_findings = {}
        for filepath in filepaths:
            findings = self.find_todos_in_file(filepath)
            if findings:
                all_findings[filepath] = findings
        return all_findings
    
    def detect_duplicate_code(self, filepaths, min_lines=5):
        """Detecta código duplicado entre archivos"""
        # Implementación simplificada - busca bloques de líneas idénticas
        duplicates = []
        
        file_contents = {}
        for filepath in filepaths:
            if not is_text_file(filepath):
                continue
            content, error = safe_read_file(filepath)
            if not error and content:
                # Eliminar líneas vacías y comentarios simples
                lines = [line.strip() for line in content.split('\n') 
                        if line.strip() and not line.strip().startswith('#') 
                        and not line.strip().startswith('//')]
                file_contents[filepath] = lines
        
        # Comparar archivos
        files = list(file_contents.keys())
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                file1, file2 = files[i], files[j]
                lines1, lines2 = file_contents[file1], file_contents[file2]
                
                # Buscar bloques comunes
                common_blocks = self._find_common_blocks(lines1, lines2, min_lines)
                if common_blocks:
                    duplicates.append({
                        'file1': file1,
                        'file2': file2,
                        'blocks': common_blocks
                    })
        
        return duplicates
    
    def _find_common_blocks(self, lines1, lines2, min_lines):
        """Encuentra bloques de líneas comunes"""
        blocks = []
        i = 0
        while i < len(lines1):
            j = 0
            while j < len(lines2):
                # Contar líneas consecutivas iguales
                count = 0
                while (i + count < len(lines1) and 
                       j + count < len(lines2) and 
                       lines1[i + count] == lines2[j + count]):
                    count += 1
                
                if count >= min_lines:
                    blocks.append({
                        'lines': count,
                        'start1': i,
                        'start2': j,
                        'content': lines1[i:i+count]
                    })
                    i += count
                    j += count
                else:
                    j += 1
            i += 1
        
        return blocks
    
    def get_file_metrics(self, filepath):
        """Obtiene métricas de un archivo"""
        if not is_text_file(filepath):
            return None
        
        content, error = safe_read_file(filepath)
        if error:
            return None
        
        lines = content.split('\n')
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#') or stripped.startswith('//'):
                comment_lines += 1
            else:
                code_lines += 1
        
        return {
            'total_lines': len(lines),
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'file_size': len(content)
        }
    
    def analyze_project_complexity(self, filepaths):
        """Analiza la complejidad del proyecto"""
        metrics = {
            'total_files': len(filepaths),
            'by_extension': defaultdict(int),
            'total_lines': 0,
            'total_code_lines': 0,
            'total_comment_lines': 0,
            'largest_files': []
        }
        
        file_metrics = []
        for filepath in filepaths:
            if not os.path.isfile(filepath):
                continue
            
            ext = os.path.splitext(filepath)[1] or 'sin extensión'
            metrics['by_extension'][ext] += 1
            
            file_metric = self.get_file_metrics(filepath)
            if file_metric:
                metrics['total_lines'] += file_metric['total_lines']
                metrics['total_code_lines'] += file_metric['code_lines']
                metrics['total_comment_lines'] += file_metric['comment_lines']
                
                file_metrics.append({
                    'path': filepath,
                    'lines': file_metric['total_lines']
                })
        
        # Top archivos más grandes
        file_metrics.sort(key=lambda x: x['lines'], reverse=True)
        metrics['largest_files'] = file_metrics[:10]
        
        return metrics
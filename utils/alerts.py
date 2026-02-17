from tkinter import messagebox

class AlertManager:
    """Sistema de alertas inteligentes para carpetas sensibles"""
    
    WARNING_FOLDERS = {
        'node_modules': {
            'title': '⚠️ Node Modules Detectado',
            'message': 'Estás marcando "node_modules" que puede contener miles de archivos.\n\n¿Estás seguro de continuar?',
            'level': 'warning'
        },
        'venv': {
            'title': '⚠️ Virtual Environment Detectado',
            'message': 'Estás marcando un entorno virtual de Python.\n\nEsto puede incluir muchos archivos de librerías.\n¿Continuar?',
            'level': 'warning'
        },
        '.venv': {
            'title': '⚠️ Virtual Environment Detectado',
            'message': 'Estás marcando un entorno virtual de Python.\n\nEsto puede incluir muchos archivos de librerías.\n¿Continuar?',
            'level': 'warning'
        },
        'env': {
            'title': '⚠️ Environment Detectado',
            'message': 'Estás marcando una carpeta de entorno.\n\n¿Estás seguro?',
            'level': 'warning'
        },
        '.git': {
            'title': '⚠️ Carpeta Git Detectada',
            'message': 'Estás marcando la carpeta .git que contiene el historial completo del repositorio.\n\n¿Realmente necesitas esto?',
            'level': 'warning'
        },
        '__pycache__': {
            'title': '⚠️ Cache de Python',
            'message': 'Estás marcando archivos cache de Python (.pyc).\n\nGeneralmente no necesitas esto.\n¿Continuar?',
            'level': 'info'
        },
        'dist': {
            'title': '⚠️ Carpeta de Distribución',
            'message': 'Estás marcando la carpeta "dist" con archivos compilados.\n\n¿Es necesario?',
            'level': 'info'
        },
        'build': {
            'title': '⚠️ Carpeta Build',
            'message': 'Estás marcando la carpeta "build" con archivos compilados.\n\n¿Es necesario?',
            'level': 'info'
        }
    }
    
    def __init__(self):
        self.suppressed_warnings = set()
    
    def should_warn(self, folder_name):
        """Verifica si debe mostrar alerta para una carpeta"""
        folder_lower = folder_name.lower()
        return folder_lower in self.WARNING_FOLDERS and folder_lower not in self.suppressed_warnings
    
    def show_warning(self, folder_name):
        """Muestra alerta para una carpeta específica"""
        folder_lower = folder_name.lower()
        if folder_lower not in self.WARNING_FOLDERS:
            return True
        
        warning_info = self.WARNING_FOLDERS[folder_lower]
        
        if warning_info['level'] == 'warning':
            result = messagebox.askyesno(
                warning_info['title'],
                warning_info['message']
            )
            return result
        else:
            result = messagebox.askokcancel(
                warning_info['title'],
                warning_info['message']
            )
            return result
    
    def suppress_warning(self, folder_name):
        """Suprime advertencias futuras para esta carpeta"""
        self.suppressed_warnings.add(folder_name.lower())
    
    def reset_suppressions(self):
        """Resetea todas las advertencias suprimidas"""
        self.suppressed_warnings.clear()
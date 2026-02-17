import os

class SelectionManager:
    """Gestiona el estado de selección de archivos y carpetas"""
    
    def __init__(self):
        self.selected_items = set()  # Paths absolutos
        self.selection_state = {}  # node_id -> estado
    
    def toggle_selection(self, item_path):
        """Marca/desmarca un item"""
        if item_path in self.selected_items:
            self.selected_items.remove(item_path)
            return False
        else:
            self.selected_items.add(item_path)
            return True
    
    def select_item(self, item_path):
        """Marca un item"""
        self.selected_items.add(item_path)
    
    def deselect_item(self, item_path):
        """Desmarca un item"""
        self.selected_items.discard(item_path)
    
    def is_selected(self, item_path):
        """Verifica si un item está seleccionado"""
        return item_path in self.selected_items
    
    def get_selected_files(self):
        """Retorna solo archivos seleccionados"""
        return [path for path in self.selected_items if os.path.isfile(path)]
    
    def get_selected_folders(self):
        """Retorna solo carpetas seleccionadas"""
        return [path for path in self.selected_items if os.path.isdir(path)]
    
    def get_all_selected(self):
        """Retorna todos los items seleccionados"""
        return list(self.selected_items)
    
    def clear_selection(self):
        """Limpia todas las selecciones"""
        self.selected_items.clear()
        self.selection_state.clear()
    
    def get_selection_count(self):
        """Cuenta items seleccionados"""
        return len(self.selected_items)
    
    def select_all_in_folder(self, folder_path):
        """Selecciona recursivamente todo en una carpeta"""
        if not os.path.isdir(folder_path):
            return
        
        try:
            for root, dirs, files in os.walk(folder_path):
                # Agregar la carpeta actual
                self.selected_items.add(root)
                
                # Agregar todos los archivos
                for file in files:
                    filepath = os.path.join(root, file)
                    self.selected_items.add(filepath)
                
                # Agregar todas las subcarpetas
                for dir_name in dirs:
                    dirpath = os.path.join(root, dir_name)
                    self.selected_items.add(dirpath)
        except Exception as e:
            print(f"Error selecting folder contents: {e}")
    
    def deselect_all_in_folder(self, folder_path):
        """Deselecciona recursivamente todo en una carpeta"""
        if not os.path.isdir(folder_path):
            return
        
        # Crear lista temporal para evitar modificar durante iteración
        to_remove = []
        for item in self.selected_items:
            if item.startswith(folder_path):
                to_remove.append(item)
        
        for item in to_remove:
            self.selected_items.discard(item)
    
    def save_state(self, node_id, state):
        """Guarda el estado de un nodo del árbol"""
        self.selection_state[node_id] = state
    
    def get_state(self, node_id):
        """Obtiene el estado de un nodo"""
        return self.selection_state.get(node_id, False)
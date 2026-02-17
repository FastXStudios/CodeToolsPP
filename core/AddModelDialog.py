import tkinter as tk
from tkinter import messagebox

from gui.components import CustomToplevel

class AddModelDialog(CustomToplevel):
    def __init__(self, parent, theme_manager, language_manager, ai_manager):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            title="Agregar Modelo Personalizado",
            size="520x420",
            min_size=(480, 380),
            max_size=(700, 500)
        )
        
        self.language_manager = language_manager
        self.ai_manager = ai_manager
        self.result = None
        
        self._create_widgets()
        self.apply_theme()
    
    def _create_widgets(self):
        # Frame de contenido
        content = tk.Frame(self.content_frame)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nombre del modelo
        tk.Label(content, text="Nombre del modelo:", 
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        self.name_entry = tk.Entry(content, font=("Segoe UI", 10))
        self.name_entry.pack(fill="x", pady=(0, 12))
        self.name_entry.insert(0, "Mi Modelo Custom")
        
        # Model ID
        tk.Label(content, text="Model ID (ej: anthropic/claude-3-opus):", 
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        self.model_id_entry = tk.Entry(content, font=("Segoe UI", 10))
        self.model_id_entry.pack(fill="x", pady=(0, 12))
        
        # API Key
        tk.Label(content, text="API Key de OpenRouter:", 
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        self.api_key_entry = tk.Entry(content, font=("Segoe UI", 10), show="*")
        self.api_key_entry.pack(fill="x", pady=(0, 12))
        
        # Descripción
        tk.Label(content, text="Descripción (opcional):", 
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        self.desc_entry = tk.Entry(content, font=("Segoe UI", 10))
        self.desc_entry.pack(fill="x", pady=(0, 12))
        
        # Max tokens
        tk.Label(content, text="Máximo de tokens:", 
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        self.tokens_spinbox = tk.Spinbox(content, from_=1000, to=200000, 
                                        increment=1000, font=("Segoe UI", 10))
        self.tokens_spinbox.delete(0, tk.END)
        self.tokens_spinbox.insert(0, "8000")
        self.tokens_spinbox.pack(fill="x", pady=(0, 20))
        
        # Botones
        btn_frame = tk.Frame(content)
        btn_frame.pack(fill="x")
        
        tk.Button(btn_frame, text="  Agregar", command=self._on_add,
                 font=("Segoe UI", 9), cursor="hand2", 
                 bd=0, relief="flat", padx=14, pady=7).pack(side="left", padx=(0, 6))
        
        tk.Button(btn_frame, text="  Cancelar", command=self.destroy,
                 font=("Segoe UI", 9), cursor="hand2",
                 bd=0, relief="flat", padx=14, pady=7).pack(side="left")
    
    def _on_add(self):
        name = self.name_entry.get().strip()
        model_id = self.model_id_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        desc = self.desc_entry.get().strip()
        max_tokens = int(self.tokens_spinbox.get())
        
        if not name or not model_id or not api_key:
            messagebox.showwarning("Campos requeridos", 
                                 "Completa todos los campos obligatorios")
            return
        
        # Generar key única
        key = f"custom_{name.lower().replace(' ', '_')}"
        
        # Agregar al manager
        self.ai_manager.add_custom_model(
            key=key,
            name=name,
            model_id=model_id,
            api_key=api_key,
            logo="ai.gif",
            max_tokens=max_tokens,
            description=desc
        )
        
        self.result = key
        self.destroy()
    
    def apply_theme(self):
        self.apply_base_theme()
        # Aplicar tema a widgets...
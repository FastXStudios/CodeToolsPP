"""
AI Manager para Code Tools++
Gestiona la integración con OpenRouter API y múltiples modelos de IA
"""

import os
import json
import requests
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class AIManager:
    """
    Gestor centralizado de IA con soporte para:
    - Configuración desde GitHub (keys renovables sin reempaquetar)
    - Múltiples modelos (Google Gemini, DeepSeek, custom)
    - Filtrado inteligente de archivos
    - Gestión de contexto y tokens
    """
    
    # Modelos built-in (fallback si GitHub falla)
    DEFAULT_MODELS = {
        "deepseek": {
            "name": "DeepSeek V3.2",
            "model_id": "deepseek/deepseek-chat",
            "api_key": "coloca-tu-key",
            "logo": "deepseek.gif",
            "max_tokens": 8000,
            "description": "Modelo incluido",
            "is_builtin": True  # Nuevo campo
        }
    }
    
    # Directorios a ignorar (entornos virtuales, dependencias, etc)
    IGNORED_DIRS = {
        'node_modules', 'venv', '.venv', 'env', '.env',
        '__pycache__', '.git', '.svn', '.hg',
        'dist', 'build', '.next', '.nuxt', 'out',
        'target', 'bin', 'obj',
        '.idea', '.vscode', '.vs',
        'coverage', '.pytest_cache', '.mypy_cache',
        'site-packages', 'Lib', 'lib', 'Scripts',
        '.egg-info', 'eggs', 'bower_components',
        '.gradle', '.m2', '.ivy2',
        'vendor', 'packages', 'deps',
    }
    
    # Extensiones a ignorar
    IGNORED_EXTENSIONS = {
        '.pyc', '.pyo', '.so', '.dll', '.exe', '.o', '.a',
        '.min.js', '.min.css', '.map',
        '.lock', '.log',
        '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
        '.mp3', '.mp4', '.avi', '.mov',
        '.zip', '.tar', '.gz', '.rar', '.7z',
        '.pdf', '.doc', '.docx',
    }
    
    # Límites de tamaño
    MAX_FILE_SIZE = 1024 * 1024  # 1MB por archivo
    MAX_LINES_PER_FILE = 500
    MAX_TOTAL_TOKENS = 100000  # ~100K tokens máximo de contexto
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.models = {}
        self.current_model = None
        self.custom_models = {}
        
        # Cargar configuración
        self._load_config()
    
    # LÍNEA 85-110: Reemplazar _load_config con esto:
    def _load_config(self):
        """Carga configuración LOCAL únicamente - SIN GITHUB"""
        # Cargar modelos por defecto
        self.models = self.DEFAULT_MODELS.copy()
        
        # Directorio para logos personalizados
        self.custom_logos_dir = "assets/logos/custom"
        os.makedirs(self.custom_logos_dir, exist_ok=True)
        
        # Cargar modelos custom guardados
        custom = self.config_manager.get("ai_custom_models", {})
        self.custom_models = custom
        self.models.update(custom)
        
        # ✅ PERSISTIR modelo actual correctamente
        saved_model = self.config_manager.get("ai_current_model", "deepseek")
        self.current_model = saved_model if saved_model in self.models else "deepseek"
    
    def get_available_models(self) -> List[Dict]:
        """Retorna lista de modelos disponibles"""
        return [
            {
                "key": key,
                "name": data["name"],
                "description": data.get("description", ""),
                "logo": data.get("logo", "ai.gif"),
                "is_custom": key in self.custom_models
            }
            for key, data in self.models.items()
        ]
    
    def set_current_model(self, model_key: str):
        """Cambia el modelo actual"""
        if model_key in self.models:
            self.current_model = model_key
            self.config_manager.set("ai_current_model", model_key)
            return True
        return False
    
    # LÍNEA 130: Agregar método para subir logos personalizados:
    def add_custom_model(self, key: str, name: str, model_id: str, 
                        api_key: str, logo_path: str = None,
                        max_tokens: int = 8000, description: str = ""):
        """
        Agrega modelo personalizado con logo opcional
        
        Args:
            logo_path: Ruta al PNG/GIF del logo (se copiará a assets/logos/custom/)
        """
        import shutil
        
        # Manejar logo personalizado
        logo_filename = "ai.gif"  # default
        
        if logo_path and os.path.exists(logo_path):
            ext = os.path.splitext(logo_path)[1]
            logo_filename = f"{key}{ext}"
            dest_path = os.path.join(self.custom_logos_dir, logo_filename)
            
            try:
                shutil.copy2(logo_path, dest_path)
                logo_filename = f"custom/{logo_filename}"  # Ruta relativa
            except Exception as e:
                print(f"Error copiando logo: {e}")
                logo_filename = "ai.gif"
        
        custom_model = {
            "name": name,
            "model_id": model_id,
            "api_key": api_key,
            "logo": logo_filename,
            "max_tokens": max_tokens,
            "description": description,
            "is_builtin": False
        }
        
        self.custom_models[key] = custom_model
        self.models[key] = custom_model
        
        # ✅ GUARDAR para persistencia
        self.config_manager.set("ai_custom_models", self.custom_models)
        return True
    
    def remove_custom_model(self, key: str):
        """Elimina un modelo personalizado"""
        if key in self.custom_models:
            del self.custom_models[key]
            del self.models[key]
            self.config_manager.set("ai_custom_models", self.custom_models)
            
            # Si era el modelo actual, cambiar a default
            if self.current_model == key:
                self.current_model = "deepseek"
                self.config_manager.set("ai_current_model", "deepseek")
            return True
        return False
    
    def prepare_context(self, files: List[str], file_manager) -> Tuple[str, Dict]:
        """
        Prepara el contexto de archivos para enviar a la IA
        Filtra archivos grandes, binarios, y directorios ignorados
        """
        context_parts = []
        stats = {
            "total_files": len(files),
            "included_files": 0,
            "skipped_files": 0,
            "total_lines": 0,
            "estimated_tokens": 0
        }
        
        for filepath in files:
            # Verificar si debe ignorarse
            if self._should_ignore_file(filepath):
                stats["skipped_files"] += 1
                continue
            
            # Verificar si es archivo
            if not os.path.isfile(filepath):
                stats["skipped_files"] += 1
                continue
            
            # Verificar tamaño
            try:
                file_size = os.path.getsize(filepath)
                if file_size > self.MAX_FILE_SIZE:
                    stats["skipped_files"] += 1
                    continue
            except:
                stats["skipped_files"] += 1
                continue
            
            # Leer contenido
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.readlines()
                
                # Truncar si es muy largo
                if len(content) > self.MAX_LINES_PER_FILE:
                    content = content[:self.MAX_LINES_PER_FILE]
                    content.append(f"\n... (archivo truncado, {len(content)} líneas más)")
                
                relative_path = file_manager.get_relative_path(filepath)
                
                context_parts.append(f"=== Archivo: {relative_path} ===")
                context_parts.append("".join(content))
                context_parts.append("")
                
                stats["included_files"] += 1
                stats["total_lines"] += len(content)
                
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                stats["skipped_files"] += 1
        
        context = "\n".join(context_parts)
        stats["estimated_tokens"] = len(context) // 4  # Estimación aproximada
        
        return context, stats
    
    def _should_ignore_file(self, filepath: str) -> bool:
        """Verifica si un archivo debe ser ignorado"""
        path = Path(filepath)
        
        # Verificar directorios ignorados
        for part in path.parts:
            if part in self.IGNORED_DIRS:
                return True
        
        # Verificar extensión
        if path.suffix in self.IGNORED_EXTENSIONS:
            return True
        
        return False
    
    def send_request(self, prompt: str, context: str = "", 
                    system_prompt: str = "", temperature: float = 0.7) -> Dict:
        """
        Envía una petición a la API de OpenRouter
        Retorna: {"success": bool, "content": str, "error": str, "usage": dict}
        """
        if not self.current_model or self.current_model not in self.models:
            return {
                "success": False,
                "content": "",
                "error": "No hay modelo seleccionado",
                "usage": {}
            }
        
        model_data = self.models[self.current_model]
        api_key = model_data["api_key"]
        model_id = model_data["model_id"]
        
        # Construir mensaje
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        user_content = prompt
        if context:
            user_content = f"{context}\n\n{prompt}"
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        # Hacer petición
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/byronc377/code-tools-plus",
                "X-Title": "Code Tools++"
            }
            
            data = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": model_data.get("max_tokens", 8000)
            }
            
            start_time = time.time()
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "error": "",
                    "usage": result.get("usage", {}),
                    "elapsed_time": elapsed_time
                }
            else:
                error_msg = self._parse_error(response)
                return {
                    "success": False,
                    "content": "",
                    "error": error_msg,
                    "usage": {}
                }
                
        except requests.Timeout:
            return {
                "success": False,
                "content": "",
                "error": "Tiempo de espera agotado (60s). Intenta con menos archivos.",
                "usage": {}
            }
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "error": f"Error de conexión: {str(e)}",
                "usage": {}
            }
    
    def _parse_error(self, response) -> str:
        """Parsea errores de la API"""
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Error desconocido")
            
            # Errores comunes
            if "rate_limit" in error_msg.lower():
                return "Límite de peticiones alcanzado. Espera un momento."
            elif "tokens" in error_msg.lower():
                return "Límite de tokens excedido. Selecciona menos archivos."
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                return "API key inválida. Verifica tu configuración."
            else:
                return f"Error de API: {error_msg}"
        except:
            return f"Error HTTP {response.status_code}"
    
    def send_request_async(self, prompt: str, context: str = "",
                          system_prompt: str = "", 
                          callback: callable = None) -> None:
        """
        Versión asíncrona de send_request para UI no bloqueante
        callback: función que recibe el resultado
        """
        import threading
        
        def worker():
            result = self.send_request(prompt, context, system_prompt)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    # ═══════════════════════════════════════════════════════════
    # FUNCIONES DE IA PRE-DEFINIDAS
    # ═══════════════════════════════════════════════════════════
    
    def analyze_code(self, files: List[str], file_manager) -> Dict:
        """Análisis general de código"""
        context, stats = self.prepare_context(files, file_manager)
        
        if stats["included_files"] == 0:
            return {
                "success": False,
                "content": "",
                "error": "No hay archivos válidos para analizar"
            }
        
        system_prompt = """Eres un experto en análisis de código. 
Analiza el código proporcionado y proporciona:
1. Resumen general del proyecto
2. Arquitectura y patrones detectados
3. Calidad del código
4. Posibles mejoras
5. Problemas o code smells detectados"""
        
        prompt = f"""Analiza el siguiente código ({stats['included_files']} archivos, {stats['total_lines']} líneas):

Proporciona un análisis detallado y profesional."""
        
        return self.send_request(prompt, context, system_prompt)
    
    def fix_code(self, files: List[str], file_manager, specific_issue: str = "") -> Dict:
        """Detecta y sugiere fixes para errores"""
        context, stats = self.prepare_context(files, file_manager)
        
        if stats["included_files"] == 0:
            return {
                "success": False,
                "content": "",
                "error": "No hay archivos válidos para analizar"
            }
        
        system_prompt = """Eres un experto en debugging y corrección de código.
Identifica errores, bugs, problemas de sintaxis, y proporciona soluciones claras."""
        
        issue_context = f"\n\nProblema específico: {specific_issue}" if specific_issue else ""
        
        prompt = f"""Analiza el siguiente código y detecta:
1. Errores de sintaxis
2. Bugs potenciales
3. Problemas de lógica
4. Vulnerabilidades
5. Código problemático

Proporciona soluciones claras y código corregido cuando sea necesario.{issue_context}"""
        
        return self.send_request(prompt, context, system_prompt)
    
    def generate_documentation(self, files: List[str], file_manager) -> Dict:
        """Genera documentación automática"""
        context, stats = self.prepare_context(files, file_manager)
        
        if stats["included_files"] == 0:
            return {
                "success": False,
                "content": "",
                "error": "No hay archivos válidos para documentar"
            }
        
        system_prompt = """Eres un experto en documentación técnica.
Genera documentación clara, profesional y completa en formato Markdown."""
        
        prompt = """Genera documentación completa para este código incluyendo:
1. Descripción general
2. Estructura de archivos
3. Funciones/clases principales
4. Uso y ejemplos
5. Dependencias
6. Configuración necesaria"""
        
        return self.send_request(prompt, context, system_prompt)
    
    def optimize_code(self, files: List[str], file_manager) -> Dict:
        """Sugiere optimizaciones de rendimiento"""
        context, stats = self.prepare_context(files, file_manager)
        
        if stats["included_files"] == 0:
            return {
                "success": False,
                "content": "",
                "error": "No hay archivos válidos para optimizar"
            }
        
        system_prompt = """Eres un experto en optimización de código y rendimiento.
Identifica cuellos de botella y proporciona mejoras concretas."""
        
        prompt = """Analiza el código y sugiere optimizaciones para:
1. Rendimiento (tiempo de ejecución)
2. Uso de memoria
3. Complejidad algorítmica
4. Mejores prácticas
5. Refactoring sugerido

Proporciona código optimizado cuando sea relevante."""
        
        return self.send_request(prompt, context, system_prompt)
    
    def explain_code(self, files: List[str], file_manager) -> Dict:
        """Explica el código de manera educativa"""
        context, stats = self.prepare_context(files, file_manager)
        
        if stats["included_files"] == 0:
            return {
                "success": False,
                "content": "",
                "error": "No hay archivos válidos para explicar"
            }
        
        system_prompt = """Eres un profesor experto en programación.
Explica el código de manera clara y educativa, asumiendo diferentes niveles de experiencia."""
        
        prompt = """Explica este código de manera clara y educativa:
1. ¿Qué hace el código?
2. ¿Cómo funciona?
3. Conceptos clave utilizados
4. Por qué está estructurado así
5. Posibles mejoras educativas

Usa ejemplos y analogías cuando sea útil."""
        
        return self.send_request(prompt, context, system_prompt)
    
    def apply_modifications(self, files: List[str], file_manager, 
                           ai_response: str) -> Tuple[bool, str]:
        """
        Aplica modificaciones sugeridas por la IA al código
        PELIGROSO: Requiere confirmación del usuario
        
        Retorna: (success, message)
        """
        # TODO: Implementar parsing inteligente de respuestas AI
        # y aplicación segura de cambios
        
        # Por ahora, retornar False para evitar modificaciones accidentales
        return False, "Función en desarrollo. Por seguridad, copia el código manualmente."

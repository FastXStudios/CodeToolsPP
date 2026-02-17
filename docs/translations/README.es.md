<div align="center">
  <img src="../../docs/screenshots/icon.png" alt="Code Tools++" width="90"/>
  <h1>Code Tools ++</h1>

  <p><strong>Kit de herramientas de escritorio con IA para desarrolladores que trabajan con grandes bases de código.</strong><br>
  Explora, analiza, limpia, documenta y chatea con tu código — todo desde una sola interfaz.</p>
  <p>Idioma: haz clic en las banderas</p>

  <p align="center">
    <a href="../../README.md"><img src="../../assets/flags/en.png" width="32" height="32" alt="English"></a>
    <a href="README.es.md"><img src="../../assets/flags/es.png" width="32" height="32" alt="Español"></a>
    <a href="README.zh.md"><img src="../../assets/flags/zh.png" width="32" height="32" alt="中文"></a>
    <a href="README.ru.md"><img src="../../assets/flags/ru.png" width="32" height="32" alt="Русский"></a>
  </p>

  <p>
    <a href="#instalación"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python"></a>
    <a href="#instalación"><img src="https://img.shields.io/badge/Plataforma-Windows-0078D6?logo=windows&logoColor=white" alt="Plataforma"></a>
    <a href="#tecnologías"><img src="https://img.shields.io/badge/GUI-Tkinter-FFB000" alt="GUI"></a>
    <a href="#chat-ia--motor-de-modelos"><img src="https://img.shields.io/badge/IA-DeepSeek%20%7C%20OpenRouter-6C47FF?logo=openai&logoColor=white" alt="IA"></a>
    <a href="#licencia"><img src="https://img.shields.io/badge/Licencia-MIT-22c55e.svg" alt="Licencia"></a>
  </p>

  <p>
    <a href="#características">Características</a> •
    <a href="#chat-ia--motor-de-modelos">Motor IA</a> •
    <a href="#instalación">Instalar</a> •
    <a href="#inicio-rápido-30-segundos">Uso</a> •
    <a href="#arquitectura-del-proyecto">Arquitectura</a> •
    <a href="#hoja-de-ruta">Hoja de ruta</a>
  </p>

  <hr>

  <p><em>Deja de copiar archivos a mano. Deja de cambiar entre 5 herramientas. Empieza a entregar.</em></p>
</div>

---

## ⬇️ Descargar

<div align="center">

<h3>Code Tools ++ v1.0.0</h3>

<a href="https://fastxstudios.github.io/CodeToolsLandingPage/">
  <img src="https://img.shields.io/badge/Descargar-Instalador_Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Instalador Windows">
</a>
&nbsp;
<a href="https://fastxstudios.github.io/CodeToolsLandingPage/">
  <img src="https://img.shields.io/badge/Descargar-Versión_Portátil-FFB000?style=for-the-badge&logoColor=white" alt="Versión Portátil">
</a>

</div>

---

## ¿Por qué Code Tools ++?

Todo desarrollador que alguna vez ha preparado una base de código para revisión por IA, auditoría o una entrega ha hecho esto:

1. Abrir carpetas manualmente y seleccionar archivos uno a uno.
2. Copiar y pegar contenido en un prompt — esperando no haberse olvidado contexto.
3. Buscar TODO/FIXMEs y código muerto por separado.
4. Limpiar sentencias `print()` archivo por archivo.
5. Escribir un README desde cero al final del sprint.

**Code Tools ++ elimina todo eso.** Es una aplicación de escritorio nativa (Python + Tkinter) construida específicamente para los flujos de trabajo que los desarrolladores realmente usan — con un asistente de IA integrado como característica de primera clase, no como un añadido.

---

## Características

### 🤖 Chat IA & Motor de Modelos

Este es el diferenciador principal. Code Tools ++ incluye una interfaz de IA conversacional completa directamente conectada a tus archivos seleccionados.

**Modelo integrado:** [DeepSeek](https://platform.deepseek.com/) — un LLM de alto rendimiento y rentable optimizado para tareas de código.

**Soporte de modelos personalizados vía [OpenRouter](https://openrouter.ai/):** Agrega cualquier modelo disponible en OpenRouter (GPT-4o, Claude, Gemini, Mistral, LLaMA, etc.) proporcionando un ID de modelo y clave API. Sin dependencias adicionales. El selector de modelos admite logos GIF animados por modelo, selección persistente entre sesiones y eliminación de entradas personalizadas con un clic.

**Modos de contexto:**
- `Smart` — envía metadatos de archivo (nombre, extensión, cantidad de líneas, tamaño) para consultas de contexto ligeras.
- `Full` — envía el contenido completo de los archivos para análisis profundo, refactorización y generación de documentación.

**Acciones integradas (prompts de un clic):**

| Acción | Qué hace |
|---|---|
| **Analizar** | Revisa los archivos seleccionados en busca de estructura, patrones y problemas |
| **Corregir Errores** | Identifica bugs y sugiere código corregido |
| **Documentar** | Genera docstrings en línea y documentación a nivel de función |
| **Optimizar** | Propone mejoras de rendimiento y refactorización |
| **Explicar** | Produce explicaciones en lenguaje natural de lo que hace el código |

**Renderizado Markdown en el chat:** Las respuestas de la IA renderizan bloques de código con resaltado de sintaxis (Python, JS/TS, JSON, Bash), un botón de copiar por bloque y ajuste de texto automático — no solo texto plano.

**Persistencia:** El historial de chat, el modelo seleccionado, el modo de contexto y el contador de tokens se guardan en disco y se restauran entre sesiones.

---

### 🗂️ Explorador Inteligente de Repositorio

- Árbol de archivos con selección por casillas de verificación de forma recursiva.
- Advertencias visuales para directorios pesados/ignorados (`node_modules`, `venv`, `.git`, `dist`, etc.) antes de incluirlos accidentalmente.
- Historial de carpetas recientes con menú visual y limpieza con un clic.
- Búsqueda avanzada de archivos con navegación rápida.

---

### 📤 Exportación Profesional para IA y Trabajo Diario

Cuatro modos de exportación diseñados para flujos de trabajo reales de desarrolladores:

| Modo | Salida |
|---|---|
| **Copiar con Contenido** | Contenido completo de archivos, concatenado |
| **Copiar Solo Rutas** | Rutas relativas de los archivos seleccionados |
| **Copiar Árbol** | Estructura de directorio en ASCII |
| **Copiar para LLM** | Formato estructurado optimizado para prompts de IA — incluye rutas, marcadores de lenguaje y separadores limpios |

Todos los modos disponibles desde un menú de exportación estilizado. Guardar en archivo disponible directamente.

---

### 📊 Panel de Calidad Técnica

Una sola vista que muestra lo que de otro modo tardarías 20 minutos en recopilar:

- **Estadísticas del proyecto:** total de archivos, líneas de código, distribución de tamaño.
- **Rastreador de TODO/FIXME:** lista cada anotación con su ubicación en el archivo.
- **Detector de duplicados:** señala archivos con contenido idéntico o casi idéntico.
- **Distribución por lenguaje:** desglose por tipo de archivo con métricas clave.

No se requieren herramientas externas. Se ejecuta completamente sobre el proyecto local.

---

### 🧹 LimpMax — Limpiador de Código Masivo y Seguro

Elimina artefactos de desarrollo antes de commits, releases o revisiones de código:

- Elimina sentencias `print()` / `console.log()` / `logging.*` según las reglas de cada lenguaje.
- Elimina comentarios en línea (configurable por lenguaje).
- Diseñado para limpieza previa a la entrega — rápido, determinista y reversible si se combina con control de versiones.

---

### 📝 Generador Integrado de README

- Genera un README completo en Markdown basado en la estructura del proyecto.
- Vista previa en vivo con Markdown renderizado.
- Traducción de idiomas en tiempo real (ES / EN / ZH / RU) — cambia el idioma y la vista previa se actualiza de inmediato.
- Útil para estandarizar documentación entre equipos o publicar proyectos de código abierto rápidamente.

---

### ⚡ UX Construida para la Velocidad

- Menús personalizados (`Recientes`, `Exportar`) con íconos PNG.
- Vista previa de archivos en tiempo real.
- Cambio de tema e idioma en caliente sin necesidad de reiniciar.
- Atajos de teclado para un flujo de trabajo continuo.

| Atajo | Acción |
|---|---|
| `Ctrl+O` | Abrir carpeta |
| `Ctrl+Q` | Salir de la aplicación |
| `F5` | Actualizar árbol de archivos |
| `E` / `Espacio` | Marcar / Desmarcar archivo |
| `Ctrl+C` | Copiar seleccionados |
| `Ctrl+D` | Limpiar selección |
| `Ctrl+F` | Buscar archivos |
| `Ctrl+P` | Mostrar/Ocultar vista previa |
| `Doble Clic` | Marcar archivo |
| `Clic Derecho` | Abrir menú contextual |
| `Ctrl++` | Acercar zoom |
| `Ctrl+-` | Alejar zoom |
| `Ctrl+0` | Restablecer zoom |
| `Ctrl+Scroll` | Zoom con scroll del ratón |

---

## Idiomas Soportados (UI)

`Español` · `English` · `中文` · `Русский`

---

## Instalación

### Requisitos previos

- Python 3.12+
- Windows (principal), Linux/macOS (funcional, no completamente probado)

### 1. Clonar

```bash
git clone https://github.com/FastXStudios/CodeToolsPP.git
cd CodeToolsPP
```

### 2. Crear entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar

```bash
python main.py
```

---

## Inicio Rápido (30 segundos)

```
1. Abre tu carpeta de proyecto  →  Ctrl+O
2. Selecciona los archivos relevantes  →  árbol de casillas
3. Abre el Chat IA  →  pregunta cualquier cosa sobre tu código
4. Exporta contexto para LLM  →  Menú Exportar → Copiar para LLM
5. Revisa el Panel  →  encuentra TODOs, duplicados, métricas
6. Ejecuta LimpMax  →  elimina logs de depuración antes del commit
7. Genera el README  →  Herramientas → Generador de README
```

---

## Configuración de IA

### Usando el modelo DeepSeek integrado

DeepSeek viene preconfigurado. Agrega tu clave API en **Configuración → IA → Clave API**.  
Obtén una clave en [https://openrouter.ai/](https://openrouter.ai/).

### Agregar un modelo personalizado (OpenRouter o cualquier endpoint compatible con OpenAI)

1. Abre la ventana de Chat IA.
2. Haz clic en **Seleccionar Modelo → Agregar Modelo Personalizado**.
3. Completa:
   - **Nombre** — nombre para mostrar (ej. `GPT-4o`)
   - **ID del Modelo** — tal como aparece en OpenRouter (ej. `openai/gpt-4o`)
   - **Clave API** — tu clave de OpenRouter
   - **Máx. Tokens** — límite de la ventana de contexto
   - **Logo** — PNG/GIF opcional para la tarjeta del modelo
4. Guardar. El modelo aparece en el selector de inmediato.

Los modelos de OpenRouter incluyen: `openai/gpt-4o`, `anthropic/claude-3-5-sonnet`, `google/gemini-pro`, `meta-llama/llama-3-70b-instruct`, `mistralai/mistral-large`, y cientos más.

---

## Arquitectura del Proyecto

```
main.py
├── core/
│   ├── ai_manager.py          # Registro de modelos, llamadas API, preparación de contexto
│   ├── code_analyzer.py       # Análisis estático, detección de TODO/FIXME
│   ├── export_manager.py      # Todos los formatos de exportación, incluido modo LLM
│   ├── file_manager.py        # E/S de archivos, metadatos, consultas de información
│   ├── limpmax_processor.py   # Motor de limpieza de código con conciencia de lenguaje
│   ├── project_stats.py       # Agregación de métricas
│   ├── selection_manager.py   # Gestión del estado de casillas de verificación
│   └── startup_preloader.py   # Inicialización en segundo plano
├── gui/
│   ├── main_window.py
│   ├── tree_view.py
│   ├── preview_window.py
│   ├── dashboard_window.py
│   ├── ai_window.py           # UI completa de chat IA con renderizado Markdown
│   ├── limpmax_window.py
│   ├── search_dialog.py
│   ├── readme_generator_dialog.py
│   ├── recent_folders_menu.py
│   ├── export_menu.py
│   ├── widgets/
│   └── components/
└── utils/
    ├── config_manager.py
    ├── language_manager.py    # i18n: ES / EN / ZH / RU
    ├── theme_manager.py
    ├── file_icons.py
    ├── alerts.py
    └── helpers.py
```

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12+ |
| GUI | Tkinter / ttk |
| Imágenes | Pillow |
| Renderizado HTML | tkinterweb |
| Gráficos | matplotlib |
| Markdown | markdown2 |
| HTTP | requests |
| Portapapeles | pyperclip |
| IA | API REST compatible con OpenAI (DeepSeek, OpenRouter) |

---

## Compilar Ejecutable (PyInstaller)

```powershell
  .\.venv\Scripts\python.exe -m PyInstaller
  --noconfirm --clean --onefile 
  --windowed --name "CodeToolsPP" 
  --icon ".\icon.ico" --add-data ".\assets;assets" 
  --add-data ".\data;data" 
  --add-data ".\icon.ico;." 
  --hidden-import "PIL._tkinter_finder" 
  --collect-submodules "PIL" 
  --collect-data "tkinterweb" 
  .\main.py
```

Salida: `dist/CodeToolsPP.exe`

---

## Capturas de Pantalla

**Interfaz Principal:** Interfaz principal con barra de herramientas y contadores de archivos, líneas y tamaño.
![Main](../../docs/screenshots/main.png)

**Chat IA:** Chat de IA con opciones de análisis de archivos.
![AI Chat](../../docs/screenshots/ai-chat.png)

**Selector de Modelos:** Selector de modelos de IA con DeepSeek V3.2 activo y opción para agregar modelos personalizados.
![Model Selector](../../docs/screenshots/model-selector.png)

**Menú de Exportación:** Menú de exportación con opciones para copiar rutas, estructura de árbol y formato listo para LLM.
![Export](../../docs/screenshots/export-menu.png)

**Panel:** Panel de estadísticas con distribución de archivos, histograma y paginación.
![Dashboard](../../docs/screenshots/dashboard.png)

**LimpMax:** Herramienta de limpieza máxima para eliminar prints/logs y comentarios por lenguaje.
![LimpMax](../../docs/screenshots/limpmax.png)

**Generador de README:** Generador de README con secciones configurables, insignias y vista previa.
![README Generator](../../docs/screenshots/readme-generator.png)

---

## Casos de Uso Reales

- **Depuración asistida por IA:** Selecciona el módulo roto → abre el chat IA → "¿Por qué esta función devuelve None?" — el contexto completo del archivo se envía automáticamente.
- **Auditoría pre-refactorización:** Abre un repositorio heredado → el Panel muestra distribución de lenguajes, recuento de TODOs y archivos duplicados en segundos.
- **Limpieza pre-commit:** Ejecuta LimpMax para eliminar todas las sentencias `print()`/`console.log()` en 40 archivos a la vez.
- **Documentación técnica:** Genera README a partir de la estructura del proyecto, tradúcelo al inglés o chino, expórtalo — en menos de 2 minutos.
- **Incorporación de equipo:** Guía a un nuevo desarrollador por la estructura del proyecto usando la exportación de árbol + copia optimizada para LLM para una orientación instantánea.
- **Preparación de revisión de código:** Exporta los archivos seleccionados como contexto LLM, pégalo en tu IA preferida sin ruido alguno.

---

## Hoja de Ruta

- [ ] Optimización de rendimiento para repositorios muy grandes (>10k archivos)
- [ ] Más presets de exportación LLM (plantillas de system prompt, conciencia del presupuesto de tokens)
- [ ] Reglas extendidas de LimpMax y controles de seguridad por archivo
- [ ] Suite de pruebas automatizadas
- [ ] Pipeline de lanzamiento y soporte de actualización automática
- [ ] Empaquetado para Linux/macOS

---

## Contribuir

1. Haz un fork del repositorio.
2. Crea una rama: `git checkout -b feature/tu-mejora`
3. Confirma: `git commit -m "feat: tu mejora"`
4. Sube: `git push origin feature/tu-mejora`
5. Abre un Pull Request.

---

## Recursos de Terceros

Este proyecto incorpora íconos de:

**vscode-material-icon-theme**  
Copyright (c) 2025 Material Extensions  
Licenciado bajo la Licencia MIT  
https://github.com/material-extensions/vscode-material-icon-theme  

La licencia original se incluye en el directorio `licenses/`.

---

## Licencia

[Licencia MIT](LICENSE)

---

## Autor

**Byron Vera**  
GitHub: [FastXStudios](https://github.com/FastXStudios/CodeToolsPP)  
Email: byronvera113@gmail.com
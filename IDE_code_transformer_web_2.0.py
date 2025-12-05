import requests
import json
import sys
import re
from flask import Flask, request, jsonify

# --- CONFIGURACIÓN DEL LLM ---
API_URL = "http://172.20.10.2:1234/v1/chat/completions"
MODEL = "meta-llama-3.1-8b-instruct"

# Lenguajes soportados (Usados en la interfaz y para el prompt del LLM)
LANGUAGES = {
    "python": "Python",
    "javascript": "JavaScript",
    "java": "Java",
    "cpp": "C++",
    "csharp": "C#",
    "ruby": "Ruby",
    "go": "Go",
}

# --- FUNCIÓN DE CONEXIÓN CON LLM ---
def get_llm_response(prompt, is_refactor=False):
    system_content = "Eres un asistente de codificación útil. Analiza el código proporcionado, corrige errores mínimos si es necesario (como typos en funciones estándar). No agregues código extra innecesario. Responde solo con el código corregido, y si se requiere, agrega una línea de separación '---' seguida de una sección 'Cambios' con una breve descripción de los cambios realizados o 'Ningún cambio necesario'."
    if is_refactor:
        system_content = "Eres un asistente de codificación útil. Refactoriza el código Python proporcionado para optimizarlo, mejorar la legibilidad, eficiencia y estructura, sin cambiar su funcionalidad. No corrijas errores, solo refactoriza. Responde solo con el código refactorizado, y agrega una línea de separación '---' seguida de una sección 'Cambios' con una breve descripción de los cambios realizados o 'Ningún cambio necesario'."
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        return f"Error al conectar con el LLM: {e}"

# --- CONFIGURACIÓN DE FLASK ---
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # El HTML ha sido modificado para incluir el sidebar y el esquema de color oscuro.
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Asistente de Codificación (IDE-Style)</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <style>
            /* Variables de color para un tema VS Code Dark */
            :root {{
                --main-bg: #1e1e1e; /* Fondo principal (cercano al negro absoluto) */
                --sidebar-bg: #252526; /* Fondo del sidebar */
                --ide-bg: #1e1e1e; /* Fondo del editor */
                --text-color: #d4d4d4; /* Texto principal */
                --border-color: #3f3f46;
                --button-bg: #4f4f4f; /* Botón discreto */
                --button-hover: #5a5a5a;
                --accent-color: #61afef; /* Color de acento */
                --file-color: #cccccc;
                --folder-color: #808080;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--main-bg);
                margin: 0;
                color: var(--text-color);
                display: flex;
                min-height: 100vh;
                overflow: hidden; /* Oculta barras de desplazamiento innecesarias en el cuerpo */
            }}
            /* Diseño de dos paneles (Sidebar + Contenido Principal) */
            .main-layout {{
                display: flex;
                width: 100%;
                max-width: 1200px; /* Ancho máximo para mejor visualización */
                margin: 0 auto;
                border: 1px solid var(--border-color);
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }}
            /* --- Explorador de Proyectos (Sidebar) --- */
            .sidebar {{
                width: 250px;
                flex-shrink: 0;
                background-color: var(--sidebar-bg);
                border-right: 1px solid var(--border-color);
                padding-top: 20px;
                overflow-y: auto;
            }}
            .sidebar-header {{
                font-size: 16px;
                font-weight: 600;
                padding: 0 15px 10px;
                color: var(--file-color);
                border-bottom: 1px solid var(--border-color);
                margin-bottom: 10px;
            }}
            .file-tree {{
                padding: 5px 0;
                font-size: 14px;
            }}
            .tree-item {{
                padding: 4px 15px;
                cursor: pointer;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .tree-item:hover {{
                background-color: rgba(var(--accent-color), 0.1);
            }}
            .folder-name {{
                color: var(--folder-color);
                font-weight: 500;
            }}
            .file-name {{
                color: var(--file-color);
            }}
            .indent {{
                padding-left: 15px;
            }}
            .icon {{
                margin-right: 5px;
                color: var(--accent-color);
            }}
            /* --- Contenido Principal (Editor + Resultados) --- */
            .main-content {{
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                padding: 15px;
            }}
            h1 {{
                font-size: 24px;
                font-weight: 400;
                text-align: center;
                margin: 0 0 15px 0;
                color: var(--text-color);
            }}
            /* Estilos para el Editor (Área de código de entrada) */
            .editor-area {{
                display: flex;
                flex-direction: column;
                flex-grow: 1;
                min-height: 350px;
                position: relative;
                margin-bottom: 15px;
            }}
            textarea#code {{
                flex-grow: 1;
                width: 100%;
                padding: 15px;
                border: 1px solid var(--border-color);
                border-radius: 4px 4px 0 0;
                font-size: 16px;
                resize: none;
                background: var(--ide-bg);
                color: var(--text-color);
                /* Fuente de codificación */
                font-family: 'SF Mono', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
                box-sizing: border-box;
                line-height: 1.5;
                outline: none;
            }}
            /* Controles inferiores del editor */
            .editor-controls {{
                display: flex;
                justify-content: flex-end; /* Mover select a la derecha */
                align-items: center;
                padding: 8px 15px;
                background: var(--sidebar-bg);
                border: 1px solid var(--border-color);
                border-top: none;
                border-radius: 0 0 4px 4px;
            }}
            label[for="language"] {{
                font-size: 14px;
                margin-right: 10px;
            }}
            select#language {{
                width: auto;
                padding: 5px 10px;
                border: 1px solid var(--border-color);
                border-radius: 3px;
                font-size: 13px;
                background: var(--ide-bg);
                color: var(--text-color);
                margin-right: 15px;
                appearance: none;
                cursor: pointer;
            }}
            button[type="submit"], #refactor-button {{
                width: auto;
                padding: 8px 18px;
                background-color: var(--button-bg);
                color: var(--text-color);
                border: 1px solid var(--border-color);
                border-radius: 3px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: background-color 0.3s;
            }}
            button[type="submit"]:hover, #refactor-button:hover {{
                background-color: var(--button-hover);
            }}
            #refactor-button {{
                display: none;
                margin-left: 10px;
            }}
            /* Sección de Resultados */
            #result-section {{
                flex-shrink: 0;
                margin-top: 15px;
                background: var(--ide-bg);
                border-radius: 4px;
                border: 1px solid var(--border-color);
                min-height: 150px;
                padding: 15px;
            }}
            #result-title {{
                font-size: 16px;
                font-weight: 500;
                margin-bottom: 10px;
                color: var(--accent-color);
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 5px;
            }}
            /* Contenedor de Código Resaltado */
            #result-content {{
                padding: 5px 0;
                overflow-x: auto;
            }}
            /* Estilo para el código con resaltado de sintaxis */
            #result-content pre code {{
                display: block;
                padding: 0 !important;
                margin: 0;
                color: var(--text-color);
                line-height: 1.4;
                font-family: 'SF Mono', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
                font-size: 13px;
                background: var(--ide-bg) !important; /* Asegura que el fondo sea el mismo que el del editor */
            }}
            /* Estilo para el resultado en texto simple (e.g., errores o notas de cambios) */
            .simple-text {{
                font-size: 13px;
                white-space: pre-wrap;
                word-wrap: break-word;
                font-family: 'SF Mono', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
                color: var(--text-color);
                line-height: 1.4;
            }}
        </style>
    </head>
    <body>
        <div class="main-layout">
            <div class="sidebar">
                <div class="sidebar-header">EXPLORADOR</div>
                <div class="file-tree">
                    <div class="tree-item folder-name"><span class="icon">📁</span> Proyecto_Asistente</div>
                    <div class="indent">
                        <div class="tree-item folder-name"><span class="icon">📁</span> src</div>
                        <div class="indent">
                            <div class="tree-item file-name"><span class="icon">📄</span> app.py</div>
                            <div class="tree-item file-name"><span class="icon">📄</span> models.py</div>
                            <div class="tree-item file-name"><span class="icon">📄</span> utils.js</div>
                        </div>
                        <div class="tree-item folder-name"><span class="icon">📁</span> tests</div>
                        <div class="indent">
                            <div class="tree-item file-name"><span class="icon">📄</span> test_app.py</div>
                        </div>
                        <div class="tree-item file-name"><span class="icon">📄</span> requirements.txt</div>
                        <div class="tree-item file-name"><span class="icon">📄</span> README.md</div>
                    </div>
                </div>
            </div>
            <div class="main-content">
                <h1>Asistente de Codificación <span style="font-size: 0.7em;">(Con ayuda de Llama 3.1)</span></h1>
                <form id="code-form" class="editor-area">
                    <textarea name="code" id="code" placeholder="Pega el código que deseas revisar. Puedes copiarlo de la barra lateral si lo deseas..."></textarea>
                    <div class="editor-controls">
                        <label for="language">Lenguaje:</label>
                        <select name="language" id="language">
                            <option value="">-- Elige uno --</option>
                            {languages}
                        </select>
                        <button type="submit">Ejecutar Asistencia</button>
                        <button type="button" id="refactor-button">Refactorizar</button>
                    </div>
                </form>
                <div id="result-section">
                    <div id="result-title">Resultado:</div>
                    <div id="result-content" class="simple-text">Esperando procesamiento...</div>
                </div>
            </div>
        </div>
        <script>
            // Función auxiliar para crear la estructura de resaltado de sintaxis
            function createHighlightedContent(code, lang) {{
                // 1. Crear el elemento <pre>
                const pre = document.createElement('pre');
                // 2. Crear el elemento <code>
                const codeElement = document.createElement('code');
                codeElement.className = 'language-' + lang;
                // Dividir la respuesta en Código y Sección de Cambios
                const parts = code.split('---');
                let codePart = parts[0].trim();
                let changesPart = parts.length > 1 ? parts[1].trim() : '';
                // 3. Establecer el contenido de texto (necesario para highlight.js)
                codeElement.textContent = codePart;
                // 4. Aplicar el resaltado (usa la función de highlight.js)
                hljs.highlightElement(codeElement);
                // 5. Unir los elementos
                pre.appendChild(codeElement);
                let finalHTML = pre.outerHTML;
                // 6. Añadir la sección de cambios si existe
                if (changesPart) {{
                    // Usa <pre> para mantener el formato de las notas, pero con la clase simple-text
                    finalHTML += '<br><br><strong>Cambios/Notas:</strong><pre class="simple-text">' + changesPart + '</pre>';
                }}
                return finalHTML;
            }}
            const form = document.getElementById('code-form');
            const languageSelect = document.getElementById('language');
            const refactorButton = document.getElementById('refactor-button');
            const resultTitle = document.getElementById('result-title');
            const resultContent = document.getElementById('result-content');

            // Mostrar/Ocultar botón de refactorizar basado en el lenguaje seleccionado
            languageSelect.addEventListener('change', (e) => {{
                if (e.target.value === 'python') {{
                    refactorButton.style.display = 'inline-block';
                }} else {{
                    refactorButton.style.display = 'none';
                }}
            }});

            // Función para procesar (común para ambos botones)
            async function processCode(action) {{
                const code = document.getElementById('code').value.trim();
                const language = languageSelect.value;
                if (!code || !language) {{
                    resultTitle.textContent = 'Resultado:';
                    resultContent.innerHTML = 'Por favor, proporciona código válido y selecciona un lenguaje.';
                    resultContent.classList.add('simple-text');
                    return;
                }}
                resultTitle.textContent = `Resultado (Procesando...)`;
                resultContent.innerHTML = '<span class="simple-text">Procesando...</span>';
                resultContent.classList.add('simple-text');
                try {{
                    const response = await fetch('/process', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ code, language, action }})
                    }});
                    const data = await response.json();
                    resultTitle.textContent = `${{action === 'refactor' ? 'Código Refactorizado' : 'Código Corregido'}} (${{data.language}}):`;
                    if (data.result.startsWith('Error al conectar')) {{
                        resultContent.innerHTML = '<span style="color: #ff4444;">' + data.result + '</span>'; // Error en rojo vibrante
                        resultContent.classList.add('simple-text');
                    }} else {{
                        // Utilizar la función de resaltado
                        resultContent.innerHTML = createHighlightedContent(data.result, data.language_key);
                        resultContent.classList.remove('simple-text'); // Quitar la clase de texto simple
                    }}
                }} catch (error) {{
                    resultTitle.textContent = 'Resultado:';
                    resultContent.innerHTML = '<span style="color: #ff4444;">Error al procesar la solicitud.</span>';
                    resultContent.classList.add('simple-text');
                }}
            }}

            // Evento para el botón de submit (Asistencia regular)
            form.addEventListener('submit', async (e) => {{
                e.preventDefault();
                await processCode('assist');
            }});

            // Evento para el botón de refactorizar
            refactorButton.addEventListener('click', async () => {{
                await processCode('refactor');
            }});
        </script>
    </body>
    </html>
    """
    languages_html = ""
    for key, name in LANGUAGES.items():
        languages_html += f'<option value="{key}">{name}</option>\n'
    return html.format(languages=languages_html)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    code = data.get('code', '').strip()
    language_key = data.get('language', '')
    action = data.get('action', 'assist')
    language = LANGUAGES.get(language_key, '')
    if code and language:
        if action == 'refactor' and language_key != 'python':
            return jsonify({'result': 'Refactorización solo disponible para Python.', 'language': language, 'language_key': language_key})
        if action == 'refactor':
            prompt = f"Refactoriza el siguiente código en {language} para optimizarlo. El código va primero, y la sección de Cambios debe ser separada por una línea '---'.\n\n{code}"
            result = get_llm_response(prompt, is_refactor=True)
        else:
            prompt = f"Revisa el siguiente código en {language}. Corrige errores mínimos si es necesario (como typos en funciones estándar, e.g., 'prant' a 'print'). Si el código está perfecto, devuelvelo idéntico. Recuerda: el código va primero, y la sección de Cambios debe ser separada por una línea '---'.\n\n{code}"
            result = get_llm_response(prompt)
        return jsonify({
            'result': result,
            'language': language,
            'language_key': language_key
        })
    else:
        return jsonify({'result': 'Por favor, proporciona código válido y selecciona un lenguaje.', 'language': '', 'language_key': ''})

if __name__ == "__main__":
    print("Iniciando el servidor web en http://127.0.0.1:5000/")
    app.run(debug=True)
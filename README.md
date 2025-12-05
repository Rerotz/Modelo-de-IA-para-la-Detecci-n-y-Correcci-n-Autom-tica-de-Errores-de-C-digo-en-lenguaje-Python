

Powered by Llama 3.1 & Flask




Sobre el Proyecto

Arquitectura

Características

Instalación y Uso

Estructura del Proyecto

Equipo de Desarrollo

📖 Sobre el Proyecto

Este proyecto, desarrollado como parte del curso de Inteligencia Artificial en la Universidad Andina del Cusco, busca solucionar la frustración común de los desarrolladores: el tiempo perdido en errores de sintaxis y lógica simple.

Utilizando la potencia de los Large Language Models (LLM), específicamente Meta Llama 3.1-8B, nuestra aplicación ofrece un entorno tipo IDE web donde los usuarios pueden pegar su código y recibir correcciones instantáneas o sugerencias de optimización, manteniendo el estilo y la estructura original.

🏗 Arquitectura

El sistema sigue una arquitectura cliente-servidor desacoplada que permite la inferencia en hardware local o servidores remotos.

graph TD
    User[👤 Usuario Dev] -->|Input Código| Frontend[💻 Web Interface (HTML/JS)]
    Frontend -->|POST Request| Backend[🐍 Flask Server]
    Backend -->|Prompt Engineering| LLM_API[🤖 Llama 3.1 API (Local/Cloud)]
    LLM_API -->|Código Corregido| Backend
    Backend -->|JSON + Highlight| Frontend
    Frontend -->|Display| User


Stack Tecnológico

Frontend: HTML5, CSS3 (VS Code Dark Theme), Vanilla JS, Highlight.js.

Backend: Python, Flask.

IA Engine: Meta Llama 3.1-8B-Instruct (vía API local/remota).

Comunicación: REST API.

✨ Características

🎨 Interfaz IDE-Style: Diseño oscuro inspirado en VS Code para reducir la fatiga visual.

⚡ Corrección Inteligente: Detecta errores de sintaxis y lógica en múltiples lenguajes (Python, JS, Java, C++, etc.).

🔄 Refactorización (Python): Botón exclusivo para optimizar código Python, mejorando eficiencia y legibilidad sin alterar la funcionalidad.

📝 Explicación de Cambios: No solo arregla el código, sino que explica qué cambió y por qué en una sección de notas.

🌈 Syntax Highlighting: Resaltado de sintaxis automático para fácil lectura.

🚀 Instalación y Uso

Sigue estos pasos para desplegar el aplicativo en tu entorno local.

Prerrequisitos

Python 3.8 o superior.

Acceso a un servidor de inferencia Llama 3 (LM Studio, Ollama, o API Local).

Pasos

Clonar el repositorio

git clone [https://github.com/tu-usuario/ai-code-fixer.git](https://github.com/tu-usuario/ai-code-fixer.git)
cd ai-code-fixer


Instalar dependencias

pip install -r requirements.txt


Configurar el Modelo
Abre app.py y asegúrate de que la variable API_URL apunte a tu servidor de inferencia.

# En app.py
API_URL = "http://localhost:1234/v1/chat/completions" # Ejemplo con LM Studio


Ejecutar la aplicación

python app.py


Acceder
Abre tu navegador y ve a http://127.0.0.1:5000.





<div align="center">





<p>Universidad Andina del Cusco - 2025-II</p>
<img src="https://www.google.com/search?q=https://upload.wikimedia.org/wikipedia/commons/f/fa/Escudo_de_la_Universidad_Andina_del_Cusco.png" width="50" alt="Logo UAC">
</div>

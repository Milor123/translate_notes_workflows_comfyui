# Traductor de Notas para Workflows de ComfyUI

Este script de Python traduce las notas de texto dentro de tus archivos de workflow (`.json`) de ComfyUI, permitiéndote elegir entre una traducción rápida con Google Translate o una de mayor calidad y contexto con la API de OpenRouter.

## 🚀 Características

* **Identificación Automática**: Detecta automáticamente los nodos de tipo `Note` dentro del JSON de tu workflow.
* **Dos Modos de Traducción**:
    * **Google Translate**: Rápido y sencillo, no requiere API Key. Ideal para traducciones generales.
    * **OpenRouter AI**: Permite usar modelos de IA avanzados (GPT, Claude, Mistral, Gemini, etc.) para traducciones más precisas y conscientes del contexto. Requiere una API Key de OpenRouter.
* **Altamente Configurable**:
    * Gestiona tu API Key, URL, modelo de IA y otros parámetros a través de un archivo `config.ini`.
    * Define el idioma de origen y de destino.
    * Opción de **detección automática del idioma** (`AUTO`).
* **Contexto Específico para IA**: Al usar OpenRouter, se envía un _system prompt_ detallado a la IA para que entienda el contexto de ComfyUI, asegurando que los términos técnicos se traduzcan con precisión.
* **Seguro**: Nunca sobrescribe tu archivo original. Guarda el resultado en un nuevo archivo con un nombre descriptivo (ej., `workflow_traducido_ai_en_a_es.json`).
* **Manejo de Errores**: Si una nota no puede ser traducida, el script mantiene el texto original en lugar de fallar, asegurando la integridad del workflow.

## 📋 Requisitos

* Python 3.7 o superior.
* Librerías de Python: `deep_translator` y `openai`.

Puedes instalarlas fácilmente con pip:
```bash
pip install deep_translator openai
```

## 🔧 Configuración

Para usar la traducción con **OpenRouter AI**, es necesario configurar el archivo `config.ini`. Si el archivo no existe, se creará uno automáticamente con valores por defecto la primera vez que ejecutes el script.

**Pasos:**

1.  **Crea el archivo `config.ini`** en el mismo directorio que el script (o déja que el script lo cree por ti).
2.  **Edita el archivo** con tus datos:

```ini
[OpenRouter]
# Fundamental: Reemplaza esto con tu API Key de OpenRouter.
API_KEY = TU_OPENROUTER_API_KEY_AQUI

# Opcional: Modelo de IA a utilizar. Consulta la documentación de OpenRouter para más modelos.
MODEL_NAME = openai/gpt-4o

# Opcionales: Déjalos como están si no estás seguro.
BASE_URL = https://openrouter.ai/api/v1
HTTP_REFERER = https://tu-sitio.com
X_TITLE = Mi Traductor ComfyUI

[General]
# Idioma de origen (ej: en, es). Usa AUTO para detección automática.
SOURCE_LANGUAGE = en

# Idioma de destino (ej: es, fr, de).
TARGET_LANGUAGE = es
```

## ▶️ Uso

1.  Asegúrate de tener Python y las librerías instaladas.
2.  Configura tu archivo `config.ini` (especialmente la `API_KEY` si vas a usar OpenRouter).
3.  Ejecuta el script desde tu terminal:

    ```bash
    python tu_script.py
    ```
    *(Reemplaza `translate_comfyui_workflow.py` con el nombre real de tu archivo)*

4.  El script te guiará pidiéndote:
    * La ruta a tu archivo de workflow `.json`.
    * El método de traducción que deseas usar (Google Translate u OpenRouter AI).

Al finalizar, se generará un nuevo archivo JSON con las notas traducidas en el mismo directorio que el original.

## 🧠 ¿Cómo Funciona la Identificación de Notas?

El script analiza la estructura del archivo `.json` y busca específicamente los nodos cuyo `type` es `"Note"`. El texto a traducir se extrae del campo `widgets_values[0]` de dichos nodos. El resto de la estructura del workflow permanece intacta para garantizar que siga siendo funcional.

## 💡 Nota sobre la Calidad de Traducción

* **Google Translate**: Es una opción rápida y efectiva para entender el contenido general. Puede que no sea la mejor para matices técnicos muy específicos.
* **OpenRouter AI**: La calidad dependerá del modelo de IA que elijas. Modelos como GPT-4o o Claude 3 Opus suelen ofrecer traducciones superiores que comprenden mejor el contexto, aunque pueden ser más lentos o tener un coste asociado en OpenRouter.

## 👨‍💻 Desarrollo

Este script fue desarrollado con la asistencia de un modelo de lenguaje grande (LLM). La base del código y la lógica fueron generados y refinados a través de interacciones con Gemini 2.5 Pro Preview 05-06. El objetivo era crear una herramienta útil y flexible para la comunidad de ComfyUI.

## ❤️ Contribuciones

Si tienes ideas para mejorar el script, encuentras un error o quieres añadir nuevas funcionalidades, ¡no dudes en abrir un *issue* o un *pull request* en el repositorio!

import json
import os
import configparser
from openai import OpenAI # Para OpenRouter
from deep_translator import GoogleTranslator # Para Google Translate

# --- Configuración ---
CONFIG_FILE = 'config.ini'
DEFAULT_CONFIG_VALUES = {
    'OpenRouter': {
        'API_KEY': 'TU_OPENROUTER_API_KEY_AQUI',
        'BASE_URL': 'https://openrouter.ai/api/v1',
        'MODEL_NAME': 'mistralai/mistral-7b-instruct',
        'HTTP_REFERER': '',
        'X_TITLE': ''
    },
    'General': {
        'TARGET_LANGUAGE': 'es'
    }
}

def load_config():
    """Carga la configuración desde config.ini, creando el archivo si no existe."""
    config = configparser.ConfigParser()
    
    # Si config.ini no existe, créalo con valores por defecto
    if not os.path.exists(CONFIG_FILE):
        print(f"Advertencia: Archivo de configuración '{CONFIG_FILE}' no encontrado.")
        print("Creando uno con valores por defecto. Por favor, edítalo con tu API Key de OpenRouter y preferencias.")
        
        for section, defaults in DEFAULT_CONFIG_VALUES.items():
            config[section] = defaults
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        # Devuelve los valores por defecto para que el script pueda al menos intentar funcionar o guiar al usuario
        return DEFAULT_CONFIG_VALUES

    config.read(CONFIG_FILE, encoding='utf-8')
    
    # Asegurar que todas las secciones y claves esperadas existan, usando defaults si no
    loaded_config_values = {}
    config_changed = False # Bandera para saber si necesitamos reescribir el config
    
    for section, defaults in DEFAULT_CONFIG_VALUES.items():
        loaded_config_values[section] = {}
        if not config.has_section(section):
            config.add_section(section)
            config_changed = True
        for key, default_value in defaults.items():
            if config.has_option(section, key):
                loaded_config_values[section][key] = config.get(section, key)
            else:
                loaded_config_values[section][key] = default_value
                config.set(section, key, default_value) # Añade la clave faltante al objeto config
                config_changed = True
                
    # Reescribir el config.ini solo si se añadieron nuevas claves por defecto o secciones
    if config_changed:
        print(f"Actualizando '{CONFIG_FILE}' con claves/secciones por defecto faltantes.")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
            
    return loaded_config_values

# --- Funciones de Traducción ---

def translate_user_note_google(text_to_translate, target_language='es'):
    """Traduce un texto dado al idioma de destino utilizando GoogleTranslator."""
    if not text_to_translate or not isinstance(text_to_translate, str) or not text_to_translate.strip():
        return text_to_translate

    try:
        translated_text = GoogleTranslator(source='en', target=target_language).translate(text_to_translate)
        if translated_text is None:
            print(f"Advertencia: La traducción de Google devolvió None para el texto: '{text_to_translate[:100]}...'")
            return text_to_translate
        return translated_text
    except Exception as e:
        print(f"Error al traducir con Google: '{text_to_translate[:100]}...'. Error: {e}")
        return text_to_translate

def translate_user_note_openrouter(text_to_translate, app_config):
    """Traduce un texto dado utilizando la API de OpenRouter."""
    if not text_to_translate or not isinstance(text_to_translate, str) or not text_to_translate.strip():
        return text_to_translate

    api_key = app_config['OpenRouter']['API_KEY']
    base_url = app_config['OpenRouter']['BASE_URL']
    model = app_config['OpenRouter']['MODEL_NAME']
    http_referer = app_config['OpenRouter']['HTTP_REFERER']
    x_title = app_config['OpenRouter']['X_TITLE']
    target_language_code = app_config['General']['TARGET_LANGUAGE']

    # Mapeo simple de códigos de idioma a nombres completos para el prompt
    language_names = {
        'es': 'Español', 'en': 'Inglés', 'fr': 'Francés', 'de': 'Alemán',
        'ja': 'Japonés', 'pt': 'Portugués', 'it': 'Italiano', 'zh-cn': 'Chino Simplificado',
        # Añadir más según sea necesario
    }
    target_language_name = language_names.get(target_language_code.lower(), target_language_code.upper())

    if not api_key or api_key == 'TU_OPENROUTER_API_KEY_AQUI':
        print("\nError: La API Key de OpenRouter no está configurada en 'config.ini'.")
        print("Por favor, edita 'config.ini' con tu clave válida.")
        return text_to_translate # Devuelve original si no hay API key

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    extra_headers = {}
    if http_referer: extra_headers["HTTP-Referer"] = http_referer
    if x_title: extra_headers["X-Title"] = x_title

    system_prompt = f"""Eres un asistente de traducción experto.
Tu tarea es traducir notas de usuario del Inglés al {target_language_name}.
Estas notas provienen de un software de generación de imágenes mediante inteligencia artificial llamado ComfyUI.
Es crucial que traduzcas con la máxima precisión los términos técnicos relacionados con la inteligencia artificial, el machine learning, los modelos de difusión (diffusion models), samplers, checkpoints, LoRAs, VAEs, y la interfaz de usuario de ComfyUI.
Si encuentras un término técnico que tiene una traducción establecida y comúnmente aceptada en {target_language_name} dentro del contexto de la IA, utilízala (por ejemplo, "machine learning" como "aprendizaje automático").
Si un término es un nombre propio de una técnica, modelo, parámetro específico de ComfyUI (ej. "Euler a", "DPM++ 2M Karras", "CFG Scale"), o si traducirlo literalmente podría causar confusión o pérdida de significado técnico, es preferible conservarlo en Inglés.
Mantén el formato original del texto, incluyendo saltos de línea, listas, y cualquier formato Markdown simple (como `*cursiva*` o `**negrita**`).
No añadas comentarios, introducciones o conclusiones propias; solo devuelve el texto traducido.
Ejemplo de nota 1:
Original: "Tip: multistep samplers usually adhere to unsampled images more effectively than others."
Traducción a {target_language_name} (ej. Español): "Consejo: los samplers de múltiples pasos suelen adherirse a las imágenes no muestreadas (unsampled) de manera más efectiva que otros."

Ejemplo de nota 2:
Original: "This is a checkpoint that, for convenience, includes the stage B lite CSBW finetune, clip G, and stage A (the FT_HQ finetune)."
Traducción a {target_language_name} (ej. Español): "Este es un checkpoint que, por conveniencia, incluye el finetune CSBW lite de la etapa B, clip G, y la etapa A (el finetune FT_HQ)."

Traduce el siguiente texto del Inglés al {target_language_name} con estas directrices:
"""

    try:
        completion = client.chat.completions.create(
            extra_headers=extra_headers if extra_headers else None,
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_to_translate}
            ],
            temperature=0.2, # Enfocado en la precisión, baja creatividad
            max_tokens=len(text_to_translate.split()) * 3 + 100 # Estimación generosa para la traducción
        )
        translated_text = completion.choices[0].message.content.strip()
        
        # Pequeña validación: si la traducción es muy corta comparada con el original, puede ser un error.
        if len(translated_text) < len(text_to_translate) * 0.3 and len(text_to_translate) > 50:
            print(f"Advertencia: La traducción de OpenRouter parece demasiado corta. '{translated_text[:100]}...' vs '{text_to_translate[:100]}...'. Se mantendrá el original.")
            return text_to_translate
            
        return translated_text
    except Exception as e:
        print(f"Error al traducir con OpenRouter (modelo: {model}): '{text_to_translate[:100]}...'. Error: {e}")
        return text_to_translate


def process_comfyui_json(filepath, translator_choice, app_config):
    """
    Procesa un archivo JSON de ComfyUI, traduce las notas de usuario y guarda el resultado.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: El archivo '{filepath}' no fue encontrado.")
        return
    except json.JSONDecodeError:
        print(f"Error: El archivo '{filepath}' no es un JSON válido.")
        return
    except Exception as e:
        print(f"Error inesperado al abrir o leer el archivo: {e}")
        return

    if 'nodes' not in data or not isinstance(data['nodes'], list):
        print("Error: El JSON no parece tener una estructura de nodos de ComfyUI válida.")
        return

    nodes_processed_count = 0
    notes_translated_count = 0
    target_lang_from_config = app_config['General']['TARGET_LANGUAGE']

    for i, node in enumerate(data['nodes']):
        # Los nodos de nota en ComfyUI tienen el tipo "Note"
        # y el texto de la nota está en widgets_values[0]
        if node.get('type') == "Note":
            nodes_processed_count += 1
            if 'widgets_values' in node and \
               isinstance(node['widgets_values'], list) and \
               len(node['widgets_values']) > 0 and \
               isinstance(node['widgets_values'][0], str):

                original_note = node['widgets_values'][0]

                if not original_note.strip(): # Saltar notas vacías o solo con espacios
                    print(f"Nodo Note ID: {node.get('id', f'índice_{i}')} - Nota vacía. Saltando.")
                    continue

                print(f"\nProcesando nodo Note ID: {node.get('id', f'índice_{i}')} (Nota {nodes_processed_count} de tipo 'Note')")
                print(f"Texto original (primeros 100 caracteres): '{original_note[:100]}...'")

                translated_note = ""
                if translator_choice == '1': # Google
                    translated_note = translate_user_note_google(original_note, target_lang_from_config)
                elif translator_choice == '2': # OpenRouter
                    # Verificar si la API key es válida antes de cada llamada podría ser excesivo,
                    # la función translate_user_note_openrouter ya lo verifica al inicio.
                    translated_note = translate_user_note_openrouter(original_note, app_config)
                
                if translated_note and translated_note != original_note and translated_note.strip():
                    node['widgets_values'][0] = translated_note
                    print(f"Texto traducido (primeros 100 caracteres): '{translated_note[:100]}...'")
                    notes_translated_count += 1
                elif not translated_note or not translated_note.strip():
                     print("Advertencia: La traducción resultó en un texto vacío. Se mantuvo el original.")
                else:
                    print("Texto no traducido (la traducción falló, es idéntica o no se realizó y se mantuvo el original).")
            else:
                print(f"Advertencia: Nodo Note ID {node.get('id', f'índice_{i}')} no tiene 'widgets_values' con el formato esperado o la nota no es un string.")

    print(f"\n--- Resumen del Procesamiento ---")
    print(f"Total de nodos en el archivo: {len(data['nodes'])}")
    print(f"Nodos de tipo 'Note' encontrados y procesados: {nodes_processed_count}")
    print(f"Notas traducidas exitosamente: {notes_translated_count}")

    # Guardar el JSON modificado
    base, ext = os.path.splitext(filepath)
    suffix = "_traducido_google" if translator_choice == '1' else "_traducido_ai"
    output_filepath = f"{base}{suffix}{ext}"

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            # indent=2 para que sea legible, ensure_ascii=False para caracteres especiales
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Archivo traducido guardado como: {output_filepath}")
    except Exception as e:
        print(f"Error al guardar el archivo traducido: {e}")

if __name__ == "__main__":
    print("Traductor de notas para JSON de ComfyUI")
    print("=======================================")
    
    app_config = load_config()

    json_file_path = input("Introduce el nombre (o ruta) del archivo .json de ComfyUI: ")
    if not json_file_path.lower().endswith(".json"):
        print("Advertencia: El archivo no parece tener extensión .json. Intentando procesar de todas formas.")
    
    if not os.path.exists(json_file_path):
        print(f"Error: El archivo '{json_file_path}' no existe. Saliendo.")
        exit()

    print("\nElige el método de traducción:")
    print("1: Google Translate (rápido, sin API, calidad estándar)")
    print("2: OpenRouter AI (requiere API Key en config.ini, mayor calidad potencial)")

    translator_choice = ""
    while translator_choice not in ['1', '2']:
        translator_choice = input("Opción (1 o 2): ").strip()
        if translator_choice not in ['1', '2']:
            print("Opción no válida. Por favor, introduce 1 o 2.")

    if translator_choice == '2':
        api_key_or = app_config['OpenRouter']['API_KEY']
        if not api_key_or or api_key_or == 'TU_OPENROUTER_API_KEY_AQUI':
            print("\nADVERTENCIA: La API Key de OpenRouter no está configurada correctamente en 'config.ini'.")
            print("No se podrá usar OpenRouter AI.")
            fallback_choice = input("¿Deseas continuar usando Google Translate en su lugar (s/N)? ").strip().lower()
            if fallback_choice == 's':
                translator_choice = '1'
                print("Cambiando a Google Translate.")
            else:
                print("Traducción cancelada. Por favor, configura tu API Key en 'config.ini'.")
                exit()
        else:
             print(f"Usando OpenRouter AI con el modelo: {app_config['OpenRouter']['MODEL_NAME']}")
             print(f"Traduciendo al idioma: {app_config['General']['TARGET_LANGUAGE']}")

    elif translator_choice == '1':
        print("Usando Google Translate.")
        print(f"Traduciendo al idioma: {app_config['General']['TARGET_LANGUAGE']}")

    process_comfyui_json(json_file_path, translator_choice, app_config)
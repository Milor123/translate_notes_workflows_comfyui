import json
import os
import configparser
from openai import OpenAI # Para OpenRouter
from deep_translator import GoogleTranslator, MyMemoryTranslator # MyMemory para detección de idioma si es necesario

# --- Configuración ---
CONFIG_FILE = 'config.ini'
DEFAULT_CONFIG_VALUES = {
    'OpenRouter': {
        'API_KEY': 'TU_OPENROUTER_API_KEY_AQUI',
        'BASE_URL': 'https://openrouter.ai/api/v1',
        'MODEL_NAME': 'openai/gpt-4o', # Modelo por defecto si no se especifica
        'HTTP_REFERER': '',
        'X_TITLE': ''
    },
    'General': {
        'SOURCE_LANGUAGE': 'en', # Idioma origen por defecto
        'TARGET_LANGUAGE': 'es'  # Idioma destino por defecto
    }
}

# --- Mapeo de Idiomas ---
LANGUAGE_NAMES = {
    'auto': 'Detectar Automáticamente',
    'en': 'Inglés', 'es': 'Español', 'fr': 'Francés', 'de': 'Alemán',
    'ja': 'Japonés', 'pt': 'Portugués', 'it': 'Italiano', 'zh-cn': 'Chino Simplificado',
    # Añadir más según sea necesario
}

def load_config():
    """Carga la configuración desde config.ini, creando el archivo si no existe."""
    config = configparser.ConfigParser()
    
    if not os.path.exists(CONFIG_FILE):
        print(f"Advertencia: Archivo de configuración '{CONFIG_FILE}' no encontrado.")
        print("Creando uno con valores por defecto. Por favor, edítalo con tu API Key de OpenRouter y preferencias.")
        
        for section, defaults in DEFAULT_CONFIG_VALUES.items():
            config[section] = defaults
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        return DEFAULT_CONFIG_VALUES

    config.read(CONFIG_FILE, encoding='utf-8')
    
    loaded_config_values = {}
    config_changed = False 
    
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
                config.set(section, key, default_value) 
                config_changed = True
                
    if config_changed:
        print(f"Actualizando '{CONFIG_FILE}' con claves/secciones por defecto faltantes.")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
            
    return loaded_config_values

def get_language_name(code):
    return LANGUAGE_NAMES.get(code.lower(), code.upper())

# --- Funciones de Traducción ---

def detect_language_mymemory(text):
    """Detecta el idioma de un texto usando MyMemoryTranslator (gratuito)."""
    if not text or not text.strip():
        return None
    try:
        # Usamos un par de idiomas comunes para la detección, MyMemory necesita un target
        detected_lang_code = MyMemoryTranslator(source='auto', target='en').translate(text, return_detected_language=True)
        if detected_lang_code and len(detected_lang_code) == 2 and detected_lang_code.lower() in LANGUAGE_NAMES:
            print(f"Idioma detectado por MyMemory: {get_language_name(detected_lang_code)} ({detected_lang_code})")
            return detected_lang_code.lower()
        else:
            print(f"MyMemory no pudo detectar el idioma confiablemente para: '{text[:50]}...'. Detectado: {detected_lang_code}")
            return None
    except Exception as e:
        print(f"Error detectando idioma con MyMemory: {e}")
        return None

def translate_user_note_google(text_to_translate, source_language='en', target_language='es'):
    """Traduce un texto dado al idioma de destino utilizando GoogleTranslator."""
    if not text_to_translate or not isinstance(text_to_translate, str) or not text_to_translate.strip():
        return text_to_translate

    src_lang_google = source_language
    if source_language.lower() == 'auto':
        print("Google Translate intentará detectar el idioma de origen automáticamente.")
        src_lang_google = 'auto'
    
    try:
        translated_text = GoogleTranslator(source=src_lang_google, target=target_language).translate(text_to_translate)
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
    model_name_from_config = app_config['OpenRouter']['MODEL_NAME']
    http_referer = app_config['OpenRouter']['HTTP_REFERER']
    x_title = app_config['OpenRouter']['X_TITLE']
    
    source_language_code = app_config['General']['SOURCE_LANGUAGE'].lower()
    target_language_code = app_config['General']['TARGET_LANGUAGE'].lower()

    if not api_key or api_key == 'TU_OPENROUTER_API_KEY_AQUI':
        print("\nError: La API Key de OpenRouter no está configurada en 'config.ini'.")
        return text_to_translate

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    extra_headers = {}
    if http_referer: extra_headers["HTTP-Referer"] = http_referer
    if x_title: extra_headers["X-Title"] = x_title

    actual_source_language_code = source_language_code
    if source_language_code == 'auto':
        print("Intentando detectar idioma de origen para traducción AI...")
        detected_lang = detect_language_mymemory(text_to_translate)
        if detected_lang:
            actual_source_language_code = detected_lang
            print(f"Idioma de origen detectado como: {get_language_name(actual_source_language_code)}")
        else:
            print("No se pudo detectar el idioma de origen automáticamente, se asumirá Inglés para el prompt.")
            actual_source_language_code = 'en' 

    source_language_name = get_language_name(actual_source_language_code)
    target_language_name = get_language_name(target_language_code)

    # Evitar traducir si el origen detectado/especificado es igual al destino
    if actual_source_language_code == target_language_code:
        print(f"El idioma de origen ({source_language_name}) y destino ({target_language_name}) son el mismo. Saltando traducción.")
        return text_to_translate

    system_prompt = f"""Eres un asistente de traducción experto.
Tu tarea es traducir notas de usuario del {source_language_name} al {target_language_name}.
Si el idioma de origen es "Detectar Automáticamente", primero identifica el idioma del texto proporcionado y luego tradúcelo.
Estas notas provienen de un software de generación de imágenes mediante inteligencia artificial llamado ComfyUI.
Es crucial que traduzcas con la máxima precisión los términos técnicos relacionados con la inteligencia artificial, el machine learning, los modelos de difusión (diffusion models), samplers, checkpoints, LoRAs, VAEs, y la interfaz de usuario de ComfyUI.
Si encuentras un término técnico que tiene una traducción establecida y comúnmente aceptada en {target_language_name} dentro del contexto de la IA, utilízala (por ejemplo, "machine learning" como "aprendizaje automático" si traduces al Español).
Si un término es un nombre propio de una técnica, modelo, parámetro específico de ComfyUI (ej. "Euler a", "DPM++ 2M Karras", "CFG Scale"), o si traducirlo literalmente podría causar confusión o pérdida de significado técnico, es preferible conservarlo en el idioma original.
Mantén el formato original del texto, incluyendo saltos de línea, listas, y cualquier formato Markdown simple (como `*cursiva*` o `**negrita**`).
No añadas comentarios, introducciones o conclusiones propias; solo devuelve el texto traducido.

Traduce el siguiente texto del {source_language_name} (o detectado automáticamente si así se indica) al {target_language_name} con estas directrices:
"""

    try:
        completion = client.chat.completions.create(
            extra_headers=extra_headers if extra_headers else None,
            model=model_name_from_config,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_to_translate}
            ],
            temperature=0.2,
            max_tokens=len(text_to_translate.split()) * 3 + 150
        )
        translated_text = completion.choices[0].message.content.strip()
        
        if len(translated_text) < len(text_to_translate) * 0.3 and len(text_to_translate) > 50:
            print(f"Advertencia: La traducción de OpenRouter parece demasiado corta. '{translated_text[:100]}...' vs '{text_to_translate[:100]}...'. Se mantendrá el original.")
            return text_to_translate
            
        return translated_text
    except Exception as e:
        print(f"Error al traducir con OpenRouter (modelo: {model_name_from_config}): '{text_to_translate[:100]}...'. Error: {e}")
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
    source_lang_from_config = app_config['General']['SOURCE_LANGUAGE']
    target_lang_from_config = app_config['General']['TARGET_LANGUAGE']

    source_lang_from_config_lower = source_lang_from_config.lower()
    target_lang_from_config_lower = target_lang_from_config.lower()

    if source_lang_from_config_lower != 'auto' and source_lang_from_config_lower == target_lang_from_config_lower:
        print(f"El idioma de origen ({get_language_name(source_lang_from_config)}) y destino ({get_language_name(target_lang_from_config)}) son el mismo en la configuración.")
        print("No se realizará ninguna traducción. Si deseas traducir, ajusta los idiomas en 'config.ini'.")
        base, ext = os.path.splitext(filepath)
        output_filepath = f"{base}_procesado_sin_traduccion{ext}"
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Archivo copiado (sin traducción) a: {output_filepath}")
        except Exception as e:
            print(f"Error al guardar la copia del archivo: {e}")
        return

    for i, node in enumerate(data['nodes']):
        if node.get('type') == "Note":
            nodes_processed_count += 1
            if 'widgets_values' in node and \
               isinstance(node['widgets_values'], list) and \
               len(node['widgets_values']) > 0 and \
               isinstance(node['widgets_values'][0], str):

                original_note = node['widgets_values'][0]

                if not original_note.strip():
                    print(f"Nodo Note ID: {node.get('id', f'índice_{i}')} - Nota vacía. Saltando.")
                    continue

                print(f"\nProcesando nodo Note ID: {node.get('id', f'índice_{i}')} (Nota {nodes_processed_count} de tipo 'Note')")
                print(f"Texto original (primeros 100 caracteres): '{original_note[:100]}...'")

                translated_note = ""
                if translator_choice == '1': # Google
                    translated_note = translate_user_note_google(original_note, source_lang_from_config, target_lang_from_config)
                elif translator_choice == '2': # OpenRouter
                    translated_note = translate_user_note_openrouter(original_note, app_config)
                
                if translated_note and translated_note.strip() and translated_note != original_note :
                    node['widgets_values'][0] = translated_note
                    print(f"Texto traducido (primeros 100 caracteres): '{translated_note[:100]}...'")
                    notes_translated_count += 1
                elif not translated_note or not translated_note.strip():
                     print("Advertencia: La traducción resultó en un texto vacío. Se mantuvo el original.")
                elif translated_note == original_note:
                    print("La traducción es idéntica al original, no se tradujo o el idioma de origen y destino son iguales para esta nota. Se mantuvo el original.")
                else:
                    print("Texto no traducido (la traducción falló o no se realizó y se mantuvo el original).")
            else:
                print(f"Advertencia: Nodo Note ID {node.get('id', f'índice_{i}')} no tiene 'widgets_values' con el formato esperado o la nota no es un string.")

    print(f"\n--- Resumen del Procesamiento ---")
    print(f"Total de nodos en el archivo: {len(data['nodes'])}")
    print(f"Nodos de tipo 'Note' encontrados y procesados: {nodes_processed_count}")
    print(f"Notas traducidas exitosamente: {notes_translated_count}")

    base, ext = os.path.splitext(filepath)
    suffix_translator = "_google" if translator_choice == '1' else "_ai"
    # Para el sufijo de idioma, si el origen es AUTO, podríamos no incluirlo o poner 'auto'
    src_display_suffix = source_lang_from_config.lower() if source_lang_from_config.lower() != 'auto' else 'auto'
    suffix_lang = f"_{src_display_suffix}_a_{target_lang_from_config.lower()}"
    output_filepath = f"{base}_traducido{suffix_translator}{suffix_lang}{ext}"

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Archivo traducido guardado como: {output_filepath}")
    except Exception as e:
        print(f"Error al guardar el archivo traducido: {e}")

if __name__ == "__main__":
    print("Traductor de notas para JSON de ComfyUI v2.1") # Pequeña actualización de versión
    print("===========================================")
    
    app_config = load_config()

    json_file_path = input("Introduce el nombre (o ruta) del archivo .json de ComfyUI: ")
    if not json_file_path.lower().endswith(".json"):
        print("Advertencia: El archivo no parece tener extensión .json. Intentando procesar de todas formas.")
    
    if not os.path.exists(json_file_path):
        print(f"Error: El archivo '{json_file_path}' no existe. Saliendo.")
        exit()

    print("\nConfiguración de Idiomas actual (desde config.ini):")
    src_lang_cfg = app_config['General']['SOURCE_LANGUAGE']
    tgt_lang_cfg = app_config['General']['TARGET_LANGUAGE']
    print(f"Idioma de Origen: {get_language_name(src_lang_cfg)} ({src_lang_cfg})")
    print(f"Idioma de Destino: {get_language_name(tgt_lang_cfg)} ({tgt_lang_cfg})")

    print("\nElige el método de traducción:")
    print("1: Google Translate (rápido, sin API Key, calidad estándar)")
    print("2: OpenRouter AI (requiere API Key en config.ini, mayor calidad potencial)")

    translator_choice = ""
    while translator_choice not in ['1', '2']:
        translator_choice = input("Opción (1 o 2): ").strip()
        if translator_choice not in ['1', '2']:
            print("Opción no válida. Por favor, introduce 1 o 2.")

    if translator_choice == '2':
        api_key_or = app_config['OpenRouter']['API_KEY']
        model_or = app_config['OpenRouter']['MODEL_NAME']
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
             print(f"Usando OpenRouter AI con el modelo: {model_or}")
             if src_lang_cfg.lower() == 'auto':
                 print(f"Intentando detectar idioma de origen automáticamente y traduciendo a: {get_language_name(tgt_lang_cfg)}")
             else:
                 print(f"Traduciendo de {get_language_name(src_lang_cfg)} a {get_language_name(tgt_lang_cfg)}")
    elif translator_choice == '1':
        print("Usando Google Translate.")
        if src_lang_cfg.lower() == 'auto':
            print(f"Intentando detectar idioma de origen automáticamente y traduciendo a: {get_language_name(tgt_lang_cfg)}")
        else:
            print(f"Traduciendo de {get_language_name(src_lang_cfg)} a {get_language_name(tgt_lang_cfg)}")
            
    process_comfyui_json(json_file_path, translator_choice, app_config)

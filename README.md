# ComfyUI Workflow Note Translator

This Python script translates the text notes within your ComfyUI workflow files (`.json`), allowing you to choose between a quick translation via Google Translate or a higher-quality, context-aware translation using the OpenRouter API.

## 🚀 Features

* **Automatic Detection**: Automatically identifies nodes of type `Note` within your workflow's JSON file.
* **Two Translation Modes**:
    * **Google Translate**: Fast and simple, no API key required. Ideal for general-purpose translations.
    * **OpenRouter AI**: Allows you to use advanced AI models (GPT, Claude, Mistral, Gemini, etc.) for more accurate and context-aware translations. Requires an OpenRouter API Key.
* **Highly Configurable**:
    * Manage your API Key, base URL, preferred AI model, and other settings via a `config.ini` file.
    * Define the source and target languages for translation.
    * Option for **automatic language detection** (`AUTO`).
* **AI-Specific Context**: When using OpenRouter, a detailed system prompt is sent to the AI to provide it with the context of ComfyUI, ensuring technical terms are translated accurately.
* **Safe**: It never overwrites your original file. The result is saved to a new, descriptively named file (e.g., `workflow_translated_ai_en_to_es.json`).
* **Error Handling**: If a note fails to translate, the script keeps the original text instead of crashing, ensuring the integrity of your workflow.

## 📋 Requirements

* Python 3.7 or higher.
* The following Python libraries: `deep_translator` and `openai`.

You can easily install them using pip:
```bash
pip install deep_translator openai
```

## 🔧 Configuration

To use the **OpenRouter AI** translation, you must configure the `config.ini` file. If this file doesn't exist, one will be created automatically with default values the first time you run the script.

**Steps:**

1.  **Create the `config.ini` file** in the same directory as the script (or let the script create it for you).
2.  **Edit the file** with your information:

```ini
[OpenRouter]
# Required: Replace this with your API Key from OpenRouter.
API_KEY = YOUR_OPENROUTER_API_KEY_HERE

# Optional: The AI model to use. Check the OpenRouter documentation for more models.
MODEL_NAME = openai/gpt-4o

# Optional: You can leave these as they are if you're unsure.
BASE_URL = https://openrouter.ai/api/v1
HTTP_REFERER = https://your-site.com
X_TITLE = My ComfyUI Translator

[General]
# Source language (e.g., en, es). Use AUTO for automatic detection.
SOURCE_LANGUAGE = en

# Target language (e.g., es, fr, de).
TARGET_LANGUAGE = es
```

## ▶️ Usage

1.  Make sure you have Python and the required libraries installed.
2.  Set up your `config.ini` file (especially the `API_KEY` if using OpenRouter).
3.  Run the script from your terminal:

    ```bash
    python your_script.py
    ```
    *(Replace `translate_comfyui_workflow.py` with the actual name of your file)*

4.  The script will guide you by asking for:
    * The path to your `.json` workflow file.
    * The translation method you wish to use (Google Translate or OpenRouter AI).

When finished, a new JSON file with the translated notes will be generated in the same directory as the original.

## 🧠 How Note Detection Works

The script parses the `.json` file structure and specifically looks for nodes where the `type` is `"Note"`. The text to be translated is extracted from the `widgets_values[0]` field of these nodes. The rest of the workflow structure remains untouched to ensure it stays fully functional.

## 💡 A Note on Translation Quality

* **Google Translate**: A quick and effective option for understanding the general content. It may not be ideal for highly specific technical nuances.
* **OpenRouter AI**: The quality will depend on the AI model you choose. Models like GPT-4o or Claude 3 Opus typically offer superior translations that better grasp the context, although they may be slower or have an associated cost on OpenRouter.

## 👨‍💻 Development

This script was developed with the assistance of a large language model (LLM). The core code and logic were generated and refined through interactions with Claude 3 Opus. The goal was to create a useful and flexible tool for the ComfyUI community.

## ❤️ Contributions

If you have ideas to improve the script, find a bug, or want to add new features, feel free to open an issue or a pull request in the repository!

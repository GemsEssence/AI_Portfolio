from googletrans import Translator

translator = Translator()

def translate_text(text: str, target_lang: str = "en") -> str:
    """Translate given text into target language (default English)."""
    try:
        if not text or target_lang == "en":
            return text
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        print("Translation error:", e)
        return text

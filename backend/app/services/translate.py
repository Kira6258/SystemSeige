import logging

from langdetect import LangDetectException, detect

logger = logging.getLogger("clearfinance")


def detect_language(text: str, fallback: str = "en") -> str:
    if not text or not text.strip():
        return fallback
        
    # Heuristic for short English phrases that langdetect often misclassifies
    cleaned = text.lower().strip()
    common_english_words = {
        "hello", "hi", "hey", "how", "what", "where", "why", "who", "when", "is", "are", "am", 
        "you", "i", "my", "car", "debt", "loan", "bank", "buy", "save", "income", "expense",
        "budget", "tax", "insurance", "investment", "return", "stocks", "goal", "goals", "money"
    }
    words = set(cleaned.split())
    if words.intersection(common_english_words) and cleaned.isascii():
        return "en"
        
    try:
        return detect(text)
    except LangDetectException:
        return fallback


def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == "en" or not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator

        return GoogleTranslator(source="auto", target="en").translate(text)
    except Exception:
        logger.exception("[ERROR] translation to English failed, using original text")
        return text


def translate_from_english(text: str, target_lang: str) -> str:
    if target_lang == "en" or not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator

        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except Exception:
        logger.exception("[ERROR] translation from English failed, using original text")
        return text

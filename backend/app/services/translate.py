import logging

from langdetect import LangDetectException, detect

logger = logging.getLogger("clearfinance")


def detect_language(text: str, fallback: str = "en") -> str:
    if not text or not text.strip():
        return fallback
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

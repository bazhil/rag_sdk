"""
Модуль для автоматического определения языка текста и адаптивного кросс-языкового поиска.
"""

from typing import Optional, Union, List
import re


class LanguageDetector:
    """Детектор языка с поддержкой автоматического перевода для улучшения поиска."""
    
    def __init__(self):
        self._langdetect = None
        self._translator = None
        print("[LANG_DETECTOR] LanguageDetector initialized")
        
    def _load_langdetect(self):
        """Ленивая загрузка библиотеки определения языка."""
        if self._langdetect is None:
            try:
                from langdetect import detect, DetectorFactory
                # Делаем результаты детекции детерминированными
                DetectorFactory.seed = 0
                self._langdetect = detect
                print("[LANG_DETECTOR] langdetect library loaded")
            except ImportError:
                print("[LANG_DETECTOR] WARNING: langdetect not installed")
                print("[LANG_DETECTOR] Install with: pip install langdetect")
                self._langdetect = False
        return self._langdetect if self._langdetect else None
    
    def _load_translator(self):
        """Ленивая загрузка переводчика."""
        if self._translator is None:
            try:
                from deep_translator import GoogleTranslator
                self._translator = GoogleTranslator
                print("[LANG_DETECTOR] Translator loaded (deep-translator)")
            except ImportError:
                print("[LANG_DETECTOR] WARNING: deep-translator not installed")
                print("[LANG_DETECTOR] Install with: pip install deep-translator")
                self._translator = False
        return self._translator if self._translator else None
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Определяет язык текста.
        
        Args:
            text: текст для анализа
            
        Returns:
            Код языка (ISO 639-1) или None если не удалось определить
        """
        if not text or len(text.strip()) < 10:
            return None
        
        detect_func = self._load_langdetect()
        if not detect_func:
            return None
        
        try:
            # Используем первые 1000 символов для определения языка
            sample = text[:1000].strip()
            lang = detect_func(sample)
            print(f"[LANG_DETECTOR] Detected language: {lang}")
            return lang
        except Exception as e:
            print(f"[LANG_DETECTOR] Language detection error: {e}")
            return None
    
    def detect_document_language(self, chunks: List[str], sample_size: int = 5) -> Optional[str]:
        """
        Определяет язык документа на основе нескольких его фрагментов.
        
        Args:
            chunks: список фрагментов документа
            sample_size: количество фрагментов для анализа
            
        Returns:
            Наиболее вероятный код языка или None
        """
        if not chunks:
            return None
        
        # Берем несколько фрагментов из разных частей документа
        sample_chunks = []
        step = max(1, len(chunks) // sample_size)
        for i in range(0, min(len(chunks), sample_size * step), step):
            if i < len(chunks):
                sample_chunks.append(chunks[i])
        
        # Определяем язык для каждого фрагмента
        languages = []
        for chunk in sample_chunks:
            lang = self.detect_language(chunk)
            if lang:
                languages.append(lang)
        
        if not languages:
            return None
        
        # Находим наиболее частый язык
        lang_counts = {}
        for lang in languages:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        most_common_lang = max(lang_counts, key=lang_counts.get)
        confidence = lang_counts[most_common_lang] / len(languages)
        
        print(f"[LANG_DETECTOR] Document language: {most_common_lang} (confidence: {confidence:.1%})")
        return most_common_lang
    
    def translate_text(self, text: str, target_lang: str) -> Optional[str]:
        """
        Переводит текст на целевой язык.
        
        Args:
            text: исходный текст
            target_lang: целевой язык (ISO 639-1)
            
        Returns:
            Переведенный текст или None при ошибке
        """
        translator_class = self._load_translator()
        if not translator_class:
            return None
        
        try:
            # Определяем исходный язык
            source_lang = self.detect_language(text)
            
            # Если уже на целевом языке, не переводим
            if source_lang == target_lang:
                print(f"[LANG_DETECTOR] Text already in target language ({target_lang})")
                return text
            
            # Переводим с использованием deep-translator
            translator = translator_class(source=source_lang, target=target_lang)
            translation = translator.translate(text)
            
            print(f"[LANG_DETECTOR] Translated from {source_lang} to {target_lang}")
            print(f"[LANG_DETECTOR]   Original: {text[:100]}...")
            print(f"[LANG_DETECTOR]   Translated: {translation[:100]}...")
            return translation
            
        except Exception as e:
            print(f"[LANG_DETECTOR] Translation error: {e}")
            return None
    
    def should_translate_query(self, query_lang: Optional[str], document_lang: Optional[str]) -> bool:
        """
        Определяет, нужно ли переводить запрос для улучшения поиска.
        
        Args:
            query_lang: язык запроса
            document_lang: язык документа
            
        Returns:
            True если перевод может улучшить качество поиска
        """
        # Если языки не определены, не переводим
        if not query_lang or not document_lang:
            return False
        
        # Если языки одинаковые, перевод не нужен
        if query_lang == document_lang:
            return False
        
        # Перевод рекомендуется для разных языков
        print(f"[LANG_DETECTOR] Cross-lingual query detected: {query_lang} -> {document_lang}")
        return True
    
    def create_multilingual_query(self, query: str, target_langs: List[str]) -> List[str]:
        """
        Создает мультиязычные варианты запроса для параллельного поиска.
        
        Args:
            query: исходный запрос
            target_langs: список целевых языков
            
        Returns:
            Список вариантов запроса на разных языках
        """
        translator_class = self._load_translator()
        if not translator_class:
            return [query]
        
        queries = [query]  # Всегда включаем оригинальный запрос
        query_lang = self.detect_language(query)
        
        for target_lang in target_langs:
            if target_lang == query_lang:
                continue
            
            translated = self.translate_text(query, target_lang)
            if translated and translated != query:
                queries.append(translated)
        
        print(f"[LANG_DETECTOR] Generated {len(queries)} query variants")
        return queries


# Глобальный экземпляр детектора
_detector_instance = None


def get_language_detector() -> LanguageDetector:
    """Получить глобальный экземпляр детектора языка."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = LanguageDetector()
    return _detector_instance


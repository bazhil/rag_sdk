"""
Модуль для веб-поиска с использованием DuckDuckGo.
Основан на статье: https://huggingface.co/learn/cookbook/multiagent_rag_system
"""

import sys
import os
from typing import List, Dict, Any, Optional
import asyncio
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'llm_manager'))

from .config import settings

# Global LLM instance
_llm_instance = None


def _get_llm():
    """Получает или создает экземпляр LLM."""
    global _llm_instance
    if _llm_instance is None:
        from llm_manager.llm_factory import create_llm
        _llm_instance = create_llm()
    return _llm_instance


class WebSearchManager:
    """
    Менеджер для веб-поиска с использованием DuckDuckGo.
    Выполняет поиск, извлекает контент веб-страниц и генерирует суммаризацию.
    """
    
    def __init__(self):
        print("[WEB_SEARCH] Initializing WebSearchManager...")
        self.results_count = settings.web_search_results_count
        self.max_retries = settings.web_search_max_retries
        print(f"[WEB_SEARCH] Results count: {self.results_count}")
        print(f"[WEB_SEARCH] Max retries: {self.max_retries}")
    
    def _search_duckduckgo_html(self, query: str) -> List[Dict[str, Any]]:
        """
        Выполняет поиск в DuckDuckGo через HTML (fallback метод).
        
        Args:
            query: поисковый запрос
            
        Returns:
            Список результатов поиска
        """
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse
        import time
        import random
        
        try:
            print(f"[WEB_SEARCH] HTML search for: '{query}'")
            
            # Создаем сессию для сохранения cookies
            session = requests.Session()
            
            # Список различных User-Agent для ротации
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            
            results = []
            
            for attempt in range(self.max_retries):
                try:
                    # Задержка перед попыткой (увеличивающаяся)
                    if attempt > 0:
                        delay = (attempt * 3) + random.uniform(1, 3)
                        print(f"[WEB_SEARCH] Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                    
                    # Имитируем браузер с ротацией User-Agent
                    headers = {
                        'User-Agent': random.choice(user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Cache-Control': 'max-age=0'
                    }
                    
                    # Сначала заходим на главную страницу для получения cookies
                    if attempt == 0:
                        print(f"[WEB_SEARCH] Getting cookies from main page...")
                        session.get('https://duckduckgo.com/', headers=headers, timeout=10)
                        time.sleep(random.uniform(1, 2))
                    
                    # Кодируем запрос для URL
                    encoded_query = urllib.parse.quote_plus(query)
                    
                    # Используем обычный поиск, а не html версию
                    url = f"https://duckduckgo.com/html/?q={encoded_query}&kl=us-en"
                    
                    print(f"[WEB_SEARCH] Attempt {attempt + 1}/{self.max_retries}: Requesting {url}")
                    
                    response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
                    
                    print(f"[WEB_SEARCH] Response status: {response.status_code}, content length: {len(response.content)}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Проверяем различные варианты структуры результатов
                        # Вариант 1: result__body (новый формат)
                        search_results = soup.find_all('div', class_='result__body')
                        if not search_results:
                            # Вариант 2: результаты в links_main
                            search_results = soup.find_all('div', class_='links_main')
                        if not search_results:
                            # Вариант 3: web-result
                            search_results = soup.find_all('div', class_='web-result')
                        
                        print(f"[WEB_SEARCH] Found {len(search_results)} result containers")
                        
                        for result in search_results[:self.results_count]:
                            try:
                                # Извлекаем заголовок и ссылку
                                title_elem = result.find('a', class_='result__a')
                                if not title_elem:
                                    title_elem = result.find('a', class_='result-link')
                                if not title_elem:
                                    title_elem = result.find('a')
                                
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                url_link = title_elem.get('href', '')
                                
                                # Извлекаем описание
                                snippet_elem = result.find('a', class_='result__snippet')
                                if not snippet_elem:
                                    snippet_elem = result.find('div', class_='result__snippet')
                                if not snippet_elem:
                                    snippet_elem = result.find('div', class_='snippet')
                                
                                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                                
                                if title and url_link:
                                    results.append({
                                        'title': title,
                                        'url': url_link,
                                        'snippet': snippet
                                    })
                                    print(f"[WEB_SEARCH] Added result: {title[:50]}...")
                                    
                            except Exception as parse_error:
                                print(f"[WEB_SEARCH] Error parsing result: {parse_error}")
                                continue
                        
                        if results:
                            print(f"[WEB_SEARCH] HTML search found {len(results)} results")
                            return results
                        else:
                            print(f"[WEB_SEARCH] No results parsed from HTML, trying next attempt...")
                    else:
                        print(f"[WEB_SEARCH] Bad status code: {response.status_code}")
                    
                except Exception as e:
                    print(f"[WEB_SEARCH] HTML search attempt {attempt + 1} failed: {e}")
            
            return results
            
        except Exception as e:
            print(f"[WEB_SEARCH] HTML search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """
        Выполняет поиск в DuckDuckGo с fallback на HTML метод.
        
        Args:
            query: поисковый запрос
            
        Returns:
            Список результатов поиска
        """
        try:
            from duckduckgo_search import DDGS
            import time
            
            print(f"[WEB_SEARCH] Searching DuckDuckGo for: '{query}'")
            
            results = []
            
            # Пробуем API метод
            for attempt in range(2):  # Только 2 попытки для API
                try:
                    ddgs = DDGS(timeout=15)
                    search_results = list(ddgs.text(
                        keywords=query,
                        max_results=self.results_count
                    ))
                    
                    for result in search_results:
                        results.append({
                            'title': result.get('title', ''),
                            'url': result.get('href', ''),
                            'snippet': result.get('body', ''),
                        })
                    
                    if results:
                        print(f"[WEB_SEARCH] API method: found {len(results)} results")
                        return results
                        
                except Exception as search_error:
                    print(f"[WEB_SEARCH] API attempt {attempt + 1}/2 failed: {search_error}")
                    if attempt < 1:
                        time.sleep(3)
                    continue
            
            # Если API не сработал, пробуем HTML метод
            print(f"[WEB_SEARCH] API method failed, trying HTML fallback...")
            results = self._search_duckduckgo_html(query)
            
            if not results:
                print(f"[WEB_SEARCH] All methods failed, no results found")
            
            return results
            
        except Exception as e:
            print(f"[WEB_SEARCH] Error during DuckDuckGo search: {e}")
            import traceback
            traceback.print_exc()
            
            # Последняя попытка через HTML
            try:
                return self._search_duckduckgo_html(query)
            except:
                return []
    
    def _fetch_webpage_content(self, url: str, max_length: int = 5000) -> Optional[str]:
        """
        Извлекает содержимое веб-страницы.
        
        Args:
            url: URL веб-страницы
            max_length: максимальная длина извлекаемого текста
            
        Returns:
            Текстовое содержимое страницы или None при ошибке
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            print(f"[WEB_SEARCH] Fetching content from: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Удаляем скрипты и стили
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Извлекаем текст
            text = soup.get_text(separator=' ', strip=True)
            
            # Ограничиваем длину
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            print(f"[WEB_SEARCH] Extracted {len(text)} characters")
            return text
            
        except Exception as e:
            print(f"[WEB_SEARCH] Error fetching webpage {url}: {e}")
            return None
    
    async def search_and_summarize(
        self,
        query: str,
        fetch_content: bool = True
    ) -> Dict[str, Any]:
        """
        Выполняет поиск и создает суммаризацию результатов.
        
        Args:
            query: поисковый запрос
            fetch_content: нужно ли извлекать содержимое веб-страниц
            
        Returns:
            Словарь с результатами поиска и суммаризацией
        """
        print(f"\n[WEB_SEARCH] ========== WEB SEARCH REQUEST ==========")
        print(f"[WEB_SEARCH] Query: {query}")
        print(f"[WEB_SEARCH] Fetch content: {fetch_content}")
        
        # Выполняем поиск
        search_results = self._search_duckduckgo(query)
        
        if not search_results:
            return {
                'query': query,
                'results': [],
                'summary': '''К сожалению, не удалось найти результаты по вашему запросу.

**Возможные причины:**
- DuckDuckGo временно ограничил автоматические запросы (rate limiting)
- Проблемы с сетевым подключением
- Запрос был заблокирован антиботом

**Что можно сделать:**
1. Попробуйте повторить запрос через несколько минут
2. Используйте более простые или общие запросы
3. Проверьте логи приложения для подробностей

💡 **Совет:** Переключитесь на режим RAG для работы с загруженными документами.''',
                'sources_count': 0
            }
        
        # Если нужно, извлекаем содержимое страниц
        enriched_results = []
        for result in search_results:
            enriched_result = result.copy()
            
            if fetch_content and result.get('url'):
                content = self._fetch_webpage_content(result['url'])
                if content:
                    enriched_result['content'] = content
            
            enriched_results.append(enriched_result)
        
        # Генерируем суммаризацию с помощью LLM
        summary = await self._generate_summary(query, enriched_results)
        
        print(f"[WEB_SEARCH] Summary generated: {len(summary)} chars")
        print(f"[WEB_SEARCH] ========================================\n")
        
        return {
            'query': query,
            'results': search_results,  # Возвращаем базовые результаты без content
            'summary': summary,
            'sources_count': len(search_results)
        }
    
    async def _generate_summary(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Генерирует суммаризацию результатов поиска с помощью LLM.
        
        Args:
            query: исходный поисковый запрос
            results: список результатов поиска с содержимым
            
        Returns:
            Суммаризированный ответ
        """
        print("[WEB_SEARCH] Generating summary with LLM...")
        
        # Формируем контекст из результатов поиска
        context_parts = []
        for i, result in enumerate(results, 1):
            part = f"**Источник {i}: {result['title']}**\n"
            part += f"URL: {result['url']}\n"
            part += f"Описание: {result['snippet']}\n"
            
            if 'content' in result and result['content']:
                # Ограничиваем длину контента
                content = result['content'][:2000]
                part += f"Содержимое: {content}\n"
            
            context_parts.append(part)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Создаем промпт для LLM
        prompt = f"""На основе результатов веб-поиска предоставь подробный и структурированный ответ на вопрос пользователя.

ВОПРОС ПОЛЬЗОВАТЕЛЯ:
{query}

РЕЗУЛЬТАТЫ ПОИСКА:
{context}

ТРЕБОВАНИЯ К ОТВЕТУ:
1. Дай развернутый, информативный ответ на вопрос пользователя
2. Используй информацию из всех релевантных источников
3. Структурируй ответ с заголовками и списками
4. В конце добавь раздел "Источники" со ссылками на использованные материалы
5. Указывай номера источников в тексте в формате [1], [2] и т.д.
6. Пиши на том же языке, что и вопрос пользователя

ФОРМАТ ОТВЕТА:
[Твой подробный ответ с ссылками на источники]

## Источники:
1. [Название источника 1] - URL
2. [Название источника 2] - URL
...

ОТВЕТ:"""
        
        # Получаем ответ от LLM
        llm = _get_llm()
        summary = await llm.get_response("", prompt)
        
        return summary


# Глобальный экземпляр менеджера
_web_search_manager = None


def get_web_search_manager() -> WebSearchManager:
    """Возвращает синглтон экземпляр WebSearchManager."""
    global _web_search_manager
    if _web_search_manager is None:
        _web_search_manager = WebSearchManager()
    return _web_search_manager


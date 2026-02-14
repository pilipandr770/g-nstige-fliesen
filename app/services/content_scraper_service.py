"""
Сервис для автоматического извлечения контента с сайтов производителей плитки.
Парсит коллекции, проекты и новости для автоматического наполнения сайта.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from urllib.parse import urljoin, urlparse
from werkzeug.utils import secure_filename
import hashlib

# Импортируем индивидуальные парсеры
from app.services.manufacturer_parsers import ManufacturerParserFactory


class ContentScraperService:
    """
    Сервис для извлечения контента с сайтов производителей керамической плитки.
    Поддерживает различные структуры сайтов и типы контента.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Конфигурация для разных производителей
        self.manufacturer_configs = {
            'aparici': {
                'base_url': 'https://www.aparici.com/de',
                'collections_path': '/kollektionen',
                'projects_path': '/projekte',
                'blog_path': '/blog'
            },
            'ape': {
                'base_url': 'https://www.apegrupo.com/de',
                'collections_path': '/produkte',
                'projects_path': '/projekte'
            },
            'lafabbrica': {
                'base_url': 'https://www.lafabbrica.it/de',
                'collections_path': '/collections',
                'projects_path': '/projects'
            },
            'dune': {
                'base_url': 'https://duneceramics.com/de',
                'collections_path': '/serien',
                'projects_path': '/projekte',
                'blog_path': '/blog'
            },
            'equipe': {
                'base_url': 'https://www.equipeceramicas.com/de',
                'collections_path': '/kollektionen',
                'projects_path': '/projekte',
                'news_path': '/news'
            },
            'casalgrande': {
                'base_url': 'https://www.casalgrandepadana.de',
                'collections_path': '/produkte',
                'projects_path': '/realisierte-projekte',
                'magazine_path': '/magazine'
            },
            'baldocer': {
                'base_url': 'https://baldocer.com',
                'collections_path': '/producto/novedad',
                'projects_path': '/proyectos'
            },
            'distrimat': {
                'base_url': 'https://www.distrimat.es/en',
                'collections_path': '/collections',
                'projects_path': '/projects'
            },
            'estudi-ceramico': {
                'base_url': 'https://eceramico.com/en',
                'collections_path': '/collections',
                'projects_path': '/projects'
            },
            'etile': {
                'base_url': 'https://de.etile.es',
                'collections_path': '/kollektionen',
                'projects_path': '/projekte'
            },
            'exagres': {
                'base_url': 'https://www.exagres.es/en',
                'collections_path': '/collections',
                'projects_path': '/projects'
            },
            'gazzini': {
                'base_url': 'https://www.ceramicagazzini.it/de',
                'collections_path': '/kollektionen',
                'projects_path': '/projekte'
            },
            'halcon': {
                'base_url': 'https://www.halconceramicas.com',
                'collections_path': '/colecciones',
                'projects_path': '/ambientes',
                'blog_path': '/blog'
            },
            'novoceram': {
                'base_url': 'https://www.novoceram.fr',
                'collections_path': '/carrelage/collections',
                'projects_path': '/realisations',
                'blog_path': '/blog'
            },
            'roced': {
                'base_url': 'https://roced.es',
                'collections_path': '/colecciones',
                'projects_path': '/proyectos'
            },
            'tuscania': {
                'base_url': 'https://tuscaniagres.it',
                'collections_path': '/collezioni',
                'projects_path': '/progetti'
            },
            'unicom-starker': {
                'base_url': 'https://www.unicomstarker.com/home',
                'collections_path': '/collections',
                'projects_path': '/projects'
            }
        }
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Загружает страницу и возвращает BeautifulSoup объект."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {str(e)}")
            return None
    
    def normalize_url(self, url: str, base_url: str) -> str:
        """Преобразует относительный URL в абсолютный."""
        if not url:
            return ''
        return urljoin(base_url, url)
    
    def download_image(self, image_url: str, manufacturer_slug: str) -> Optional[str]:
        """Скачивает изображение и сохраняет локально."""
        if not image_url:
            return None
        
        # Проверяем, что URL валиден
        if not image_url.startswith('http'):
            print(f"  ⚠️  Невалидный URL изображения: {image_url}")
            return None
        
        try:
            # Генерируем уникальное имя файла
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:10]
            ext = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
            # Убираем query параметры из расширения
            ext = ext.split('?')[0]
            if not ext or len(ext) > 5:
                ext = '.jpg'
            filename = f"{manufacturer_slug}_{url_hash}{ext}"
            
            # Путь для сохранения
            upload_dir = os.path.join('app', 'static', 'uploads', 'manufacturers')
            os.makedirs(upload_dir, exist_ok=True)
            
            filepath = os.path.join(upload_dir, filename)
            
            # Проверяем, не скачано ли уже
            if os.path.exists(filepath):
                print(f"  ℹ️  Изображение уже существует: {filename}")
                return f'manufacturers/{filename}'
            
            # Скачиваем изображение
            print(f"  ⬇️  Скачивание: {image_url[:80]}...")
            response = requests.get(image_url, headers=self.headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # Проверяем тип контента
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                print(f"  ⚠️  Не является изображением: {content_type}")
                return None
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"  ✓ Сохранено: {filename}")
            
            # Возвращаем относительный путь
            return f'manufacturers/{filename}'
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Ошибка запроса для {image_url}: {str(e)}")
            return None
        except Exception as e:
            print(f"  ❌ Ошибка при скачивании изображения {image_url}: {str(e)}")
            return None
    
    def extract_full_content(self, url: str, manufacturer_slug: str) -> Dict[str, str]:
        """
        Извлекает полный контент со страницы детального просмотра.
        
        Args:
            url: URL страницы с контентом
            manufacturer_slug: Идентификатор производителя для сохранения изображений
            
        Returns:
            Dict с полями full_content, technical_specs
        """
        soup = self.fetch_page(url)
        if not soup:
            return {'full_content': '', 'technical_specs': ''}
        
        # Удаляем все ненужные элементы по тегам
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Удаляем элементы по классам и ID (навигация, меню, формы, боковые панели)
        unwanted_patterns = [
            'menu', 'navigation', 'nav', 'sidebar', 'side-bar', 'widget',
            'breadcrumb', 'search', 'form', 'modal', 'popup', 'cookie',
            'social', 'share', 'comment', 'footer', 'header', 'top-bar',
            'banner', 'advert', 'promo', 'newsletter', 'subscribe'
        ]
        
        for pattern in unwanted_patterns:
            # Удаляем по классу
            for element in soup.find_all(class_=re.compile(pattern, re.I)):
                element.decompose()
            # Удаляем по ID
            for element in soup.find_all(id=re.compile(pattern, re.I)):
                element.decompose()
        
        # Ищем основной контент - более специфичные селекторы
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', class_=re.compile(r'(^|\s)(content|main|article|entry|post|detail|product|project)(\s|$)', re.I)) or
            soup.find('div', id=re.compile(r'(content|main|article)', re.I))
        )
        
        if not main_content:
            # В крайнем случае берем body
            main_content = soup.find('body')
        
        if not main_content:
            return {'full_content': '', 'technical_specs': ''}
        
        seen_texts = set()  # Для фильтрации дубликатов
        full_content_parts = []
        
        # Извлекаем заголовок страницы (h1)
        h1 = main_content.find('h1')
        if h1:
            title_text = h1.get_text(strip=True)
            if title_text and len(title_text) > 3:
                full_content_parts.append(f"<h1>{title_text}</h1>")
                seen_texts.add(title_text.lower())
        
        # Извлекаем остальные заголовки
        for h in main_content.find_all(['h2', 'h3', 'h4'], limit=15):
            text = h.get_text(strip=True)
            text_lower = text.lower()
            # Фильтруем короткие и повторяющиеся заголовки
            if text and len(text) > 5 and text_lower not in seen_texts:
                # Пропускаем заголовки-ссылки на другие страницы
                if not any(keyword in text_lower for keyword in ['produkte', 'kollektionen', 'kontakt', 'einloggen', 'registrieren', 'alle']):
                    tag_name = h.name
                    full_content_parts.append(f"<{tag_name}>{text}</{tag_name}>")
                    seen_texts.add(text_lower)
        
        # Извлекаем параграфы с более строгой фильтрацией
        paragraph_count = 0
        for p in main_content.find_all('p', limit=100):
            if paragraph_count >= 20:  # Максимум 20 параграфов
                break
                
            text = p.get_text(strip=True)
            text_lower = text.lower()
            
            # Фильтруем:
            # - Слишком короткие (меньше 50 символов)
            # - Дубликаты
            # - Навигационные фразы
            if (text and len(text) >= 50 and text_lower not in seen_texts and
                not any(keyword in text_lower for keyword in [
                    'brauche hilfe', 'suche nach', 'cookie', 'einloggen', 
                    'registrieren', 'alle produkte', 'datenschutz', 'impressum'
                ])):
                full_content_parts.append(f"<p>{text}</p>")
                seen_texts.add(text_lower)
                paragraph_count += 1
        
        # Извлекаем списки (только небольшие, содержательные)
        list_count = 0
        for ul in main_content.find_all(['ul', 'ol'], limit=5):
            if list_count >= 3:  # Максимум 3 списка
                break
                
            items = []
            for li in ul.find_all('li', limit=10):
                text = li.get_text(strip=True)
                text_lower = text.lower()
                # Фильтруем короткие и навигационные пункты
                if (text and len(text) >= 10 and len(text) <= 200 and 
                    text_lower not in seen_texts and
                    not any(keyword in text_lower for keyword in ['produkte', 'kollektionen', 'kontakt'])):
                    items.append(f"<li>{text}</li>")
                    seen_texts.add(text_lower)
            
            if len(items) >= 2:  # Только если есть хотя бы 2 осмысленных пункта
                list_tag = ul.name
                full_content_parts.append(f"<{list_tag}>{''.join(items)}</{list_tag}>")
                list_count += 1
        
        # Ищем и скачиваем изображения из контента (только уникальные)
        seen_images = set()
        for img in main_content.find_all('img', limit=10):
            img_url = img.get('src') or img.get('data-src')
            if img_url and img_url not in seen_images:
                seen_images.add(img_url)
                # Нормализуем URL
                img_url = self.normalize_url(img_url, url)
                # Пропускаем маленькие изображения (логотипы, иконки)
                width = img.get('width', '0')
                if width and width.isdigit() and int(width) < 100:
                    continue
                # Скачиваем изображение
                local_path = self.download_image(img_url, manufacturer_slug)
                if local_path:
                    alt_text = img.get('alt', 'Product image')
                    full_content_parts.append(f'<img src="/static/uploads/{local_path}" alt="{alt_text}" class="img-fluid my-3">')
        
        # Ищем технические характеристики
        technical_specs = ""
        specs_keywords = ['spec', 'technical', 'характеристики', 'данные', 'details', 'properties', 'features', 'formato', 'acabado']
        
        for keyword in specs_keywords:
            specs_section = soup.find(['div', 'section', 'table'], class_=re.compile(keyword, re.I))
            if specs_section:
                specs_items = []
                
                # Если это таблица
                if specs_section.name == 'table':
                    for row in specs_section.find_all('tr', limit=20):
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            label = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            if label and value and len(label) < 100:
                                specs_items.append(f"{label}: {value}")
                else:
                    # Ищем пары ключ-значение
                    for item in specs_section.find_all(['li', 'p', 'div'], limit=20):
                        text = item.get_text(strip=True)
                        if text and 10 < len(text) < 200:
                            specs_items.append(text)
                
                if specs_items:
                    technical_specs = "\n".join(specs_items[:15])  # Максимум 15 характеристик
                    break
        
        full_content = "\n".join(full_content_parts)
        
        return {
            'full_content': full_content,
            'technical_specs': technical_specs
        }
    
    def extract_collections(self, manufacturer_slug: str) -> List[Dict]:
        """
        Извлекает коллекции плитки с сайта производителя.
        
        Args:
            manufacturer_slug: Идентификатор производителя (aparici, dune, etc.)
            
        Returns:
            List[Dict]: Список коллекций с названием, описанием, изображением, полным контентом
        """
        config = self.manufacturer_configs.get(manufacturer_slug)
        if not config:
            return []
        
        url = config['base_url'] + config.get('collections_path', '')
        soup = self.fetch_page(url)
        
        if not soup:
            return []
        
        collections = []
        seen_urls = set()  # Для избежания дубликатов
        
        # Расширенный поиск ссылок на коллекции
        collection_links = (
            soup.find_all('a', href=re.compile(r'/(collections?|serien|kollektionen?|produkt|colecciones|collezioni)/')) +
            soup.find_all('a', class_=re.compile(r'collection|product|serie', re.I))
        )
        
        print(f"Найдено {len(collection_links)} ссылок на коллекции для {manufacturer_slug}")
        
        for link in collection_links[:15]:  # Ограничиваем количество для производительности
            # Формируем source_url
            href = link.get('href', '')
            source_url = self.normalize_url(href, config['base_url'])
            
            # Пропускаем дубликаты и недействительные URL
            if source_url in seen_urls or not source_url or not source_url.startswith('http'):
                continue
            seen_urls.add(source_url)
            
            # Извлекаем заголовок с превью
            title = link.get_text(strip=True)
            if not title or len(title) < 3:
                # Ищем заголовок в дочерних элементах
                title_elem = link.find(['h2', 'h3', 'h4', 'h5', 'span', 'div'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
            
            # Если нет заголовка, пропускаем
            if not title or len(title) < 3 or len(title) > 100:
                continue
            
            print(f"Обработка коллекции: {title} - {source_url}")
            
            # Ищем превью изображение на странице списка
            preview_image = None
            
            # Сначала ищем внутри ссылки
            img = link.find('img')
            if not img:
                # Если не нашли, ищем в родительском контейнере
                parent = link.find_parent(['div', 'article', 'li'])
                if parent:
                    img = parent.find('img')
            
            if img:
                img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                if img_src:
                    # Нормализуем URL
                    img_src = self.normalize_url(img_src, config['base_url'])
                    # Скачиваем превью изображение
                    preview_image = self.download_image(img_src, manufacturer_slug)
                    if preview_image:
                        print(f"  ✓ Скачано превью изображение: {preview_image}")
                else:
                    print(f"  ⚠️  Изображение найдено, но src пустой")
            else:
                print(f"  ⚠️  Превью изображение не найдено для {title}")
            
            # Ищем короткое описание на странице списка
            short_description = ""
            # Ищем описание в родительском контейнере ссылки
            parent = link.find_parent(['div', 'article'])
            if parent:
                desc_elem = parent.find(['p', 'div'], class_=re.compile(r'desc|subtitle|text|summary', re.I))
                if desc_elem:
                    short_description = desc_elem.get_text(strip=True)[:200]
            
            # Заходим на детальную страницу коллекции для получения полного контента
            full_data = self.extract_full_content(source_url, manufacturer_slug)
            
            # Если нет превью изображения, попробуем взять из full_content
            # (в full_content уже есть скачанные изображения)
            final_image = preview_image
            if not final_image and full_data.get('full_content'):
                # Попробуем извлечь первое изображение из full_content
                import re as regex
                img_match = regex.search(r'<img src="([^"]+)"', full_data.get('full_content', ''))
                if img_match:
                    # Берем путь из уже обработанного контента
                    final_image = img_match.group(1).replace('/static/uploads/', '')
            
            # Используем full_content для описания, если short_description пустое
            final_description = short_description
            if not final_description and full_data.get('full_content'):
                # Берем первые 300 символов текста (без HTML тегов)
                import re as regex
                text_only = regex.sub(r'<[^>]+>', '', full_data.get('full_content', ''))
                final_description = text_only[:300].strip()
            
            # Объединяем данные
            collections.append({
                'title': title,
                'description': final_description,
                'full_content': full_data.get('full_content', ''),
                'technical_specs': full_data.get('technical_specs', ''),
                'image_url': final_image,  # Может быть путь к локальному файлу или None
                'source_url': source_url
            })
            
            print(f"  ✓ Коллекция добавлена: {title}, изображение: {final_image or 'нет'}\n")
        
        print(f"Извлечено {len(collections)} коллекций для {manufacturer_slug}")
        return collections
    
    def extract_projects(self, manufacturer_slug: str) -> List[Dict]:
        """
        Извлекает проекты/реализации с сайта производителя.
        
        Args:
            manufacturer_slug: Идентификатор производителя
            
        Returns:
            List[Dict]: Список проектов с названием, описанием, изображением, полным контентом
        """
        config = self.manufacturer_configs.get(manufacturer_slug)
        if not config or 'projects_path' not in config:
            return []
        
        url = config['base_url'] + config['projects_path']
        soup = self.fetch_page(url)
        
        if not soup:
            return []
        
        projects = []
        seen_urls = set()
        
        # Ищем проекты по различным паттернам
        project_cards = soup.find_all(['article', 'div', 'a'], class_=re.compile(r'project|realiz|card|proyecto'))
        
        # Также ищем прямые ссылки на проекты
        project_links = soup.find_all('a', href=re.compile(r'/(project|proyecto|realiz|references?)/'))
        all_elements = list(project_cards) + list(project_links)
        
        print(f"Найдено {len(all_elements)} элементов проектов для {manufacturer_slug}")
        
        for element in all_elements[:12]:  # Ограничиваем для производительности
            # Извлекаем название
            if element.name == 'a':
                title = element.get_text(strip=True)
                link_elem = element
            else:
                title_elem = element.find(['h2', 'h3', 'h4', 'h5'])
                title = title_elem.get_text(strip=True) if title_elem else None
                link_elem = element.find('a')
            
            if not title or len(title) < 3:
                continue
            
            # Извлекаем ссылку на детальную страницу
            source_url = ""
            if link_elem:
                href = link_elem.get('href', '')
                source_url = self.normalize_url(href, config['base_url'])
            
            # Пропускаем дубликаты и пустые ссылки
            if not source_url or source_url in seen_urls:
                continue
            seen_urls.add(source_url)
            
            # Ищем превью изображение
            img = element.find('img')
            preview_image = None
            if img:
                img_src = img.get('src') or img.get('data-src')
                if img_src:
                    img_src = self.normalize_url(img_src, config['base_url'])
                    preview_image = self.download_image(img_src, manufacturer_slug)
            
            # Короткое описание
            desc_elem = element.find('p')
            short_description = desc_elem.get_text(strip=True)[:200] if desc_elem else ""
            
            print(f"Обработка проекта: {title}")
            
            # Заходим на детальную страницу для получения полного контента
            full_data = self.extract_full_content(source_url, manufacturer_slug)
            
            projects.append({
                'title': title,
                'description': short_description if short_description else full_data.get('full_content', '')[:300],
                'full_content': full_data.get('full_content', ''),
                'technical_specs': full_data.get('technical_specs', ''),
                'image_url': preview_image,
                'source_url': source_url
            })
        
        print(f"Извлечено {len(projects)} проектов для {manufacturer_slug}")
        return projects
    
    def extract_blog_posts(self, manufacturer_slug: str) -> List[Dict]:
        """
        Извлекает статьи из блога/новостей производителя.
        
        Args:
            manufacturer_slug: Идентификатор производителя
            
        Returns:
            List[Dict]: Список статей с названием, анонсом, датой, полным контентом
        """
        config = self.manufacturer_configs.get(manufacturer_slug)
        if not config:
            return []
        
        blog_path = config.get('blog_path') or config.get('news_path') or config.get('magazine_path')
        if not blog_path:
            return []
        
        url = config['base_url'] + blog_path
        soup = self.fetch_page(url)
        
        if not soup:
            return []
        
        posts = []
        seen_urls = set()
        
        # Ищем статьи по различным паттернам
        post_cards = soup.find_all(['article', 'div'], class_=re.compile(r'post|article|blog|news|noticia'))
        
        # Также ищем прямые ссылки на статьи
        post_links = soup.find_all('a', href=re.compile(r'/(post|article|blog|news|noticia)/'))
        all_elements = list(post_cards) + list(post_links)
        
        print(f"Найдено {len(all_elements)} элементов блога для {manufacturer_slug}")
        
        for element in all_elements[:8]:  # Ограничиваем количество
            # Извлекаем название
            if element.name == 'a':
                title = element.get_text(strip=True)
                link_elem = element
            else:
                title_elem = element.find(['h2', 'h3', 'h4'])
                title = title_elem.get_text(strip=True) if title_elem else None
                link_elem = element.find('a')
            
            if not title or len(title) < 5:
                continue
            
            # Извлекаем ссылку
            source_url = ""
            if link_elem:
                href = link_elem.get('href', '')
                source_url = self.normalize_url(href, config['base_url'])
            
            # Пропускаем дубликаты
            if not source_url or source_url in seen_urls:
                continue
            seen_urls.add(source_url)
            
            # Ищем превью изображение
            img = element.find('img')
            preview_image = None
            if img:
                img_src = img.get('src') or img.get('data-src')
                if img_src:
                    img_src = self.normalize_url(img_src, config['base_url'])
                    preview_image = self.download_image(img_src, manufacturer_slug)
            
            # Извлекаем анонс
            desc_elem = element.find('p')
            short_content = desc_elem.get_text(strip=True)[:200] if desc_elem else ""
            
            # Извлекаем дату (если есть)
            date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time|fecha'))
            created_at = None
            if date_elem:
                try:
                    date_text = date_elem.get_text(strip=True)
                    # Placeholder - можно добавить парсинг разных форматов дат
                    created_at = datetime.now()
                except:
                    pass
            
            print(f"Обработка статьи блога: {title}")
            
            # Заходим на детальную страницу для получения полного контента
            full_data = self.extract_full_content(source_url, manufacturer_slug)
            
            posts.append({
                'title': title,
                'content': short_content if short_content else full_data.get('full_content', '')[:300],
                'full_content': full_data.get('full_content', ''),
                'image_url': preview_image,
                'source_url': source_url,
                'created_at': created_at
            })
        
        print(f"Извлечено {len(posts)} статей блога для {manufacturer_slug}")
        return posts
    
    def extract_all_content(self, manufacturer_slug: str) -> Dict:
        """
        Извлекает весь контент с сайта производителя (коллекции, проекты, блог).
        Использует индивидуальный парсер если доступен, иначе базовый.
        
        Args:
            manufacturer_slug: Идентификатор производителя
            
        Returns:
            Dict: Словарь с ключами collections, projects, blog_posts
        """
        print(f"\n==== Извлечение контента для {manufacturer_slug} ====")
        
        # Пытаемся получить специфичный парсер для этого производителя
        custom_parser = ManufacturerParserFactory.get_parser(manufacturer_slug)
        
        if custom_parser:
            # Используем индивидуальный парсер
            print(f"✨ Используется индивидуальный парсер для {manufacturer_slug}")
            try:
                return {
                    'collections': custom_parser.extract_collections(),
                    'projects': custom_parser.extract_projects(),
                    'blog_posts': custom_parser.extract_blog_posts()
                }
            except Exception as e:
                print(f"❌ Ошибка в индивидуальном парсере: {str(e)}")
                print("⚠️  Переключение на базовый парсер...")
        
        # Используем базовый парсер
        print(f"📝 Используется базовый парсер для {manufacturer_slug}")
        return {
            'collections': self.extract_collections(manufacturer_slug),
            'projects': self.extract_projects(manufacturer_slug),
            'blog_posts': self.extract_blog_posts(manufacturer_slug)
        }
    
    def get_manufacturer_info(self, manufacturer_slug: str) -> Optional[Dict]:
        """
        Извлекает основную информацию о производителе с главной страницы.
        
        Args:
            manufacturer_slug: Идентификатор производителя
            
        Returns:
            Dict: Информация о производителе (название, описание, страна)
        """
        config = self.manufacturer_configs.get(manufacturer_slug)
        if not config:
            return None
        
        soup = self.fetch_page(config['base_url'])
        if not soup:
            return None
        
        # Ищем описание компании
        about_section = soup.find(['section', 'div'], class_=re.compile(r'about|company|firma'))
        description = ""
        if about_section:
            desc_elem = about_section.find('p')
            if desc_elem:
                description = desc_elem.get_text(strip=True)
        
        # Ищем логотип
        logo = soup.find('img', {'alt': re.compile(r'logo', re.I)})
        logo_url = logo.get('src') if logo else None
        
        return {
            'name': manufacturer_slug.title(),
            'website': config['base_url'],
            'description': description,
            'logo_url': logo_url
        }


# Создаем глобальный экземпляр сервиса
scraper_service = ContentScraperService()

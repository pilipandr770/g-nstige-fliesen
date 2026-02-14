"""
Индивидуальные парсеры для каждого производителя плитки.
Каждый парсер знает специфическую структуру сайта своего производителя.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import re
from urllib.parse import urljoin, urlparse
import os
import hashlib
from werkzeug.utils import secure_filename
import time  # Для задержек между запросами


class BaseManufacturerParser(ABC):
    """Базовый класс парсера для производителя"""
    
    def __init__(self, base_url: str, slug: str):
        self.base_url = base_url
        self.slug = slug
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Загружает страницу"""
        try:
            print(f"  📄 Загрузка: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"  ❌ Ошибка загрузки {url}: {str(e)}")
            return None
    
    def normalize_url(self, url: str) -> str:
        """Преобразует относительный URL в абсолютный"""
        if not url:
            return ''
        return urljoin(self.base_url, url)
    
    def download_image(self, image_url: str, retry_count: int = 3) -> Optional[str]:
        """Скачивает изображение и сохраняет локально с механизмом повторных попыток."""
        if not image_url:
            return None
        
        # Проверяем, что URL валиден
        if not image_url.startswith('http'):
            print(f"  ⚠️  Невалидный URL изображения: {image_url}")
            return None
        
        # Генерируем уникальное имя файла
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:10]
        ext = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
        # Убираем query параметры из расширения
        ext = ext.split('?')[0]
        if not ext or len(ext) > 5:
            ext = '.jpg'
        filename = f"{self.slug}_{url_hash}{ext}"
        
        # Путь для сохранения
        upload_dir = os.path.join('app', 'static', 'uploads', 'manufacturers')
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        
        # Проверяем, не скачано ли уже
        if os.path.exists(filepath):
            print(f"  ℹ️  Изображение уже существует: {filename}")
            return f'manufacturers/{filename}'
        
        # Пробуем скачать с повторными попытками
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    print(f"  🔄 Повторная попытка {attempt + 1}/{retry_count}...")
                
                # Скачиваем изображение
                print(f"  ⬇️  Скачивание: {image_url[:80]}...")
                response = requests.get(image_url, headers=self.headers, timeout=20, stream=True)
                response.raise_for_status()
                
                # Проверяем тип контента
                content_type = response.headers.get('content-type', '')
                if 'image' not in content_type:
                    print(f"  ⚠️  Не является изображением: {content_type}")
                    return None
                
                # Сохраняем файл
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Проверяем что файл не пустой и не слишком маленький (обычно < 5KB это thumbnail или сломанный файл)
                # А также не слишком большой (> 3MB это обычно неоптимизированное изображение)
                file_size = os.path.getsize(filepath)
                min_size = 5000      # Минимум 5KB
                max_size = 20000000  # Максимум 20MB
                
                if file_size < min_size:
                    print(f"  ⚠️  Файл слишком маленький ({file_size} bytes), пропускаем")
                    os.remove(filepath)
                    if attempt < retry_count - 1:
                        continue
                    return None
                
                if file_size > max_size:
                    print(f"  ⚠️  Файл слишком большой ({file_size / 1000000:.1f} MB), пропускаем")
                    os.remove(filepath)
                    if attempt < retry_count - 1:
                        continue
                    return None
                
                print(f"  ✓ Сохранено: {filename} ({os.path.getsize(filepath)} bytes)")
                
                # Возвращаем относительный путь
                return f'manufacturers/{filename}'
                
            except requests.exceptions.Timeout as e:
                print(f"  ⏱️  Таймаут при скачивании: {str(e)}")
                if attempt < retry_count - 1:
                    continue
                return None
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Ошибка запроса для {image_url}: {str(e)}")
                if attempt < retry_count - 1:
                    continue
                return None
            except Exception as e:
                print(f"  ❌ Ошибка сохранения изображения: {str(e)}")
                if attempt < retry_count - 1:
                    continue
                return None
        
        return None
    
    def extract_logo(self) -> Optional[str]:
        """Извлекает логотип производителя с главной страницы"""
        print(f"🔍 Поиск логотипа для {self.slug}...")
        
        soup = self.fetch_page(self.base_url)
        if not soup:
            return None
        
        # Ищем логотип по различным паттернам
        logo = None
        
        # 1. По alt атрибуту
        logo_img = soup.find('img', {'alt': re.compile(r'logo', re.I)})
        if logo_img:
            logo = logo_img.get('src') or logo_img.get('data-src')
        
        # 2. По классу
        if not logo:
            logo_img = soup.find('img', class_=re.compile(r'logo', re.I))
            if logo_img:
                logo = logo_img.get('src') or logo_img.get('data-src')
        
        # 3. В header navbar
        if not logo:
            header = soup.find(['header', 'nav'], class_=re.compile(r'navbar|header', re.I))
            if header:
                logo_img = header.find('img')
                if logo_img:
                    logo = logo_img.get('src') or logo_img.get('data-src')
        
        if logo:
            logo_url = self.normalize_url(logo)
            # Скачиваем логотип
            local_path = self.download_image(logo_url)
            return local_path
        
        print(f"  ⚠️  Логотип не найден")
        return None
    
    @abstractmethod
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции с сайта производителя"""
        pass
    
    @abstractmethod
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детальную информацию о коллекции"""
        pass
    
    @abstractmethod
    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты с сайта производителя"""
        pass
    
    @abstractmethod
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога с сайта производителя"""
        pass


class ApariciParser(BaseManufacturerParser):
    """Парсер для Aparici (https://www.aparici.com/de)"""
    
    def __init__(self):
        super().__init__('https://www.aparici.com/de', 'aparici')
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Aparici"""
        print("🔍 Парсинг коллекций Aparici...")
        
        soup = self.fetch_page(f"{self.base_url}/kollektionen")
        if not soup:
            return []
        
        collections = []
        
        # Aparici: ищем ссылки с классом sub-menu_colecciones-item
        collection_links = soup.find_all('a', class_='sub-menu_colecciones-item')
        
        # Альтернативно - ищем все ссылки с href содержащим /kollektionen/
        if not collection_links:
            all_links = soup.find_all('a', href=True)
            collection_links = [link for link in all_links if '/kollektionen/' in link.get('href', '') and link.get('href', '') != f'{self.base_url}/kollektionen']
        
        print(f"  Найдено {len(collection_links)} ссылок на коллекции")
        
        for idx, link in enumerate(collection_links[:20], 1):  # Увеличил лимит до 20
            collection_url = self.normalize_url(link.get('href', ''))
            if not collection_url or collection_url == f'{self.base_url}/kollektionen':
                continue
            
            # Извлекаем название из текста ссылки
            title = link.get_text(strip=True)
            
            if not title or len(title) < 2:
                continue
            
            print(f"  🔗 Обработка коллекции {idx}/{len(collection_links[:20])}: {title}")
            
            # Получаем детальную информацию со страницы коллекции
            detail = self.extract_collection_detail(collection_url)
            
            # Если есть изображение в детальной информации, скачиваем его
            local_image_path = None
            if detail.get('image_url'):
                local_image_path = self.download_image(detail['image_url'])
            
            # Проверяем что получили изображение
            if not local_image_path and not detail.get('image_url'):
                print(f"  ⚠️  Коллекция {title} пропущена - нет изображения")
                continue
            
            collections.append({
                'title': title,
                'description': detail.get('description', ''),
                'full_content': detail.get('full_content', ''),
                'technical_specs': detail.get('technical_specs', ''),
                'image_url': local_image_path or detail.get('image_url'),
                'source_url': collection_url
            })
            
            print(f"  ✓ Коллекция {title} добавлена")
            
            # Задержка между запросами чтобы не перегружать сервер
            if idx < len(collection_links[:20]):
                time.sleep(0.5)  # 500ms задержка
        
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции Aparici"""
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        # Извлекаем заголовок (для уверенности)
        h1 = soup.find('h1', class_='s-headerCorporate_title')
        title = h1.get_text(strip=True) if h1 else ''
        
        # Ищем главное изображение коллекции
        # В Aparici это обычно большое изображение с классом img-fluid и alt равным названию коллекции
        main_image = None
        
        # Ищем изображения с alt равным названию или содержащим его
        images = soup.find_all('img', class_='img-fluid')
        for img in images:
            alt = img.get('alt', '').lower()
            src = img.get('src') or img.get('data-src')
            
            # Пропускаем логотипы
            if 'logo' in alt or 'logo' in (src or '').lower():
                continue
            
            # Ищем изображения с подходящим alt
            if alt and len(alt) > 2 and '_big' in (src or '') or 'rect' in (src or ''):
                main_image = self.normalize_url(src)
                break
        
        # Если не нашли, берем первое большое изображение
        if not main_image:
            for img in images:
                src = img.get('src') or img.get('data-src')
                if src and 'logo' not in src.lower():
                    main_image = self.normalize_url(src)
                    break
        
        # Ищем описание (если есть)
        description = ""
        # В Aparici описания обычно минимальны, но попробуем найти
        desc_elem = soup.find('div', class_=re.compile(r'description|intro|summary', re.I))
        if desc_elem:
            paragraphs = desc_elem.find_all('p')
            if paragraphs:
                desc_texts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Фильтруем навигационные фразы
                    if text and len(text) > 30 and 'brauche hilfe' not in text.lower() and 'einloggen' not in text.lower():
                        desc_texts.append(text)
                if desc_texts:
                    description = ' '.join(desc_texts[:2])[:300]
        
        # Ищем технические характеристики
        specs = ""
        # В Aparici могут быть блоки с форматами и отделкой
        specs_sections = soup.find_all(['div', 'section'], class_=re.compile(r'formato|acabado|caracteristica|specs', re.I))
        if specs_sections:
            specs_items = []
            for section in specs_sections[:3]:
                # Ищем все текстовые элементы
                items = section.find_all(['li', 'p', 'span'], limit=20)
                for item in items:
                    text = item.get_text(strip=True)
                    if text and 10 < len(text) < 100:
                        specs_items.append(text)
            if specs_items:
                specs = "\n".join(specs_items[:15])
        
        # Собираем полный контент - берем все изображения продуктов
        content_parts = []
        product_images = soup.find_all('img', {'alt': title})
        for img in product_images[:8]:
            src = img.get('src') or img.get('data-src')
            if src and 'logo' not in src.lower():
                img_url = self.normalize_url(src)
                content_parts.append(f'<img src="{img_url}" alt="{title}" class="img-fluid mb-3">')
        
        return {
            'description': description or f'Kollektion {title}',
            'full_content': '\n'.join(content_parts),
            'technical_specs': specs,
            'image_url': main_image
        }
    
    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты Aparici"""
        print("🔍 Парсинг проектов Aparici...")
        
        soup = self.fetch_page(f"{self.base_url}/projekte")
        if not soup:
            return []
        
        projects = []
        
        # Aparici: проекты в div с классом e_projectList
        project_cards = soup.find_all('div', class_='e_projectList')
        
        print(f"  Найдено {len(project_cards)} проектов")
        
        for idx, card in enumerate(project_cards[:20], 1):
            # Ищем ссылку внутри
            link = card.find('a', class_='e_projectList-container')
            if not link:
                link = card.find('a')
            
            if not link:
                continue
            
            project_url = self.normalize_url(link.get('href', ''))
            if not project_url:
                continue
            
            # Извлекаем заголовок - текст ссылки или h-элемент
            title = ''
            title_elem = card.find(['h2', 'h3', 'h4', 'h5'])
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                # Берем текст из ссылки, очищаем от лишнего
                title_text = link.get_text(strip=True)
                # Убираем части типа "Restaurants|Spain"
                if '|' in title_text:
                    parts = title_text.split('|')
                    # Берем последнюю часть (название проекта)
                    title = parts[-1].strip() if len(parts) > 1 else title_text
                else:
                    title = title_text
            
            if not title or len(title) < 3:
                continue
            
            print(f"  🔗 Обработка проекта {idx}/{len(project_cards[:20])}: {title[:50]}")
            
            # Извлекаем изображение
            img = card.find('img', class_='e_projectList-image')
            if not img:
                img = card.find('img')
            
            image_url = None
            local_image_path = None
            if img:
                image_url = self.normalize_url(img.get('src') or img.get('data-src') or img.get('data-lazy', ''))
                if image_url:
                    local_image_path = self.download_image(image_url)
            
            # Пропускаем проекты без изображений
            if not local_image_path and not image_url:
                print(f"  ⚠️  Проект {title} пропущен - нет изображения")
                continue
            
            # Извлекаем описание если есть
            description = ''
            desc_elem = card.find('div', class_='e_projectList-content')
            if desc_elem:
                description = desc_elem.get_text(strip=True)[:300]
            
            projects.append({
                'title': title,
                'description': description,
                'full_content': '',
                'image_url': local_image_path or image_url,
                'source_url': project_url
            })
            
            print(f"  ✓ Проект {title[:50]} добавлен")
            
            # Задержка между запросами
            if idx < len(project_cards[:20]):
                time.sleep(0.3)
        
        return projects
    
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога Aparici"""
        print("🔍 Парсинг блога Aparici...")
        
        soup = self.fetch_page(f"{self.base_url}/blog")
        if not soup:
            return []
        
        blog_posts = []
        
        # Aparici: статьи блога в div с изображением класса e_noticiaList-image
        # Ищем все ссылки на статьи (не категории)
        all_links = soup.find_all('a', href=True)
        blog_article_links = []
        
        for link in all_links:
            href = link.get('href', '')
            # Фильтруем: категории имеют length=6, статьи length=7+
            if '/blog/' in href and len(href.split('/')) > 6:
                if href not in [bl.get('href') for bl in blog_article_links]:
                    blog_article_links.append(link)
        
        print(f"  Найдено {len(blog_article_links)} статей блога")
        
        for idx, link in enumerate(blog_article_links[:15], 1):
            article_url = self.normalize_url(link.get('href', ''))
            if not article_url:
                continue
            
            # Извлекаем заголовок
            title = link.get_text(strip=True)
            
            # Очищаем заголовок от категорий и дат
            if title:
                # Убираем категорию и дату в начале (например "Trends23 Januar 2026")
                import re
                # Ищем дату и убираем всё до неё
                date_match = re.search(r'\d{1,2}\s+\w+\s+\d{4}', title)
                if date_match:
                    title = title[date_match.end():].strip()
            
            if not title or len(title) < 5:
                continue
            
            print(f"  🔗 Обработка статьи {idx}/{len(blog_article_links[:15])}: {title[:50]}")
            
            # Ищем изображение - оно должно быть внутри или рядом с ссылкой
            parent = link.parent
            img = None
            
            # Ищем в самой ссылке
            img = link.find('img', class_='e_noticiaList-image')
            
            # Если нет, ищем в родителе
            if not img and parent:
                img = parent.find('img', class_='e_noticiaList-image')
            
            # Если всё ещё нет, ищем любое изображение рядом
            if not img and parent:
                img = parent.find('img')
            
            image_url = None
            local_image_path = None
            if img:
                image_url = self.normalize_url(img.get('src') or img.get('data-src') or img.get('data-lazy', ''))
                if image_url:
                    local_image_path = self.download_image(image_url)
            
            # Для блога изображение желательно, но не обязательно
            if not local_image_path and not image_url:
                print(f"  ⚠️  Статья {title} без изображения")
            
            blog_posts.append({
                'title': title,
                'content': '',  # Краткое описание можно добавить при необходимости
                'full_content': '',
                'image_url': local_image_path or image_url,
                'source_url': article_url
            })
            
            print(f"  ✓ Статья {title[:50]} добавлена")
            
            # Задержка между запросами
            if idx < len(blog_article_links[:15]):
                time.sleep(0.3)
        
        return blog_posts


class DuneParser(BaseManufacturerParser):
    """Парсер для Dune Ceramics"""
    
    def __init__(self):
        super().__init__('https://duneceramics.com/de', 'dune')
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Dune"""
        print("🔍 Парсинг коллекций Dune...")

        soup = self.fetch_page(f"{self.base_url}/serien")
        if not soup:
            return []

        collections = []
        seen = set()

        # Dune uses /serien/<slug> (and /series for other langs)
        links = soup.find_all('a', href=re.compile(r'/(serien|series)/'))
        for a in links:
            href = a.get('href')
            if not href:
                continue
            full = self.normalize_url(href)
            if full in seen:
                continue
            seen.add(full)

            title = a.get_text(strip=True)
            if not title or len(title) < 2:
                # try nearby heading
                h = a.find_previous(['h2', 'h3'])
                title = h.get_text(strip=True) if h else full.rstrip('/').split('/')[-1].replace('-', ' ').title()

            # try to get image from the link or parent
            img = a.find('img')
            if not img:
                parent = a.find_parent(['div', 'li', 'figure', 'article'])
                if parent:
                    img = parent.find('img')

            image_path = None
            image_url = None
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy')
                if src and not src.startswith('data:'):
                    image_url = self.normalize_url(src)
                    image_path = self.download_image(image_url)

            detail = self.extract_collection_detail(full) or {}

            # Prefer detail page images (they are more specific), fall back to link/thumbnail
            chosen_image = None
            detail_images = detail.get('images') or []
            if detail_images:
                chosen_image = detail_images[0]
            else:
                chosen_image = image_path or image_url

            collections.append({
                'title': title,
                'description': detail.get('description', ''),
                'full_content': detail.get('full_content', ''),
                'technical_specs': detail.get('technical_specs', ''),
                'image_url': chosen_image,
                'source_url': full
            })

        print(f"  ✅ Найдено коллекций: {len(collections)}")
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции Dune"""
        soup = self.fetch_page(url)
        if not soup:
            return {}
        description = ""
        content_parts = []

        desc_elem = soup.find('div', class_=re.compile(r'description|intro|text|content', re.I))
        if desc_elem:
            description = desc_elem.get_text(strip=True)[:300]
            for p in desc_elem.find_all('p', limit=6):
                t = p.get_text(strip=True)
                if t:
                    content_parts.append(f"<p>{t}</p>")

        # Collect image URLs from the detail page, deduplicate and prefer images
        images = []
        candidates = []
        parsed_path = urlparse(url).path.rstrip('/')
        slug = parsed_path.split('/')[-1].lower() if parsed_path else ''

        # Nav/menu category keywords to exclude (these appear in navigation and repeat often)
        nav_keywords = ['pavimentos', 'revestimientos', 'mosaicos', 'lavabos', 'sanitarios', 
                        'ceramica', 'porcelanico']  # Generic category names
        
        # Remove nav/footer/header from consideration
        nav_header = soup.find(['nav', 'header', 'footer'])
        if nav_header:
            for elem in nav_header.find_all('img'):
                elem.decompose()

        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            # normalize and skip data URLs and small site assets
            if src.startswith('data:'):
                continue
            norm = self.normalize_url(src)
            low = norm.lower()
            
            # Skip logos and site navigation assets
            if 'logo' in low:
                continue
            if '/assets/images/' in low:
                continue
            
            # Skip known nav category images (pavimentos, revestimientos, mosaicos)
            # These repeat and are not collection-specific
            if any(kw in low for kw in nav_keywords):
                # Check if it's a specific collection image (contains slug) or generic category
                if not (slug and slug in low):
                    # This looks like a generic category image, skip it
                    continue
            
            candidates.append(norm)

        # Deduplicate while preserving order
        seen_urls = set()
        unique = []
        for c in candidates:
            if c in seen_urls:
                continue
            seen_urls.add(c)
            unique.append(c)

        # Prefer images that include the collection slug or contain 'serie'/'amb' (ambient/product images)
        def score_image(u: str) -> int:
            lu = u.lower()
            # Collection-specific (highest priority)
            if slug and slug in lu:
                return 0
            # Ambient/product images
            if 'amb-' in lu:
                return 1
            # Series images
            if 'serie' in lu or 'series' in lu:
                return 2
            # Fallback - generic product-related
            return 3

        unique.sort(key=score_image)

        # Download up to 8 preferred images
        for src in unique:
            p = self.download_image(src)
            if p:
                images.append(p)
            if len(images) >= 8:
                break

        return {
            'description': description,
            'full_content': '\n'.join(content_parts),
            'technical_specs': '',
            'images': images
        }
    
    def extract_projects(self) -> List[Dict]:
        return []
    
    def extract_blog_posts(self) -> List[Dict]:
        posts = []
        # Dune exposes a blog at /blog
        candidates = [f"{self.base_url}/blog", f"{self.base_url}/de/blog", f"{self.base_url}/en/blog"]
        soup = None
        for c in candidates:
            soup = self.fetch_page(c)
            if soup:
                break
        if not soup:
            return posts

        seen = set()
        # common article selectors
        for sel in ['article', '[class*=post]', '[class*=blog]', 'div.card', 'div.post-item']:
            elems = soup.select(sel)
            if not elems:
                continue
            for el in elems:
                a = el.find('a', href=True)
                if not a:
                    continue
                full = self.normalize_url(a.get('href'))
                if full in seen:
                    continue
                seen.add(full)

                title = (el.find(['h1', 'h2', 'h3']) and el.find(['h1', 'h2', 'h3']).get_text(strip=True)) or a.get_text(strip=True)
                img = el.find('img') or a.find('img')
                image = None
                if img:
                    src = img.get('src') or img.get('data-src')
                    if src and 'logo' not in src:
                        image = self.download_image(self.normalize_url(src))

                posts.append({'title': title, 'url': full, 'image_url': image, 'excerpt': ''})
            if posts:
                break

        print(f"  ✅ Найдено статей: {len(posts)}")
        return posts


class EquipeParser(BaseManufacturerParser):
    """Парсер для Equipe Ceramicas"""
    
    def __init__(self):
        super().__init__('https://www.equipeceramicas.com/de', 'equipe')
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Equipe"""
        print("🔍 Парсинг коллекций Equipe (портфолио)...")

        collections = []
        visited = set()

        # Основная страница коллекций
        start_url = f"{self.base_url}/kollektionen"
        page = 1
        while True:
            url = start_url if page == 1 else f"{start_url}/page/{page}/"
            soup = self.fetch_page(url)
            if not soup:
                break

            # Ищем ссылки на элементы портфолио (portfolio-item)
            links = soup.find_all('a', href=re.compile(r'/portfolio-item/'))
            if not links:
                # Альтернативно ищем карточки с классом portfolio
                links = [a for a in soup.find_all('a', href=True) if '/portfolio-item/' in a.get('href', '')]

            for a in links:
                href = a.get('href')
                if not href:
                    continue
                full = self.normalize_url(href)
                if full in visited:
                    continue
                visited.add(full)

                # Заголовок: текст ссылки или ближайший <h3>/<h2>
                title = a.get_text(strip=True)
                if not title:
                    h = a.find_previous(['h2', 'h3', 'h4'])
                    title = h.get_text(strip=True) if h else full.rstrip('/').split('/')[-1].replace('-', ' ').title()

                # Изображение: внутри ссылки или в родителе
                img = a.find('img')
                if not img:
                    parent = a.find_parent(['div', 'article', 'figure'])
                    if parent:
                        img = parent.find('img')

                image_path = None
                if img:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy')
                    if src and not src.startswith('data:'):
                        image_path = self.download_image(self.normalize_url(src))

                # Собираем детальную информацию
                detail = self.extract_collection_detail(full) or {}

                collections.append({
                    'title': title,
                    'description': detail.get('description', ''),
                    'full_content': detail.get('full_content', ''),
                    'technical_specs': detail.get('technical_specs', ''),
                    'image_url': image_path or detail.get('images', [None])[0],
                    'source_url': full
                })

            # Проверяем пагинацию: есть ли ссылка на следующую страницу
            pager = soup.find('a', href=re.compile(r'/kollektionen/page/\d+/'))
            if pager:
                page += 1
                time.sleep(0.3)
                continue
            break

        print(f"  ✅ Найдено коллекций: {len(collections)}")
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        soup = self.fetch_page(url)
        if not soup:
            return {}

        description = ""
        content_parts = []

        # Заголовок
        h1 = soup.find(['h1', 'h2'])
        title = h1.get_text(strip=True) if h1 else url.rstrip('/').split('/')[-1]

        # Описание из meta или первых параграфов
        meta = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
        if meta and meta.get('content'):
            description = meta.get('content')[:300]
        else:
            main = soup.find(['main', 'article', 'div'], class_=re.compile(r'content|portfolio|single', re.I))
            if main:
                for p in main.find_all('p', limit=6):
                    text = p.get_text(strip=True)
                    if len(text) > 30:
                        if not description:
                            description = text[:300]
                        content_parts.append(f"<p>{text}</p>")

        # Сбор изображений (wp uploads)
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and ('wp-content' in src or 'uploads' in src):
                p = self.download_image(self.normalize_url(src))
                if p:
                    images.append(p)
            if len(images) >= 8:
                break

        return {
            'title': title,
            'description': description,
            'full_content': '\n'.join(content_parts),
            'technical_specs': '',
            'images': images
        }

    def extract_projects(self) -> List[Dict]:
        print("🔍 Парсинг проектов Equipe...")
        projects = []
        soup = self.fetch_page(f"{self.base_url}/projekte")
        if not soup:
            return projects

        links = soup.find_all('a', href=re.compile(r'/portfolio-item/'))
        seen = set()
        for a in links[:200]:
            href = a.get('href')
            if not href:
                continue
            full = self.normalize_url(href)
            if full in seen:
                continue
            seen.add(full)

            title = a.get_text(strip=True) or a.find_previous(['h2', 'h3']).get_text(strip=True)
            img = a.find('img') or a.find_parent().find('img') if a.find_parent() else None
            image_path = None
            if img:
                src = img.get('src') or img.get('data-src')
                if src:
                    image_path = self.download_image(self.normalize_url(src))

            projects.append({'title': title, 'description': '', 'full_content': '', 'image_url': image_path, 'source_url': full})

        print(f"  ✅ Найдено проектов: {len(projects)}")
        return projects
    
    def extract_projects(self) -> List[Dict]:
        return []
    
    def extract_blog_posts(self) -> List[Dict]:
        print("🔍 Парсинг новостей Equipe...")
        posts = []

        # Try common blog/news paths; prefer /blog/ or /news/
        candidates = [f"{self.base_url}/blog/", f"{self.base_url}/news/", f"{self.base_url}/de/news/"]
        soup = None
        for c in candidates:
            soup = self.fetch_page(c)
            if soup:
                base_page = c
                break
        if not soup:
            return posts

        # Find article elements (article, .post, .news, .entry)
        article_selectors = ['article', '[class*=post]', '[class*=news]', '[class*=entry]', 'div.card', 'div.blog-item']
        seen = set()

        for sel in article_selectors:
            elems = soup.select(sel)
            if not elems:
                continue
            for el in elems:
                a = el.find('a', href=True)
                if not a:
                    continue
                href = a.get('href')
                if not href:
                    continue
                full = self.normalize_url(href)
                if full in seen:
                    continue
                seen.add(full)

                title = (el.find(['h1', 'h2', 'h3']) and el.find(['h1', 'h2', 'h3']).get_text(strip=True)) or a.get_text(strip=True) or ''
                img = el.find('img') or a.find('img') or el.find_previous('img')
                image_path = None
                if img:
                    src = img.get('src') or img.get('data-src')
                    if src:
                        p = self.normalize_url(src)
                        # avoid manufacturer logo
                        if self.slug in p or 'logo' in p:
                            pass
                        else:
                            image_path = self.download_image(p)

                posts.append({'title': title, 'url': full, 'image_url': image_path, 'excerpt': ''})

            if posts:
                break

        print(f"  ✅ Найдено статей: {len(posts)}")
        return posts


class ApeParser(BaseManufacturerParser):
    """Парсер для APE Grupo"""
    
    def __init__(self):
        super().__init__('https://www.apegrupo.com/de', 'ape')
    
    def extract_logo(self) -> Optional[str]:
        """Извлекает логотип APE Grupo"""
        print(f"🔍 Поиск логотипа для {self.slug}...")
        
        soup = self.fetch_page(self.base_url)
        if not soup:
            return None
        
        # APE: логотип находится по определенному пути
        img = soup.find('img', src=re.compile(r'logo_apegrupo'))
        if img:
            logo_url = self.normalize_url(img.get('src'))
            if logo_url:
                return self.download_image(logo_url)
        
        print("  ⚠️  Логотип не найден")
        return None
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции APE Grupo"""
        print("🔍 Парсинг коллекций APE Grupo...")
        
        soup = self.fetch_page(f"{self.base_url}/produkte")
        if not soup:
            return []
        
        collections = []
        
        # APE: коллекции в контейнере listado_buscador_productos
        container = soup.find('div', class_='listado_buscador_productos')
        if not container:
            print("  ⚠️  Контейнер с коллекциями не найден")
            return []
        
        links = container.find_all('a', href=True, limit=15)
        print(f"  Найдено {len(links)} коллекций")
        
        for idx, link in enumerate(links, 1):
            href = link.get('href', '')
            if not href or '/produkte/' not in href:
                continue
            
            print(f"  🔗 Обработка коллекции {idx}/{len(links)}")
            
            # Название из slug URL
            slug = href.rstrip('/').split('/')[-1]
            title = slug.replace('-', ' ').title()
            
            collection_url = self.normalize_url(href)
            
            # Изображение
            img = link.find('img')
            image_url = None
            local_image_path = None
            if img:
                image_url = self.normalize_url(img.get('src') or img.get('data-src', ''))
                if image_url:
                    local_image_path = self.download_image(image_url)
            
            if not local_image_path and not image_url:
                print(f"  ⚠️  Коллекция {title} без изображения")
                continue
            
            collections.append({
                'title': title,
                'description': f'Serie {title}',
                'full_content': '',
                'technical_specs': '',
                'image_url': local_image_path or image_url,
                'source_url': collection_url
            })
            
            print(f"  ✓ Коллекция {title} добавлена")
            
            # Задержка
            if idx < len(links):
                time.sleep(0.5)
        
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции"""
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        description = ""
        content_parts = []
        
        # Ищем основной контент
        main = soup.find(['main', 'article', 'div'], class_=lambda x: x and 'content' in str(x).lower())
        if main:
            for p in main.find_all('p', limit=5):
                text = p.get_text(strip=True)
                if len(text) > 50:
                    if not description:
                        description = text[:300]
                    content_parts.append(f"<p>{text}</p>")
        
        return {
            'description': description,
            'full_content': '\n'.join(content_parts),
            'technical_specs': ''
        }
    
    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты APE Grupo"""
        print("🔍 Парсинг проектов APE Grupo...")
        
        soup = self.fetch_page(f"{self.base_url}/projekte")
        if not soup:
            return []
        
        projects = []
        
        # APE: ищем ссылки на конкретные проекты
        project_links = soup.find_all('a', href=re.compile(r'/projekte/.+/\d+'))
        
        # Убираем дубликаты
        unique_projects = {}
        for link in project_links:
            href = link.get('href')
            if href not in unique_projects:
                unique_projects[href] = link
        
        print(f"  Найдено {len(unique_projects)} проектов")
        
        for idx, (href, link) in enumerate(list(unique_projects.items())[:10], 1):
            print(f"  🔗 Обработка проекта {idx}/{min(10, len(unique_projects))}")
            
            project_url = self.normalize_url(href)
            
            # Название
            title = link.get_text(strip=True)
            
            # Ищем изображение
            img = link.find('img')
            if not img and link.parent:
                img = link.parent.find('img')
            
            image_url = None
            local_image_path = None
            if img:
                image_url = self.normalize_url(img.get('src') or img.get('data-src', ''))
                if image_url:
                    local_image_path = self.download_image(image_url)
            
            if not title or len(title) < 2:
                print(f"  ⚠️  Проект без названия")
                continue
            
            if not local_image_path and not image_url:
                print(f"  ⚠️  Проект {title} без изображения")
                continue
            
            projects.append({
                'title': title[:100],
                'description': '',
                'full_content': '',
                'technical_specs': '',
                'image_url': local_image_path or image_url,
                'source_url': project_url
            })
            
            print(f"  ✓ Проект {title[:50]} добавлен")
            
            # Задержка
            if idx < len(unique_projects):
                time.sleep(0.5)
        
        return projects
    
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога APE Grupo"""
        print("🔍 Парсинг блога APE Grupo...")
        
        soup = self.fetch_page(f"{self.base_url}/blog")
        if not soup:
            return []
        
        blog_posts = []
        
        # APE: ищем ссылки на статьи блога
        blog_links = soup.find_all('a', href=re.compile(r'/blog/.+'))
        
        # Убираем дубликаты и категории (минимум 4 слеша)
        unique_blogs = {}
        for link in blog_links:
            href = link.get('href')
            # Только полные статьи
            if href.count('/') > 3 and href not in unique_blogs:
                # Исключаем категории
                if 'category' not in href:
                    unique_blogs[href] = link
        
        print(f"  Найдено {len(unique_blogs)} статей блога")
        
        for idx, (href, link) in enumerate(list(unique_blogs.items())[:10], 1):
            print(f"  🔗 Обработка статьи {idx}/{min(10, len(unique_blogs))}")
            
            article_url = self.normalize_url(href)
            
            # Название
            title = link.get_text(strip=True)
            
            # Ищем изображение
            img = link.find('img')
            if not img and link.parent:
                img = link.parent.find('img')
            
            image_url = None
            local_image_path = None
            if img:
                image_url = self.normalize_url(img.get('src') or img.get('data-src', ''))
                if image_url:
                    local_image_path = self.download_image(image_url)
            
            if not title or len(title) < 3:
                print(f"  ⚠️  Статья без названия")
                continue
            
            blog_posts.append({
                'title': title[:150],
                'content': '',
                'full_content': '',
                'image_url': local_image_path or image_url,
                'source_url': article_url
            })
            
            print(f"  ✓ Статья {title[:50]} добавлена")
            
            # Задержка
            if idx < len(unique_blogs):
                time.sleep(0.3)
        
        return blog_posts


class LaFabbricaParser(BaseManufacturerParser):
    """Парсер для La Fabbrica / AVA"""
    
    def __init__(self):
        super().__init__('https://www.lafabbrica.it/de', 'lafabbrica')
    
    def extract_logo(self) -> Optional[str]:
        """Извлекает логотип La Fabbrica"""
        print(f"🔍 Поиск логотипа для {self.slug}...")
        
        soup = self.fetch_page(self.base_url)
        if not soup:
            return None
        
        # La Fabbrica: логотип с определенным паттерном
        img = soup.find('img', src=re.compile(r'(logo|Senza-titolo)', re.I))
        if img:
            logo_url = self.normalize_url(img.get('src'))
            if logo_url:
                return self.download_image(logo_url)
        
        print("  ⚠️  Логотип не найден")
        return None
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции La Fabbrica из разных категорий"""
        print("🔍 Парсинг коллекций La Fabbrica...")
        
        collections = []
        seen_urls = set()
        
        # Категории коллекций
        categories = [
            'marmor-effekt',
            'stein-effekt',
            'holz-effekt',
            'zement-effekt',
            'metall-effekt'
        ]
        
        # Собираем коллекции из всех категорий
        for category in categories:
            print(f"  📂 Категория: {category}")
            soup = self.fetch_page(f"{self.base_url}/kollektionen/{category}/")
            if not soup:
                continue
            
            # Ищем ссылки на коллекции, которые содержат изображения
            # На странице категории каждая коллекция имеет ссылку с изображением
            links = soup.find_all('a', href=re.compile(r'/de/collections/.+'))
            
            for link in links:
                href = link.get('href')
                if not href or href in seen_urls:
                    continue
                
                # Ищем изображение в этой ссылке или рядом с ней
                img = link.find('img')
                if not img and link.parent:
                    # Попытка найти изображение рядом с ссылкой
                    parent = link.parent
                    img = parent.find('img')
                
                if not img:
                    continue
                
                # Получаем URL изображения
                img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src', '')
                if not img_src or 'wp-content' not in img_src:
                    continue
                
                # Исключаем анимированные GIF и логотипы
                if any(x in img_src.lower() for x in ['.gif', 'logo', 'senza-titolo', 'icon', 'menu']):
                    continue
                
                seen_urls.add(href)
                
                # Название из URL или alt текста
                slug = href.rstrip('/').split('/')[-1]
                title = img.get('alt', '').strip() or slug.replace('-', ' ').title()
                
                # Нормализуем и скачиваем изображение
                image_url = self.normalize_url(img_src)
                local_image_path = None
                if image_url:
                    local_image_path = self.download_image(image_url)
                
                if local_image_path or image_url:
                    collections.append({
                        'title': title,
                        'description': f'Kollektion {title}',
                        'full_content': '',
                        'technical_specs': '',
                        'image_url': local_image_path or image_url,
                        'source_url': self.normalize_url(href)
                    })
                    
                    print(f"  ✓ Коллекция {title} добавлена")
                
                # Ограничение на количество коллекций
                if len(collections) >= 15:
                    break
            
            if len(collections) >= 15:
                break
            
            time.sleep(0.3)
        
        print(f"  📊 Итого: {len(collections)} коллекций")
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции"""
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        description = ""
        content_parts = []
        
        # Ищем основной контент
        main = soup.find(['main', 'article', 'div'], class_=lambda x: x and 'content' in str(x).lower())
        if main:
            for p in main.find_all('p', limit=5):
                text = p.get_text(strip=True)
                if len(text) > 50:
                    if not description:
                        description = text[:300]
                    content_parts.append(f"<p>{text}</p>")
        
        return {
            'description': description,
            'full_content': '\n'.join(content_parts),
            'technical_specs': ''
        }
    
    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты La Fabbrica"""
        print("🔍 Парсинг проектов La Fabbrica...")
        
        soup = self.fetch_page(f"{self.base_url}/projects")
        if not soup:
            return []
        
        projects = []
        
        # Ищем контейнеры с проектами
        containers = soup.find_all(['div', 'article'], class_=lambda x: x and 'post' in str(x).lower())
        
        # Ищем ссылки на проекты
        project_links = soup.find_all('a', href=re.compile(r'/de/projects/.+'))
        
        # Убираем дубликаты
        unique_projects = {}
        for link in project_links:
            href = link.get('href')
            # Только полные URL проектов (длиннее 40 символов)
            if len(href) > 40 and href not in unique_projects:
                unique_projects[href] = link
        
        print(f"  Найдено {len(unique_projects)} проектов")
        
        for idx, (href, link) in enumerate(list(unique_projects.items())[:10], 1):
            print(f"  🔗 Обработка проекта {idx}/{min(10, len(unique_projects))}")
            
            project_url = self.normalize_url(href)
            
            # Название из текста ссылки или из URL
            title = link.get_text(strip=True)
            if not title or len(title) < 3:
                # Название из URL
                slug = href.rstrip('/').split('/')[-1]
                title = slug.replace('-', ' ').title()
            
            # Ищем изображение
            img = link.find('img')
            if not img and link.parent:
                img = link.parent.find('img')
            
            image_url = None
            local_image_path = None
            if img:
                image_url = self.normalize_url(img.get('src') or img.get('data-src') or img.get('data-lazy-src', ''))
                if image_url and 'placeholder' not in image_url:
                    local_image_path = self.download_image(image_url)
            
            if not title or len(title) < 3:
                print(f"  ⚠️  Проект без названия")
                continue
            
            if not local_image_path and not image_url:
                print(f"  ⚠️  Проект {title} без изображения")
                continue
            
            projects.append({
                'title': title[:100],
                'description': '',
                'full_content': '',
                'technical_specs': '',
                'image_url': local_image_path or image_url,
                'source_url': project_url
            })
            
            print(f"  ✓ Проект {title[:50]} добавлен")
            
            time.sleep(0.5)
        
        return projects
    
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога La Fabbrica"""
        print("🔍 Парсинг блога La Fabbrica...")
        
        soup = self.fetch_page(f"{self.base_url}/blog")
        if not soup:
            return []
        
        blog_posts = []
        
        # Ищем ссылки на статьи
        blog_links = soup.find_all('a', href=re.compile(r'/de/blog/.+'))
        
        # Убираем дубликаты и категории
        unique_blogs = {}
        for link in blog_links:
            href = link.get('href')
            # Только статьи (длинные URL)
            if len(href) > 40 and 'category' not in href and href not in unique_blogs:
                unique_blogs[href] = link
        
        print(f"  Найдено {len(unique_blogs)} статей блога")
        
        for idx, (href, link) in enumerate(list(unique_blogs.items())[:10], 1):
            print(f"  🔗 Обработка статьи {idx}/{min(10, len(unique_blogs))}")
            
            article_url = self.normalize_url(href)
            
            # Название
            title = link.get_text(strip=True)
            if not title or len(title) < 3:
                slug = href.rstrip('/').split('/')[-1]
                title = slug.replace('-', ' ').title()
            
            # Изображение
            img = link.find('img')
            if not img and link.parent:
                img = link.parent.find('img')
            
            image_url = None
            local_image_path = None
            if img:
                image_url = self.normalize_url(img.get('src') or img.get('data-src') or img.get('data-lazy-src', ''))
                if image_url:
                    local_image_path = self.download_image(image_url)
            
            if not title or len(title) < 3:
                print(f"  ⚠️  Статья без названия")
                continue
            
            blog_posts.append({
                'title': title[:150],
                'content': '',
                'full_content': '',
                'image_url': local_image_path or image_url,
                'source_url': article_url
            })
            
            print(f"  ✓ Статья {title[:50]} добавлена")
            
            time.sleep(0.3)
        
        return blog_posts


class BaldocerParser(BaseManufacturerParser):
    """Парсер для Baldocer"""
    
    def __init__(self):
        super().__init__('https://baldocer.com', 'baldocer')
    
    def extract_logo(self) -> Optional[str]:
        """Извлекает логотип Baldocer"""
        print(f"🔍 Поиск логотипа для {self.slug}...")
        
        # Известный URL логотипа
        logo_url = f"{self.base_url}/wp-content/uploads/2018/06/logo.png"
        return self.download_image(logo_url)
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Baldocer (продуктовые линейки)"""
        print("🔍 Парсинг коллекций Baldocer...")
        
        collections = []
        
        soup = self.fetch_page(f"{self.base_url}/producto/")
        if not soup:
            return collections
        
        # Определенные категории продуктов Baldocer
        categories = [
            ('porcelanico', 'Pasta porcelánica'),
            ('pasta-blanca', 'Pasta blanca'),
            ('bplus', 'b|plus'),
            ('bthin', 'b|thin'),
            ('bout', 'b|&out')
        ]
        
        # Сначала ищем все изображения категорий на главной странице /producto/
        category_images = {}
        for img in soup.find_all('img'):
            parent_link = img.find_parent('a')
            if not parent_link:
                continue
            
            href = parent_link.get('href', '')
            src = img.get('src') or img.get('data-src')
            
            # Проверяем, ведет ли ссылка на одну из наших категорий
            for slug, name in categories:
                if f'/producto/{slug}/' in href and src and '/uploads/' in src:
                    # Пропускаем мелкие иконки
                    if any(skip in src.lower() for skip in ['logo', 'icon', 'flag', 'facebook', 'instagram', 'linkedin', 'pinterest', 'youtube', 'login']):
                        continue
                    
                    category_images[slug] = src
                    break
        
        print(f"  📸 Найдено изображений на главной странице: {len(category_images)}")
        
        # Теперь создаем коллекции с правильными изображениями
        for slug, name in categories:
            category_url = f"{self.base_url}/producto/{slug}/"
            
            print(f"  📂 Обработка категории: {name}")
            
            # Используем изображение с главной страницы
            image_url = None
            if slug in category_images:
                full_url = self.normalize_url(category_images[slug])
                image_url = self.download_image(full_url)
            
            collection_data = {
                'title': name,
                'url': category_url,
                'image_url': image_url,
                'description': f'Baldocer {name}'
            }
            
            collections.append(collection_data)
            print(f"    ✅ {name}: {'изображение найдено' if image_url else 'без изображения'}")
            
            time.sleep(0.2)
        
        print(f"  ✅ Найдено {len(collections)} коллекций")
        return collections
    
    def extract_collection_detail(self, collection_url: str) -> Optional[Dict]:
        """Извлекает детали коллекции Baldocer"""
        print(f"  🔎 Парсинг деталей коллекции: {collection_url}")
        
        soup = self.fetch_page(collection_url)
        if not soup:
            return None
        
        # Название коллекции
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else collection_url.rstrip('/').split('/')[-1]
        
        # Изображения
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and '/uploads/' in src:
                # Пропускаем логотипы, иконки
                if any(skip in src.lower() for skip in ['logo', 'icon', 'flag', 'facebook', 'instagram', 'linkedin', 'pinterest', 'youtube']):
                    continue
                
                full_url = self.normalize_url(src)
                image_path = self.download_image(full_url)
                if image_path:
                    images.append(image_path)
                    if len(images) >= 5:
                        break
        
        # Описание из мета-тегов
        description = ""
        meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        return {
            'title': title,
            'url': collection_url,
            'description': description,
            'images': images
        }
    
    def extract_projects(self) -> List[Dict]:
        """Baldocer не имеет раздела проектов"""
        print("  ℹ️  Baldocer не имеет раздела проектов")
        return []
    
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога Baldocer"""
        print("🔍 Парсинг блога Baldocer...")
        
        blog_posts = []
        
        soup = self.fetch_page(f"{self.base_url}/noticias/")
        if not soup:
            return blog_posts
        
        # Ищем статьи
        articles = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'post|article|news', re.I))
        
        for article in articles[:10]:
            # Ищем ссылку на статью
            link = article.find('a', href=True)
            if not link:
                continue
            
            href = link.get('href')
            if not href or '/noticias/' not in href:
                continue
            
            # Название
            title_tag = article.find(['h1', 'h2', 'h3', 'h4'])
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)
            
            if not title or len(title) < 3:
                continue
            
            # Изображение
            img = article.find('img')
            image_url = None
            if img:
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = self.normalize_url(src)
                    image_url = self.download_image(full_url)
            
            blog_posts.append({
                'title': title,
                'url': self.normalize_url(href),
                'image_url': image_url,
                'excerpt': ''
            })
        
        print(f"  ✅ Найдено {len(blog_posts)} статей")
        return blog_posts


class CasalgrandeParser(BaseManufacturerParser):
    """Парсер для Casalgrande Padana"""

    def __init__(self):
        super().__init__('https://www.casalgrandepadana.com', 'casalgrande')

    def extract_logo(self) -> Optional[str]:
        """Пытаемся найти логотип на главной странице"""
        print(f"🔍 Поиск логотипа для {self.slug}...")
        soup = self.fetch_page(self.base_url)
        if not soup:
            return None
        # 1) Поиск по <img> с alt/class/src содержащим 'logo'
        img = soup.find('img', {'alt': re.compile(r'logo', re.I)}) or soup.find('img', class_=re.compile(r'logo', re.I)) or soup.find('img', src=re.compile(r'logo', re.I))
        if img:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy')
            if src and not src.startswith('data:'):
                return self.download_image(self.normalize_url(src))

        # 2) Meta og:image / twitter:image
        meta_og = soup.find('meta', property=re.compile(r'og:image', re.I)) or soup.find('meta', attrs={'name': re.compile(r'twitter:image', re.I)})
        if meta_og and meta_og.get('content'):
            og = meta_og.get('content')
            if og and not og.startswith('data:'):
                return self.download_image(self.normalize_url(og))

        # 3) link rel icons (favicon / apple-touch-icon)
        link_icon = soup.find('link', rel=re.compile(r'icon', re.I))
        if link_icon and link_icon.get('href'):
            href = link_icon.get('href')
            if href and not href.startswith('data:'):
                path = self.download_image(self.normalize_url(href))
                if path:
                    return path

        # 4) Попытка сохранить inline <svg> как файл
        svg = soup.find('svg', class_=re.compile(r'logo', re.I)) or soup.find('svg', id=re.compile(r'logo', re.I))
        if svg:
            try:
                svg_str = str(svg)
                # сохранение svg в uploads
                url_hash = hashlib.md5(svg_str.encode()).hexdigest()[:10]
                filename = f"{self.slug}_logo_{url_hash}.svg"
                upload_dir = os.path.join('app', 'static', 'uploads', 'manufacturers')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(svg_str)
                print(f"  ✓ Сохранён inline SVG как {filename}")
                return f'manufacturers/{filename}'
            except Exception as e:
                print(f"  ❌ Ошибка сохранения inline SVG: {e}")

        # 5) Широкий поиск: первый логотип-похожий <img> в header/nav или с небольшим размером
        header = soup.find(['header', 'nav'])
        candidates = []
        if header:
            candidates = header.find_all('img')
        if not candidates:
            candidates = soup.find_all('img', src=True)[:20]

        for img in candidates:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy')
            if not src or src.startswith('data:'):
                continue
            # пропускаем явные продуктовые изображения (media с длинными путями), но позволим логотипы
            lowered = src.lower()
            if 'logo' in lowered or 'favicon' in lowered or 'brand' in lowered or 'casalgrandepadana' in lowered:
                path = self.download_image(self.normalize_url(src))
                if path:
                    return path

        print("  ⚠️  Логотип не найден автоматически")
        return None

    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции/продукты через sitemap-prodotti.xml"""
        print("🔍 Парсинг коллекций Casalgrande через sitemap...")
        collections = []

        sitemap_url = f"{self.base_url}/sitemap-prodotti.xml"
        try:
            r = requests.get(sitemap_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200:
                print(f"  ⚠️  Sitemap недоступен: {sitemap_url} -> {r.status_code}")
                return collections

            soup = BeautifulSoup(r.content, 'xml')
            urls = soup.find_all('url')
            print(f"  В sitemap найдено записей: {len(urls)}")

            for url_tag in urls:
                loc = url_tag.find('loc')
                if not loc:
                    continue
                page_url = loc.get_text(strip=True)

                # Только product pages (/product/slug)
                if '/product/' not in page_url:
                    continue

                title = page_url.rstrip('/').split('/')[-1].replace('-', ' ').title()
                image_tag = url_tag.find('image:loc') or url_tag.find('image')
                image_url = None
                if image_tag:
                    img = image_tag.get_text(strip=True)
                    if img:
                        image_url = self.download_image(self.normalize_url(img))

                collections.append({
                    'title': title,
                    'url': page_url,
                    'image_url': image_url,
                    'description': ''
                })

                if len(collections) >= 200:
                    break

        except Exception as e:
            print(f"  Ошибка при чтении sitemap: {e}")

        print(f"  ✅ Найдено коллекций: {len(collections)}")
        return collections

    def extract_collection_detail(self, collection_url: str) -> Optional[Dict]:
        print(f"  🔎 Парсинг деталей коллекции: {collection_url}")
        soup = self.fetch_page(collection_url)
        if not soup:
            return None

        title_tag = soup.find(['h1', 'h2'])
        title = title_tag.get_text(strip=True) if title_tag else collection_url.rstrip('/').split('/')[-1]

        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and 'media' in src or 'filer_public' in src:
                path = self.download_image(self.normalize_url(src))
                if path:
                    images.append(path)
            if len(images) >= 8:
                break

        desc = ''
        meta = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
        if meta:
            desc = meta.get('content', '')

        return {
            'title': title,
            'url': collection_url,
            'description': desc,
            'images': images
        }

    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты через sitemap-realizzazioni.xml"""
        print("🔍 Парсинг проектов Casalgrande через sitemap...")
        projects = []
        sitemap = f"{self.base_url}/sitemap-realizzazioni.xml"
        try:
            r = requests.get(sitemap, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200:
                return projects
            soup = BeautifulSoup(r.content, 'xml')
            for url_tag in soup.find_all('url')[:100]:
                loc = url_tag.find('loc')
                if not loc:
                    continue
                page_url = loc.get_text(strip=True)
                title = page_url.rstrip('/').split('/')[-1].replace('-', ' ').title()
                # try to find image
                image_tag = url_tag.find('image:loc') or url_tag.find('image')
                image = None
                if image_tag:
                    image = self.download_image(self.normalize_url(image_tag.get_text(strip=True)))
                projects.append({'title': title, 'url': page_url, 'image_url': image, 'description': ''})
        except Exception as e:
            print('  Error reading projects sitemap:', e)
        print(f"  ✅ Найдено проектов: {len(projects)}")
        return projects

    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает новости через sitemap-news.xml"""
        print("🔍 Парсинг новостей Casalgrande через sitemap...")
        posts = []
        sitemap = f"{self.base_url}/sitemap-news.xml"
        try:
            r = requests.get(sitemap, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200:
                return posts
            soup = BeautifulSoup(r.content, 'xml')
            for url_tag in soup.find_all('url')[:100]:
                loc = url_tag.find('loc')
                if not loc:
                    continue
                page_url = loc.get_text(strip=True)
                title = page_url.rstrip('/').split('/')[-1].replace('-', ' ').title()
                posts.append({'title': title, 'url': page_url, 'image_url': None, 'excerpt': ''})
        except Exception as e:
            print('  Error reading news sitemap:', e)
        print(f"  ✅ Найдено статей: {len(posts)}")
        return posts


class DistrimatParser(BaseManufacturerParser):
    """Парсер для Distrimat (https://www.distrimat.es/en)"""

    def __init__(self):
        super().__init__('https://www.distrimat.es/en', 'distrimat')

    def extract_logo(self) -> Optional[str]:
        print(f"🔍 Поиск логотипа для {self.slug}...")
        soup = self.fetch_page(self.base_url)
        if not soup:
            return None

        # Ищем явный логотип по имени файла или по alt
        img = soup.find('img', alt=re.compile(r'logotipo|logo', re.I))
        if not img:
            img = soup.find('img', src=re.compile(r'distrimat', re.I))
        if img:
            src = img.get('src') or img.get('data-src')
            if src and not src.startswith('data:'):
                return self.download_image(self.normalize_url(src))

        # Фоллбек: og:image
        meta = soup.find('meta', property=re.compile(r'og:image', re.I))
        if meta and meta.get('content'):
            return self.download_image(self.normalize_url(meta.get('content')))

        print('  ⚠️  Логотип не найден автоматически')
        return None

    def extract_collections(self) -> List[Dict]:
        """Парсинг серий/коллекций через страницу категории Ceramics"""
        print("🔍 Парсинг коллекций Distrimat...")
        collections = []

        category_path = '/categoria-producto/ceramics-en/'
        soup = self.fetch_page(f"{self.base_url}{category_path}")
        if not soup:
            return collections

        # Ищем ссылки на подкатегории/серии
        links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href and '/categoria-producto/' in href and href.rstrip('/') != f"{self.base_url}{category_path.rstrip('/')}":
                links.append(a)

        # Уникализируем по href
        seen = set()
        filtered = []
        for a in links:
            href = a.get('href')
            if href and href not in seen:
                seen.add(href)
                filtered.append(a)

        print(f"  Найдено потенциальных серий: {len(filtered)}")

        for idx, a in enumerate(filtered[:200], 1):
            href = a.get('href')
            title = a.get_text(strip=True) or href.rstrip('/').split('/')[-1].replace('-', ' ').title()
            image_url = None
            img = a.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src:
                    image_url = self.download_image(self.normalize_url(src))

            collections.append({'title': title, 'description': '', 'image_url': image_url, 'source_url': href})

            if idx < len(filtered[:200]):
                time.sleep(0.2)

        print(f"  ✅ Найдено коллекций: {len(collections)}")
        return collections

    def extract_collection_detail(self, url: str) -> Optional[Dict]:
        print(f"  🔎 Парсинг деталей коллекции: {url}")
        soup = self.fetch_page(url)
        if not soup:
            return None

        title_tag = soup.find(['h1', 'h2'])
        title = title_tag.get_text(strip=True) if title_tag else url.rstrip('/').split('/')[-1]

        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and ('wp-content' in src or 'uploads' in src):
                p = self.download_image(self.normalize_url(src))
                if p:
                    images.append(p)
            if len(images) >= 8:
                break

        desc = ''
        meta = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
        if meta:
            desc = meta.get('content', '')

        return {'title': title, 'url': url, 'description': desc, 'images': images}

    def extract_projects(self) -> List[Dict]:
        return []

    def extract_blog_posts(self) -> List[Dict]:
        return []


class EstudiCeremicoParser(BaseManufacturerParser):
    """Парсер для Estudi Ceramico"""
    
    def __init__(self):
        super().__init__('https://eceramico.com', 'estudi-ceramico')
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Estudi Ceramico"""
        print("🔍 Парсинг коллекций Estudi Ceramico...")
        
        soup = self.fetch_page(f"{self.base_url}/en/collections/")
        if not soup:
            return []
        
        collections = []
        seen = set()
        
        # Ищем ссылки на серии (formato: /serie/{slug}/)
        links = soup.find_all('a', href=re.compile(r'/serie/'))
        
        for link in links:
            href = link.get('href')
            if not href:
                continue
            
            full_url = self.normalize_url(href)
            if full_url in seen:
                continue
            seen.add(full_url)
            
            # Заголовок
            title = link.get_text(strip=True)
            if not title or len(title) < 2:
                continue
            
            print(f"  🔗 Коллекция: {title}")
            
            # Извлекаем детали со страницы коллекции
            detail = self.extract_collection_detail(full_url) or {}
            
            # Предпочитаем изображение со страницы деталей
            chosen_image = None
            detail_images = detail.get('images') or []
            if detail_images:
                chosen_image = detail_images[0]
            
            collections.append({
                'title': title,
                'description': detail.get('description', ''),
                'full_content': detail.get('full_content', ''),
                'technical_specs': detail.get('technical_specs', ''),
                'image_url': chosen_image,
                'source_url': full_url
            })
            
            time.sleep(0.2)
        
        print(f"  ✅ Найдено коллекций: {len(collections)}")
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции Estudi Ceramico"""
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        description = ""
        content_parts = []
        images = []
        
        # Заголовок
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        else:
            title = url.rstrip('/').split('/')[-1].title()
        
        # Описание
        desc_elem = soup.find('div', class_=lambda x: x and any(k in str(x).lower() for k in ['content', 'description', 'intro']))
        if desc_elem:
            description = desc_elem.get_text(strip=True)[:300]
        
        # Сбор изображений (исключаем логотипы и навигацию)
        candidates = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not src or src.startswith('data:'):
                continue
            
            norm = self.normalize_url(src)
            low = norm.lower()
            
            # Пропускаем логотипы, флаги и иконки
            if any(k in low for k in ['logo', 'flag', 'icon', 'svg', 'loader']):
                continue
            
            # Пропускаем очень маленькие изображения (обычно иконки)
            if '/res/' in low or '/flags/' in low or '/assets/' in low:
                continue
            
            candidates.append(norm)
        
        # Дедупликация
        seen = set()
        unique = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                unique.append(c)
        
        # Загружаем до 8 изображений
        for src in unique:
            p = self.download_image(src)
            if p:
                images.append(p)
            if len(images) >= 8:
                break
        
        return {
            'title': title,
            'description': description,
            'full_content': '\n'.join(content_parts),
            'technical_specs': '',
            'images': images
        }
    
    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты Estudi Ceramico"""
        print("🔍 Парсинг проектов Estudi Ceramico...")
        
        soup = self.fetch_page(f"{self.base_url}/en/projects/")
        if not soup:
            return []
        
        projects = []
        seen = set()
        
        # Ищем ссылки на проекты в странице
        links = soup.find_all('a', href=lambda x: x and '/projects/' in x and x != f"{self.base_url}/en/projects/")
        
        for link in links:
            href = link.get('href')
            if not href:
                continue
            
            full_url = self.normalize_url(href)
            if full_url in seen:
                continue
            seen.add(full_url)
            
            title = link.get_text(strip=True)
            if not title or len(title) < 2:
                continue
            
            # Ищем изображение рядом с ссылкой
            img = link.find('img')
            if not img:
                parent = link.find_parent(['div', 'article', 'figure'])
                if parent:
                    img = parent.find('img')
            
            image = None
            if img:
                src = img.get('src') or img.get('data-src')
                if src and not src.startswith('data:'):
                    image = self.download_image(self.normalize_url(src))
            
            if not image:
                continue  # Пропускаем проекты без изображений
            
            projects.append({
                'title': title,
                'description': '',
                'full_content': '',
                'image_url': image,
                'source_url': full_url
            })
            
            time.sleep(0.2)
        
        print(f"  ✅ Найдено проектов: {len(projects)}")
        return projects
    
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога Estudi Ceramico"""
        print("🔍 Парсинг блога Estudi Ceramico...")
        
        # Проверяем оба варианта URL (с /en/ и без)
        candidates = [f"{self.base_url}/en/blog/", f"{self.base_url}/blog/"]
        soup = None
        blog_url = None
        
        for c in candidates:
            soup = self.fetch_page(c)
            if soup:
                blog_url = c
                break
        
        if not soup:
            return []
        
        posts = []
        seen = set()
        
        # Ищем ссылки на статьи блога
        links = soup.find_all('a', href=lambda x: x and '/blog/' in x)
        
        for link in links:
            href = link.get('href')
            if not href or href == blog_url:
                continue
            
            full_url = self.normalize_url(href)
            if full_url in seen:
                continue
            seen.add(full_url)
            
            title = link.get_text(strip=True)
            if not title or len(title) < 3:
                continue
            
            # Ищем изображение (если есть)
            img = link.find('img')
            if not img:
                parent = link.find_parent(['div', 'article', 'figure'])
                if parent:
                    img = parent.find('img')
            
            image = None
            if img:
                src = img.get('src') or img.get('data-src')
                if src and not src.startswith('data:') and 'logo' not in src.lower():
                    image = self.download_image(self.normalize_url(src))
            
            # Для блога изображение необязательно
            posts.append({
                'title': title,
                'excerpt': '',
                'full_content': '',
                'image_url': image,
                'url': full_url
            })
            
            time.sleep(0.1)
        
        print(f"  ✅ Найдено статей: {len(posts)}")
        return posts

class EtileParser(BaseManufacturerParser):
    """Парсер для Etile Ceramics"""
    
    def __init__(self):
        super().__init__('https://en.etile.es', 'etile')
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Etile Ceramics"""
        print("🔍 Парсинг коллекций Etile Ceramics...")
        
        soup = self.fetch_page(f"{self.base_url}/etile/")
        if not soup:
            return []
        
        collections = []
        
        # Ищем элементы коллекций (используют jQuery gridder)
        gridder_items = soup.find_all('li', class_='gridder-list')
        
        for item in gridder_items:
            # Получаем slug из id
            item_id = item.get('id', '')
            if not item_id.startswith('collection-'):
                continue
            
            slug = item_id.replace('collection-', '')
            
            # Получаем ссылку на содержимое
            content_ref = item.get('data-griddercontent', '')
            if not content_ref:
                continue
            
            print(f"  🔗 Коллекция: {slug}")
            
            # Ищем соответствующий раздел содержимого
            content_id = content_ref.lstrip('#')
            content_elem = soup.find(id=content_id)
            
            images = []
            description = ""
            
            if content_elem:
                # Ищем все изображения и выбираем первое, которое больше 5KB
                all_imgs = content_elem.find_all('img')
                
                for img in all_imgs:
                    img_src = img.get('src', '')
                    img_alt = img.get('alt', '')
                    
                    # Пропускаем маленькие иконки (обычно < 1KB)
                    if not img_src or 'icon' in img_alt.lower() or 'logo' in img_alt.lower():
                        continue
                    
                    img_path = self.download_image(img_src)
                    if img_path:
                        images.append(img_path)
                        # Берём только одно изображение (первое правильное)
                        break
                
                # Пытаемся получить описание
                text_elem = content_elem.find('p') or content_elem.find('div', class_='description')
                if text_elem:
                    description = text_elem.get_text(strip=True)[:300]
            
            # Добавляем коллекцию все равно, даже без изображения
            collections.append({
                'title': slug.replace('-', ' ').title(),
                'description': description,
                'full_content': '',
                'technical_specs': '',
                'image_url': images[0] if images else None,
                'source_url': f"{self.base_url}/etile/#{slug}"
            })
            
            time.sleep(0.1)
        
        print(f"  ✅ Найдено коллекций: {len(collections)}")
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции (для Etile не требуется)"""
        return {}
    
    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты Etile Ceramics"""
        print("🔍 Парсинг проектов Etile Ceramics...")
        # На сайте Etile нет отдельной страницы проектов
        print("  ℹ️  Проекты не найдены")
        return []
    
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога Etile Ceramics"""
        print("🔍 Парсинг блога Etile Ceramics...")
        # На сайте Etile нет отдельного блога
        print("  ℹ️  Блог не найден")
        return []


class ExagresParser(BaseManufacturerParser):
    """Парсер для Exagres Ceramics"""
    
    def __init__(self):
        super().__init__('https://www.exagres.es', 'exagres')
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Exagres Ceramics"""
        print("🔍 Парсинг коллекций Exagres Ceramics...")
        
        # Извлекаем ссылки на коллекции со страницы категорий
        soup = self.fetch_page(f"{self.base_url}/colecciones-residencial/")
        if not soup:
            return []
        
        collections = []
        
        # Ищем ссылки на коллекции
        all_links = soup.find_all('a', href=True)
        
        # Фильтруем ссылки по ключевым словам коллекций
        collection_keywords = ['gresan', 'pavim', 'piscina', 'torelo', 'fachada', 'suelo', 'vierteagua', 'pasamano', 'deck']
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Проверяем, является ли это ссылкой на коллекцию
            if not href or len(text) < 3:
                continue
            
            if not any(keyword in href.lower() for keyword in collection_keywords):
                continue
            
            # Пропускаем уже добавленные коллекции
            if any(c['source_url'] == href for c in collections):
                continue
            
            print(f"  🔗 Коллекция: {text}")
            
            # Пытаемся получить изображение и описание со страницы коллекции
            image_url = None
            description = ""
            
            # Посещаем страницу коллекции
            collection_soup = self.fetch_page(href)
            if collection_soup:
                # Ищем изображение в main контенте (не в header/footer)
                # Ищем в больших контейнерах, где обычно лежит основное изображение
                
                image_candidates = []
                
                # 1. Ищем в <picture>, которая обычно содержит основное изображение
                picture_tags = collection_soup.find_all('picture')
                for picture in picture_tags:
                    img = picture.find('img')
                    if img:
                        src = img.get('src', '')
                        if src and 'icon' not in src.lower() and 'logo' not in src.lower():
                            image_candidates.append(src)
                
                # 2. Ищем изображения в больших контейнерах (hero, main, content)
                main_containers = collection_soup.find_all(['div', 'section'], class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in ['hero', 'main', 'content', 'featured', 'collection', 'banner']
                ))
                
                for container in main_containers:
                    imgs = container.find_all('img')
                    for img in imgs:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        
                        # Пропускаем иконки, логотипы, и явно маленькие изображения
                        if not src or 'icon' in alt.lower() or 'logo' in alt.lower():
                            continue
                        
                        # Предпочитаем изображения, которые выглядят как контент (по alt тексту)
                        if alt and len(alt) > 3:
                            image_candidates.insert(0, src)  # Приоритет
                        else:
                            image_candidates.append(src)
                
                # 3. Если контейнеров не нашли, ищем все img кроме явно маленьких
                if not image_candidates:
                    img_tags = collection_soup.find_all('img')
                    for img in img_tags:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        width = img.get('width', '')
                        height = img.get('height', '')
                        
                        if not src or 'icon' in alt.lower() or 'logo' in alt.lower():
                            continue
                        
                        # Пропускаем явно маленькие изображения (иконки)
                        if width and int(str(width).replace('px', '')) < 200:
                            continue
                        if height and int(str(height).replace('px', '')) < 200:
                            continue
                        
                        image_candidates.append(src)
                
                # Скачиваем лучший кандидат
                for candidate in image_candidates:
                    if not candidate:
                        continue
                    img_path = self.download_image(candidate)
                    if img_path:
                        image_url = img_path
                        break
                
                # Пытаемся получить описание
                desc_elem = collection_soup.find('p') or collection_soup.find('div', class_=lambda x: x and 'description' in x.lower())
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:300]
            
            # Добавляем коллекцию
            collections.append({
                'title': text,
                'description': description,
                'full_content': '',
                'technical_specs': '',
                'image_url': image_url,
                'source_url': href
            })
            
            time.sleep(0.2)  # Небольшая задержка между запросами
        
        print(f"  ✅ Найдено коллекций: {len(collections)}")
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции"""
        return {}
    
    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты Exagres Ceramics"""
        print("🔍 Парсинг проектов Exagres Ceramics...")
        # На сайте Exagres нет отдельной страницы проектов
        print("  ℹ️  Проекты не найдены")
        return []
    
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога Exagres Ceramics"""
        print("🔍 Парсинг блога Exagres Ceramics...")
        
        blog_posts = []
        soup = self.fetch_page(f"{self.base_url}/blog/")
        if not soup:
            print("  ℹ️  Блог не найден")
            return []
        
        # Ищем ссылки на статьи блога
        blog_links = soup.find_all('a', href=lambda x: x and '/blog/' in x and len(x) > 10)
        
        for link in blog_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Проверяем, что это ссылка на отдельную статью
            if not href or len(text) < 5 or href.endswith('/blog/') or 'http' not in href and self.base_url not in href:
                continue
            
            # Пропускаем уже добавленные
            if any(p['source_url'] == href for p in blog_posts):
                continue
            
            print(f"  📝 Статья: {text[:60]}")
            
            # Пытаемся получить изображение и описание
            description = ""
            images = []
            
            post_soup = self.fetch_page(href)
            if post_soup:
                # Получаем описание (первый абзац)
                p_tag = post_soup.find('p')
                if p_tag:
                    description = p_tag.get_text(strip=True)[:300]
                
                # Получаем первое изображение
                img = post_soup.find('img')
                if img:
                    src = img.get('src', '')
                    img_path = self.download_image(src)
                    if img_path:
                        images.append(img_path)
            
            blog_posts.append({
                'title': text,
                'description': description,
                'full_content': '',
                'image_url': images[0] if images else None,
                'source_url': href,
                'published': True
            })
            
            time.sleep(0.1)
        
        print(f"  ✅ Найдено статей: {len(blog_posts)}")
        return blog_posts


class HalconParser(BaseManufacturerParser):
    """Парсер для Halcon Ceramicas"""
    
    def __init__(self):
        super().__init__('https://www.halconceramicas.com', 'halcon')
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Halcon Ceramicas"""
        print("🔍 Парсинг коллекций Halcon Ceramicas...")
        
        soup = self.fetch_page(f"{self.base_url}/colecciones")
        if not soup:
            return []
        
        collections = []
        
        # Ищем все ссылки на коллекции
        for link in soup.find_all('a', href=lambda x: x and '/colecciones/' in x):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if not href or len(text) < 2:
                continue
            
            # Нормализуем URL
            if not href.startswith('http'):
                href = urljoin(self.base_url, href)
            
            # Пропускаем уже добавленные
            if any(c['source_url'] == href for c in collections):
                continue
            
            print(f"  🔗 Коллекция: {text}")
            
            images = []
            description = ""
            
            # Посещаем страницу коллекции
            collection_soup = self.fetch_page(href)
            if collection_soup:
                # Извлекаем название коллекции из URL для поиска уникальных изображений
                # Например: "coleccion-capri" -> "capri"
                url_parts = href.rstrip('/').split('/')
                collection_slug = url_parts[-1] if url_parts else text.lower()
                
                # Убираем префиксы типа "coleccion-", "dolomite-" и т.д.
                if '-' in collection_slug:
                    # Берём последнюю значащую часть после удаления "coleccion-"
                    parts = collection_slug.replace('coleccion-', '').split('-')
                    # Объединяем первые 2 части (например "coleccion-grand-canyon" -> "grand-canyon")
                    collection_slug = '-'.join(parts[:2]) if len(parts) > 1 else parts[0]
                
                # Ищем все изображения
                img_tags = collection_soup.find_all('img')
                
                # Фильтруем и выбираем подходящее изображение
                collection_images = []  # Изображения с названием коллекции
                fallback_images = []    # Другие изображения из /storage/
                
                for img in img_tags:
                    src = img.get('src', '')
                    
                    if not src:
                        continue
                    
                    src_lower = src.lower()
                    
                    # Пропускаем явные логотипы, иконки и социальные медиа
                    if any(word in src_lower for word in 
                           ['logo', 'icon', 'instagram', 'facebook', 'twitter', 'linkedin', 
                            'pixel', 'tracking', 'svg', '1x1', 'white-pixel']):
                        continue
                    
                    # Используем изображения из хранилища
                    if '/storage/' in src_lower:
                        # Пропускаем явно маленькие изображения (thumbnails и PNG)
                        if 'thumb' not in src_lower and '.png' not in src_lower:
                            # Проверяем, содержит ли изображение название коллекции
                            if collection_slug in src_lower:
                                collection_images.append(src)
                            else:
                                fallback_images.append(src)
                
                # Выбираем изображение: сначала пытаемся найти с названием коллекции
                img_to_download = None
                
                # Сначала ищем medium качество в коллекции
                for img_src in collection_images:
                    if 'medium' in img_src.lower():
                        img_to_download = img_src
                        break
                
                # Если нет medium, ищем любое другое с названием коллекции
                if not img_to_download and collection_images:
                    img_to_download = collection_images[0]
                
                # В крайнем случае используем fallback (но предпочитаем не использовать)
                # if not img_to_download and fallback_images:
                #     img_to_download = fallback_images[0]
                
                if img_to_download:
                    img_path = self.download_image(img_to_download)
                    if img_path:
                        images.append(img_path)
                
                # Получаем описание
                paras = collection_soup.find_all('p')
                for p in paras:
                    text_content = p.get_text(strip=True)
                    if len(text_content) > 20 and 'javascript' not in text_content.lower():
                        description = text_content[:300]
                        break
            
            collections.append({
                'title': text,
                'description': description,
                'full_content': '',
                'technical_specs': '',
                'image_url': images[0] if images else None,
                'source_url': href
            })
            
            time.sleep(0.15)
        
        print(f"  ✅ Найдено коллекций: {len(collections)}")
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции"""
        return {}
    
    def extract_projects(self) -> List[Dict]:
        """Извлекает проекты Halcon Ceramicas"""
        print("🔍 Парсинг проектов Halcon Ceramicas...")
        
        # На сайте проекты находятся в категории PROYECTOS блога
        projects = []
        soup = self.fetch_page(f"{self.base_url}/blog/proyectos")
        
        if not soup:
            print("  ℹ️  Проекты не найдены")
            return []
        
        # Ищем ссылки на проекты
        for link in soup.find_all('a', href=lambda x: x and '/blog/' in x):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if not href or len(text) < 5 or href.endswith('/blog/proyectos'):
                continue
            
            if not href.startswith('http'):
                href = urljoin(self.base_url, href)
            
            if any(p['source_url'] == href for p in projects):
                continue
            
            print(f"  📐 Проект: {text[:50]}")
            
            images = []
            description = ""
            
            project_soup = self.fetch_page(href)
            if project_soup:
                img = project_soup.find('img')
                if img:
                    src = img.get('src', '')
                    img_path = self.download_image(src)
                    if img_path:
                        images.append(img_path)
                
                p_tag = project_soup.find('p')
                if p_tag:
                    description = p_tag.get_text(strip=True)[:300]
            
            projects.append({
                'title': text,
                'description': description,
                'image_url': images[0] if images else None,
                'source_url': href
            })
            
            time.sleep(0.1)
        
        print(f"  ✅ Найдено проектов: {len(projects)}")
        return projects
    
    def extract_blog_posts(self) -> List[Dict]:
        """Извлекает статьи блога Halcon Ceramicas"""
        print("🔍 Парсинг блога Halcon Ceramicas...")
        
        blog_posts = []
        soup = self.fetch_page(f"{self.base_url}/blog")
        
        if not soup:
            print("  ℹ️  Блог не найден")
            return []
        
        # Ищем все посты блога
        for link in soup.find_all('a', href=lambda x: x and '/blog/' in x):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Пропускаем категории и короткие тексты
            if not href or len(text) < 5 or href.endswith('/blog') or href.endswith('/blog/'):
                continue
            
            # Пропускаем категории (ferias, novedades, proyectos, нoticias)
            if '/blog/ferias' in href or '/blog/novedades' in href or '/blog/proyectos' in href or '/blog/noticias' in href:
                continue
            
            if not href.startswith('http'):
                href = urljoin(self.base_url, href)
            
            if any(b['source_url'] == href for b in blog_posts):
                continue
            
            print(f"  📝 Статья: {text[:50]}")
            
            images = []
            description = ""
            
            post_soup = self.fetch_page(href)
            if post_soup:
                img = post_soup.find('img')
                if img:
                    src = img.get('src', '')
                    img_path = self.download_image(src)
                    if img_path:
                        images.append(img_path)
                
                p_tag = post_soup.find('p')
                if p_tag:
                    description = p_tag.get_text(strip=True)[:300]
            
            blog_posts.append({
                'title': text,
                'description': description,
                'image_url': images[0] if images else None,
                'source_url': href,
                'published': True
            })
            
            time.sleep(0.1)
        
        print(f"  ✅ Найдено статей: {len(blog_posts)}")
        return blog_posts


class RocedParser(BaseManufacturerParser):
    """Парсер для Roced (Испания)"""
    
    def __init__(self):
        super().__init__('https://roced.es', 'roced')
    
    def extract_collections(self) -> List[Dict]:
        """Извлекает коллекции Roced"""
        print("🔍 Парсинг коллекций Roced...")
        soup = self.fetch_page(f"{self.base_url}/productos/")
        if not soup:
            return []
        
        collections = []
        
        for link in soup.find_all('a', href=lambda x: x and '/ceramica/' in x):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if not href or len(text) < 2:
                continue
            if not href.startswith('http'):
                href = urljoin(self.base_url, href)
            if any(c['source_url'] == href for c in collections):
                continue
            
            print(f"  🔗 Коллекция: {text}")
            images = []
            description = ""
            
            collection_soup = self.fetch_page(href)
            if collection_soup:
                img_tags = collection_soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    if src and 'logo' not in src.lower():
                        img_path = self.download_image(src)
                        if img_path:
                            images.append(img_path)
                            break
                paras = collection_soup.find_all('p')
                for p in paras:
                    text_content = p.get_text(strip=True)
                    if len(text_content) > 20:
                        description = text_content[:300]
                        break
            
            collections.append({
                'title': text,
                'description': description,
                'full_content': '',
                'technical_specs': '',
                'image_url': images[0] if images else None,
                'source_url': href
            })
        
        return collections
    
    def extract_collection_detail(self, url: str) -> Dict:
        """Извлекает детали коллекции"""
        return {'description': ''}
    
    def extract_projects(self) -> List[Dict]:
        return []
    
    def extract_blog_posts(self) -> List[Dict]:
        print("🔍 Парсинг блога Roced...")
        soup = self.fetch_page(f"{self.base_url}/blog/")
        if not soup:
            return []
        blog_posts = []
        for link in soup.find_all('a', href=lambda x: x and '/blog/' in x):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if not href or len(text) < 3 or href.endswith('/blog/'):
                continue
            if not href.startswith('http'):
                href = urljoin(self.base_url, href)
            if any(p['source_url'] == href for p in blog_posts):
                continue
            print(f"  📝 Статья: {text}")
            blog_posts.append({'title': text, 'description': '', 'full_content': '', 'image_url': None, 'source_url': href})
        return blog_posts


class TuscaniParser(BaseManufacturerParser):
    """Парсер для Tuscania (Италия)"""
    def __init__(self):
        super().__init__('https://tuscaniagres.it', 'tuscania')
    def extract_collections(self) -> List[Dict]:
        print("🔍 Парсинг коллекций Tuscania...")
        soup = self.fetch_page(f"{self.base_url}/piastrelle/")
        if not soup:
            return []
        collections = []
        seen_urls = set()
        for link in soup.find_all('a', href=lambda x: x and '/collezioni/' in x):
            href = link.get('href', '').rstrip('/')
            if not href or href in seen_urls or '/collezioni/' not in href:
                continue
            # Skip the main /collezioni/ link
            if href.endswith('/collezioni'):
                continue
            if not href.startswith('http'):
                href = urljoin(self.base_url, href)
            seen_urls.add(href)
            
            # Extract collection name from URL
            coll_name = href.rstrip('/').split('/')[-1]
            if not coll_name or len(coll_name) < 2:
                continue
            
            print(f"  🔗 Коллекция: {coll_name}")
            images = []
            collection_soup = self.fetch_page(href)
            if collection_soup:
                img_tags = collection_soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    if src and 'logo' not in src.lower():
                        img_path = self.download_image(src)
                        if img_path:
                            images.append(img_path)
                            break
            collections.append({'title': coll_name, 'description': '', 'full_content': '', 'technical_specs': '', 'image_url': images[0] if images else None, 'source_url': href})
        return collections
    def extract_collection_detail(self, url: str) -> Dict:
        return {'description': ''}
    def extract_projects(self) -> List[Dict]:
        return []
    def extract_blog_posts(self) -> List[Dict]:
        return []


class UnicomStarkerParser(BaseManufacturerParser):
    """Парсер для Unicom Starker (Италия)"""
    def __init__(self):
        super().__init__('https://www.unicomstarker.com', 'unicom-starker')
    def extract_collections(self) -> List[Dict]:
        print("🔍 Парсинг коллекций Unicom Starker...")
        soup = self.fetch_page(f"{self.base_url}/home")
        if not soup:
            return []
        collections = []
        for link in soup.find_all('a', href=lambda x: x and ('/products' in (x or '').lower() or '/collection' in (x or '').lower())):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if not href or len(text) < 2:
                continue
            if not href.startswith('http'):
                href = urljoin(self.base_url, href)
            if any(c['source_url'] == href for c in collections):
                continue
            print(f"  🔗 Коллекция: {text}")
            images = []
            collection_soup = self.fetch_page(href)
            if collection_soup:
                img_tags = collection_soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    if src and 'logo' not in src.lower():
                        img_path = self.download_image(src)
                        if img_path:
                            images.append(img_path)
                            break
            collections.append({'title': text, 'description': '', 'full_content': '', 'technical_specs': '', 'image_url': images[0] if images else None, 'source_url': href})
        return collections
    def extract_collection_detail(self, url: str) -> Dict:
        return {'description': ''}
    def extract_projects(self) -> List[Dict]:
        return []
    def extract_blog_posts(self) -> List[Dict]:
        return []


class GazziniParser(BaseManufacturerParser):
    """Парсер для Gazzini (Италия)"""
    def __init__(self):
        super().__init__('https://www.ceramicagazzini.it', 'gazzini')
        # Hardcoded collection list since the site blocks automated 403 on /collezioni/ listing
        self.collections_data = [
            ('amalfi-lux', 'Amalfi Lux'),
            ('antique-portofino', 'Antique Portofino'),
            ('artwork', 'Artwork'),
            ('atelier', 'Atelier'),
            ('atlantic-blue', 'Atlantic Blue'),
            ('avenue-white', 'Avenue White'),
            ('blauwsteen', 'Blauwsteen'),
            ('briques', 'Briques'),
            ('calacatta-emerald', 'Calacatta Emerald'),
            ('calacatta-oro', 'Calacatta Oro'),
        ]
    
    def extract_collections(self) -> List[Dict]:
        print("🔍 Парсинг коллекций Gazzini...")
        collections = []
        for slug, name in self.collections_data:
            url = f"{self.base_url}/collezioni/{slug}/"
            print(f"  🔗 Коллекция: {name}")
            images = []
            collection_soup = self.fetch_page(url)
            if collection_soup:
                img_tags = collection_soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    if src and 'logo' not in src.lower():
                        img_path = self.download_image(src)
                        if img_path:
                            images.append(img_path)
                            break
            collections.append({'title': name, 'description': '', 'full_content': '', 'technical_specs': '', 'image_url': images[0] if images else None, 'source_url': url})
        return collections
    def extract_collection_detail(self, url: str) -> Dict:
        return {'description': ''}
    def extract_projects(self) -> List[Dict]:
        return []
    def extract_blog_posts(self) -> List[Dict]:
        return []


# Фабрика парсеров
class ManufacturerParserFactory:
    """Фабрика для создания парсеров производителей"""
    
    @staticmethod
    def get_parser(manufacturer_slug: str) -> Optional[BaseManufacturerParser]:
        """Возвращает парсер для указанного производителя"""
        parsers = {
            'aparici': ApariciParser,
            'dune': DuneParser,
            'equipe': EquipeParser,
            'ape': ApeParser,
            'lafabbrica': LaFabbricaParser,
            'baldocer': BaldocerParser,
            'casalgrande': CasalgrandeParser,
            'distrimat': DistrimatParser,
            'estudi-ceramico': EstudiCeremicoParser,
            'etile': EtileParser,
            'exagres': ExagresParser,
            'gazzini': GazziniParser,
            'halcon': HalconParser,
            'roced': RocedParser,
            'tuscania': TuscaniParser,
            'unicom-starker': UnicomStarkerParser,
            # Добавляйте новые парсеры здесь
        }
        
        parser_class = parsers.get(manufacturer_slug)
        if parser_class:
            return parser_class()
        else:
            print(f"⚠️  Специфичный парсер для {manufacturer_slug} не найден, используется базовый")
            return None

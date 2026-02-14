"""
Анализ структуры сайта APE Grupo для создания парсера
"""
import requests
from bs4 import BeautifulSoup

base_url = 'https://www.apegrupo.com/de'

print("="*80)
print("АНАЛИЗ САЙТА APE GRUPO")
print("="*80)

# 1. Главная страница - логотип
print("\n1. ПОИСК ЛОГОТИПА")
print("-"*80)
try:
    response = requests.get(base_url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем логотип
    logo_candidates = []
    
    # В header/navbar
    header = soup.find(['header', 'nav'])
    if header:
        imgs = header.find_all('img', limit=5)
        for img in imgs:
            src = img.get('src', '')
            alt = img.get('alt', '')
            if 'logo' in src.lower() or 'logo' in alt.lower():
                logo_candidates.append(f"  ✓ {src} (alt: {alt})")
        
    # Просто поиск по alt
    for img in soup.find_all('img', limit=10):
        alt = img.get('alt', '').lower()
        src = img.get('src', '')
        if 'ape' in alt or 'logo' in alt:
            logo_candidates.append(f"  ✓ {src} (alt: {img.get('alt')})")
    
    if logo_candidates:
        print("Найдены кандидаты на логотип:")
        for candidate in logo_candidates[:3]:
            print(candidate)
    else:
        print("⚠️ Логотип не найден стандартным способом")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 2. Коллекции
print("\n2. ПОИСК КОЛЛЕКЦИЙ")
print("-"*80)
collections_urls = [
    '/de/kollektionen',
    '/de/produkte',
    '/de/collections',
    '/de/products'
]

for url_path in collections_urls:
    try:
        url = base_url + url_path
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✓ Найден: {url}")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем элементы коллекций
            collection_classes = ['collection', 'product', 'tile', 'serie']
            for cls in collection_classes:
                items = soup.find_all(class_=lambda x: x and cls in x.lower())
                if items:
                    print(f"  → Найдено {len(items)} элементов с классом '{cls}'")
                    if items:
                        first_item = items[0]
                        print(f"  → Первый элемент класса: {first_item.get('class')}")
                        # Ищем ссылку
                        link = first_item.find('a')
                        if link:
                            print(f"  → Ссылка: {link.get('href')}")
                        # Ищем изображение
                        img = first_item.find('img')
                        if img:
                            print(f"  → Изображение: {img.get('src')}")
            break
    except:
        continue

# 3. Проекты
print("\n3. ПОИСК ПРОЕКТОВ")
print("-"*80)
projects_urls = [
    '/de/projekte',
    '/de/projects',
    '/de/realizaciones',
    '/de/referenzen'
]

for url_path in projects_urls:
    try:
        url = base_url + url_path
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✓ Найден: {url}")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем элементы проектов
            project_classes = ['project', 'work', 'reference', 'realizaci']
            for cls in project_classes:
                items = soup.find_all(class_=lambda x: x and cls in x.lower())
                if items:
                    print(f"  → Найдено {len(items)} элементов с классом '{cls}'")
                    if items:
                        first_item = items[0]
                        print(f"  → Первый элемент класса: {first_item.get('class')}")
            break
    except:
        continue

# 4. Блог/Новости
print("\n4. ПОИСК БЛОГА/НОВОСТЕЙ")
print("-"*80)
blog_urls = [
    '/de/blog',
    '/de/news',
    '/de/neuigkeiten',
    '/de/aktuelles',
    '/de/noticias'
]

for url_path in blog_urls:
    try:
        url = base_url + url_path
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✓ Найден: {url} (status: {response.status_code})")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем элементы блога
            blog_classes = ['blog', 'news', 'article', 'post']
            for cls in blog_classes:
                items = soup.find_all(class_=lambda x: x and cls in x.lower())
                if items:
                    print(f"  → Найдено {len(items)} элементов с классом '{cls}'")
            break
    except Exception as e:
        continue

print("\n" + "="*80)

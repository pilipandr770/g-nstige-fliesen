"""
Детальный анализ структуры коллекций Casalgrande Padana
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.casalgrandepadana.com'

print("="*80)
print("CASALGRANDE PADANA - СТРУКТУРА КОЛЛЕКЦИЙ")
print("="*80)

# Проверяем страницу продуктов
print("\n1. Анализ /de/produkte...")
try:
    r = requests.get(base_url + '/de/produkte', headers=headers, timeout=15)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    print(f"   Статус: {r.status_code}")
    
    # Ищем ссылки на коллекции
    links = soup.find_all('a', href=True)
    collection_links = set()
    
    for link in links:
        href = link.get('href', '')
        # Паттерн для коллекций: /de/produkte/[название]
        if '/de/produkte/' in href and href.count('/') > 2:
            collection_links.add(href)
    
    print(f"   Найдено уникальных ссылок на коллекции: {len(collection_links)}")
    
    if collection_links:
        print("\n   Примеры коллекций:")
        for idx, href in enumerate(list(collection_links)[:10], 1):
            print(f"     {idx}. {href}")
    
    # Ищем класcы для карточек коллекций
    print("\n   Поиск контейнеров коллекций...")
    divs = soup.find_all(['div', 'article', 'section'], class_=True, limit=100)
    classes = {}
    for div in divs:
        for cls in div.get('class', []):
            if any(keyword in cls.lower() for keyword in ['product', 'collection', 'card', 'item', 'grid']):
                classes[cls] = classes.get(cls, 0) + 1
    
    if classes:
        print("   Релевантные классы (топ 10):")
        for cls, count in sorted(classes.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"     {cls}: {count}")

except Exception as e:
    print(f"   Ошибка: {e}")

# Проверяем страницу проектов
print("\n2. Анализ /de/projects...")
try:
    r = requests.get(base_url + '/de/projects', headers=headers, timeout=15)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    print(f"   Статус: {r.status_code}")
    
    # Ищем проекты
    links = soup.find_all('a', href=True)
    project_links = set()
    
    for link in links:
        href = link.get('href', '')
        if '/magazine/projects/' in href or '/de/projects/' in href:
            project_links.add(href)
    
    print(f"   Найдено проектов: {len(project_links)}")
    
    if project_links:
        print("\n   Примеры проектов:")
        for idx, href in enumerate(list(project_links)[:5], 1):
            print(f"     {idx}. {href}")

except Exception as e:
    print(f"   Ошибка: {e}")

# Проверяем новости
print("\n3. Анализ /magazine/news...")
try:
    r = requests.get(base_url + '/magazine/news', headers=headers, timeout=15)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    print(f"   Статус: {r.status_code}")
    
    # Ищем новости
    links = soup.find_all('a', href=True)
    news_links = set()
    
    for link in links:
        href = link.get('href', '')
        if '/magazine/news/' in href and href.count('/') > 2:
            news_links.add(href)
    
    print(f"   Найдено новостей: {len(news_links)}")
    
    if news_links:
        print("\n   Примеры новостей:")
        for idx, href in enumerate(list(news_links)[:5], 1):
            print(f"     {idx}. {href}")

except Exception as e:
    print(f"   Ошибка: {e}")

# Проверяем логотип
print("\n4. Поиск логотипа...")
try:
    r = requests.get(base_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Ищем изображения в header/nav
    for tag in ['header', 'nav']:
        container = soup.find(tag)
        if container:
            imgs = container.find_all('img')
            for img in imgs:
                src = img.get('src', '')
                alt = img.get('alt', '')
                if 'logo' in src.lower() or 'logo' in alt.lower():
                    print(f"   ✓ Логотип: {src}")
                    break
    
    # Альтернативный поиск
    all_imgs = soup.find_all('img', limit=20)
    print(f"\n   Первые 5 изображений на странице:")
    for img in all_imgs[:5]:
        src = img.get('src', 'no src')
        alt = img.get('alt', 'no alt')
        print(f"     - {alt[:50]}: {src[:80]}")

except Exception as e:
    print(f"   Ошибка: {e}")

print("\n" + "="*80)

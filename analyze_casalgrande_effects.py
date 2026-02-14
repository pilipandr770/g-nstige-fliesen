"""
Анализ коллекций Casalgrande Padana через категории эффектов
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.casalgrandepadana.com'

print("="*80)
print("CASALGRANDE PADANA - КАТЕГОРИИ ЭФФЕКТОВ")
print("="*80)

# Категории эффектов
effects = [
    ('stone', 'Stone'),
    ('marble', 'Marble'),
    ('metal', 'Metal'),
    ('wood', 'Wood'),
    ('colour', 'Colour'),
    ('cement', 'Cement'),
    ('technic', 'Technic'),
    ('terrazzo', 'Terrazzo'),
    ('granite', 'Granite')
]

all_collections = set()

for effect_slug, effect_name in effects:
    print(f"\n{effect_name}:")
    url = f"{base_url}/products/effect/{effect_slug}"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        print(f"  Статус: {r.status_code}")
        
        # Ищем ссылки на коллекции
        links = soup.find_all('a', href=True)
        collections = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Коллекции могут быть в /products/[название]
            if href.startswith('/products/') and href.count('/') == 2:
                slug = href.split('/')[-1]
                if slug not in ['effect', 'bim-object'] and len(slug) > 2:
                    collections.append((text, href))
                    all_collections.add((text, href))
        
        # Убираем дубликаты
        unique = {}
        for text, href in collections:
            if href not in unique:
                unique[href] = text
        
        print(f"  Найдено коллекций: {len(unique)}")
        
        # Показываем первые 3
        for href, text in list(unique.items())[:3]:
            print(f"    - {text}: {href}")
        
    except Exception as e:
        print(f"  Ошибка: {e}")

print("\n" + "="*80)
print(f"ВСЕГО УНИКАЛЬНЫХ КОЛЛЕКЦИЙ: {len(all_collections)}")
print("="*80)

if all_collections:
    print("\nПримеры коллекций:")
    for idx, (text, href) in enumerate(list(all_collections)[:15], 1):
        print(f"{idx}. {text}: {href}")

# Проверяем одну конкретную коллекцию
if all_collections:
    sample_text, sample_href = list(all_collections)[0]
    print(f"\n{'='*80}")
    print(f"ПРОВЕРКА КОЛЛЕКЦИИ: {sample_text}")
    print("="*80)
    
    try:
        r = requests.get(base_url + sample_href, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        print(f"Статус: {r.status_code}")
        
        # Ищем изображения коллекции
        imgs = soup.find_all('img', limit=10)
        print(f"\nИзображения (первые 3):")
        for img in imgs[:3]:
            src = img.get('src', '')
            alt = img.get('alt', 'no alt')
            print(f"  - {alt[:50]}: {src[:100]}")
        
        # Ищем описание
        metas = soup.find_all('meta')
        for meta in metas:
            if meta.get('name') == 'description' or meta.get('property') == 'og:description':
                print(f"\nОписание: {meta.get('content', '')[:200]}")
                break
        
    except Exception as e:
        print(f"Ошибка: {e}")

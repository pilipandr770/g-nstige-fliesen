"""
Анализ конкретной категории коллекций La Fabbrica
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.lafabbrica.it'

print("="*80)
print("АНАЛИЗ КАТЕГОРИИ КОЛЛЕКЦИЙ LA FABBRICA")
print("="*80)

# Проверяем категорию "Marmor-Effekt"
print("\n📦 КАТЕГОРИЯ: Marmor-Effekt")
print("-"*80)
try:
    response = requests.get(base_url + '/de/kollektionen/marmor-effekt/', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем все ссылки на странице
    all_links = soup.find_all('a', href=True)
    
    # Фильтруем ссылки на коллекции (должны быть в /de/ и содержать длинный путь)
    collection_links = []
    for link in all_links:
        href = link.get('href')
        # Ссылки на конкретные коллекции обычно длиннее, чем на категории
        if '/de/' in href and href.count('/') > 4:
            # Исключаем общие ссылки
            if not any(x in href for x in ['kollektionen', 'produkte', 'projects', 'blog', 'focus-on']):
                collection_links.append(link)
    
    print(f"Найдено {len(collection_links)} потенциальных коллекций")
    
    # Убираем дубликаты
    unique_collections = {}
    for link in collection_links:
        href = link.get('href')
        if href not in unique_collections:
            unique_collections[href] = link
    
    print(f"Уникальных: {len(unique_collections)}")
    
    for i, (href, link) in enumerate(list(unique_collections.items())[:10], 1):
        print(f"\nКоллекция {i}:")
        print(f"  URL: {href}")
        
        # Название
        title = link.get_text(strip=True)
        print(f"  Текст: {title[:50]}")
        
        # Изображение
        img = link.find('img')
        if not img:
            # Ищем в родителе
            parent = link.parent
            if parent:
                img = parent.find('img')
        
        if img:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            print(f"  Изображение: {src}")
        
        # Класс родителя
        if link.parent:
            print(f"  Родитель: {link.parent.name}, класс: {link.parent.get('class')}")
    
    # Показываем все классы элементов с изображениями
    print("\n\nКлассы элементов с изображениями:")
    imgs = soup.find_all('img', limit=20)
    for img in imgs[:5]:
        parent = img.parent
        if parent and parent.name == 'a':
            classes = parent.get('class', [])
            print(f"  • Ссылка с img, класс: {classes}")
        elif parent:
            classes = parent.get('class', [])
            print(f"  • {parent.name} с img, класс: {classes}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)

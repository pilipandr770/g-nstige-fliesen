"""
Детальный анализ структуры страниц La Fabbrica
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.lafabbrica.it'

print("="*80)
print("ДЕТАЛЬНЫЙ АНАЛИЗ СТРУКТУРЫ LA FABBRICA")
print("="*80)

# 1. КОЛЛЕКЦИИ
print("\n📦 КОЛЛЕКЦИИ (/de/collections)")
print("-"*80)
try:
    response = requests.get(base_url + '/de/collections', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем ссылки на коллекции
    collection_links = soup.find_all('a', href=re.compile(r'/collection/'))
    
    print(f"Найдено {len(collection_links)} ссылок на коллекции")
    
    # Убираем дубликаты
    unique_collections = {}
    for link in collection_links:
        href = link.get('href')
        if href not in unique_collections:
            unique_collections[href] = link
    
    print(f"Уникальных коллекций: {len(unique_collections)}")
    
    for i, (href, link) in enumerate(list(unique_collections.items())[:5], 1):
        print(f"\nКоллекция {i}:")
        print(f"  URL: {href}")
        
        # Название
        title = link.get_text(strip=True)
        print(f"  Текст: {title[:50]}")
        
        # Изображение
        img = link.find('img')
        if not img and link.parent:
            img = link.parent.find('img')
        
        if img:
            print(f"  Изображение: {img.get('src')}")
            print(f"  Alt: {img.get('alt')}")
        
        # Класс контейнера
        parent = link.parent
        if parent:
            print(f"  Родитель: {parent.name}, класс: {parent.get('class')}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 2. ПРОЕКТЫ
print("\n\n🏗️ ПРОЕКТЫ (/de/projects)")
print("-"*80)
try:
    response = requests.get(base_url + '/de/projects', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем ссылки на проекты
    project_links = soup.find_all('a', href=re.compile(r'/project/'))
    
    unique_projects = {}
    for link in project_links:
        href = link.get('href')
        if href not in unique_projects:
            unique_projects[href] = link
    
    print(f"Найдено {len(unique_projects)} уникальных проектов")
    
    for i, (href, link) in enumerate(list(unique_projects.items())[:5], 1):
        print(f"\nПроект {i}:")
        print(f"  URL: {href}")
        
        # Название
        title = link.get_text(strip=True)
        if not title:
            # Ищем заголовок рядом
            parent = link.parent
            if parent:
                h_tag = parent.find(['h1', 'h2', 'h3', 'h4'])
                if h_tag:
                    title = h_tag.get_text(strip=True)
        
        print(f"  Название: {title[:50]}")
        
        # Изображение
        img = link.find('img')
        if not img and link.parent:
            img = link.parent.find('img')
        
        if img:
            print(f"  Изображение: {img.get('src')}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 3. БЛОГ
print("\n\n📰 БЛОГ (/de/blog)")
print("-"*80)
try:
    response = requests.get(base_url + '/de/blog', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем статьи блога
    blog_links = soup.find_all('a', href=re.compile(r'/blog/.+'))
    
    unique_blogs = {}
    for link in blog_links:
        href = link.get('href')
        # Исключаем категории
        if href.count('/') > 3 and href not in unique_blogs:
            unique_blogs[href] = link
    
    print(f"Найдено {len(unique_blogs)} статей блога")
    
    for i, (href, link) in enumerate(list(unique_blogs.items())[:5], 1):
        print(f"\nСтатья {i}:")
        print(f"  URL: {href}")
        
        # Название
        title = link.get_text(strip=True)
        print(f"  Название: {title[:60]}")
        
        # Изображение
        img = link.find('img')
        if not img and link.parent:
            img = link.parent.find('img')
        
        if img:
            print(f"  Изображение: {img.get('src')}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "="*80)

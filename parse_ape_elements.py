"""
Детальный парсинг элементов APE Grupo
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.apegrupo.com'

print("="*80)
print("ДЕТАЛЬНЫЙ ПАРСИНГ ЭЛЕМЕНТОВ APE GRUPO")
print("="*80)

# 1. КОЛЛЕКЦИИ - находим все элементы внутри listado_buscador_productos
print("\n1. КОЛЛЕКЦИИ")
print("-"*80)
try:
    response = requests.get(base_url + '/de/produkte', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Находим контейнер с коллекциями
    container = soup.find('div', class_='listado_buscador_productos')
    if container:
        # Ищем все ссылки внутри
        links = container.find_all('a', href=True)
        print(f"Найдено {len(links)} коллекций\n")
        
        for i, link in enumerate(links[:5], 1):
            href = link.get('href')
            
            # Изображение
            img = link.find('img')
            img_src = img.get('src') if img else None
            
            # Название - может быть в alt или нужно парсить из href
            title = img.get('alt') if img and img.get('alt') else href.split('/')[-2] if '/' in href else ''
            
            print(f"Коллекция {i}:")
            print(f"  URL: {href}")
            print(f"  Название: {title}")
            print(f"  Изображение: {img_src}")
            print()
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 2. ПРОЕКТЫ - ищем ссылки на projekte
print("\n2. ПРОЕКТЫ")
print("-"*80)
try:
    response = requests.get(base_url + '/de/projekte', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем все ссылки, которые ведут на конкретные проекты
    # Обычно это /de/projekte/название-проекта/
    project_links = soup.find_all('a', href=re.compile(r'/de/projekte/.+/'))
    
    # Убираем дубликаты
    unique_projects = {}
    for link in project_links:
        href = link.get('href')
        if href not in unique_projects:
            unique_projects[href] = link
    
    print(f"Найдено {len(unique_projects)} уникальных проектов\n")
    
    for i, (href, link) in enumerate(list(unique_projects.items())[:5], 1):
        # Ищем изображение - может быть внутри ссылки или в родителе
        img = link.find('img')
        if not img:
            parent = link.parent
            if parent:
                img = parent.find('img')
        
        img_src = img.get('src') if img else None
        
        # Название
        title_text = link.get_text(strip=True)
        if not title_text and img:
            title_text = img.get('alt', '')
        
        print(f"Проект {i}:")
        print(f"  URL: {href}")
        print(f"  Название: {title_text}")
        print(f"  Изображение: {img_src}")
        print()
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 3. БЛОГ
print("\n3. БЛОГ")
print("-"*80)
try:
    response = requests.get(base_url + '/de/blog', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем ссылки на статьи блога
    blog_links = soup.find_all('a', href=re.compile(r'/(de/)?blog/.+'))
    
    # Убираем дубликаты и категории
    unique_blogs = {}
    for link in blog_links:
        href = link.get('href')
        # Только полные статьи, не категории
        if href.count('/') > 3 and href not in unique_blogs:
            unique_blogs[href] = link
    
    print(f"Найдено {len(unique_blogs)} статей блога\n")
    
    for i, (href, link) in enumerate(list(unique_blogs.items())[:5], 1):
        # Ищем изображение
        img = link.find('img')
        if not img:
            parent = link.parent
            if parent:
                img = parent.find('img')
        
        img_src = img.get('src') if img else None
        
        # Название
        title_text = link.get_text(strip=True)
        
        print(f"Статья {i}:")
        print(f"  URL: {href}")
        print(f"  Название: {title_text[:60]}")
        print(f"  Изображение: {img_src}")
        print()
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("="*80)

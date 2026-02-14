"""
Поиск проектов на странице La Fabbrica projects
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10...64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.lafabbrica.it'

print("="*80)
print("АНАЛИЗ ПРОЕКТОВ LA FABBRICA")
print("="*80)

try:
    response = requests.get(base_url + '/de/projects', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем ссылки, содержащие /de/ и достаточно длинные
    all_links = soup.find_all('a', href=True)
    
    # Фильтруем проекты
    project_links = []
    for link in all_links:
        href = link.get('href')
        # Проект должен быть в /de/ и иметь длинный путь
        if '/de/' in href and href.count('/') > 3:
            # Исключаем меню и служебные ссылки
            if not any(x in href for x in ['kollektionen', 'produkte', 'projects', 'blog', 'focus-on', 'avastone']):
                project_links.append(link)
    
    print(f"Найдено {len(project_links)} потенциальных проектов")
    
    # Убираем дубликаты
    unique_projects = {}
    for link in project_links:
        href = link.get('href')
        if href not in unique_projects and len(href) > 30:  # Только длинные URL
            unique_projects[href] = link
    
    print(f"Уникальных: {len(unique_projects)}\n")
    
    for i, (href, link) in enumerate(list(unique_projects.items())[:10], 1):
        print(f"Проект {i}:")
        print(f"  URL: {href}")
        
        # Название
        title = link.get_text(strip=True)
        if title:
            print(f"  Текст: {title[:60]}")
        
        # Изображение
        img = link.find('img')
        if not img and link.parent:
            img = link.parent.find('img')
        
        if img:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                print(f"  Изображение: {src[:80]}...")
        print()
    
    # Проверяем, есть ли элементы с определенными классами
    print("\nПоиск контейнеров проектов...")
    containers = soup.find_all(['div', 'article'], class_=lambda x: x and ('project' in str(x).lower() or 'post' in str(x).lower()))
    print(f"Найдено {len(containers)} контейнеров с классами 'project' или 'post'")
    
    if containers:
        for i, container in enumerate(containers[:3], 1):
            print(f"\nКонтейнер {i}:")
            print(f"  Класс: {container.get('class')}")
            link = container.find('a', href=True)
            if link:
                print(f"  Ссылка: {link.get('href')}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)

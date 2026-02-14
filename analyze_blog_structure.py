"""
Детальный анализ структуры блога Aparici
"""

import requests
from bs4 import BeautifulSoup
import re

def analyze_blog_structure():
    url = 'https://www.aparici.com/de/blog'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"🔍 Анализ блога: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=" * 60)
        print("1. Все ссылки на статьи блога:")
        print("=" * 60)
        
        blog_links = soup.find_all('a', href=re.compile(r'/blog/'))
        
        unique_links = {}
        for link in blog_links:
            href = link.get('href')
            if href and href not in unique_links and len(href.split('/')) > 3:  # Не главная страница блога
                unique_links[href] = link.get_text(strip=True)
        
        print(f"Найдено {len(unique_links)} уникальных статей\n")
        
        for i, (href, text) in enumerate(list(unique_links.items())[:10], 1):
            print(f"{i}. {href}")
            print(f"   Заголовок: {text[:80]}")
            print()
        
        print("\n" + "=" * 60)
        print("2. Структура карточек статей:")
        print("=" * 60)
        
        # Ищем контейнеры статей
        possible_containers = soup.find_all(['article', 'div'], class_=re.compile(r'blog|post|article|card', re.I))
        
        print(f"Найдено {len(possible_containers)} контейнеров\n")
        
        for i, container in enumerate(possible_containers[:5], 1):
            print(f"Контейнер {i}:")
            print(f"  Tag: {container.name}")
            print(f"  Classes: {container.get('class', [])}")
            
            # Ищем ссылку
            link = container.find('a', href=re.compile(r'/blog/'))
            if link:
                print(f"  Ссылка: {link.get('href')}")
            
            # Ищем заголовок
            title = container.find(['h1', 'h2', 'h3', 'h4'])
            if title:
                print(f"  Заголовок: {title.get_text(strip=True)[:60]}")
            
            # Ищем изображение
            img = container.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                print(f"  Изображение: {src[:60] if src else 'no src'}")
            
            # Ищем описание/контент
            paragraphs = container.find_all('p')
            if paragraphs:
                print(f"  Параграфов: {len(paragraphs)}")
            
            print()
        
        print("\n" + "=" * 60)
        print("3. Все классы на странице (первые 30):")
        print("=" * 60)
        
        all_classes = set()
        for tag in soup.find_all(class_=True):
            classes = tag.get('class', [])
            all_classes.update(classes)
        
        sorted_classes = sorted(all_classes)
        for cls in sorted_classes[:30]:
            print(f"   - {cls}")
        
        print("\n" + "=" * 60)
        print("4. Изображения на странице:")
        print("=" * 60)
        
        images = soup.find_all('img')
        print(f"Всего изображений: {len(images)}\n")
        
        for i, img in enumerate(images[:10], 1):
            src = img.get('src') or img.get('data-src')
            alt = img.get('alt', 'no alt')
            classes = img.get('class', [])
            
            print(f"{i}. Src: {src[:60] if src else 'no src'}")
            print(f"   Alt: {alt[:50]}")
            print(f"   Classes: {classes}")
            
            parent = img.parent
            if parent and parent.name == 'a':
                print(f"   В ссылке: {parent.get('href', 'no href')[:60]}")
            print()
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_blog_structure()

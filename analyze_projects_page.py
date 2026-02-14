"""
Анализ страницы проектов Aparici
"""

import requests
from bs4 import BeautifulSoup

def analyze_projects_page():
    url = 'https://www.aparici.com/de/projekte'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"🔍 Анализ страницы проектов: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=" * 60)
        print("1. Все ссылки с 'projekt' в href:")
        print("=" * 60)
        
        links = soup.find_all('a', href=True)
        project_links = [link for link in links if any(kw in link['href'].lower() for kw in ['projekt', 'project', 'referenz', 'reference'])]
        
        for i, link in enumerate(project_links[:10], 1):
            print(f"{i}. Href: {link.get('href')}")
            print(f"   Text: {link.get_text(strip=True)[:50]}")
            print(f"   Classes: {link.get('class', [])}")
            
            # Проверяем parent
            parent = link.parent
            if parent:
                print(f"   Parent tag: {parent.name}, classes: {parent.get('class', [])}")
            
            # Проверяем img внутри
            img = link.find('img')
            if img:
                print(f"   ✓ Есть изображение: {img.get('src', img.get('data-src', 'no src'))[:50]}")
            print()
        
        print("\n" + "=" * 60)
        print("2. Все article элементы:")
        print("=" * 60)
        
        articles = soup.find_all('article')
        print(f"Найдено {len(articles)} article элементов")
        for i, article in enumerate(articles[:5], 1):
            print(f"{i}. Classes: {article.get('class', [])}")
            link = article.find('a', href=True)
            if link:
                print(f"   Ссылка: {link.get('href')}")
            title = article.find(['h1', 'h2', 'h3', 'h4'])
            if title:
                print(f"   Заголовок: {title.get_text(strip=True)}")
            img = article.find('img')
            if img:
                print(f"   Изображение: {img.get('src', 'no src')[:50]}")
            print()
        
        print("\n" + "=" * 60)
        print("3. Div с классами 'project', 'reference', 'referenz':")
        print("=" * 60)
        
        import re
        divs = soup.find_all('div', class_=re.compile(r'project|reference|referenz', re.I))
        print(f"Найдено {len(divs)} div элементов")
        for i, div in enumerate(divs[:5], 1):
            print(f"{i}. Classes: {div.get('class', [])}")
            link = div.find('a', href=True)
            if link:
                print(f"   Ссылка: {link.get('href')}")
            title = div.find(['h1', 'h2', 'h3', 'h4'])
            if title:
                print(f"   Заголовок: {title.get_text(strip=True)}")
            img = div.find('img')
            if img:
                print(f"   Изображение: {img.get('src', img.get('data-src', 'no src'))[:50]}")
            print()
        
        print("\n" + "=" * 60)
        print("4. Все изображения на странице (первые 10):")
        print("=" * 60)
        
        images = soup.find_all('img')
        print(f"Всего изображений: {len(images)}")
        for i, img in enumerate(images[:10], 1):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy')
            alt = img.get('alt', 'no alt')
            print(f"{i}. Src: {src[:80] if src else 'no src'}")
            print(f"   Alt: {alt[:50]}")
            print(f"   Classes: {img.get('class', [])}")
            
            # Проверяем родителя
            parent = img.parent
            if parent and parent.name == 'a':
                print(f"   В ссылке: {parent.get('href', 'no href')}")
            print()
        
        print("\n" + "=" * 60)
        print("5. Основная структура страницы:")
        print("=" * 60)
        
        # Ищем main, section
        main = soup.find(['main', 'section'])
        if main:
            print(f"Контейнер: {main.name}")
            print(f"Classes: {main.get('class', [])}")
            
            # Сколько карточек/элементов внутри
            cards = main.find_all(['div', 'article'], limit=20)
            print(f"Элементов внутри: {len(cards)}")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_projects_page()

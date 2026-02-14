"""
Скрипт для анализа HTML структуры сайта Aparici
"""

import requests
from bs4 import BeautifulSoup

def analyze_aparici():
    url = 'https://www.aparici.com/de/kollektionen'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"🔍 Анализ структуры: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=" * 60)
        print("1. Все ссылки с 'kollektion' или 'serie' в href:")
        print("=" * 60)
        
        links = soup.find_all('a', href=True)
        collection_links = [link for link in links if any(kw in link['href'].lower() for kw in ['kollektion', 'serie', 'collection'])]
        
        for i, link in enumerate(collection_links[:10], 1):
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
        print("2. Все div с классами содержащими 'product', 'card', 'item':")
        print("=" * 60)
        
        import re
        divs = soup.find_all('div', class_=re.compile(r'product|card|item|collection|serie', re.I))
        
        for i, div in enumerate(divs[:5], 1):
            print(f"{i}. Tag: {div.name}")
            print(f"   Classes: {div.get('class', [])}")
            
            # Ищем ссылку внутри
            link_inside = div.find('a', href=True)
            if link_inside:
                print(f"   ✓ Есть ссылка: {link_inside.get('href')}")
            
            # Ищем заголовок
            title = div.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if title:
                print(f"   ✓ Заголовок: {title.get_text(strip=True)}")
            
            # Ищем изображение
            img = div.find('img')
            if img:
                print(f"   ✓ Изображение: {img.get('src', img.get('data-src', 'no src'))[:50]}")
            print()
        
        print("\n" + "=" * 60)
        print("3. Все article элементы:")
        print("=" * 60)
        
        articles = soup.find_all('article')
        for i, article in enumerate(articles[:5], 1):
            print(f"{i}. Classes: {article.get('class', [])}")
            link = article.find('a', href=True)
            if link:
                print(f"   Ссылка: {link.get('href')}")
            title = article.find(['h1', 'h2', 'h3', 'h4'])
            if title:
                print(f"   Заголовок: {title.get_text(strip=True)}")
            print()
        
        print("\n" + "=" * 60)
        print("4. Список всех уникальных классов на странице (первые 30):")
        print("=" * 60)
        
        all_classes = set()
        for tag in soup.find_all(class_=True):
            classes = tag.get('class', [])
            all_classes.update(classes)
        
        sorted_classes = sorted(all_classes)
        for cls in sorted_classes[:30]:
            print(f"   - {cls}")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")

if __name__ == '__main__':
    analyze_aparici()

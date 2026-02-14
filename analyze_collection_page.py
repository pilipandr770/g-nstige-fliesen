"""
Анализ страницы отдельной коллекции Aparici
"""

import requests
from bs4 import BeautifulSoup

def analyze_collection_page():
    # Пример URL коллекции
    url = 'https://www.aparici.com/de/kollektionen/ibiza'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"🔍 Анализ страницы коллекции: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=" * 60)
        print("1. Все изображения на странице (первые 10):")
        print("=" * 60)
        
        images = soup.find_all('img')
        for i, img in enumerate(images[:10], 1):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy')
            print(f"{i}. Src: {src[:80] if src else 'no src'}")
            print(f"   Alt: {img.get('alt', 'no alt')}")
            print(f"   Classes: {img.get('class', [])}")
            print()
        
        print("\n" + "=" * 60)
        print("2. Заголовок страницы:")
        print("=" * 60)
        
        h1 = soup.find('h1')
        if h1:
            print(f"H1: {h1.get_text(strip=True)}")
            print(f"Classes: {h1.get('class', [])}")
        
        print("\n" + "=" * 60)
        print("3. Описание/контент:")
        print("=" * 60)
        
        # Ищем все параграфы
        paragraphs = soup.find_all('p')
        for i, p in enumerate(paragraphs[:5], 1):
            text = p.get_text(strip=True)
            if len(text) > 30:
                print(f"{i}. {text[:150]}...")
                print(f"   Parent: {p.parent.name}, classes: {p.parent.get('class', [])}")
                print()
        
        print("\n" + "=" * 60)
        print("4. Основной контейнер контента:")
        print("=" * 60)
        
        # Ищем main, article или div с классами content
        main = soup.find(['main', 'article'])
        if main:
            print(f"Найден контейнер: {main.name}")
            print(f"Classes: {main.get('class', [])}")
        
        # Ищем divs с классами содержащими description, content, detail
        import re
        content_divs = soup.find_all('div', class_=re.compile(r'description|content|detail|info', re.I))
        print(f"\nНайдено {len(content_divs)} div с классами description/content/detail/info")
        for div in content_divs[:3]:
            print(f"- Classes: {div.get('class', [])}")
            text = div.get_text(strip=True)
            if text:
                print(f"  Text: {text[:100]}...")
        
        print("\n" + "=" * 60)
        print("5. Технические спецификации:")
        print("=" * 60)
        
        # Ищем таблицы, списки с характеристиками
        tables = soup.find_all('table')
        if tables:
            print(f"Найдено {len(tables)} таблиц")
            for table in tables[:2]:
                rows = table.find_all('tr')
                for row in rows[:5]:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        print(' | '.join([cell.get_text(strip=True) for cell in cells]))
        
        specs_divs = soup.find_all(['div', 'dl'], class_=re.compile(r'spec|technical|formato|acabado|caracteristica', re.I))
        if specs_divs:
            print(f"\nНайдено {len(specs_divs)} блоков спецификаций")
            for div in specs_divs[:2]:
                print(f"Classes: {div.get('class', [])}")
                print(f"Text: {div.get_text(strip=True)[:200]}...")
                print()
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")

if __name__ == '__main__':
    analyze_collection_page()

"""
Детальный анализ структуры страниц APE Grupo
"""
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.apegrupo.com'

print("="*80)
print("ДЕТАЛЬНЫЙ АНАЛИЗ СТРУКТУРЫ APE GRUPO")
print("="*80)

# 1. КОЛЛЕКЦИИ
print("\n📦 КОЛЛЕКЦИИ (/de/produkte)")
print("-"*80)
try:
    response = requests.get(base_url + '/de/produkte', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем контейнер с коллекциями
    containers = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and ('product' in str(x).lower() or 'collection' in str(x).lower() or 'serie' in str(x).lower()))
    
    if containers:
        print(f"Найдено {len(containers)} контейнеров")
        for i, container in enumerate(containers[:3], 1):
            print(f"\nКонтейнер {i}:")
            print(f"  Тег: {container.name}")
            print(f"  Класс: {container.get('class')}")
            
            # Ищем ссылку
            link = container.find('a', href=True)
            if link:
                print(f"  Ссылка: {link.get('href')}")
                print(f"  Текст: {link.get_text(strip=True)[:50]}")
            
            # Ищем изображение
            img = container.find('img')
            if img:
                print(f"  Изображение: {img.get('src')}")
                print(f"  Alt: {img.get('alt')}")
    else:
        # Альтернативный поиск - все ссылки на продукты
        all_links = soup.find_all('a', href=lambda x: x and '/produkte/' in x)
        print(f"Найдено {len(all_links)} ссылок на продукты")
        for link in all_links[:5]:
            print(f"  • {link.get('href')} - {link.get_text(strip=True)[:30]}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 2. ПРОЕКТЫ
print("\n🏗️ ПРОЕКТЫ (/de/projekte)")
print("-"*80)
try:
    response = requests.get(base_url + '/de/projekte', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем контейнер с проектами
    containers = soup.find_all(['div', 'article'], class_=lambda x: x and ('project' in str(x).lower() or 'work' in str(x).lower() or 'reference' in str(x).lower()))
    
    if containers:
        print(f"Найдено {len(containers)} контейнеров проектов")
        for i, container in enumerate(containers[:3], 1):
            print(f"\nПроект {i}:")
            print(f"  Класс: {container.get('class')}")
            
            # Ищем заголовок
            title = container.find(['h1', 'h2', 'h3', 'h4'])
            if title:
                print(f"  Название: {title.get_text(strip=True)}")
            
            # Ищем ссылку
            link = container.find('a', href=True)
            if link:
                print(f"  Ссылка: {link.get('href')}")
            
            # Ищем изображение
            img = container.find('img')
            if img:
                print(f"  Изображение: {img.get('src')}")
    else:
        # Альтернативный поиск
        all_links = soup.find_all('a', href=lambda x: x and '/projekte/' in x)
        print(f"Найдено {len(all_links)} ссылок на проекты")
        
        # Показываем все классы div на странице
        all_divs = soup.find_all('div', class_=True, limit=30)
        classes_set = set()
        for div in all_divs:
            classes = div.get('class', [])
            if isinstance(classes, list):
                classes_set.update(classes)
        
        print(f"\nВсе уникальные классы на странице (первые 20):")
        for cls in sorted(list(classes_set))[:20]:
            print(f"  • {cls}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 3. БЛОГ
print("\n📰 БЛОГ (/de/blog)")
print("-"*80)
try:
    response = requests.get(base_url + '/de/blog', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем статьи
    articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('blog' in str(x).lower() or 'post' in str(x).lower() or 'news' in str(x).lower()))
    
    if articles:
        print(f"Найдено {len(articles)} статей")
        for i, article in enumerate(articles[:3], 1):
            print(f"\nСтатья {i}:")
            print(f"  Класс: {article.get('class')}")
            
            # Заголовок
            title = article.find(['h1', 'h2', 'h3'])
            if title:
                print(f"  Заголовок: {title.get_text(strip=True)[:50]}")
            
            # Ссылка
            link = article.find('a', href=True)
            if link:
                print(f"  Ссылка: {link.get('href')}")
            
            # Изображение
            img = article.find('img')
            if img:
                print(f"  Изображение: {img.get('src')}")
    else:
        all_links = soup.find_all('a', href=lambda x: x and '/blog/' in x)
        print(f"Найдено {len(all_links)} ссылок на блог")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "="*80)

"""
Анализ сайта Casalgrande Padana
"""
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.casalgrandepadana.com'

print("="*80)
print("CASALGRANDE PADANA - АНАЛИЗ САЙТА")
print("="*80)

# Проверяем доступность
print("\n1. Проверка доступности сайта...")
try:
    response = requests.get(base_url, headers=headers, timeout=15)
    print(f"   Статус: {response.status_code}")
    print(f"   URL: {response.url}")
except Exception as e:
    print(f"   Ошибка: {e}")
    exit(1)

# Проверяем языковые версии
print("\n2. Проверка языковых версий...")
for lang in ['/de', '/en', '/it', '/es']:
    try:
        r = requests.get(base_url + lang, headers=headers, timeout=10)
        print(f"   {lang}: {r.status_code}")
    except:
        print(f"   {lang}: недоступен")

# Пробуем найти структуру
print("\n3. Поиск структуры сайта...")
soup = BeautifulSoup(response.content, 'html.parser')

# Ищем логотип
print("\n   Логотип:")
logo = soup.find('img', src=lambda x: x and 'logo' in x.lower())
if logo:
    print(f"   ✓ Найден: {logo.get('src')}")
else:
    print("   ✗ Не найден по паттерну 'logo'")
    # Ищем все изображения в header
    header = soup.find(['header', 'nav'])
    if header:
        imgs = header.find_all('img', limit=5)
        if imgs:
            print("   Изображения в header:")
            for img in imgs:
                print(f"     - {img.get('src', 'no src')}")

# Ищем навигацию
print("\n   Навигация:")
nav_links = soup.find_all('a', href=True, limit=50)
print(f"   Всего ссылок: {len(nav_links)}")

# Фильтруем интересные разделы
interesting = []
for link in nav_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    if any(keyword in href.lower() for keyword in ['collection', 'kollekt', 'produkt', 'product', 'serie', 'project', 'blog', 'news', 'article']):
        interesting.append((text, href))

if interesting:
    print("   Интересные разделы:")
    seen = set()
    for text, href in interesting[:15]:
        if href not in seen:
            print(f"     {text}: {href}")
            seen.add(href)

# Проверяем типичные пути
print("\n4. Проверка типичных путей...")
paths = [
    '/de/kollektionen',
    '/de/collections',
    '/de/products',
    '/de/produkte',
    '/de/projekte',
    '/de/projects',
    '/de/blog',
    '/de/news',
    '/collections',
    '/products',
    '/projects'
]

for path in paths:
    try:
        r = requests.get(base_url + path, headers=headers, timeout=8)
        if r.status_code == 200:
            print(f"   ✓ {path}: {r.status_code}")
    except:
        pass

print("\n" + "="*80)

"""
Анализ структуры сайта La Fabbrica для создания парсера
"""
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8'
}

base_url = 'https://www.lafabbrica.it'

print("="*80)
print("АНАЛИЗ САЙТА LA FABBRICA")
print("="*80)

# 1. Главная страница
print("\n1. ТЕСТ ДОСТУПНОСТИ")
print("-"*80)
try:
    response = requests.get(base_url + '/de', headers=headers, timeout=15, allow_redirects=True)
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    print(f"Content-Length: {len(response.content)} bytes")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        print(f"Title: {title.get_text() if title else 'Не найден'}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 2. Логотип
print("\n2. ПОИСК ЛОГОТИПА")
print("-"*80)
try:
    response = requests.get(base_url + '/de', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем логотипы
    logos = soup.find_all('img', limit=10)
    for img in logos[:5]:
        src = img.get('src', '')
        alt = img.get('alt', '')
        if 'logo' in src.lower() or 'logo' in alt.lower() or 'fabbrica' in src.lower():
            print(f"  ✓ {src}")
            print(f"    alt: {alt}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 3. Проверка разделов
print("\n3. ПРОВЕРКА РАЗДЕЛОВ")
print("-"*80)
sections = [
    '/de/collections',
    '/de/kollektionen',
    '/de/produkte',
    '/de/projects',
    '/de/projekte',
    '/de/references',
    '/de/referenzen',
    '/de/blog',
    '/de/news',
    '/de/neuigkeiten'
]

for section in sections:
    try:
        url = base_url + section
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            print(f"  ✓ {section} -> {response.status_code}")
    except:
        pass

print("\n" + "="*80)

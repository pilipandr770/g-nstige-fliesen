"""
Детальный анализ APE Grupo с headers
"""
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8'
}

base_url = 'https://www.apegrupo.com'

print("ТЕСТ ДОСТУПНОСТИ САЙТА APE GRUPO")
print("="*80)

# Тест главной страницы
try:
    print("\n1. Главная страница...")
    response = requests.get(base_url + '/de', headers=headers, timeout=15, allow_redirects=True)
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    print(f"   Content-Length: {len(response.content)} bytes")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Проверяем title
        title = soup.find('title')
        print(f"   Title: {title.get_text() if title else 'Не найден'}")
        
        # Ищем nav/menu
        nav = soup.find(['nav', 'header'])
        if nav:
            links = nav.find_all('a', href=True)
            print(f"\n   Найдено {len(links)} ссылок в навигации:")
            for link in links[:10]:
                href = link.get('href')
                text = link.get_text(strip=True)
                if text:
                    print(f"     • {text}: {href}")
        
        # Ищем логотип
        print("\n2. Поиск логотипа...")
        logos = soup.find_all('img', limit=15)
        for img in logos[:5]:
            src = img.get('src', '')
            alt = img.get('alt', '')
            classes = img.get('class', [])
            if src:
                print(f"   IMG: {src}")
                print(f"        alt='{alt}', class={classes}")
                
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

# Проверка возможных разделов
print("\n3. Проверка разделов сайта...")
sections = [
    '/de/kollektionen',
    '/de/produkte', 
    '/de/collections',
    '/de/projekte',
    '/de/projects',
    '/de/blog',
    '/de/neuigkeiten',
    '/de',
    '/es',
    '/en'
]

for section in sections:
    try:
        url = base_url + section
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            print(f"   ✓ {section} -> {response.status_code}")
    except:
        pass

print("\n" + "="*80)

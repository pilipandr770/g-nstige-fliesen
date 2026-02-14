"""
Глубокий анализ HTML структуры La Fabbrica
"""
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.lafabbrica.it'

print("="*80)
print("HTML СТРУКТУРА LA FABBRICA")
print("="*80)

# КОЛЛЕКЦИИ
print("\n1. КОЛЛЕКЦИИ - ВСЕ ССЫЛКИ")
print("-"*80)
try:
    response = requests.get(base_url + '/de/collections', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Все ссылки на странице
    all_links = soup.find_all('a', href=True)
    print(f"Всего ссылок на странице: {len(all_links)}")
    
    # Показываем первые 20 ссылок
    print("\nПервые 20 ссылок:")
    for i, link in enumerate(all_links[:20], 1):
        href = link.get('href')
        text = link.get_text(strip=True)[:40]
        print(f"{i}. {href}")
        if text:
            print(f"   Текст: {text}")
    
    # Все уникальные классы div на странице
    all_divs = soup.find_all('div', class_=True, limit=50)
    classes_set = set()
    for div in all_divs:
        classes = div.get('class', [])
        if isinstance(classes, list):
            classes_set.update(classes)
    
    print(f"\nУникальные классы DIV (первые 30):")
    for cls in sorted(list(classes_set))[:30]:
        print(f"  • {cls}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

# ПРОЕКТЫ
print("\n\n2. ПРОЕКТЫ - ВСЕ ССЫЛКИ")
print("-"*80)
try:
    response = requests.get(base_url + '/de/projects', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Все ссылки на странице
    all_links = soup.find_all('a', href=True)
    print(f"Всего ссылок на странице: {len(all_links)}")
    
    # Показываем первые 15 ссылок
    print("\nПервые 15 ссылок:")
    for i, link in enumerate(all_links[:15], 1):
        href = link.get('href')
        text = link.get_text(strip=True)[:40]
        print(f"{i}. {href}")
        if text:
            print(f"   Текст: {text}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "="*80)

"""
Поиск JSON данных на странице Casalgrande Padana
"""
import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.casalgrandepadana.com'

print("="*80)
print("CASALGRANDE PADANA - ПОИСК JSON ДАННЫХ")
print("="*80)

try:
    r = requests.get(base_url + '/products', headers=headers, timeout=15)
    html = r.text
    
    print(f"Статус: {r.status_code}")
    print(f"Размер HTML: {len(html)} байт\n")
    
    # Ищем JSON в <script> тегах
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    
    print(f"Найдено <script> тегов: {len(scripts)}\n")
    
    # Ищем __NEXT_DATA__
    for script in scripts:
        if script.string and '__NEXT_DATA__' in script.string:
            print("OK - Найден __NEXT_DATA__!")
            
            try:
                # Извлекаем JSON
                match = re.search(r'__NEXT_DATA__\s*=\s*({.*?})\s*module\.exports', script.string, re.DOTALL)
                if not match:
                    match = re.search(r'__NEXT_DATA__\s*=\s*({.*})', script.string, re.DOTALL)
                
                if match:
                    json_str = match.group(1)
                    data = json.loads(json_str)
                    
                    print("OK - JSON успешно распарсен!")
                    print(f"\nОсновные ключи:")
                    for key in data.keys():
                        print(f"  - {key}")
                    
                    # Ищем данные о продуктах
                    if 'props' in data:
                        props = data['props']
                        print(f"\nКлючи в props:")
                        if isinstance(props, dict):
                            for key in props.keys():
                                print(f"  - {key}")
                            
                            # Ищем pageProps
                            if 'pageProps' in props:
                                page_props = props['pageProps']
                                print(f"\nКлючи в pageProps:")
                                if isinstance(page_props, dict):
                                    for key in list(page_props.keys())[:10]:
                                        value = page_props[key]
                                        value_type = type(value).__name__
                                        if isinstance(value, (list, dict)):
                                            length = len(value)
                                            print(f"  - {key}: {value_type} (length: {length})")
                                        else:
                                            print(f"  - {key}: {value_type}")
                                    
                                    # Ищем коллекции/продукты
                                    for key in page_props.keys():
                                        if any(keyword in key.lower() for keyword in ['product', 'collection', 'serie', 'item']):
                                            print(f"\nOK - Найден ключ с данными: {key}")
                                            data_value = page_props[key]
                                            if isinstance(data_value, list) and len(data_value) > 0:
                                                print(f"  Количество элементов: {len(data_value)}")
                                                print(f"  Пример первого элемента:")
                                                first = data_value[0]
                                                if isinstance(first, dict):
                                                    for k in list(first.keys())[:10]:
                                                        print(f"    - {k}: {first[k] if not isinstance(first[k], (dict, list)) else type(first[k]).__name__}")
                
            except Exception as e:
                print(f"Ошибка при парсинге JSON: {e}")
                import traceback
                traceback.print_exc()
            
            break
    else:
        print("FAIL - __NEXT_DATA__ не найден")
        
        # Попробуем другой подход - поиск любых JSON данных
        print("\nПоиск других JSON данных...")
        for script in scripts[:10]:
            if script.string and len(script.string) > 100:
                if '{' in script.string and '"' in script.string:
                    print(f"  Скрипт длиной {len(script.string)} байт содержит JSON-подобные данные")
                    # Показываем начало
                    preview = script.string[:200]
                    print(f"    Начало: {preview}")

except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)

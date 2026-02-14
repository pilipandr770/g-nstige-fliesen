"""
Поиск и загрузка Next.js _next/data JSON для Casalgrande Padana
"""
import requests
from bs4 import BeautifulSoup
import re
import json

headers = {'User-Agent': 'Mozilla/5.0'}
base = 'https://www.casalgrandepadana.com'

def try_get(url):
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r
    except Exception as e:
        print(f"  Ошибка запроса {url}: {e}")
        return None

print('='*80)
print('CASALGRANDE PADANA - TRY _NEXT/DATA')
print('='*80)

paths_to_check = ['/products', '/de/produkte', '/de/products', '/']
html = ''
for p in paths_to_check:
    r = try_get(base + p)
    if not r:
        continue
    print(f"Checked {p}: status {r.status_code}")
    if not html:
        html = r.text

if not html:
    print('No HTML retrieved, abort')
    raise SystemExit

soup = BeautifulSoup(html, 'html.parser')
text = html

# 1) Ищем явные ссылки на /_next/data/
found_next_data = set(re.findall(r'/_next/data/[^\"\'<> ]+\.json', text))
if found_next_data:
    print('\nFound _next/data links in HTML:')
    for f in found_next_data:
        print(' ', f)

# Попробуем получить каждый
candidates = []
for f in found_next_data:
    candidates.append(base.rstrip('/') + f)

# 2) Если не найдено, извлекаем buildId из /_next/static/
if not candidates:
    scripts = soup.find_all('script', src=True)
    build_ids = set()
    for s in scripts:
        src = s['src']
        m = re.search(r'/_next/static/([^/]+)/', src)
        if m:
            build_ids.add(m.group(1))
    if build_ids:
        print('\nDetected build ids:', build_ids)
        for build in build_ids:
            # Try common page json paths
            possible = [
                f'/_next/data/{build}/products.json',
                f'/_next/data/{build}/de/produkte.json',
                f'/_next/data/{build}/de/products.json',
                f'/_next/data/{build}/products/index.json',
                f'/_next/data/{build}/de/produkte/index.json',
                f'/_next/data/{build}/products.json',
                f'/_next/data/{build}/de/produkte.json'
            ]
            for p in possible:
                candidates.append(base.rstrip('/') + p)

# 3) Добавим fallback-адреса
if not candidates:
    guess = base.rstrip('/') + '/_next/data/production/products.json'
    candidates.append(guess)

print('\nCandidates to try:')
for c in candidates:
    print(' ', c)

# Try to fetch candidates
for c in candidates:
    r = try_get(c)
    if not r:
        continue
    print(f"\nTried {c} -> status {r.status_code}")
    ctype = r.headers.get('Content-Type','')
    if r.status_code == 200 and ('application/json' in ctype or r.text.strip().startswith('{')):
        print('  Looks like JSON, trying to parse...')
        try:
            data = r.json()
            print('  JSON keys:', list(data.keys())[:20])
            # try to find products inside
            def search_for_products(d, path=''):
                results = []
                if isinstance(d, dict):
                    for k, v in d.items():
                        if any(keyword in k.lower() for keyword in ['product','products','collection','collections','items','nodes','results']):
                            results.append((path + '/' + k, type(v), (len(v) if isinstance(v,(list,dict)) else None)))
                        results += search_for_products(v, path + '/' + k)
                elif isinstance(d, list):
                    for i, el in enumerate(d[:5]):
                        results += search_for_products(el, path + f'[{i}]')
                return results
            found = search_for_products(data)
            if found:
                print('  Potential product keys found:')
                for f in found[:20]:
                    print('   -', f)
            else:
                print('  No obvious product keys found in JSON')
        except Exception as e:
            print('  Failed to parse JSON:', e)
    else:
        print('  Not JSON or not available')

print('\nDone')

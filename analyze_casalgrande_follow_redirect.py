"""
Follow redirect target found in Next JSON and inspect collections
"""
import requests
import json

headers={'User-Agent':'Mozilla/5.0'}
base='https://www.casalgrandepadana.com'
build='KegsobMiXVgfNGSOn8I1q'

paths=['/de/produkte/sammlugen/','/de/produkte/sammlungen/','/de/produkte/sammlung/','/de/produkte/sammlugen','/de/produkte/sammlungen','/de/produkte/']
for p in paths:
    try:
        r=requests.get(base+p, headers=headers, timeout=15)
        print(p, r.status_code)
        if r.status_code==200:
            print('  snippet:', r.text[:300].replace('\n',' '))
    except Exception as e:
        print('  error', p, e)

# Try JSON at sammlugen
json_url = f"{base}/_next/data/{build}/de/produkte/sammlugen.json"
print('\nTrying', json_url)
try:
    r = requests.get(json_url, headers=headers, timeout=15)
    print('status', r.status_code)
    if r.status_code==200:
        data = r.json()
        print('Top keys:', list(data.keys()))
        print('\npageProps keys:', list(data.get('pageProps',{}).keys()))
        print('\nPreview of pageProps:')
        print(json.dumps(data.get('pageProps',{}), ensure_ascii=False, indent=2)[:2000])
    else:
        print('Not found')
except Exception as e:
    print('Error fetching JSON:', e)

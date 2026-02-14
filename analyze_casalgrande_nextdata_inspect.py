"""
Inspect specific Next.js data JSON for Casalgrande Padana
"""
import requests
import json

url = 'https://www.casalgrandepadana.com/_next/data/KegsobMiXVgfNGSOn8I1q/de/produkte.json'
headers = {'User-Agent': 'Mozilla/5.0'}

print('Fetching', url)
r = requests.get(url, headers=headers, timeout=15)
print('Status', r.status_code)
if r.status_code != 200:
    raise SystemExit

data = r.json()

print('\nTop-level keys:', list(data.keys()))

if 'pageProps' in data:
    pp = data['pageProps']
    print('\npageProps keys:', list(pp.keys())[:50])
    # For each key, print type and len if applicable
    for k in pp:
        v = pp[k]
        t = type(v).__name__
        if isinstance(v, (list, dict)):
            print(f"- {k}: {t}, length={len(v)}")
        else:
            print(f"- {k}: {t}")

    # Try to find nested lists that might be products
    def find_lists(obj, path=''):
        results = []
        if isinstance(obj, dict):
            for key, val in obj.items():
                results += find_lists(val, path + '/' + key)
        elif isinstance(obj, list):
            results.append((path, len(obj)))
            for i, item in enumerate(obj[:3]):
                results += find_lists(item, path + f'[{i}]')
        return results

    lists = find_lists(pp)
    print('\nFound lists in pageProps (path, len):')
    for p, l in lists[:50]:
        print(' ', p, l)

    # If there are big lists, print sample element keys
    big_lists = [p for p, l in lists if l >= 1]
    if big_lists:
        sample_path = big_lists[0]
        print('\nSample path:', sample_path)

else:
    print('No pageProps')

# Pretty print a small part for inspection
print('\nDumping small preview of pageProps:')
pp_preview = json.dumps(data.get('pageProps', {}), ensure_ascii=False, indent=2)[:3000]
print(pp_preview)

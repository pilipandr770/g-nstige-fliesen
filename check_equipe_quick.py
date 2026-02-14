import requests
from bs4 import BeautifulSoup

base = 'https://www.equipeceramicas.com/de'
headers = {'User-Agent':'Mozilla/5.0'}

def count_portfolio(url):
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, 'html.parser')
    links = {a.get('href') for a in soup.find_all('a', href=True) if '/portfolio-item/' in a.get('href')}
    return len(links), links

# collections
cols_count, cols = count_portfolio(base + '/kollektionen')
# projects
projs_count, projs = count_portfolio(base + '/projekte')

# news: look for article links on /news/
r = requests.get(base + '/news/', headers=headers, timeout=15)
r.raise_for_status()
soup = BeautifulSoup(r.content, 'html.parser')
news_links = {a.get('href') for a in soup.find_all('a', href=True) if '/de/' in a.get('href') and a.get_text(strip=True)}
news_count = len(news_links)

print('Quick counts:')
print('Collections (portfolio-item) on /kollektionen:', cols_count)
print('Projects (portfolio-item) on /projekte:', projs_count)
print('News links on /news/:', news_count)

print('\nSample collections (first 10):')
for i, l in enumerate(list(cols)[:10],1):
    print(f'{i}.', l)

print('\nSample projects (first 10):')
for i, l in enumerate(list(projs)[:10],1):
    print(f'{i}.', l)

print('\nDone')

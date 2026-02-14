"""
Отладка ссылок блога - выводим все href для анализа
"""
import requests
from bs4 import BeautifulSoup

url = 'https://www.aparici.com/de/blog'
print(f"Загрузка: {url}\n")

response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.content, 'html.parser')

all_links = soup.find_all('a', href=True)

blog_links = [link for link in all_links if '/blog/' in link.get('href', '')]

print(f"Всего ссылок с /blog/: {len(blog_links)}\n")

# Показываем первые 20
for i, link in enumerate(blog_links[:20], 1):
    href = link.get('href')
    text = link.get_text(strip=True)
    print(f"{i}. href: {href}")
    print(f"   текст: {text}")
    print(f"   parts: {href.split('/')}")
    print(f"   length: {len(href.split('/'))}")
    print()

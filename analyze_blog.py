"""
Анализ страницы новостей/блога Aparici
"""

import requests
from bs4 import BeautifulSoup

def analyze_blog():
    # Возможные URL для блога/новостей
    possible_urls = [
        'https://www.aparici.com/de/blog',
        'https://www.aparici.com/de/news',
        'https://www.aparici.com/de/neuigkeiten',
        'https://www.aparici.com/de/actualidad',
        'https://www.aparici.com/de',  # Главная
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in possible_urls:
        print(f"\n{'='*60}")
        print(f"Проверка: {url}")
        print('='*60)
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Статус: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Ищем ссылки на блог в навигации
                nav_links = soup.find_all('a', href=True)
                blog_links = [link for link in nav_links if any(word in link.get('href', '').lower() or word in link.get_text().lower() 
                                                                 for word in ['blog', 'news', 'neuigkeit', 'actualidad', 'noticia'])]
                
                if blog_links:
                    print(f"\n✓ Найдены ссылки на блог/новости:")
                    for link in blog_links[:5]:
                        print(f"  - {link.get('href')} | Текст: {link.get_text(strip=True)}")
                else:
                    print("\n⚠️  Ссылки на блог не найдены в навигации")
                
                # Проверяем наличие статей на текущей странице
                import re
                articles = soup.find_all(['article', 'div'], class_=re.compile(r'post|article|news|blog', re.I))
                
                if articles:
                    print(f"\n✓ Найдены элементы статей: {len(articles)}")
                    for i, article in enumerate(articles[:3], 1):
                        title = article.find(['h1', 'h2', 'h3', 'h4'])
                        if title:
                            print(f"  {i}. {title.get_text(strip=True)[:60]}")
                else:
                    print("\n⚠️  Статьи не найдены на этой странице")
                    
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")

if __name__ == '__main__':
    analyze_blog()

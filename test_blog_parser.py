"""
Тестирование парсера блога Aparici
"""

from app.services.manufacturer_parsers import ApariciParser

def test_blog():
    parser = ApariciParser()
    
    print("=" * 60)
    print("ТЕСТ ПАРСЕРА БЛОГА APARICI")
    print("=" * 60)
    
    blog_posts = parser.extract_blog_posts()
    
    print(f"\n📊 Результаты: найдено {len(blog_posts)} статей\n")
    
    for i, post in enumerate(blog_posts[:5], 1):
        print(f"--- Статья {i} ---")
        print(f"Название: {post['title']}")
        print(f"Изображение: {post['image_url']}")
        print(f"URL: {post['source_url']}")
        print()

if __name__ == '__main__':
    test_blog()

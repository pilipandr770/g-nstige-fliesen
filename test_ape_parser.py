"""
Тест парсера APE Grupo
"""
from app.services.manufacturer_parsers import ApeParser

print("="*80)
print("ТЕСТ ПАРСЕРА APE GRUPO")
print("="*80)

parser = ApeParser()

print("\n1. ТЕСТ ЛОГОТИПА")
print("-"*80)
logo = parser.extract_logo()
if logo:
    print(f"✓ Логотип найден: {logo}")
else:
    print("❌ Логотип не найден")

print("\n2. ТЕСТ КОЛЛЕКЦИЙ")
print("-"*80)
collections = parser.extract_collections()
print(f"\n📊 Результат: {len(collections)} коллекций")
for i, col in enumerate(collections[:3], 1):
    print(f"\n--- Коллекция {i} ---")
    print(f"Название: {col.get('title')}")
    print(f"Изображение: {col.get('image_url')}")
    print(f"URL: {col.get('source_url')}")

print("\n3. ТЕСТ ПРОЕКТОВ")
print("-"*80)
projects = parser.extract_projects()
print(f"\n📊 Результат: {len(projects)} проектов")
for i, proj in enumerate(projects[:3], 1):
    print(f"\n--- Проект {i} ---")
    print(f"Название: {proj.get('title')}")
    print(f"Изображение: {proj.get('image_url')}")
    print(f"URL: {proj.get('source_url')}")

print("\n4. ТЕСТ БЛОГА")
print("-"*80)
blog = parser.extract_blog_posts()
print(f"\n📊 Результат: {len(blog)} статей")
for i, post in enumerate(blog[:3], 1):
    print(f"\n--- Статья {i} ---")
    print(f"Название: {post.get('title')}")
    print(f"Изображение: {post.get('image_url')}")
    print(f"URL: {post.get('source_url')}")

print("\n" + "="*80)
print("ИТОГО:")
print(f"  Логотип: {'✓' if logo else '❌'}")
print(f"  Коллекции: {len(collections)}")
print(f"  Проекты: {len(projects)}")
print(f"  Блог: {len(blog)}")
print("="*80)

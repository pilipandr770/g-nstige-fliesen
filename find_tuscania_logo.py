from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from collections import Counter

app = create_app()
with app.app_context():
    tuscania = Manufacturer.query.filter_by(slug='tuscania').first()
    if tuscania:
        content = ManufacturerContent.query.filter_by(manufacturer_id=tuscania.id).all()
        print(f'Tuscania контента: {len(content)}')
        
        # Найти картинки, которые повторяются
        images = [c.image_url for c in content if c.image_url]
        image_counts = Counter(images)
        
        print(f'\nПовторяющиеся картинки (потенциальные логотипы):')
        for img_url, count in image_counts.most_common(10):
            print(f'  {count:3}x - {img_url[:100]}')
        
        # Показать первые несколько контента
        print(f'\nПервые 5 элементов контента:')
        for item in content[:5]:
            print(f'  - {item.title}: {item.image_url[:80] if item.image_url else "NO IMAGE"}')
        
        # Рекомендация
        print(f'\n\nВсего уникальных картинок: {len(image_counts)}')
        if image_counts:
            most_common = image_counts.most_common(1)[0]
            print(f'Рекомендуемый логотип: {most_common[1]}x повторений')
            print(f'  URL: {most_common[0]}')

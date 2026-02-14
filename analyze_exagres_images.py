import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app
from app.models import Manufacturer, ManufacturerContent
import os

app = create_app()
with app.app_context():
    exagres = Manufacturer.query.filter_by(slug='exagres').first()
    if exagres:
        content = ManufacturerContent.query.filter_by(manufacturer_id=exagres.id).all()
        
        print('Проверка изображений Exagres:')
        print('=' * 60)
        
        # Группируем по image_url
        image_urls = {}
        for item in content:
            if item.image_url:
                if item.image_url not in image_urls:
                    image_urls[item.image_url] = []
                image_urls[item.image_url].append(item.title)
        
        print(f'Уникальных картинок: {len(image_urls)}')
        print(f'Всего контента: {len(content)}')
        
        for img_url, titles in sorted(image_urls.items(), key=lambda x: -len(x[1])):
            count = len(titles)
            print(f'\n🖼️  {img_url}')
            print(f'   Используется в {count} коллекциях:')
            for title in titles[:5]:
                print(f'     - {title}')
            if count > 5:
                print(f'     ... и еще {count - 5} больше')
            
            # Проверим файл на диске
            filepath = os.path.join('app', 'static', 'uploads', img_url.replace('manufacturers/', ''))
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f'   Размер файла: {size} bytes')

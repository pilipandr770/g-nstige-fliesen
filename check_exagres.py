from app import create_app, db
from app.models import Manufacturer, ManufacturerContent

app = create_app()
with app.app_context():
    exagres = Manufacturer.query.filter_by(slug='exagres').first()
    if exagres:
        print(f'Exagres ID: {exagres.id}')
        content = ManufacturerContent.query.filter_by(manufacturer_id=exagres.id).all()
        print(f'Всего контента: {len(content)}')
        
        # Подсчитаем картинки
        with_images = [c for c in content if c.image_url]
        without_images = [c for c in content if not c.image_url]
        
        print(f'\nСОЖ КАРТИНОК: {len(with_images)}/{len(content)}')
        
        if without_images:
            print(f'\nБЕЗ КАРТИНОК ({len(without_images)}):')
            for item in without_images[:10]:
                print(f'  - {item.title} (type: {item.content_type})')
        
        if with_images:
            print(f'\nС КАРТИНКАМИ ({len(with_images)}):')
            for item in with_images[:5]:
                print(f'  - {item.title}: {item.image_url[:60]}...')
    else:
        print('Exagres не найден!')

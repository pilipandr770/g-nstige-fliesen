from app import create_app
from app.models import Manufacturer, ManufacturerContent

app = create_app()
with app.test_client() as client:
    with app.app_context():
        exagres = Manufacturer.query.filter_by(slug='exagres').first()
        if exagres:
            content = ManufacturerContent.query.filter_by(manufacturer_id=exagres.id).all()
            print(f'Exagres: {len(content)} items')
            
            with_images = [c for c in content if c.image_url]
            without_images = [c for c in content if not c.image_url]
            
            print(f'С картинками: {len(with_images)}')
            print(f'Без картинок: {len(without_images)}')
            
            if without_images:
                print(f'\nБЕЗ КАРТИНОК:')
                for item in without_images[:5]:
                    print(f'  - {item.title} (type: {item.content_type}, image_url: "{item.image_url}")')
        else:
            print('Exagres not found')

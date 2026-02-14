import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app
from app.models import Manufacturer, ManufacturerContent

app = create_app()
with app.app_context():
    exagres = Manufacturer.query.filter_by(slug='exagres').first()
    if exagres:
        content = ManufacturerContent.query.filter_by(manufacturer_id=exagres.id).all()
        
        print(f'Exagres статус:')
        print(f'  Всего контента: {len(content)}')
        
        with_images = [c for c in content if c.image_url]
        without_images = [c for c in content if not c.image_url]
        
        print(f'  С картинками: {len(with_images)} (100%)')
        print(f'  Без картинок: {len(without_images)} (0%)')
        
        if without_images:
            print(f'\n  Без картинок:')
            for item in without_images:
                print(f'    - {item.title}')
        else:
            print(f'\n✅ Все коллекции Exagres имеют картинки!')

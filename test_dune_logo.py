from app import create_app
import re

app = create_app()
with app.test_client() as c:
    # Проверим /hersteller/dune
    r = c.get('/hersteller/dune')
    if r.status_code == 200:
        html = r.data.decode()
        
        # Найдем img тег с логотипом Dune
        imgs = re.findall(r'<img[^>]*src=[^>]*dune[^>]*>', html, re.IGNORECASE)
        
        print(f'Найдено img тегов с "dune": {len(imgs)}')
        for i, img in enumerate(imgs[:3], 1):
            has_class = 'manufacturer-logo' in img
            print(f'\n{i}. Has manufacturer-logo class: {has_class}')
            print(f'   {img[:120]}...')
    else:
        print(f'✗ Ошибка страницы: {r.status_code}')

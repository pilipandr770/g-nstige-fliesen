"""
Полная проверка логотипа Baldocer
"""
from app import create_app, db
from app.models import Manufacturer
import os

app = create_app()

with app.app_context():
    # Проверяем БД
    baldocer = Manufacturer.query.filter_by(slug='baldocer').first()
    
    print("="*60)
    print("ПРОВЕРКА ЛОГОТИПА BALDOCER")
    print("="*60)
    
    if not baldocer:
        print("❌ Baldocer не найден в БД!")
        exit(1)
    
    print(f"\n1. База данных:")
    print(f"   Производитель: {baldocer.name}")
    print(f"   Slug: {baldocer.slug}")
    print(f"   Logo в БД: {baldocer.logo}")
    print(f"   Активен: {baldocer.active}")
    
    if not baldocer.logo:
        print("\n❌ ПРОБЛЕМА: Логотип не установлен в БД!")
        exit(1)
    
    print(f"\n   ✅ Логотип установлен в БД")
    
    # Проверяем файл
    print(f"\n2. Файловая система:")
    logo_full_path = os.path.join('app', 'static', 'uploads', baldocer.logo)
    
    if os.path.exists(logo_full_path):
        size = os.path.getsize(logo_full_path)
        print(f"   ✅ Файл существует: {logo_full_path}")
        print(f"   Размер: {size} байт ({size/1024:.2f} KB)")
        
        # Проверяем изображение
        try:
            from PIL import Image
            img = Image.open(logo_full_path)
            print(f"   Формат: {img.format}")
            print(f"   Размеры: {img.size[0]}x{img.size[1]} px")
        except Exception as e:
            print(f"   ⚠️  Не удалось прочитать изображение: {e}")
    else:
        print(f"   ❌ Файл НЕ существует: {logo_full_path}")
        exit(1)
    
    # Формируем URL как в шаблоне
    print(f"\n3. URL для шаблона:")
    template_path = 'uploads/' + baldocer.logo
    print(f"   Template path: {template_path}")
    print(f"   В браузере будет: /static/{template_path}")
    
    # Проверяем что путь правильный
    full_web_path = f"/static/uploads/{baldocer.logo}"
    print(f"   Полный web путь: {full_web_path}")
    
    print(f"\n{'='*60}")
    print("✅ ВСЕ В ПОРЯДКЕ!")
    print(f"{'='*60}")
    print("\nЕсли логотип не виден на сайте:")
    print("1. Обновите страницу (Ctrl+R)")
    print("2. Очистите кэш браузера (Ctrl+Shift+R)")
    print("3. Перезапустите сервер Flask")
    print("4. Проверьте консоль браузера на ошибки 404")

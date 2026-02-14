"""
Скрипт для очистки и пересинхронизации контента производителя
"""

import sys
from app import create_app, db
from app.models import Manufacturer, ManufacturerContent

def clear_manufacturer_content(manufacturer_slug):
    """Удаляет весь контент производителя"""
    app = create_app()
    with app.app_context():
        manufacturer = Manufacturer.query.filter_by(slug=manufacturer_slug).first()
        
        if not manufacturer:
            print(f"❌ Производитель '{manufacturer_slug}' не найден")
            return
        
        print(f"\n🗑️  Очистка контента для {manufacturer.name}...")
        
        # Подсчитываем что будет удалено
        content_count = ManufacturerContent.query.filter_by(manufacturer_id=manufacturer.id).count()
        
        if content_count == 0:
            print("   ℹ️  Контент отсутствует, нечего удалять")
            return
        
        # Удаляем
        ManufacturerContent.query.filter_by(manufacturer_id=manufacturer.id).delete()
        db.session.commit()
        
        print(f"   ✅ Удалено {content_count} элементов контента")
        print(f"\n💡 Теперь используйте кнопку 'Inhalt synchronisieren' в админ-панели")
        print(f"   или перейдите по адресу:")
        print(f"   http://127.0.0.1:5000/admin/manufacturers/{manufacturer.id}/sync")

def show_content_stats(manufacturer_slug):
    """Показывает статистику контента производителя"""
    app = create_app()
    with app.app_context():
        manufacturer = Manufacturer.query.filter_by(slug=manufacturer_slug).first()
        
        if not manufacturer:
            print(f"❌ Производитель '{manufacturer_slug}' не найден")
            return
        
        print(f"\n📊 Статистика контента для {manufacturer.name}:")
        print("=" * 60)
        
        # Коллекции
        collections = ManufacturerContent.query.filter_by(
            manufacturer_id=manufacturer.id,
            content_type='collection'
        ).all()
        
        collections_with_images = [c for c in collections if c.image_url]
        collections_without_images = [c for c in collections if not c.image_url]
        
        print(f"\n📦 Коллекции:")
        print(f"   Всего: {len(collections)}")
        print(f"   ✓ С изображениями: {len(collections_with_images)}")
        print(f"   ⚠️  Без изображений: {len(collections_without_images)}")
        
        if collections_without_images:
            print(f"\n   Коллекции без изображений:")
            for c in collections_without_images[:5]:
                print(f"      - {c.title}")
        
        # Проекты
        projects = ManufacturerContent.query.filter_by(
            manufacturer_id=manufacturer.id,
            content_type='project'
        ).all()
        
        projects_with_images = [p for p in projects if p.image_url]
        projects_without_images = [p for p in projects if not p.image_url]
        
        print(f"\n🏗️  Проекты:")
        print(f"   Всего: {len(projects)}")
        print(f"   ✓ С изображениями: {len(projects_with_images)}")
        print(f"   ⚠️  Без изображений: {len(projects_without_images)}")
        
        # Блог
        blog_posts = ManufacturerContent.query.filter_by(
            manufacturer_id=manufacturer.id,
            content_type='blog'
        ).count()
        
        print(f"\n📝 Статьи блога: {blog_posts}")
        
        print("\n" + "=" * 60)

def list_all_manufacturers():
    """Показывает список всех производителей"""
    app = create_app()
    with app.app_context():
        manufacturers = Manufacturer.query.order_by(Manufacturer.name).all()
        
        print("\n📋 Список производителей:")
        print("=" * 60)
        
        for m in manufacturers:
            content_count = ManufacturerContent.query.filter_by(manufacturer_id=m.id).count()
            last_sync = m.last_sync.strftime('%Y-%m-%d %H:%M') if m.last_sync else 'Никогда'
            
            print(f"\n{m.name} ({m.slug})")
            print(f"   Контент: {content_count} элементов")
            print(f"   Последняя синхронизация: {last_sync}")
            print(f"   Сайт: {m.website}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\n📖 Использование:")
        print("   python manage_content.py list              - показать всех производителей")
        print("   python manage_content.py stats <slug>      - статистика контента")
        print("   python manage_content.py clear <slug>      - очистить контент")
        print("\n📌 Примеры:")
        print("   python manage_content.py list")
        print("   python manage_content.py stats aparici")
        print("   python manage_content.py clear aparici")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'list':
        list_all_manufacturers()
    elif command == 'stats':
        if len(sys.argv) < 3:
            print("❌ Укажите slug производителя")
            sys.exit(1)
        show_content_stats(sys.argv[2])
    elif command == 'clear':
        if len(sys.argv) < 3:
            print("❌ Укажите slug производителя")
            sys.exit(1)
        
        slug = sys.argv[2]
        print(f"\n⚠️  ВНИМАНИЕ: Будет удален весь контент производителя '{slug}'")
        confirm = input("   Продолжить? (yes/no): ")
        
        if confirm.lower() in ['yes', 'y', 'да']:
            clear_manufacturer_content(slug)
        else:
            print("   Отменено")
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("   Используйте: list, stats, clear")

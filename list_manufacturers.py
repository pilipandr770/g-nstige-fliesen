"""
Показываем список всех производителей и статус их парсеров
"""
from app import create_app, db
from app.models import Manufacturer, ManufacturerContent

app = create_app()

with app.app_context():
    manufacturers = Manufacturer.query.filter_by(active=True).order_by(Manufacturer.name).all()
    
    print(f"\n{'='*80}")
    print(f"ПРОИЗВОДИТЕЛИ В СИСТЕМЕ: {len(manufacturers)}")
    print(f"{'='*80}\n")
    
    for idx, m in enumerate(manufacturers, 1):
        # Проверяем наличие парсера
        parser_status = "❌ Нет парсера"
        if m.slug in ['aparici', 'dune', 'equipe']:
            parser_status = "✅ Есть парсер"
        
        # Проверяем наличие логотипа
        logo_status = "✅" if m.logo else "❌"
        
        # Проверяем контент
        collections = ManufacturerContent.query.filter_by(
            manufacturer_id=m.id, 
            content_type='collection'
        ).count()
        
        projects = ManufacturerContent.query.filter_by(
            manufacturer_id=m.id, 
            content_type='project'
        ).count()
        
        blog = ManufacturerContent.query.filter_by(
            manufacturer_id=m.id, 
            content_type='blog'
        ).count()
        
        print(f"{idx}. {m.name} ({m.slug})")
        print(f"   Сайт: {m.website}")
        print(f"   Парсер: {parser_status}")
        print(f"   Логотип: {logo_status}")
        print(f"   Контент: {collections} коллекций, {projects} проектов, {blog} блог")
        print()

"""
Скрипт миграции базы данных для добавления системы производителей.

Выполняет:
1. Создание таблицы manufacturers
2. Создание таблицы manufacturer_content
3. Добавление новых полей в таблицу blog_posts
"""

from app import create_app, db

def migrate_database():
    app = create_app()
    with app.app_context():
        print("🔧 Начало миграции базы данных...")
        
        try:
            # Создаем все новые таблицы
            db.create_all()
            print("✅ Таблицы созданы/обновлены")
            
            # Добавление новых колонок в существующую таблицу blog_posts
            # Примечание: SQLAlchemy create_all() не добавляет новые колонки в существующие таблицы
            # Нужно выполнить ALTER TABLE вручную
            
            from sqlalchemy import text
            
            # Проверяем и добавляем колонки в BlogPost
            inspector = db.inspect(db.engine)
            blog_columns = [col['name'] for col in inspector.get_columns('blog_posts')]
            
            if 'category' not in blog_columns:
                print("➕ Добавление колонки 'category' в blog_posts...")
                db.session.execute(text('ALTER TABLE blog_posts ADD COLUMN category VARCHAR(100)'))
                db.session.commit()
                print("✅ Колонка 'category' добавлена")
            
            if 'manufacturer_id' not in blog_columns:
                print("➕ Добавление колонки 'manufacturer_id' в blog_posts...")
                db.session.execute(text('ALTER TABLE blog_posts ADD COLUMN manufacturer_id INTEGER'))
                db.session.commit()
                print("✅ Колонка 'manufacturer_id' добавлена")
            
            if 'image_url' not in blog_columns:
                print("➕ Добавление колонки 'image_url' в blog_posts...")
                db.session.execute(text('ALTER TABLE blog_posts ADD COLUMN image_url VARCHAR(500)'))
                db.session.commit()
                print("✅ Колонка 'image_url' добавлена")
            
            if 'published' not in blog_columns:
                print("➕ Добавление колонки 'published' в blog_posts...")
                db.session.execute(text('ALTER TABLE blog_posts ADD COLUMN published BOOLEAN DEFAULT TRUE'))
                db.session.commit()
                print("✅ Колонка 'published' добавлена")
            
            # Добавление foreign key constraint (опционально)
            # db.session.execute(text(
            #     'ALTER TABLE blog_posts ADD CONSTRAINT fk_blog_manufacturer '
            #     'FOREIGN KEY (manufacturer_id) REFERENCES manufacturers (id)'
            # ))
            
            print("\n🎉 Миграция завершена успешно!")
            print("\nТеперь вы можете:")
            print("1. Войти в админ-панель: http://localhost:5000/admin")
            print("2. Перейти в раздел 'Hersteller'")
            print("3. Добавить производителей и синхронизировать их контент")
            
        except Exception as e:
            print(f"❌ Ошибка при миграции: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_database()

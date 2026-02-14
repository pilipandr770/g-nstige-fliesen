"""
Скрипт для создания тестовых производителей
"""

from app import create_app, db
from app.models import Manufacturer

def create_test_manufacturers():
    app = create_app()
    with app.app_context():
        print("🏭 Создание тестовых производителей...")
        
        # Проверяем, есть ли уже производители
        existing = Manufacturer.query.count()
        if existing > 0:
            print(f"⚠️  Уже есть {existing} производителей в базе")
            response = input("Хотите удалить существующих и создать новых? (y/n): ")
            if response.lower() != 'y':
                print("❌ Отменено")
                return
            Manufacturer.query.delete()
            db.session.commit()
            print("🗑️  Существующие производители удалены")
        
        manufacturers_data = [
            {
                'name': 'Aparici',
                'slug': 'aparici',
                'website': 'https://www.aparici.com/de',
                'description': 'Spanischer Hersteller von Design-Keramikfliesen seit 1961. Bekannt für innovative Designs und Oberflächenbearbeitungen.',
                'country': 'Spanien',
                'order': 1,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'APE Grupo',
                'slug': 'ape',
                'website': 'https://www.apegrupo.com/de',
                'description': 'Spanische Unternehmensgruppe mit vielseitigen Keramikkollektionen für jeden Stil.',
                'country': 'Spanien',
                'order': 2,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'La Fabbrica / AVA',
                'slug': 'lafabbrica',
                'website': 'https://www.lafabbrica.it/de',
                'description': 'Italienischer Premium-Hersteller von Feinsteinzeug mit eleganten Designs inspiriert von Natur und Luxus.',
                'country': 'Italien',
                'order': 3,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Baldocer',
                'slug': 'baldocer',
                'website': 'https://baldocer.com',
                'description': 'Spanischer Fliesenhersteller mit über 30 Jahren Erfahrung. Spezialisiert auf Porzellan und Großformat-Fliesen.',
                'country': 'Spanien',
                'order': 4,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Casalgrande Padana',
                'slug': 'casalgrande',
                'website': 'https://www.casalgrandepadana.de',
                'description': 'Italienischer Hersteller hochwertiger Feinsteinzeugfliesen mit Fokus auf architektonische Lösungen.',
                'country': 'Italien',
                'order': 5,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Distrimat',
                'slug': 'distrimat',
                'website': 'https://www.distrimat.es/en',
                'description': 'Spanischer Vertriebspartner und Hersteller mit breiter Palette an Keramikprodukten.',
                'country': 'Spanien',
                'order': 6,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Dune Ceramics',
                'slug': 'dune',
                'website': 'https://duneceramics.com/de',
                'description': 'Designer von Boden- und Wandfliesen mit Fokus auf einzigartige Projekte und trendige Designs.',
                'country': 'Spanien',
                'order': 7,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Equipe Ceramicas',
                'slug': 'equipe',
                'website': 'https://www.equipeceramicas.com/de',
                'description': 'Weltweit führend auf dem Markt für Wand- und Bodenfliesen im Kleinformat. "Small tiles, big design".',
                'country': 'Spanien',
                'order': 8,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Estudi Ceramico',
                'slug': 'estudi-ceramico',
                'website': 'https://eceramico.com/en',
                'description': 'Spanisches Keramikstudio mit innovativen und kreativen Fliesenlösungen.',
                'country': 'Spanien',
                'order': 9,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Etile',
                'slug': 'etile',
                'website': 'https://de.etile.es',
                'description': 'Spanischer Hersteller dekorativer Keramikfliesen mit mediterranem Charakter.',
                'country': 'Spanien',
                'order': 10,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Exagres',
                'slug': 'exagres',
                'website': 'https://www.exagres.es/en',
                'description': 'Spanischer Keramikhersteller mit modernen und klassischen Kollektionen.',
                'country': 'Spanien',
                'order': 11,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Gazzini',
                'slug': 'gazzini',
                'website': 'https://www.ceramicagazzini.it/de',
                'description': 'Italienische Keramikmanufaktur mit Tradition und hoher Handwerkskunst.',
                'country': 'Italien',
                'order': 12,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Halcon Ceramicas',
                'slug': 'halcon',
                'website': 'https://www.halconceramicas.com',
                'description': 'Spanischer Hersteller mit über 60 Jahren Erfahrung. Produkte mit Charakter für alle Bedürfnisse.',
                'country': 'Spanien',
                'order': 13,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Novoceram',
                'slug': 'novoceram',
                'website': 'https://www.novoceram.fr',
                'description': 'Französischer Hersteller seit 1863. Interpretiert die Werte der französischen Eleganz mit Feinsteinzeug.',
                'country': 'Frankreich',
                'order': 14,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Roced',
                'slug': 'roced',
                'website': 'https://roced.es',
                'description': 'Spanischer Keramikhersteller mit modernen Designs und technischen Innovationen.',
                'country': 'Spanien',
                'order': 15,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Tuscania',
                'slug': 'tuscania',
                'website': 'https://tuscaniagres.it',
                'description': 'Italienischer Hersteller von Feinsteinzeug mit toskanischer Handwerkskunst und Design.',
                'country': 'Italien',
                'order': 16,
                'active': True,
                'auto_sync': False
            },
            {
                'name': 'Unicom Starker',
                'slug': 'unicom-starker',
                'website': 'https://www.unicomstarker.com/home',
                'description': 'Italienische Marke der Gruppo Ceramiche Ricchetti mit hochwertigen technischen Keramiklösungen.',
                'country': 'Italien',
                'order': 17,
                'active': True,
                'auto_sync': False
            }
        ]
        
        for data in manufacturers_data:
            manufacturer = Manufacturer(**data)
            db.session.add(manufacturer)
            print(f"✅ {data['name']} добавлен")
        
        db.session.commit()
        
        print(f"\n🎉 Успешно создано {len(manufacturers_data)} производителей!")
        print("\n📝 Следующие шаги:")
        print("1. Обновите страницу /admin/manufacturers")
        print("2. Нажмите кнопку 🔄 напротив любого производителя для синхронизации")
        print("3. Посетите /hersteller для просмотра публичной страницы")

if __name__ == "__main__":
    create_test_manufacturers()

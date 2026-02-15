import os
import click
from sqlalchemy import text
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    
    # Convert DATABASE_URL to use psycopg driver for SQLAlchemy
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    
    schema = os.getenv("DB_SCHEMA")
    engine_options = {
        "pool_pre_ping": True,  # Test connections before using
        "pool_recycle": 300,    # Recycle connections after 5 minutes
        "pool_size": 5,         # Connection pool size
        "max_overflow": 2,      # Allow 2 extra connections when pool is full
        "connect_args": {}
    }
    
    if schema:
        engine_options["connect_args"]["options"] = f"-csearch_path={schema}"
    
    # Add SSL configuration for PostgreSQL (fixes SSL decryption errors)
    engine_options["connect_args"]["sslmode"] = "require"
    
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Flask-Login setup
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Bitte melden Sie sich an."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    from .routes import public_routes, admin_routes, api_routes, auth_routes
    app.register_blueprint(public_routes)
    app.register_blueprint(admin_routes, url_prefix="/admin")
    app.register_blueprint(api_routes, url_prefix="/api")
    app.register_blueprint(auth_routes, url_prefix="/auth")

    with app.app_context():
        if schema:
            with db.engine.begin() as connection:
                connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        from . import models
        db.create_all()

    # CLI command: flask create-admin
    @app.cli.command("create-admin")
    @click.option("--username", default="admin", help="Admin username")
    @click.option("--email", default="admin@fliesen-showroom.de", help="Admin email")
    @click.option("--password", default="admin123", help="Admin password")
    def create_admin(username, email, password):
        """Create an admin user."""
        from .models import User
        with app.app_context():
            if User.query.filter_by(username=username).first():
                click.echo(f"User '{username}' already exists.")
                return
            user = User(username=username, email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            click.echo(f"Admin '{username}' created successfully!")

    # CLI command: flask seed-manufacturers
    @app.cli.command("seed-manufacturers")
    def seed_manufacturers():
        """Create or update the default manufacturer list."""
        from .models import Manufacturer

        manufacturers = [
            {"name": "Aparici", "slug": "aparici", "website": "https://www.aparici.com/de"},
            {"name": "APE", "slug": "ape", "website": "https://www.apegrupo.com/de/"},
            {"name": "La Fabbrica / AVA", "slug": "lafabbrica", "website": "https://www.lafabbrica.it/de/"},
            {"name": "Baldocer", "slug": "baldocer", "website": "https://baldocer.com/"},
            {"name": "Casalgrande", "slug": "casalgrande", "website": "https://www.casalgrandepadana.de/"},
            {"name": "Distrimat", "slug": "distrimat", "website": "https://www.distrimat.es/en/"},
            {"name": "Dune", "slug": "dune", "website": "https://duneceramics.com/de"},
            {"name": "Equipe", "slug": "equipe", "website": "https://www.equipeceramicas.com/de/"},
            {"name": "Estudi Ceramico", "slug": "estudi-ceramico", "website": "https://eceramico.com/en/"},
            {"name": "Etile", "slug": "etile", "website": "https://de.etile.es/"},
            {"name": "Exagres", "slug": "exagres", "website": "https://www.exagres.es/en/"},
            {"name": "Gazzini", "slug": "gazzini", "website": "https://www.ceramicagazzini.it/de/"},
            {"name": "Halcon", "slug": "halcon", "website": "https://www.halconceramicas.com/"},
            {"name": "Novoceram", "slug": "novoceram", "website": "https://www.novoceram.fr/"},
            {"name": "Roced", "slug": "roced", "website": "https://roced.es/"},
            {"name": "Tuscania", "slug": "tuscania", "website": "https://tuscaniagres.it/"},
            {"name": "Unicomstarker", "slug": "unicom-starker", "website": "https://www.unicomstarker.com/home"},
        ]

        created = 0
        updated = 0
        for order, data in enumerate(manufacturers, start=1):
            existing = Manufacturer.query.filter_by(slug=data["slug"]).first()
            if existing:
                existing.name = data["name"]
                existing.website = data["website"]
                existing.active = True
                existing.auto_sync = True
                existing.order = order
                updated += 1
            else:
                manufacturer = Manufacturer(
                    name=data["name"],
                    slug=data["slug"],
                    website=data["website"],
                    active=True,
                    auto_sync=True,
                    order=order,
                )
                db.session.add(manufacturer)
                created += 1

        db.session.commit()
        click.echo(f"Manufacturers created: {created}, updated: {updated}.")

    # CLI command: flask generate-blog
    @app.cli.command("generate-blog")
    @click.option("--count", default=1, help="Number of articles to generate")
    @click.option("--category", default=None, help="Article category")
    @click.option("--manufacturer", default=None, help="Manufacturer slug")
    @click.option("--dry-run", is_flag=True, help="Preview without saving")
    @click.option("--force", is_flag=True, help="Run even if auto generation is disabled")
    def generate_blog(count, category, manufacturer, dry_run, force):
        """Generate blog articles using AI from collected news."""
        from .services.blog_generator_service import get_blog_generator
        from .models import ChatConfig
        from .models import BlogPost
        from datetime import datetime

        if not force:
            auto_enabled = ChatConfig.get("blog_auto_enabled", "off") == "on"
            auto_days_value = ChatConfig.get("blog_auto_days", "1,3,5")
            auto_days = {d.strip() for d in auto_days_value.split(",") if d.strip()}
            today = str(datetime.utcnow().isoweekday())
            if not auto_enabled:
                click.echo("Auto generation disabled. Skipping.")
                return
            if auto_days and today not in auto_days:
                click.echo("Auto generation not scheduled for today. Skipping.")
                return

        # Check if auto generation is enabled (skip check for manual CLI runs)
        generator = get_blog_generator()

        if dry_run:
            click.echo(f"DRY RUN: Would generate {count} article(s)")
            if manufacturer:
                result = generator.generate_from_topic(
                    f"Neuigkeiten von {manufacturer}",
                    category
                )
            else:
                topics = generator._get_fallback_topics()
                result = generator.generate_from_topic(topics[0], category)

            if 'error' in result:
                click.echo(f"Error: {result['error']}")
            else:
                click.echo(f"Title: {result.get('title', '')}")
                click.echo(f"Category: {result.get('category', '')}")
                click.echo(f"Tags: {result.get('tags', '')}")
                click.echo(f"Tokens: {result.get('tokens_used', 0)}")
            return

        results = generator.auto_generate(count=count)
        auto_publish = ChatConfig.get("blog_auto_publish", "off") == "on"
        published_count = 0
        if auto_publish:
            for r in results:
                if not r.get('success'):
                    continue
                post = BlogPost.query.get(r.get('id'))
                if post and not post.published:
                    post.published = True
                    post.status = 'published'
                    post.published_at = datetime.utcnow()
                    published_count += 1
            db.session.commit()
        for r in results:
            if r.get('success'):
                click.echo(f"Created: {r['title']} (ID: {r['id']})")
            else:
                click.echo(f"Error: {r.get('error', 'Unknown')}")

        click.echo(f"\nDone: {sum(1 for r in results if r.get('success'))}/{count} articles generated.")
        if auto_publish:
            click.echo(f"Published: {published_count}")

    # CLI command: flask fetch-news
    @app.cli.command("fetch-news")
    def fetch_news():
        """Fetch latest news from all configured sources."""
        from .services.news_scraper_service import get_news_scraper

        scraper = get_news_scraper()
        items = scraper.fetch_all_news()
        click.echo(f"Fetched {len(items)} news items from active sources.")
        for item in items[:5]:
            click.echo(f"  - {item.get('title', 'No title')[:60]}")

    # CLI command: flask publish-scheduled
    @app.cli.command("publish-scheduled")
    def publish_scheduled():
        """Publish blog posts that are scheduled for now or earlier."""
        from .models import BlogPost
        from datetime import datetime

        posts = BlogPost.query.filter(
            BlogPost.status == 'scheduled',
            BlogPost.scheduled_at <= datetime.utcnow()
        ).all()

        count = 0
        for post in posts:
            post.published = True
            post.status = 'published'
            post.published_at = datetime.utcnow()
            count += 1

        db.session.commit()
        click.echo(f"Published {count} scheduled post(s).")

    # CLI command: flask queue-auto-sync
    @app.cli.command("queue-auto-sync")
    def queue_auto_sync():
        """Queue auto-sync for all active manufacturers with auto_sync enabled."""
        from .models import Manufacturer, ManufacturerSyncJob
        from .services.sync_queue import get_sync_queue
        from .services.sync_jobs import run_manufacturer_sync

        queue = get_sync_queue()
        if not queue:
            click.echo("REDIS_URL is not set. Queue not available.")
            return

        manufacturers = Manufacturer.query.filter_by(active=True, auto_sync=True).order_by(Manufacturer.order).all()
        queued = 0
        skipped = 0

        for manufacturer in manufacturers:
            existing = ManufacturerSyncJob.query.filter(
                ManufacturerSyncJob.manufacturer_id == manufacturer.id,
                ManufacturerSyncJob.status.in_(["queued", "running"]),
            ).first()
            if existing:
                skipped += 1
                continue

            job = ManufacturerSyncJob(manufacturer_id=manufacturer.id, status="queued")
            db.session.add(job)
            db.session.commit()

            rq_job = queue.enqueue(run_manufacturer_sync, job.id)
            job.rq_job_id = rq_job.id
            db.session.commit()
            queued += 1

        click.echo(f"Queued: {queued}, skipped: {skipped}")

    # Статичные логотипы производителей — вшиты в код, не зависят от БД
    MANUFACTURER_LOGOS = {
        'aparici':          'manufacturers/aparici_8b8cce0928.gif',
        'ape':              'manufacturers/ape_cfd2dad717.svg',
        'lafabbrica':       'manufacturers/lafabbrica_d2d1fa5492.png',
        'baldocer':         'manufacturers/baldocer_d14b8028fe.png',
        'casalgrande':      'manufacturers/casalgrande_679b1723dc.jpg',
        'distrimat':        'manufacturers/distrimat_e5ec30a1d3.png',
        'dune':             'manufacturers/dune_1131c5db6b.png',
        'equipe':           'manufacturers/equipe_adbdedc5d9.png',
        'estudi-ceramico':  'manufacturers/estudi-ceramico_252c218fcc.svg',
        'etile':            'manufacturers/etile_1324a28845.png',
        'exagres':          'manufacturers/exagres_cfe6fb02d8.png',
        'gazzini':          'manufacturers/gazzini_51c2b0973c.ico',
        'halcon':           'manufacturers/halcon_7d53c05499.png',
        'novoceram':        'manufacturers/novoceram_1b957a28fe.png',
        'roced':            'manufacturers/roced_8307875706.jpg',
        'tuscania':         'manufacturers/tuscania_2920fd3bc3.png',
        'unicom-starker':   'manufacturers/unicom-starker_11d58c949a.png',
    }

    # Context processor for global template variables
    @app.context_processor
    def inject_globals():
        from .models import SocialLink
        social_links = SocialLink.query.order_by(SocialLink.order).all()
        return {
            "social_links": social_links,
            "manufacturer_logos": MANUFACTURER_LOGOS,
        }

    return app
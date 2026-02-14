from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import Page, BlogPost, ContentSource, ChatLog, User, ChatConfig, SocialLink, CarouselImage, HeroImage, Collection, Manufacturer, ManufacturerContent
from .services.chat_service import get_chat_service
from .services.content_scraper_service import scraper_service
from . import db
import requests
import os
from datetime import datetime
from werkzeug.utils import secure_filename

public_routes = Blueprint("public", __name__)
admin_routes = Blueprint("admin", __name__)
api_routes = Blueprint("api", __name__)
auth_routes = Blueprint("auth", __name__)

# ---------------------- PUBLIC ----------------------

@public_routes.route("/")
def home():
    page = Page.query.filter_by(slug="home").first()
    carousel_images = CarouselImage.query.filter_by(active=True).order_by(CarouselImage.order).all()
    hero_image = HeroImage.query.first()
    collections = Collection.query.filter_by(active=True).order_by(Collection.order).all()
    return render_template("public/home.html", page=page, carousel_images=carousel_images, hero_image=hero_image, collections=collections)

@public_routes.route("/blog")
def blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("public/blog.html", posts=posts)

@public_routes.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    success = False
    if request.method == "POST":
        # For now just show a success message
        # Later: save to DB or send email
        success = True
    return render_template("public/kontakt.html", success=success)

@public_routes.route("/impressum")
def impressum():
    return render_template("public/impressum.html")

@public_routes.route("/agb")
def agb():
    return render_template("public/agb.html")

@public_routes.route("/datenschutz")
def datenschutz():
    return render_template("public/datenschutz.html")

@public_routes.route("/hersteller")
def manufacturers():
    """Страница со списком всех производителей"""
    manufacturers = Manufacturer.query.filter_by(active=True).order_by(Manufacturer.order).all()
    return render_template("public/manufacturers.html", manufacturers=manufacturers)

@public_routes.route("/hersteller/<slug>")
def manufacturer_detail(slug):
    """Детальная страница производителя с его контентом"""
    manufacturer = Manufacturer.query.filter_by(slug=slug, active=True).first_or_404()
    
    # Получаем контент производителя по категориям
    # ВАЖНО: показываем только контент с изображениями (убираем пустые карточки)
    collections = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='collection',
        published=True
    ).filter(ManufacturerContent.image_url.isnot(None), ManufacturerContent.image_url != '').order_by(ManufacturerContent.order).limit(12).all()
    
    projects = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='project',
        published=True
    ).filter(ManufacturerContent.image_url.isnot(None), ManufacturerContent.image_url != '').order_by(ManufacturerContent.created_at.desc()).limit(6).all()
    
    blog_posts = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='blog',
        published=True
    ).order_by(ManufacturerContent.created_at.desc()).limit(4).all()
    
    return render_template("public/manufacturer_detail.html",
                         manufacturer=manufacturer,
                         collections=collections,
                         projects=projects,
                         blog_posts=blog_posts)

@public_routes.route("/hersteller/<slug>/<content_type>")
def manufacturer_content_list(slug, content_type):
    """Список всего контента определенного типа для производителя"""
    manufacturer = Manufacturer.query.filter_by(slug=slug, active=True).first_or_404()
    
    content = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type=content_type,
        published=True
    ).order_by(ManufacturerContent.created_at.desc()).all()
    
    return render_template("public/manufacturer_content_list.html",
                         manufacturer=manufacturer,
                         content=content,
                         content_type=content_type)

@public_routes.route("/hersteller/<slug>/content/<int:content_id>")
def manufacturer_content_detail(slug, content_id):
    """Детальная страница контента производителя"""
    manufacturer = Manufacturer.query.filter_by(slug=slug, active=True).first_or_404()
    content = ManufacturerContent.query.filter_by(
        id=content_id,
        manufacturer_id=manufacturer.id,
        published=True
    ).first_or_404()
    
    # Увеличиваем счетчик просмотров
    content.views += 1
    db.session.commit()
    
    # Получаем похожий контент того же типа
    related_content = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type=content.content_type,
        published=True
    ).filter(ManufacturerContent.id != content_id).order_by(ManufacturerContent.created_at.desc()).limit(3).all()
    
    return render_template("public/manufacturer_content_detail.html",
                         manufacturer=manufacturer,
                         content=content,
                         related_content=related_content)

# ---------------------- AUTH ----------------------

@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            flash(f"Willkommen, {user.username}!", "success")
            return redirect(next_page or url_for("admin.dashboard"))
        else:
            flash("Ungültiger Benutzername oder Passwort.", "danger")

    return render_template("admin/login.html")

@auth_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Erfolgreich abgemeldet.", "success")
    return redirect(url_for("public.home"))

# ---------------------- ADMIN ----------------------

@admin_routes.before_request
@login_required
def admin_before_request():
    """Protect all admin routes — require login."""
    if not current_user.is_admin:
        flash("Zugang verweigert.", "danger")
        return redirect(url_for("public.home"))

@admin_routes.route("/")
def dashboard():
    page_count = Page.query.count()
    blog_count = BlogPost.query.count()
    source_count = ContentSource.query.count()
    chat_count = ChatLog.query.count()
    recent_chats = ChatLog.query.order_by(ChatLog.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html",
                           page_count=page_count,
                           blog_count=blog_count,
                           source_count=source_count,
                           chat_count=chat_count,
                           recent_chats=recent_chats)

@admin_routes.route("/pages", methods=["GET", "POST"])
def manage_pages():
    if request.method == "POST":
        slug = request.form["slug"]
        title = request.form["title"]
        content = request.form["content"]

        page = Page.query.filter_by(slug=slug).first()
        if not page:
            page = Page(slug=slug, title=title, content=content)
            db.session.add(page)
        else:
            page.title = title
            page.content = content

        db.session.commit()
        flash("Seite gespeichert!", "success")
        return redirect(url_for("admin.manage_pages"))

    pages = Page.query.all()
    return render_template("admin/pages.html", pages=pages)

@admin_routes.route("/pages/delete/<int:page_id>")
def delete_page(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    flash("Seite gelöscht.", "success")
    return redirect(url_for("admin.manage_pages"))

@admin_routes.route("/blog", methods=["GET", "POST"])
def manage_blog():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        source_url = request.form.get("source_url")

        post = BlogPost(title=title, content=content, source_url=source_url)
        db.session.add(post)
        db.session.commit()
        flash("Blogbeitrag veröffentlicht!", "success")
        return redirect(url_for("admin.manage_blog"))

    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("admin/blog.html", posts=posts)

@admin_routes.route("/blog/delete/<int:post_id>")
def delete_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Blogbeitrag gelöscht.", "success")
    return redirect(url_for("admin.manage_blog"))

@admin_routes.route("/sources", methods=["GET", "POST"])
def manage_sources():
    if request.method == "POST":
        url = request.form["url"]
        source = ContentSource(url=url)
        db.session.add(source)
        db.session.commit()
        flash("Quelle hinzugefügt!", "success")
        return redirect(url_for("admin.manage_sources"))

    sources = ContentSource.query.all()
    return render_template("admin/sources.html", sources=sources)

@admin_routes.route("/sources/delete/<int:source_id>")
def delete_source(source_id):
    source = ContentSource.query.get_or_404(source_id)
    db.session.delete(source)
    db.session.commit()
    flash("Quelle gelöscht.", "success")
    return redirect(url_for("admin.manage_sources"))

@admin_routes.route("/chatbot", methods=["GET", "POST"])
def manage_chatbot():
    if request.method == "POST":
        instructions = request.form.get("chatbot_instructions", "").strip()
        ChatConfig.set("chatbot_instructions", instructions, "Zusätzliche Anweisungen für den Chatbot")
        flash("Chatbot-Anweisungen aktualisiert!", "success")
        return redirect(url_for("admin.manage_chatbot"))

    instructions = ChatConfig.get("chatbot_instructions", "")
    return render_template("admin/chatbot.html", instructions=instructions)

@admin_routes.route("/chat-history")
def chat_history():
    page = request.args.get("page", 1, type=int)
    chats = ChatLog.query.order_by(ChatLog.created_at.desc()).paginate(page=page, per_page=20)
    return render_template("admin/chat_history.html", chats=chats)

# ---------------------- COLLECTIONS MANAGEMENT ----------------------

@admin_routes.route("/collections", methods=["GET", "POST"])
@login_required
def manage_collections():
    if request.method == "POST":
        collection_id = request.form.get("collection_id", "").strip()
        title = request.form.get("title", "").strip()
        subtitle = request.form.get("subtitle", "").strip()
        description = request.form.get("description", "").strip()
        link_url = request.form.get("link_url", "").strip()
        
        if not title:
            flash("Titel ist erforderlich.", "danger")
            return redirect(url_for("admin.manage_collections"))

        # Get or create collection
        if collection_id and collection_id.isdigit():
            collection = Collection.query.get(int(collection_id))
            is_new = False
        else:
            collection = None
            is_new = True
        
        if not collection:
            collection = Collection(title=title, subtitle=subtitle, description=description, link_url=link_url)
            is_new = True
        else:
            collection.title = title
            collection.subtitle = subtitle
            collection.description = description
            collection.link_url = link_url

        # Handle file upload
        if "file" in request.files and request.files["file"].filename:
            file = request.files["file"]
            
            allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
            if not ("." in file.filename and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions):
                flash("Nur Bilddateien erlaubt (PNG, JPG, GIF, WebP).", "danger")
                return redirect(url_for("admin.manage_collections"))

            os.makedirs("app/static/uploads", exist_ok=True)
            
            # Delete old file if exists
            if collection.filename:
                old_path = os.path.join("app/static/uploads", collection.filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            filename = secure_filename(file.filename)
            filename = f"{datetime.now().timestamp()}_{filename}"
            filepath = os.path.join("app/static/uploads", filename)
            file.save(filepath)
            collection.filename = filename

        db.session.add(collection)
        db.session.commit()
        flash("Kollektion erfolgreich gespeichert!", "success")
        return redirect(url_for("admin.manage_collections"))

    collections = Collection.query.order_by(Collection.order).all()
    return render_template("admin/collections.html", collections=collections)

@admin_routes.route("/collections/delete/<int:collection_id>")
@login_required
def delete_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    
    # Delete file
    if collection.filename:
        filepath = os.path.join("app/static/uploads", collection.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(collection)
    db.session.commit()
    flash("Kollektion gelöscht.", "success")
    return redirect(url_for("admin.manage_collections"))

@admin_routes.route("/social-links", methods=["GET", "POST"])
@login_required
def manage_social_links():
    PLATFORMS = {
        "facebook": {"name": "Facebook", "icon": "bi-facebook"},
        "instagram": {"name": "Instagram", "icon": "bi-instagram"}
    }
    
    if request.method == "POST":
        platform_key = request.form.get("platform", "").strip().lower()
        url = request.form.get("url", "").strip()
        
        if platform_key not in PLATFORMS or not url:
            flash("Ungültige Plattform oder URL.", "danger")
            return redirect(url_for("admin.manage_social_links"))

        platform_name = PLATFORMS[platform_key]["name"]
        icon = PLATFORMS[platform_key]["icon"]

        social = SocialLink.query.filter_by(platform=platform_name).first()
        if not social:
            social = SocialLink(platform=platform_name, url=url, icon=icon, active=True)
            db.session.add(social)
        else:
            social.url = url
            social.icon = icon
        
        db.session.commit()
        flash(f"{platform_name} URL aktualisiert!", "success")
        return redirect(url_for("admin.manage_social_links"))

    social_links = {
        "facebook": SocialLink.query.filter_by(platform="Facebook").first(),
        "instagram": SocialLink.query.filter_by(platform="Instagram").first()
    }
    return render_template("admin/social_links.html", social_links=social_links, platforms=PLATFORMS)

@admin_routes.route("/social-links/delete/<int:link_id>")
@login_required
def delete_social_link(link_id):
    link = SocialLink.query.get_or_404(link_id)
    platform = link.platform
    db.session.delete(link)
    db.session.commit()
    flash(f"{platform} entfernt.", "success")
    return redirect(url_for("admin.manage_social_links"))

@admin_routes.route("/carousel", methods=["GET", "POST"])
def manage_carousel():
    if request.method == "POST":
        # Check if file was uploaded
        if "file" not in request.files:
            flash("Keine Datei ausgewählt.", "danger")
            return redirect(url_for("admin.manage_carousel"))
        
        file = request.files["file"]
        alt_text = request.form.get("alt_text", "").strip()
        link_url = request.form.get("link_url", "").strip()

        if file.filename == "":
            flash("Keine Datei ausgewählt.", "danger")
            return redirect(url_for("admin.manage_carousel"))

        # Check file extension
        allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
        if not ("." in file.filename and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions):
            flash("Nur Bilddateien erlaubt (PNG, JPG, GIF, WebP).", "danger")
            return redirect(url_for("admin.manage_carousel"))

        # Create uploads directory if needed
        os.makedirs("app/static/uploads", exist_ok=True)

        # Save file
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().timestamp()}_{filename}"
        filepath = os.path.join("app/static/uploads", filename)
        file.save(filepath)

        # Create carousel entry
        image = CarouselImage(
            filename=filename,
            alt_text=alt_text,
            link_url=link_url if link_url else None
        )
        db.session.add(image)
        db.session.commit()

        flash("Bild zur Karousell hinzugefügt!", "success")
        return redirect(url_for("admin.manage_carousel"))

    images = CarouselImage.query.filter_by(active=True).order_by(CarouselImage.order).all()
    return render_template("admin/carousel.html", images=images)

@admin_routes.route("/carousel/delete/<int:image_id>")
def delete_carousel_image(image_id):
    image = CarouselImage.query.get_or_404(image_id)
    # Delete file from disk
    filepath = os.path.join("app/static/uploads", image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(image)
    db.session.commit()
    flash("Karousellbild gelöscht.", "success")
    return redirect(url_for("admin.manage_carousel"))

# ---------------------- HERO IMAGE MANAGEMENT ----------------------

@admin_routes.route("/hero-image", methods=["GET", "POST"])
@login_required
def manage_hero_image():
    if request.method == "POST":
        # Check if file was uploaded
        if "file" not in request.files:
            flash("Keine Datei ausgewählt.", "danger")
            return redirect(url_for("admin.manage_hero_image"))
        
        file = request.files["file"]
        alt_text = request.form.get("alt_text", "").strip()

        if file.filename == "":
            flash("Keine Datei ausgewählt.", "danger")
            return redirect(url_for("admin.manage_hero_image"))

        # Check file extension
        allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
        if not ("." in file.filename and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions):
            flash("Nur Bilddateien erlaubt (PNG, JPG, GIF, WebP).", "danger")
            return redirect(url_for("admin.manage_hero_image"))

        # Delete old hero image if exists
        old_image = HeroImage.query.first()
        if old_image:
            filepath = os.path.join("app/static/uploads", old_image.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            db.session.delete(old_image)

        # Create uploads directory if needed
        os.makedirs("app/static/uploads", exist_ok=True)

        # Save new file
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().timestamp()}_{filename}"
        filepath = os.path.join("app/static/uploads", filename)
        file.save(filepath)

        # Create hero image entry
        image = HeroImage(
            filename=filename,
            alt_text=alt_text if alt_text else "Hero Bild"
        )
        db.session.add(image)
        db.session.commit()

        flash("Hero-Bild erfolgreich hochgeladen!", "success")
        return redirect(url_for("admin.manage_hero_image"))

    hero_image = HeroImage.query.first()
    return render_template("admin/hero_image.html", hero_image=hero_image)

# ---------------------- ADMIN: MANUFACTURERS ----------------------

@admin_routes.route("/manufacturers", methods=["GET", "POST"])
@login_required
def manage_manufacturers():
    """Управление производителями"""
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add" or action == "edit":
            manufacturer_id = request.form.get("manufacturer_id")
            name = request.form.get("name", "").strip()
            slug = request.form.get("slug", "").strip()
            website = request.form.get("website", "").strip()
            description = request.form.get("description", "").strip()
            country = request.form.get("country", "").strip()
            active = request.form.get("active") == "on"
            auto_sync = request.form.get("auto_sync") == "on"
            order = request.form.get("order", 0, type=int)
            
            # Handle logo upload
            logo_filename = None
            if 'logo' in request.files:
                logo_file = request.files['logo']
                if logo_file and logo_file.filename:
                    logo_filename = secure_filename(logo_file.filename)
                    logo_file.save(os.path.join('app', 'static', 'uploads', logo_filename))
            
            if manufacturer_id and action == "edit":
                # Update existing
                manufacturer = Manufacturer.query.get(manufacturer_id)
                if manufacturer:
                    manufacturer.name = name
                    manufacturer.slug = slug
                    manufacturer.website = website
                    manufacturer.description = description
                    manufacturer.country = country
                    manufacturer.active = active
                    manufacturer.auto_sync = auto_sync
                    manufacturer.order = order
                    if logo_filename:
                        manufacturer.logo = logo_filename
                    flash(f"Hersteller '{name}' wurde aktualisiert.", "success")
            else:
                # Add new
                manufacturer = Manufacturer(
                    name=name,
                    slug=slug,
                    logo=logo_filename,
                    website=website,
                    description=description,
                    country=country,
                    active=active,
                    auto_sync=auto_sync,
                    order=order
                )
                db.session.add(manufacturer)
                flash(f"Hersteller '{name}' wurde hinzugefügt.", "success")
            
            db.session.commit()
            return redirect(url_for("admin.manage_manufacturers"))
    
    manufacturers = Manufacturer.query.order_by(Manufacturer.order).all()
    return render_template("admin/manufacturers.html", manufacturers=manufacturers)

@admin_routes.route("/manufacturers/delete/<int:manufacturer_id>", methods=["POST"])
@login_required
def delete_manufacturer(manufacturer_id):
    """Удалить производителя"""
    manufacturer = Manufacturer.query.get_or_404(manufacturer_id)
    
    # Удаляем связанный контент
    ManufacturerContent.query.filter_by(manufacturer_id=manufacturer_id).delete()
    
    db.session.delete(manufacturer)
    db.session.commit()
    
    flash(f"Hersteller '{manufacturer.name}' wurde gelöscht.", "success")
    return redirect(url_for("admin.manage_manufacturers"))

@admin_routes.route("/manufacturers/<int:manufacturer_id>/sync", methods=["POST"])
@login_required
def sync_manufacturer_content(manufacturer_id):
    """Синхронизация контента производителя с его сайта"""
    manufacturer = Manufacturer.query.get_or_404(manufacturer_id)
    
    try:
        print(f"\n🔄 Начало синхронизации контента для {manufacturer.name}")
        
        # Извлекаем контент (уже с полными данными)
        all_content = scraper_service.extract_all_content(manufacturer.slug)
        
        count_added = 0
        count_skipped = 0
        
        # Сохраняем коллекции (только с изображениями!)
        collections = all_content.get('collections', [])
        print(f"\n📦 Обработка коллекций: {len(collections)}")
        for item in collections:
            # ВАЛИДАЦИЯ: Пропускаем коллекции без изображений
            if not item.get('image_url'):
                print(f"  ⚠️  Пропущена коллекция без изображения: {item.get('title', 'Без названия')}")
                count_skipped += 1
                continue
            
            # Проверяем что title тоже есть
            if not item.get('title') or len(item.get('title', '')) < 2:
                print(f"  ⚠️  Пропущена коллекция без названия")
                count_skipped += 1
                continue
            
            content = ManufacturerContent(
                manufacturer_id=manufacturer.id,
                content_type='collection',
                title=item.get('title', ''),
                description=item.get('description', ''),
                full_content=item.get('full_content', ''),
                technical_specs=item.get('technical_specs', ''),
                image_url=item.get('image_url', ''),
                source_url=item.get('source_url', ''),
                published=True
            )
            db.session.add(content)
            count_added += 1
            print(f"  ✓ Добавлена коллекция: {item.get('title', '')}")
        
        # Сохраняем проекты (только с изображениями!)
        projects = all_content.get('projects', [])
        print(f"\n🏗️  Обработка проектов: {len(projects)}")
        for item in projects:
            # ВАЛИДАЦИЯ: Пропускаем проекты без изображений
            if not item.get('image_url'):
                print(f"  ⚠️  Пропущен проект без изображения: {item.get('title', 'Без названия')}")
                count_skipped += 1
                continue
            
            if not item.get('title') or len(item.get('title', '')) < 2:
                print(f"  ⚠️  Пропущен проект без названия")
                count_skipped += 1
                continue
            
            content = ManufacturerContent(
                manufacturer_id=manufacturer.id,
                content_type='project',
                title=item.get('title', ''),
                description=item.get('description', ''),
                full_content=item.get('full_content', ''),
                technical_specs=item.get('technical_specs', ''),
                image_url=item.get('image_url', ''),
                source_url=item.get('source_url', ''),
                published=True
            )
            db.session.add(content)
            count_added += 1
            print(f"  ✓ Добавлен проект: {item.get('title', '')}")
        
        # Сохраняем блог посты
        blog_posts = all_content.get('blog_posts', [])
        print(f"\n📝 Обработка статей блога: {len(blog_posts)}")
        for item in blog_posts:
            # Для блога изображение необязательно, но название обязательно
            if not item.get('title') or len(item.get('title', '')) < 2:
                count_skipped += 1
                continue
            
            content = ManufacturerContent(
                manufacturer_id=manufacturer.id,
                content_type='blog',
                title=item.get('title', ''),
                description=item.get('content', ''),
                full_content=item.get('full_content', item.get('content', '')),
                image_url=item.get('image_url', ''),
                source_url=item.get('source_url', ''),
                published=True
            )
            db.session.add(content)
            count_added += 1
            print(f"  ✓ Добавлена статья: {item.get('title', '')}")
        
        # Обновляем время последней синхронизации
        manufacturer.last_sync = datetime.utcnow()
        db.session.commit()
        
        print(f"\n✅ Синхронизация завершена:")
        print(f"   ✓ Добавлено: {count_added} элементов")
        print(f"   ⚠️  Пропущено: {count_skipped} элементов (без изображений или названия)")
        
        flash(f"Inhalt von '{manufacturer.name}' wurde erfolgreich synchronisiert. {count_added} Einträge hinzugefügt, {count_skipped} übersprungen.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при синхронизации: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Fehler bei der Synchronisierung: {str(e)}", "danger")
    
    return redirect(url_for("admin.manage_manufacturers"))

# ---------------------- API CHATBOT ----------------------

@api_routes.route("/chat", methods=["POST"])
def chatbot():
    user_message = request.json.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Get custom instructions from config
    custom_instructions = ChatConfig.get("chatbot_instructions", "")

    # Get chat service and get response
    chat_service = get_chat_service()
    response = chat_service.chat(user_message, custom_instructions)

    # Save to database
    log = ChatLog(user_message=user_message, bot_response=response)
    db.session.add(log)
    db.session.commit()

    return jsonify({"response": response})

# ---------------------- MANUFACTURER CONTENT MANAGEMENT ----------------------

@admin_routes.route("/manufacturers/<int:manufacturer_id>/content")
@login_required
def manage_manufacturer_content(manufacturer_id):
    """Управление контентом конкретного производителя"""
    manufacturer = Manufacturer.query.get_or_404(manufacturer_id)
    
    # Получаем весь контент производителя
    collections = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer_id,
        content_type='collection'
    ).order_by(ManufacturerContent.created_at.desc()).all()
    
    projects = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer_id,
        content_type='project'
    ).order_by(ManufacturerContent.created_at.desc()).all()
    
    blog_posts = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer_id,
        content_type='blog'
    ).order_by(ManufacturerContent.created_at.desc()).all()
    
    return render_template("admin/manufacturer_content.html",
                         manufacturer=manufacturer,
                         collections=collections,
                         projects=projects,
                         blog_posts=blog_posts)

@admin_routes.route("/manufacturer-content/<int:content_id>/edit", methods=["GET", "POST"])
@login_required
def edit_manufacturer_content(content_id):
    """Редактировать элемент контента производителя"""
    content = ManufacturerContent.query.get_or_404(content_id)
    
    if request.method == "POST":
        content.title = request.form.get("title", "")
        content.description = request.form.get("description", "")
        content.full_content = request.form.get("full_content", "")
        content.technical_specs = request.form.get("technical_specs", "")
        content.source_url = request.form.get("source_url", "")
        content.published = request.form.get("published") == "on"
        
        db.session.commit()
        flash(f"'{content.title}' wurde aktualisiert.", "success")
        return redirect(url_for("admin.manage_manufacturer_content", 
                              manufacturer_id=content.manufacturer_id))
    
    return render_template("admin/edit_manufacturer_content.html", content=content)

@admin_routes.route("/manufacturer-content/<int:content_id>/delete", methods=["POST"])
@login_required
def delete_manufacturer_content(content_id):
    """Удалить элемент контента производителя"""
    content = ManufacturerContent.query.get_or_404(content_id)
    manufacturer_id = content.manufacturer_id
    title = content.title
    
    db.session.delete(content)
    db.session.commit()
    
    flash(f"'{title}' wurde gelöscht.", "success")
    return redirect(url_for("admin.manage_manufacturer_content", 
                          manufacturer_id=manufacturer_id))

@admin_routes.route("/manufacturer-content/<int:content_id>/toggle-publish", methods=["POST"])
@login_required
def toggle_publish_content(content_id):
    """Переключить статус публикации контента"""
    content = ManufacturerContent.query.get_or_404(content_id)
    content.published = not content.published
    db.session.commit()
    
    status = "veröffentlicht" if content.published else "unveröffentlicht"
    flash(f"'{content.title}' wurde {status}.", "success")
    return redirect(url_for("admin.manage_manufacturer_content", 
                          manufacturer_id=content.manufacturer_id))
from datetime import datetime
import os
import requests
from app import create_app, db
from app.models import Manufacturer, ManufacturerContent, ManufacturerSyncJob
from app.services.content_scraper_service import scraper_service


def _append_log(job, message):
    job.log = (job.log or "") + message + "\n"


def run_manufacturer_sync(sync_job_id):
    app = create_app()
    with app.app_context():
        job = ManufacturerSyncJob.query.get(sync_job_id)
        if not job:
            return

        if job.status == "canceled":
            _append_log(job, "Canceled before start")
            if not job.finished_at:
                job.finished_at = datetime.utcnow()
            db.session.commit()
            _post_webhook(job, "canceled")
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        job.total_steps = 3
        job.completed_steps = 0
        db.session.commit()

        manufacturer = Manufacturer.query.get(job.manufacturer_id)
        if not manufacturer:
            job.status = "failed"
            job.error_message = "Manufacturer not found"
            job.finished_at = datetime.utcnow()
            db.session.commit()
            _post_webhook(job, "failed")
            return

        _append_log(job, f"Start sync: {manufacturer.name} ({manufacturer.slug})")
        db.session.commit()

        try:
            deleted = ManufacturerContent.query.filter_by(manufacturer_id=manufacturer.id).delete()
            db.session.commit()
            _append_log(job, f"Deleted old content: {deleted}")
        except Exception as exc:
            db.session.rollback()
            job.status = "failed"
            job.error_message = str(exc)
            _append_log(job, f"Delete failed: {exc}")
            job.finished_at = datetime.utcnow()
            db.session.commit()
            _post_webhook(job, "failed")
            return

        try:
            all_content = scraper_service.extract_all_content(manufacturer.slug)
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
            _append_log(job, f"Extraction failed: {exc}")
            job.finished_at = datetime.utcnow()
            db.session.commit()
            _post_webhook(job, "failed")
            return

        added_total = 0
        skipped_total = 0

        try:
            added, skipped = _save_content_batch(
                manufacturer.id,
                all_content.get("collections", []),
                content_type="collection",
                require_image=True,
            )
            added_total += added
            skipped_total += skipped
            job.completed_steps = 1
            _append_log(job, f"Collections added: {added}, skipped: {skipped}")
            db.session.commit()

            added, skipped = _save_content_batch(
                manufacturer.id,
                all_content.get("projects", []),
                content_type="project",
                require_image=True,
            )
            added_total += added
            skipped_total += skipped
            job.completed_steps = 2
            _append_log(job, f"Projects added: {added}, skipped: {skipped}")
            db.session.commit()

            added, skipped = _save_content_batch(
                manufacturer.id,
                all_content.get("blog_posts", []),
                content_type="blog",
                require_image=False,
            )
            added_total += added
            skipped_total += skipped
            job.completed_steps = 3
            _append_log(job, f"Blog posts added: {added}, skipped: {skipped}")
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            job.status = "failed"
            job.error_message = str(exc)
            _append_log(job, f"Save failed: {exc}")
            job.finished_at = datetime.utcnow()
            db.session.commit()
            _post_webhook(job, "failed")
            return

        manufacturer.last_sync = datetime.utcnow()
        job.added_count = added_total
        job.skipped_count = skipped_total
        job.status = "success"
        job.finished_at = datetime.utcnow()
        _append_log(job, f"Done. Added: {added_total}, skipped: {skipped_total}")
        db.session.commit()
        _post_webhook(job, "success")


def _save_content_batch(manufacturer_id, items, content_type, require_image):
    added = 0
    skipped = 0

    for item in items:
        if require_image and not item.get("image_url"):
            skipped += 1
            continue
        title = item.get("title", "")
        if not title or len(title) < 2:
            skipped += 1
            continue

        content = ManufacturerContent(
            manufacturer_id=manufacturer_id,
            content_type=content_type,
            title=title,
            description=item.get("description", item.get("content", "")),
            full_content=item.get("full_content", item.get("content", "")),
            technical_specs=item.get("technical_specs", ""),
            image_url=item.get("image_url", ""),
            source_url=item.get("source_url", ""),
            published=True,
        )
        db.session.add(content)
        added += 1

    db.session.commit()
    return added, skipped


def _post_webhook(job, status):
    webhook_url = os.getenv("SYNC_WEBHOOK_URL")
    if not webhook_url:
        return

    payload = {
        "job_id": job.id,
        "manufacturer_id": job.manufacturer_id,
        "status": status,
        "added_count": job.added_count,
        "skipped_count": job.skipped_count,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }

    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as exc:
        _append_log(job, f"Webhook failed: {exc}")
        db.session.commit()

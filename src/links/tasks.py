from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Link


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def purge_expired_links(self, batch_size: int = 1000) -> dict:
    """
    Hard-delete expired Link rows from the database in batches.
    """
    now = timezone.now()
    total_processed = 0
    total_deleted = 0

    while True:
        # Pull a batch of expired rows (IDs only to keep memory low)
        expired_ids = list(
            Link.objects
            .filter(expire_at__isnull=False, expire_at__lte=now)
            .values_list("id", flat=True)[:batch_size]
        )
        if not expired_ids:
            break

        with transaction.atomic():
            deleted, _ = Link.objects.filter(id__in=expired_ids).delete()

        total_processed += len(expired_ids)
        total_deleted += deleted

        # If fewer than batch_size found, we're done
        if len(expired_ids) < batch_size:
            break

    return {"processed": total_processed, "deleted": total_deleted}

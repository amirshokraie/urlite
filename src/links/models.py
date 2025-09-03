from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone
from .services.base62 import encoder as _encode_base62


User = get_user_model()

class Link(models.Model):
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="links",
    )
    original_url = models.URLField(max_length=2048)
    code = models.CharField(max_length=20, unique=True)
    expire_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} : {self.original_url}"
    
    @property
    def is_expired(self) -> bool:
        return bool(self.expire_at and timezone.now() >= self.expire_at)


    def save(self, *args, **kwargs):
        if not self.pk and not self.code:
            with transaction.atomic():
                super().save(*args, **kwargs)
                self.code = _encode_base62(self.pk)
                super().save(update_fields=["code"])
        else:
            super().save(*args, **kwargs)

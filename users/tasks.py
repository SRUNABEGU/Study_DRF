from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from .models import User


@shared_task
def block_inactive_users():
    month_ago = timezone.now() - timedelta(days=30)
    User.objects.filter(is_active=True, is_superuser=False).filter(
        Q(last_login__lt=month_ago) |
        Q(last_login__isnull=True, date_joined__lt=month_ago)
    ).update(is_active=False)
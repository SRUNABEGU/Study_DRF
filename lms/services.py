from datetime import timedelta
from django.utils import timezone

from .models import Course
from .tasks import send_course_update_email


def notify_course_update(course):
    now = timezone.now()
    long_ago = now - course.updated_at > timedelta(hours=4)
    Course.objects.filter(pk=course.pk).update(updated_at=now)
    if long_ago:
        send_course_update_email.delay(course.pk)
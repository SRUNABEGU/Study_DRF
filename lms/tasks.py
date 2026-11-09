from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Course


@shared_task
def send_course_update_email(course_id):
    course = Course.objects.filter(pk=course_id).first()
    if not course:
        return
    emails = course.subscriptions.values_list('user__email', flat=True)
    for email in emails:
        send_mail(
            subject=f'Обновление курса «{course.title}»',
            message=f'В курсе «{course.title}» появились новые материалы.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
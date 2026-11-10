from django.db import models
from django.conf import settings
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    preview = models.ImageField(upload_to='lms/courses/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, blank=True, verbose_name='Владелец')

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='Последнее обновление')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']

class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    preview = models.ImageField(upload_to='lms/lessons/', blank=True, null=True, verbose_name='Превью')
    video_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, blank=True, verbose_name='Владелец')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='subscriptions')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_subscription')
        ]
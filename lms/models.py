from django.db import models
from django.conf import settings


class Course(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, blank=True, verbose_name='Владелец')


class Lesson(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, blank=True, verbose_name='Владелец')

    def __str__(self):
        return self.title
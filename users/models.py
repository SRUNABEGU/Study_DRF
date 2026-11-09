from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from lms.models import Course, Lesson


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Email обязателен')
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод на счет'
        CARD = 'card', 'Карта (Stripe)'

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='payments', verbose_name='Пользователь')
    paid_at = models.DateTimeField(default=timezone.now, verbose_name='Дата оплаты')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL,
                               null=True, blank=True, verbose_name='Оплаченный курс')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL,
                               null=True, blank=True, verbose_name='Оплаченный урок')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    method = models.CharField(max_length=10, choices=Method.choices, verbose_name='Способ оплаты')

    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    payment_link = models.URLField(max_length=1000, blank=True, null=True)
    status = models.CharField(max_length=20, default='unpaid')

    def __str__(self):
        return f'{self.user} — {self.amount} ({self.paid_at:%d.%m.%Y})'

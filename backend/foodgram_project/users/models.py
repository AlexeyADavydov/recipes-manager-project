import constants
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        unique=True,
        blank=False,
        max_length=constants.USER_EMAIL,
        verbose_name='Адрес электронной почты',
    )

    username = models.CharField(
        unique=True,
        blank=False,
        max_length=constants.USER_USERNAME,
        verbose_name='Уникальный юзернейм',
        validators=[validators.RegexValidator(
            regex=r'^[\w.@+-]+$',
        )]
    )

    first_name = models.TextField(
        blank=False,
        max_length=constants.USER_FIRST_NAME,
        verbose_name='Имя',
    )

    last_name = models.TextField(
        blank=False,
        max_length=constants.USER_LAST_NANE,
        verbose_name='Фамилия',
    )

    password = models.CharField(
        max_length=constants.USER_PASSWORD,
        verbose_name='Пароль',
        blank=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_subscriptions'
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'subscribing')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name="selfsubscribing_not_allowed",
            ),
        ]

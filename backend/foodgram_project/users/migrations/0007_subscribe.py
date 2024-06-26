# Generated by Django 3.2.16 on 2024-02-01 13:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_delete_subscribe'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscribing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'subscribing')},
            },
        ),
    ]

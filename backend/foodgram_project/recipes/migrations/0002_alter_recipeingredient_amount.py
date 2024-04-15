# Generated by Django 3.2.16 on 2024-02-09 15:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(default=0, null=True, validators=[django.core.validators.RegexValidator('^[0-9]+$')], verbose_name='Количество'),
        ),
    ]
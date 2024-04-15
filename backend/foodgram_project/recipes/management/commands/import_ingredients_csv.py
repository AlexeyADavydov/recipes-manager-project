import csv

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты'

    def add_arguments(self, parser):
        parser.add_argument('ingredients_csv', type=str,)

    def handle(self, *args, **options):

        ingredients_csv = options['ingredients_csv']

        try:
            with open(ingredients_csv, 'r', encoding='utf-8') as file:

                reader = csv.reader(file)

                ingredients = [
                    Ingredient(
                        name=row[0],
                        measurement_unit=row[1]
                    ) for row in reader
                ]

                Ingredient.objects.bulk_create(ingredients)

            self.stdout.write(self.style.SUCCESS(
                f'Загрузка завершена! Всего элементов - {len(ingredients)}'
            ))

        except Ingredient.DoesNotExist:
            raise CommandError('Ошибка')

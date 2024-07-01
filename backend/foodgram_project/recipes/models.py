import constants
from django.conf import settings
from django.core import validators
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=constants.INGR_NAME,
        verbose_name='Название',
        default='default'
    )

    measurement_unit = models.CharField(
        max_length=constants.INGR_MEASUREMENT,
        verbose_name='Единицы измерения',
        default='default'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=constants.TAG_NAME,
        verbose_name='Название',
        unique=True,
    )
    color = models.CharField(
        max_length=constants.TAG_COLOR,
        unique=True,
        verbose_name='Цвет в HEX',
        validators=[
            validators.RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Введите данные в HEX формате: #123ABC.'
            )
        ]
    )
    slug = models.SlugField(
        max_length=constants.TAG_SLUG,
        unique=True,
        verbose_name='Slug поле',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор публикации",
        null=False,
    )
    name = models.CharField(
        max_length=constants.RECIPE_NAME,
        verbose_name="Название",
    )
    image = models.ImageField(
        upload_to='recites/images/',
        verbose_name="Картинка",
    )
    text = models.TextField(
        verbose_name="Текстовое описание",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Тег",
    )
    cooking_time = models.IntegerField(
        validators=[
            validators.MinValueValidator(settings.MIN_TIME),
            validators.MaxValueValidator(settings.MAX_TIME)
        ],
        default=1,
        verbose_name="Время приготовления в минутах",
        null=False,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.IntegerField(
        default=0,
        verbose_name='Количество',
        null=True,
        validators=[
            validators.RegexValidator(r"^[0-9]+$",),
            validators.MinValueValidator(settings.MIN_AMOUNT),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipes_tags",
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tags",
        verbose_name='Ингредиент',
    )

    class Meta:
        verbose_name = 'Теги рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class RecipesAddedToShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_cart'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'


class UserFavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_favorite'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'

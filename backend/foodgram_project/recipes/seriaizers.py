import base64

from api.serializers import TagSerializer, UsersViewSerializer
from django.core.files.base import ContentFile
from django.db.models import F
from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            RecipesAddedToShoppingCart, Tag,
                            UserFavoriteRecipe)
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        read_only=True,
        many=True,
    )

    author = UsersViewSerializer(
        read_only=True,
    )

    ingredients = serializers.SerializerMethodField()

    is_favorited = serializers.SerializerMethodField()

    is_in_shopping_cart = serializers.SerializerMethodField()

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe

        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

        extra_kwargs = {
            'name': {'required': True},
            'tags': {'required': True},
            'ingredients': {'required': True},
            'cooking_time': {'required': True},
            'text': {'required': True},
            'image': {'required': True},
        }

    def validate_tags(self):
        if ('tags' and 'cooking_time') not in self.initial_data:
            raise serializers.ValidationError(
                'Ошибка: tags and cooking_time not in request'
            )

        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                'Ошибка: tags not in request'
            )

        input_tags = self.initial_data.get('tags')
        if len(input_tags) == 0:
            raise serializers.ValidationError(
                f'{input_tags} Список tags пуст.'
            )

        if len(input_tags) != len(set(input_tags)):
            raise serializers.ValidationError(
                f'{input_tags} Указаны теги с одинаковыми ID.'
            )

        tag_max_id = Tag.objects.latest('id').id

        for input_tag_id in input_tags:
            if input_tag_id not in range(0, tag_max_id + 1):
                raise serializers.ValidationError(
                    f'{input_tag_id}  Такого tag_id в базе нет  '
                )

    def validate_ingredients(self):
        input_ingredients_dataset = self.initial_data.get('ingredients')

        if not input_ingredients_dataset:
            raise serializers.ValidationError(
                'Список ингредиентов пустой'
            )

        ingredient_max_id = Ingredient.objects.latest('id').id

        for i in range(len(input_ingredients_dataset)):
            input_ingredient_id = input_ingredients_dataset[i]['id']

            if input_ingredient_id not in range(0, ingredient_max_id + 1):
                raise serializers.ValidationError(
                    f'{input_ingredient_id}  Такого ID в базе нет  '
                )

            input_ingredient_amount = input_ingredients_dataset[i]['amount']

            if not (isinstance(input_ingredient_amount, int)
                    or input_ingredient_amount.isdigit()
                    ):

                raise serializers.ValidationError(
                    'Кол-во: Неверный тип данных, должно быть целое число'
                )

            if int(input_ingredient_amount) < 1:
                raise serializers.ValidationError(
                    'Кол-во не может быть 0.'
                )

    def validate(self, attrs):
        self.validate_tags()
        self.validate_ingredients()

        return super().validate(attrs)

    def create(self, validated_data):

        input_tags = self.initial_data.get('tags')

        recipe = Recipe.objects.create(**validated_data)

        for input_tag_id in input_tags:

            tag, created = Tag.objects.get_or_create(
                id=input_tag_id
            )
            recipe.tags.add(tag)

        input_ingredients_dataset = self.initial_data.get('ingredients')

        for i in range(len(input_ingredients_dataset)):
            input_ingredient_id = input_ingredients_dataset[i]['id']

            input_ingredient_amount = int(input_ingredients_dataset[i][
                'amount'
            ])

            if RecipeIngredient.objects.values(
                'recipe_id',
                'ingredient_id'
            ).filter(
                recipe_id=recipe.id,
                ingredient_id=input_ingredient_id
            ).exists():
                raise serializers.ValidationError(
                    f'{input_ingredient_amount}  Ингредиент уже есть!.'
                )

            RecipeIngredient.objects.create(
                recipe_id=recipe.id,
                ingredient_id=input_ingredient_id,
                amount=input_ingredient_amount,
            )

        return recipe

    def update(self, instance, validated_data):

        input_ingredients_dataset = self.initial_data.get('ingredients')

        ingredient_max_id = Ingredient.objects.latest('id').id

        input_ingredient_id_checker = 0

        RecipeIngredient.objects.filter(
            recipe=instance
        ).all().delete()

        for i in range(len(input_ingredients_dataset)):
            input_ingredient_id = input_ingredients_dataset[i]['id']

            if input_ingredient_id == input_ingredient_id_checker:
                raise serializers.ValidationError(
                    'ingredient_id в запросе дублируется.'
                )
            input_ingredient_id_checker = input_ingredient_id

            if input_ingredient_id not in range(0, ingredient_max_id + 1):
                raise serializers.ValidationError(
                    f'{input_ingredient_id}  Такого ingredient_id в базе нет  '
                )

            input_ingredient_amount = int(input_ingredients_dataset[i][
                'amount'
            ])

            if input_ingredient_amount < 1:
                raise serializers.ValidationError(
                    'Кол-во не может быть 0.'
                )

            RecipeIngredient.objects.create(
                recipe_id=instance.id,
                ingredient_id=input_ingredient_id,
                amount=input_ingredient_amount,
            )

        input_tags = self.initial_data.get('tags')

        instance.tags.set(input_tags)

        instance.image = validated_data.get(
            'image',
            instance.image,
        )
        instance.name = validated_data.get(
            'name',
        )
        instance.text = validated_data.get(
            'text',
        )
        instance.cooking_time = validated_data.get(
            'cooking_time',
        )
        instance.save()

        return instance

    def get_is_favorited(self, obj):

        recipe_bollean_value = Recipe.objects.filter(
            id=obj.id).exists()

        favorite_bollean_value = UserFavoriteRecipe.objects.filter(
            recipe_id=obj.id,
            user_id=self.context.get('request').user.id
        ).exists()

        return recipe_bollean_value and favorite_bollean_value

    def get_is_in_shopping_cart(self, obj):

        recipe_bollean_value = Recipe.objects.filter(
            id=obj.id).exists()

        cart_bollean_value = RecipesAddedToShoppingCart.objects.filter(
            recipe_id=obj.id,
            user_id=self.context.get('request').user.id
        ).exists()

        return recipe_bollean_value and cart_bollean_value

    def get_ingredients(self, recipe):
        output = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F("recipeingredient__amount"),
        )
        return output


class RecipeInShoppingCartSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        source='recipe.name'
    )

    image = serializers.ImageField(source='recipe.image')

    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = RecipesAddedToShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserFavoriteRecipeSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        source='recipe.name'
    )

    image = serializers.ImageField(source='recipe.image')

    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = UserFavoriteRecipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

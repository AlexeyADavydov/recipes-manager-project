from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from users.models import Subscribe, User


class UsersViewSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, user):
        return (not self.context.get(
            'request'
        ).user.is_anonymous and Subscribe.objects.filter(
            user_id=self.context.get('request').user.id,
            subscribing__id=user.id,
        ).exists())


class UsersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        read_only_fields = ('id',)

        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output.pop('password')
        return output


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class SubscribeSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(
        source='subscribing.id'
    )
    email = serializers.ReadOnlyField(
        source='subscribing.email'
    )
    username = serializers.ReadOnlyField(
        source='subscribing.username'
    )
    first_name = serializers.ReadOnlyField(
        source='subscribing.first_name'
    )
    last_name = serializers.ReadOnlyField(
        source='subscribing.last_name'
    )

    is_subscribed = serializers.SerializerMethodField()

    recipes = serializers.SerializerMethodField()

    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, object):

        if object.user.id != object.subscribing.id:
            return Subscribe.objects.filter(
                user=object.user,
                subscribing=object.subscribing
            ).exists()
        else:
            raise serializers.ValidationError(
                'На себя подписаться нельзя',
            )

    def get_recipes_count(self, object):

        return Recipe.objects.filter(
            author_id=object.user.id,
        ).count()

    def get_recipes(self, object):

        recipes_set = Recipe.objects.filter(
            author_id=object.subscribing.id,
        )

        get_recipes_limit_str = self.context['request'].query_params.get(
            'recipes_limit', None)

        if get_recipes_limit_str is not None:
            recipes_set = recipes_set[:int(get_recipes_limit_str)]

        return [
            {
                'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image.url if recipe.image else None,
                'cooking_time': recipe.cooking_time,
            }
            for recipe in recipes_set
        ]

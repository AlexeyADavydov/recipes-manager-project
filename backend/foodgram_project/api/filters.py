import django_filters
from django_filters.rest_framework import filters
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter
from users.models import User


class RecipeFilter(django_filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart",
    )
    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited",
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(
            recipe_cart__user=self.request.user
        ) if value is True and not self.request.user.is_anonymous else queryset

    def filter_is_favorited(self, queryset, name, value):
        return queryset.filter(
            recipe_favorite__user=self.request.user
        ) if value is True and not self.request.user.is_anonymous else queryset


class IngredientFilter(SearchFilter):
    search_param = 'name'

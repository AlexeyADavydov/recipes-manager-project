from django.contrib import admin

from .forms import RecipeIngredientForm
from .models import (Ingredient, Recipe, RecipeIngredient,
                     RecipesAddedToShoppingCart, RecipeTag, Tag,
                     UserFavoriteRecipe)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'subscribers',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )

    inlines = (IngredientInline,)

    @admin.display(empty_value='???')
    def subscribers(self, obj):
        return obj.recipe_favorite.count()


class RecipeIngredientAdmin(admin.ModelAdmin):
    form = RecipeIngredientForm


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag)
admin.site.register(RecipesAddedToShoppingCart)
admin.site.register(UserFavoriteRecipe)

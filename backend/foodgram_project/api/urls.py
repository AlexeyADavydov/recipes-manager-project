from api.views import (AddRecipeToFavoriteViewSet,
                       AddRecipeToShoppingCartViewSet, IngredientViewSet,
                       RecipeViewSet, SubscribeViewSet, TagViewSet,
                       UsersViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

router.register(r'tags', TagViewSet, 'tags')
router.register(r'ingredients', IngredientViewSet, 'ingredients')

router.register(r'recipes', RecipeViewSet, 'recipes')

router.register(r'users', UsersViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('users/<int:id>/subscribe/',
         SubscribeViewSet.as_view(
             {'post': 'create',
              'delete': 'delete'
              })),
    path('recipes/<int:id>/favorite/',
         AddRecipeToFavoriteViewSet.as_view(
             {'post': 'create',
              'delete': 'delete'
              })),

    path('recipes/<int:id>/shopping_cart/',
         AddRecipeToShoppingCartViewSet.as_view(
             {'post': 'create',
              'delete': 'delete'
              })),
]

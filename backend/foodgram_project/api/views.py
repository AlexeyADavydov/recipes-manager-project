import os
from collections import defaultdict

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import LimitPerPageParametr
from api.permissions import IsOwnerOrAdministrator
from api.serializers import (IngredientSerializer, SubscribeSerializer,
                             TagSerializer, UsersSerializer,
                             UsersViewSerializer)
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            RecipesAddedToShoppingCart, Tag,
                            UserFavoriteRecipe)
from recipes.seriaizers import (RecipeInShoppingCartSerializer,
                                RecipeSerializer, UserFavoriteRecipeSerializer)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe, User


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = LimitPerPageParametr

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UsersSerializer
        return UsersViewSerializer

    @action(detail=False,
            methods=['post']
            )
    def set_password(self, request):
        user = request.user

        if user.check_password(request.data.get('current_password')):
            user.set_password(request.data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            url_path='me',
            methods=['get'],
            permission_classes=(IsAuthenticated,),
            )
    def self_addressing(self, request):

        if request.method == "GET":
            serializer = self.get_serializer(
                self.request.user,
                many=False
            )
            return Response(serializer.data)

    @action(detail=False,
            url_path='subscriptions',
            methods=['get'],
            permission_classes=(IsAuthenticated,),
            )
    def my_subscriptions(self, request):

        try:
            serializer = SubscribeSerializer(
                self.paginate_queryset(
                    Subscribe.objects.filter(user=request.user,)
                ),
                many=True,
                context={'request': request}
            )

            return self.get_paginated_response(serializer.data)

        except IntegrityError:
            return Response(
                {"detail": "Ошибка со списком подписок"},
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):
        auth_user = request.user
        subscribing = get_object_or_404(
            User, id=self.kwargs["id"]
        )

        if auth_user.id == subscribing.id:
            return Response(
                'На себя подписаться нельзя',
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscribe.objects.filter(
            user=auth_user,
            subscribing=subscribing,
        ).exists():
            return Response(
                {"detail": "Уже подписан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscribe = Subscribe.objects.create(
            user=auth_user,
            subscribing=subscribing,
        )

        serializer = SubscribeSerializer(
            subscribe,
            context={"request": request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, **kwargs):

        subs_object = Subscribe.objects.filter(
            user_id=request.user.id,
            subscribing_id=self.kwargs["id"]
        )

        user_object = User.objects.filter(
            id=self.kwargs["id"],
        )

        if not user_object.exists():
            return Response(
                {"Такого ID пользователя в базе нет"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not subs_object.exists():
            return Response(
                {"Такой подписки нет."},
                status=status.HTTP_400_BAD_REQUEST
            )

        else:
            subs_object.delete()
            return Response(
                {"Удалено"},
                status=status.HTTP_204_NO_CONTENT,
            )


class TagViewSet(viewsets.ModelViewSet):
    http_method_names = ('get')
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    http_method_names = ('get')
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = (IsOwnerOrAdministrator,)
    serializer_class = RecipeSerializer
    pagination_class = LimitPerPageParametr

    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False,
            url_path='download_shopping_cart',
            methods=['get'],
            permission_classes=[IsAuthenticated],
            )
    def download_shopping_cart(self, request):
        final_ingredients_pack = defaultdict(int)

        shopping_cart = RecipesAddedToShoppingCart.objects.filter(
            user=self.request.user
        )

        for i in range(0, len(shopping_cart)):

            recipe_ingredients_object = RecipeIngredient.objects.filter(
                recipe=shopping_cart[i].recipe_id
            )

            for i in range(0, len(recipe_ingredients_object)):
                ingredient_object = recipe_ingredients_object[i]

                final_ingredients_pack[
                    ingredient_object.ingredient_id
                ] += ingredient_object.amount

        path = settings.SHOPPING_CART_PATH

        if not os.path.exists(path):
            os.mkdir(path)

        file_path = f'{settings.SHOPPING_CART_PATH}/data.txt'

        with open(file_path, 'w') as file:
            for ingr_id, ingr_amount in final_ingredients_pack.items():

                ingr_obj = Ingredient.objects.filter(
                    pk=ingr_id
                )

                ingr_m_unit = ingr_obj[0].measurement_unit

                file.write(
                    f'{ingr_obj[0].name}: {ingr_amount} {ingr_m_unit}\n'
                )

        with open(file_path, 'r') as file:
            response = HttpResponse(file, content_type='text/plain')
            response['Content-Disposition'] = (
                f'attachment; filename={os.path.basename(file_path)}'
            )

            return response


class AddRecipeToFavoriteViewSet(viewsets.ModelViewSet):
    queryset = UserFavoriteRecipe.objects.all()
    serializer_class = UserFavoriteRecipeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):

        if not Recipe.objects.filter(
            id=self.kwargs["id"],
        ).exists():
            return Response(
                {"Такого ID рецепта в базе нет"},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe_object = Recipe.objects.get(
            id=self.kwargs["id"],
        )

        favorite_object = UserFavoriteRecipe.objects.filter(
            user=request.user,
            recipe=recipe_object,
        )

        if favorite_object.exists():
            return Response(
                {"detail": "Уже уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:

            favorite_object = UserFavoriteRecipe.objects.create(
                user=request.user,
                recipe=recipe_object,
            )

        serializer = UserFavoriteRecipeSerializer(
            favorite_object,
            context={"request": request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, **kwargs):

        recipe_object = Recipe.objects.filter(
            id=self.kwargs["id"],
        )

        if not recipe_object.exists():
            return Response(
                {"Такого ID рецепта в базе нет"},
                status=status.HTTP_404_NOT_FOUND
            )

        fav_recipe_object = UserFavoriteRecipe.objects.filter(
            user_id=request.user.id,
            recipe_id=self.kwargs["id"]
        )
        if fav_recipe_object.exists():
            fav_recipe_object.delete()
            return Response(
                {"detail": "Удалено"},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"detail": "Ошибка удаления, записи нет"},
                status=status.HTTP_400_BAD_REQUEST
            )


class AddRecipeToShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = RecipesAddedToShoppingCart.objects.all()
    serializer_class = RecipeInShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):

        if not Recipe.objects.filter(
            id=self.kwargs["id"],
        ).exists():
            return Response(
                {"Такого ID рецепта в базе нет"},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe_object = Recipe.objects.get(
            id=self.kwargs["id"],
        )

        shopping_cart = RecipesAddedToShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe_object,
        )

        if shopping_cart.exists():
            return Response(
                {"detail": "Уже уже в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            shopping_cart = RecipesAddedToShoppingCart.objects.create(
                user=request.user,
                recipe=recipe_object,
            )

        serializer = RecipeInShoppingCartSerializer(
            shopping_cart,
            context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, **kwargs):

        if not Recipe.objects.filter(
            id=self.kwargs["id"],
        ).exists():
            return Response(
                {"Такого ID рецепта в базе нет"},
                status=status.HTTP_404_NOT_FOUND
            )

        recipe_object = RecipesAddedToShoppingCart.objects.filter(
            user_id=request.user.id,
            recipe_id=self.kwargs["id"]
        )

        if recipe_object.exists():
            recipe_object.delete()
            return Response(
                {"detail": "Удалено"},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"detail": "Ошибка удаления, записи нет"},
                status=status.HTTP_400_BAD_REQUEST
            )

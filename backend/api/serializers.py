from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.transaction import atomic

from core.services import recipe_ingredients_set
from core.validators import ingredients_validator, tags_exist_validator
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class ShortRecipeSerializer(ModelSerializer):
    """Укороченный сериализатор.

    Определен для некоторых эндпоинтов.
    """

    class Meta:
        model = Recipe
        fields = "id", "name", "image", "cooking_time"
        read_only_fields = (
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "cooking_time",
            "pub_date",
        )


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, object):
        user = self.context.get("request").user

        if user.is_anonymous or (user == object):
            return False

        return user.subscriptions.filter(author=object).exists()

    def create(self, validated_data) -> User:
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSubscribeSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, object):
        return object.recipes.count()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "name",
            "color",
            "slug",
        )
        read_only_fields = (
            "name",
            "color",
            "slug",
        )

    def validate(self, data):
        for attribute, value in data.items():
            data[attribute] = value.sttrip(" #").upper()

        return data


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "name",
            "measurement_unit",
        )
        read_only_fields = (
            "name",
            "measurement_unit",
        )


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "is_favorite",
            "is_shopping_cart",
        )

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )
        return ingredients

    def get_is_favorited(self, recipe):
        user = self.context.get("view").request.user

        if user.is_anonymous:
            return False

        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get("view").request.user

        if user.is_anonymous:
            return False

        return user.carts.filter(recipe=recipe).exists()

    def validate(self, data):
        tags_ids = self.initial_data.get("tags")
        ingredients = self.initial_data.get("ingredients")

        if not tags_ids or not ingredients:
            raise ValidationError("Недостаточно данных.")

        tags = tags_exist_validator(tags_ids, Tag)
        ingredients = ingredients_validator(ingredients, Ingredient)

        data.update(
            {
                "tags": tags,
                "ingredients": ingredients,
                "author": self.context.get("request").user,
            }
        )
        return data

    @atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients_set(recipe, ingredients)
        return recipe

    @atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            recipe_ingredients_set(recipe, ingredients)

        recipe.save()
        return recipe

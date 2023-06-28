from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.TextField(
        verbose_name="Название",
    )
    color = models.CharField(
        max_length=16,
    )
    slug = models.SlugField(
        verbose_name="Slug field",
        unique=True
    )


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name="Название"
    )
    quantity = models.FloatField(
        verbose_name="Количество"
    )
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения"
    )


class Recipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        verbose_name="Тег"
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredients,
        verbose_name="Ингредиенты"
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        help_text="Введите название рецепта",
    )
    image = models.ImageField(
        verbose_name="Картинка",
        blank=True,
    )
    text = models.TextField(
        verbose_name="Текстовое описание",
        help_text="Введите описание рецепта",
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления в минутах"
    )

from core.enums import Limits, Tuples
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Length

User = get_user_model()

models.CharField.register_lookup(Length)

class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name="Название",
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        db_index=False,
    )
    slug = models.SlugField(
        verbose_name="Slug field",
        max_length=64,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Тэги"
        ordering = ("name",)
    
    def __str__(self):
        return f"{self.name} (цвет: {self.color})"


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=64,
    )
    quantity = models.FloatField(
        verbose_name="Количество",
    )
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения",
        max_length=24,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredients",
            ),
            models.CheckConstraint(
                check=models.Q(name__length__gt=0),
                name="\n%(app_label)s_%(class)s_name is empty\n",
            ),
            models.CheckConstraint(
                check=models.Q(measurement_unit__length__gt=0),
                name="\n%(app_label)s_%(class)s_measurement_unit is empty\n",
            ),
        )
    
    def __str__(self):
        return f"{self.name} {self.measurement_unit}"


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тег",
        related_name="recipes",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name="Ингредиенты",
        related_name="recipes",
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        help_text="Введите название рецепта",
        max_length=64,
    )
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="recipe_images/",
        blank=True,
    )
    text = models.TextField(
        verbose_name="Текстовое описание",
        help_text="Введите описание рецепта",
        max_length=64,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        default=0,
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "author"),
                name="unique_for_author",
            ),
            models.CheckConstraint(
                check=models.Q(name__length__gt=0),
                name="\n%(app_label)s_%(class)s_name is empty\n",
            ),
        )
    
    def __str__(self):
        return f"{self.name}. Автор: {self.author.username}"


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="В каких рецептах",
        related_name="ingredient",
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredients,
        verbose_name="Связанные ингредиенты",
        related_name="recipe",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        default=0,
    )


    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Количество ингридиентов"
        ordering = ("recipe",)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "ingredients",
                ),
                name="\n%(app_label)s_%(class)s ingredient alredy added\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.amount} {self.ingredients}"


class Favorites(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Любимые рецепты",
        related_name="in_favorites",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="favorites",
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="\n%(app_label)s_%(class)s recipe is favorite alredy\n",
            ),
        )
    
    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class Carts(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепты в списке покупок",
        related_name="in_carts",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Владелец списка",
        related_name="carts",
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="\n%(app_label)s_%(class)s recipe is in cart alredy\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"
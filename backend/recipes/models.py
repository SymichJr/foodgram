from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Length

from PIL import Image

from core.enums import Limits, Tuples
from core.validators import OneOfTwoValidator, hex_color_validator


User = get_user_model()

models.CharField.register_lookup(Length)


class Tag(models.Model):
    name = models.CharField(
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
        validators=(
            OneOfTwoValidator(
                field="Название тэга",
                first_regex="[^а-яёА-ЯЁ]+",
                second_regex="[^a-zA-Z]+",
            ),
        ),
        verbose_name="Название",
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        db_index=False,
    )
    slug = models.SlugField(
        verbose_name="Slug field",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Тэги"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} (цвет: {self.color})"

    def clean(self) -> None:
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        self.color = hex_color_validator(self.color)
        return super().clean()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
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

    def clean(self):
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()


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
        null=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        related_name="recipes",
        through="recipes.AmountIngredient",
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        help_text="Введите название рецепта",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
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
        validators=(
            MinValueValidator(
                Limits.MIN_COOKING_TIME.value,
                "Ваше блюдо уже готово!",
            ),
            MaxValueValidator(
                Limits.MAX_COOKING_TIME.value,
                "Очень долго ждать...",
            ),
        ),
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

    def clean(self):
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image.thumbnail(Tuples.RECIPE_IMAGE_SIZE)
        image.save(self.image.path)


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="В каких рецептах",
        related_name="ingredient",
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name="Связанные ингредиенты",
        related_name="recipe",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        default=0,
        validators=(
            MinValueValidator(
                Limits.MIN_AMOUNT_INGREDIENTS,
                "Не могу приготовить из ничего)!",
            ),
            MaxValueValidator(
                Limits.MAX_AMOUNT_INGREDIENTS,
                "Слишком много!",
            ),
        ),
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

    def __str__(self):
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

    def __str__(self):
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

    def __str__(self):
        return f"{self.user} -> {self.recipe}"

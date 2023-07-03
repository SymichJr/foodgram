from re import compile
from string import hexdigits

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class OneOfTwoValidator:
    first_regex = "[^а-яёА-ЯЁ]+"
    second_regex = "[^a-zA-Z]+"
    field = "Переданное значение"
    message = "<%s> на разных языках либо содержит не только буквы."

    def __init__(
        self,
        first_regex,
        second_regex,
        field,
    ):
        if first_regex is not None:
            self.first_regex = first_regex
        if second_regex is not None:
            self.second_regex = second_regex
        if field is not None:
            self.field = field
        self.message = f"\n{self.field} {self.message}\n"

        self.first_regex = compile(self.first_regex)
        self.second_regex = compile(self.second_regex)

    def __call__(self, value):
        if self.first_regex.search(value) and self.second_regex.search(value):
            raise ValidationError(self.message % value)


@deconstructible
class MinLenValidator:
    min_len = 0
    field = "Переданное значение"
    message = "\n%s недостаточной длины.\n"

    def __init__(
        self,
        min_len,
        field,
        message,
    ):
        if min_len is not None:
            self.min_len = min_len
        if field is not None:
            self.field = field
        if message is not None:
            self.message = message
        else:
            self.message = self.message % field

    def __call__(self, value):
        if len(value) < self.min_len:
            raise ValidationError(self.message)


def hex_color_validator(color):
    color = color.strip(" #")
    if len(color) not in (3, 6):
        raise ValidationError(
            f"Код цвета {color} не правильной длины ({len(color)})."
        )
    if not set(color).issubset(hexdigits):
        raise ValidationError(f"{color} не шестнадцатиричное.")
    if len(color) == 3:
        return f"#{color[0] * 2}{color[1] * 2}{color[2] * 2}".upper()
    return "#" + color.upper()


def tags_exist_validator(tags_ids, Tag):
    if not tags_ids:
        raise ValidationError("Не указаны тэги")

    tags = Tag.objects.filter(id__in=tags_ids)

    if len(tags) != len(tags_ids):
        raise ValidationError("Указан несуществующий тэг")

    return tags


def ingredients_validator(ingredients, Ingredient):
    if not ingredients:
        raise ValidationError("Не указаны ингридиенты")

    valid_ingredients = {}

    for ingredient in ingredients:
        if not (
            isinstance(ingredient["amount"], int)
            or ingredient["amount"].isdigit()
        ):
            raise ValidationError("Неправильное количество ингидиента")

        valid_ingredients[ingredient["id"]] = int(ingredient["amount"])
        if valid_ingredients[ingredient["id"]] <= 0:
            raise ValidationError("Неправильное количество ингридиента")

    if not valid_ingredients:
        raise ValidationError("Неправильные ингидиенты")

    db_ingredients = Ingredient.objects.filter(pk__in=valid_ingredients.keys())
    if not db_ingredients:
        raise ValidationError("Неправильные ингидиенты")

    for ingredient in db_ingredients:
        valid_ingredients[ingredient.pk] = (
            ingredient,
            valid_ingredients[ingredient.pk],
        )

    return valid_ingredients

# Generated by Django 4.2.3 on 2023-07-03 22:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0002_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Favorites",
            new_name="Favorite",
        ),
        migrations.RemoveConstraint(
            model_name="favorite",
            name="\nrecipes_favorites recipe is favorite alredy\n",
        ),
        migrations.AlterField(
            model_name="recipe",
            name="text",
            field=models.TextField(
                help_text="Введите описание рецепта",
                verbose_name="Текстовое описание",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="slug",
            field=models.SlugField(
                max_length=64, unique=True, verbose_name="Slug field"
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("recipe", "user"),
                name="\nrecipes_favorite recipe is favorite alredy\n",
            ),
        ),
    ]

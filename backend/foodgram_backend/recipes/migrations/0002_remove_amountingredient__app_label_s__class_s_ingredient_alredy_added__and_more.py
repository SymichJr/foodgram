# Generated by Django 4.2.2 on 2023-07-02 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='amountingredient',
            name='\n%(app_label)s_%(class)s ingredient alredy added\n',
        ),
        migrations.RemoveConstraint(
            model_name='carts',
            name='\n%(app_label)s_%(class)s recipe is in cart alredy\n',
        ),
        migrations.RemoveConstraint(
            model_name='favorites',
            name='\n%(app_label)s_%(class)s recipe is favorite alredy\n',
        ),
        migrations.RemoveConstraint(
            model_name='ingredients',
            name='\n%(app_label)s_%(class)s_name is empty\n',
        ),
        migrations.RemoveConstraint(
            model_name='ingredients',
            name='\n%(app_label)s_%(class)s_measurement_unit is empty\n',
        ),
        migrations.RemoveConstraint(
            model_name='recipe',
            name='\n%(app_label)s_%(class)s_name is empty\n',
        ),
        migrations.AddConstraint(
            model_name='amountingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredients'), name='\nrecipes_amountingredient ingredient alredy added\n'),
        ),
        migrations.AddConstraint(
            model_name='carts',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='\nrecipes_carts recipe is in cart alredy\n'),
        ),
        migrations.AddConstraint(
            model_name='favorites',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='\nrecipes_favorites recipe is favorite alredy\n'),
        ),
        migrations.AddConstraint(
            model_name='ingredients',
            constraint=models.CheckConstraint(check=models.Q(('name__length__gt', 0)), name='\nrecipes_ingredients_name is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='ingredients',
            constraint=models.CheckConstraint(check=models.Q(('measurement_unit__length__gt', 0)), name='\nrecipes_ingredients_measurement_unit is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.CheckConstraint(check=models.Q(('name__length__gt', 0)), name='\nrecipes_recipe_name is empty\n'),
        ),
    ]

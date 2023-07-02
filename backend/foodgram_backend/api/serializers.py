from collections import OrderedDict

from core.services import recipe_ingredients_set
from core.validators import ingredients_validator, tags_exist_validator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F, QuerySet
from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.serializers import ModelSerializer, SerializerMethodField

User = get_user_model()
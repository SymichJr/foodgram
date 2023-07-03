from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from users.models import MyUser, Subscription


@register(MyUser)
class MyUserAdmin(UserAdmin):
    list_display = (
        "is_active",
        "username",
        "first_name",
        "last_name",
        "email",
    )
    fields = (
        ("is_active",),
        (
            "username",
            "email",
        ),
        (
            "first_name",
            "last_name",
        ),
    )
    fieldsets = []

    search_fields = (
        "username",
        "email",
    )
    list_filter = (
        "is_active",
        "first_name",
        "email",
    )
    save_on_top = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('username')
        return queryset


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = (
        'user',
        'author',
        'date_added',
    )
    list_filter = (
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author',
    )

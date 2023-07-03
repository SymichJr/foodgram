import unicodedata

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy as _

from core import texts
from core.enums import Limits
from core.validators import MinLenValidator, OneOfTwoValidator

models.CharField.register_lookup(Length)


class MyUser(AbstractUser):
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=Limits.MAX_LEN_EMAIL_FIELD.value,
        unique=True,
        help_text=texts.USERS_HELP_EMAIL,
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        unique=True,
        help_text=texts.USERS_HELP_UNAME,
        validators=(
            MinLenValidator(
                min_len=Limits.MIN_LEN_USERNAME,
                field="username",
                message="\n%s недостаточной длины.\n",
            ),
            OneOfTwoValidator(
                field="username",
                first_regex="[^а-яёА-ЯЁ]+",
                second_regex="[^a-zA-Z]+",
            ),
        ),
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        help_text=texts.USERS_HELP_FNAME,
        validators=(
            OneOfTwoValidator(
                first_regex="[^а-яёА-ЯЁ -]+",
                second_regex="[^a-zA-Z -]+",
                field="Имя",
            ),
        ),
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        help_text=texts.USERS_HELP_FNAME,
        validators=(
            OneOfTwoValidator(
                first_regex="[^а-яёА-ЯЁ -]+",
                second_regex="[^a-zA-Z -]+",
                field="Фамилия",
            ),
        ),
    )
    password = models.CharField(
        verbose_name=_("Пароль"),
        max_length=128,
        help_text=texts.USERS_HELP_FNAME,
    )
    is_active = models.BooleanField(
        verbose_name="Активирован",
        default=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)
        constraints = (
            models.CheckConstraint(
                check=models.Q(
                    username__length__gte=Limits.MIN_LEN_USERNAME.value
                ),
                name="\nusername is too short\n",
            ),
        )

    def __str__(self):
        return f"{self.username}: {self.email}"

    @classmethod
    def normalize_email(cls, email):
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = email_name.lower() + "@" + domain_part.lower()
        return email

    @classmethod
    def normalize_username(cls, username):
        return unicodedata.normalize("NFKC", username).capitalize()

    def __normalize_human_names(self, name):
        storage = [None] * len(name)
        title = True
        idx = 0
        for letter in name:
            letter = letter.lower()
            if title:
                if not letter.isalpha():
                    continue
                else:
                    letter = letter.upper()
                    title = False
            elif letter in " -":
                title = True
            storage[idx] = letter
            idx += 1
        return "".join(storage[:idx])

    def clean(self):
        self.first_name = self.__normalize_human_names(self.first_name)
        self.last_name = self.__normalize_human_names(self.last_name)
        return super().clean()


class Subscription(models.Model):
    author = models.ForeignKey(
        verbose_name="Автор рецепта",
        related_name="subscribers",
        to=MyUser,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Подписчики",
        related_name="subscription",
        to=MyUser,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="Дата создания подписки",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=("author", "user"),
                name="\nRepeat subscription\n",
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F("user")),
                name="\nNo self sibscription\n",
            ),
        )

    def __str__(self):
        return f"{self.user.username} -> {self.author.username}"

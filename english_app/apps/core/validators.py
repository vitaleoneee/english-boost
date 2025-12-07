from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import MinimumLengthValidator


class CustomMinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Пароль слишком короткий. Минимум %(min_length)d символов."),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return _("Ваш пароль должен содержать минимум %(min_length)d символов.") % {
            "min_length": self.min_length
        }

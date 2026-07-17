from django.db import models
from django.utils.translation import gettext_lazy as _


class LearningMode(models.TextChoices):
    EN_TO_RU = "EN_TO_RU", _("English → Russian")
    RU_TO_EN = "RU_TO_EN", _("Russian → English")
    AUDIO_TO_EN = "AUDIO_TO_EN", _("Audio → English")


MODE_DETAILS = {
    LearningMode.EN_TO_RU: {
        "description": _("See an English word and type its Russian translation."),
        "icon": "bi-translate",
    },
    LearningMode.RU_TO_EN: {
        "description": _("See a Russian translation and type the English word."),
        "icon": "bi-arrow-left-right",
    },
    LearningMode.AUDIO_TO_EN: {
        "description": _("Listen to the pronunciation and type the English word."),
        "icon": "bi-volume-up-fill",
    },
}


def is_valid_mode(mode):
    return mode in LearningMode.values

from django.db import models
from django.utils.translation import gettext_lazy as _


class StudyStatus(models.TextChoices):
    LEARNED = ("LEARNED", _("Learned"))
    PROCESS = ("PROCESS", _("In progress"))


class PartOfSpeech(models.TextChoices):
    NOUN = ("NOUN", _("Noun"))
    VERB = ("VERB", _("Verb"))
    ADJECTIVE = ("ADJECTIVE", _("Adjective"))
    ADVERB = ("ADVERB", _("Adverb"))
    PRONOUN = ("PRONOUN", _("Pronoun"))
    PREPOSITION = ("PREPOSITION", _("Preposition"))
    CONJUNCTION = ("CONJUNCTION", _("Conjunction"))
    DETERMINER = ("DETERMINER", _("Determiner"))
    INTERJECTION = ("INTERJECTION", _("Interjection"))
    NUMERAL = ("NUMERAL", _("Numeral"))
    PHRASE = ("PHRASE", _("Phrase"))
    OTHER = ("OTHER", _("Other"))


class LanguageLevel(models.TextChoices):
    A1 = ("A1", "A1")
    A2 = ("A2", "A2")
    B1 = ("B1", "B1")
    B2 = ("B2", "B2")
    C1 = ("C1", "C1")
    C2 = ("C2", "C2")


class UsageRegister(models.TextChoices):
    NEUTRAL = ("NEUTRAL", _("Neutral"))
    FORMAL = ("FORMAL", _("Formal"))
    INFORMAL = ("INFORMAL", _("Informal"))
    SLANG = ("SLANG", _("Slang"))
    TECHNICAL = ("TECHNICAL", _("Technical"))
    LITERARY = ("LITERARY", _("Literary"))
    OLD_FASHIONED = ("OLD_FASHIONED", _("Old-fashioned"))

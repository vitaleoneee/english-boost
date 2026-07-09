from django.utils.translation import gettext_lazy as _

# SRS settings
SRS_LEARNED_THRESHOLD = 21  # The interval in days at which a word is considered learned
SRS_INITIAL_INTERVAL = 1  # Initial recurrence interval (in days)

WORD_ACHIEVEMENTS = [
    (5, _("Beginner")),
    (10, _("First Ten")),
    (50, _("Vocabulary Builder")),
    (100, _("Vocabulary Master")),
    (1000, _("One Thousand Words")),
]

TIME_ACHIEVEMENTS = [
    (1, _("First Day")),
    (7, _("Disciplined Learner")),
    (30, _("Like Clockwork")),
]

SRS_ACHIEVEMENTS = [
    (1, _("First Review")),
    (10, _("Power of Repetition")),
    (100, _("Memory Champion")),
]

FLAWLESS_SRS_ACHIEVEMENTS = [
    (5, _("Iron Focus")),
    (10, _("Perfect Session")),
]

# Word statuses
WORD_STATUS_PROCESS = "PROCESS"
WORD_STATUS_LEARNED = "LEARNED"

# Messages for user
SRS_WORD_NOT_AVAILABLE_MSG = _("This word is not yet available for review.")
SRS_CORRECT_ANSWER_MSG = _("Correct! The interval has been increased.")
SRS_LEARNED_MSG = _("You have learned the word — {}!")
SRS_WRONG_ANSWER_MSG = _('Incorrect. The word "{}" has been reset.')

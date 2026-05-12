# SRS settings
SRS_LEARNED_THRESHOLD = 8  # The interval in days at which a word is considered learned
SRS_INITIAL_INTERVAL = 1  # Initial recurrence interval (in days)

WORD_ACHIEVEMENTS = [
    (5, "Начинающий"),
    (10, "Первый десяток"),
    (50, "Словарный строитель"),
    (100, "Лексический мастер"),
    (1000, "Тысяча слов"),
]

TIME_ACHIEVEMENTS = [
    (1, "Первый день"),
    (7, "Ученик дисциплины"),
    (30, "Ты как часы"),
]

SRS_ACHIEVEMENTS = [
    (1, "Первое повторение"),
    (10, "Сила повторения"),
    (100, "Чемпион памяти"),
]

FLAWLESS_SRS_ACHIEVEMENTS = [(5, "Железная концентрация"), (10, "Безупречная сессия")]

# Word statuses
WORD_STATUS_PROCESS = "PROCESS"
WORD_STATUS_LEARNED = "LEARNED"

# Messages for user
SRS_WORD_NOT_FOUND_MSG = "Слово не найдено или у вас нет к нему доступа."
SRS_OBJECT_NOT_FOUND_MSG = "SRS-объект не найден."
SRS_WORD_NOT_AVAILABLE_MSG = "Слово пока недоступно для проверки."
SRS_FORM_ERROR_MSG = "Ошибка формы."
SRS_CORRECT_ANSWER_MSG = "Верно! Интервал увеличен."
SRS_LEARNED_MSG = "Вы выучили слово — {}!"
SRS_WRONG_ANSWER_MSG = 'Неверно. Слово "{}" начато заново.'

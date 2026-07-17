from dataclasses import dataclass

from apps.progress.services.modes import LearningMode


def normalize_answer(value):
    return value.strip().lower()


@dataclass(frozen=True)
class AnswerCheckResult:
    is_correct: bool
    user_answer: str
    correct_answer: str


class BaseAnswerChecker:
    def get_correct_answer(self, word):
        raise NotImplementedError

    def check(self, word, answer):
        user_answer = answer.strip()
        correct_answer = self.get_correct_answer(word).strip()
        return AnswerCheckResult(
            is_correct=normalize_answer(user_answer)
            == normalize_answer(correct_answer),
            user_answer=user_answer,
            correct_answer=correct_answer,
        )


class EnglishToRussianChecker(BaseAnswerChecker):
    def get_correct_answer(self, word):
        return word.russian_name


class RussianToEnglishChecker(BaseAnswerChecker):
    def get_correct_answer(self, word):
        return word.english_name


class AudioToEnglishChecker(RussianToEnglishChecker):
    pass


CHECKERS = {
    LearningMode.EN_TO_RU: EnglishToRussianChecker(),
    LearningMode.RU_TO_EN: RussianToEnglishChecker(),
    LearningMode.AUDIO_TO_EN: AudioToEnglishChecker(),
}


def get_answer_checker(mode):
    return CHECKERS[LearningMode(mode)]

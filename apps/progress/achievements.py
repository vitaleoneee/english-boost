from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.progress.constants import (
    WORD_ACHIEVEMENTS,
    TIME_ACHIEVEMENTS,
    SRS_ACHIEVEMENTS,
    FLAWLESS_SRS_ACHIEVEMENTS,
)
from apps.progress.models import Achievement, UserAchievement
from redis_service import r


class AchievementChecker:
    def __init__(self, user):
        self.user = user
        self.new_achievements = []

    def _check_achievement_existence(self, achievement_name):
        try:
            return Achievement.objects.get(name=achievement_name)
        except ObjectDoesNotExist:
            raise Http404(
                _(
                    "An error occurred while awarding the achievement. Please contact the developer through the website's homepage."
                )
            )

    def _try_grant_achievement(self, name):
        achievement = self._check_achievement_existence(name)
        if not UserAchievement.objects.filter(
            user=self.user, achievement=achievement
        ).exists():
            UserAchievement.objects.create(
                user=self.user, achievement=achievement, is_seen=False
            )
            self.new_achievements.append(name)

    def check_word_count(self):
        words_count = self.user.words.count()

        for threshold, name in WORD_ACHIEVEMENTS:
            if words_count >= threshold:
                self._try_grant_achievement(name)

        return self.new_achievements

    def check_deleted_words(self):
        key = f"{self.user.username}:{self.user.id}:del_counter"
        count = int(r.get(key) or 0)

        if count >= 10:
            self._try_grant_achievement(_("The Cleaner"))

        return self.new_achievements

    def check_day_count(self):
        date_today = timezone.now().date()
        counter_key = f"{self.user.username}:{self.user.id}:day_counter"
        last_date_key = f"{self.user.username}:{self.user.id}:last_day_check"

        last_date = r.get(last_date_key)
        if last_date is None or last_date != str(date_today):
            r.incr(counter_key)
            r.set(last_date_key, str(date_today))

        day_count = int(r.get(counter_key) or 0)
        for threshold, name in TIME_ACHIEVEMENTS:
            if day_count >= threshold:
                self._try_grant_achievement(name)

        return self.new_achievements

    def check_night_achievement(self):
        hours = timezone.localtime().hour
        if 0 < hours < 5:
            self._try_grant_achievement(_("Night Owl"))

        return self.new_achievements

    def check_srs_session_count(self):
        srs_session_count = int(
            r.get(f"{self.user.username}:{self.user.id}:srs_session_counter") or 0
        )
        for threshold, name in SRS_ACHIEVEMENTS:
            if srs_session_count >= threshold:
                self._try_grant_achievement(name)

        return self.new_achievements

    def check_srs_accuracy_counter(self):
        srs_accuracy_counter = int(
            r.get(f"{self.user.username}:{self.user.id}:srs_accuracy_counter") or 0
        )
        for threshold, name in FLAWLESS_SRS_ACHIEVEMENTS:
            if srs_accuracy_counter >= threshold:
                self._try_grant_achievement(name)

        return self.new_achievements

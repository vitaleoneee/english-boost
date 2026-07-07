from django.utils import timezone

from redis_service import r


class DailyCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            self._maybe_check_day(request)
        return self.get_response(request)

    def _maybe_check_day(self, request):
        today = str(timezone.now().date())
        day_key = f"{request.user.username}:{request.user.id}:last_mw_check"

        if r.get(day_key) != today:
            r.set(day_key, today, ex=86400)
            from apps.progress.achievements import AchievementChecker

            checker = AchievementChecker(request.user)
            checker.check_day_count()

        hours = timezone.localtime().hour
        if 0 < hours < 5:
            night_key = f"{request.user.username}:{request.user.id}:last_night_check"
            if r.get(night_key) != today:
                r.set(night_key, today, ex=86400)
                from apps.progress.achievements import AchievementChecker

                checker = AchievementChecker(request.user)
                checker.check_night_achievement()

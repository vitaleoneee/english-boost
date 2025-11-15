from english_app.apps.progress.achievements import AchievementChecker


def check_and_set_achievements(request, checker_method):
    checker = AchievementChecker(request, request.user)
    getattr(checker, checker_method)()

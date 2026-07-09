from apps.progress.models import UserAchievement


def unseen_achievements(request):
    if not request.user.is_authenticated:
        return {}

    achievements = list(
        UserAchievement.objects.filter(
            user=request.user,
            is_seen=False,
        ).select_related("achievement")
    )

    return {
        "unseen_achievements": achievements,
    }

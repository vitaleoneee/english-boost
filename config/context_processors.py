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

    UserAchievement.objects.filter(
        id__in=[a.id for a in achievements]
    ).update(is_seen=True)

    return {
        "unseen_achievements": achievements,
    }

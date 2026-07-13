MODERATOR_GROUP_NAME = "moderators"


def is_moderator(user):
    if not getattr(user, "is_authenticated", False):
        return False
    return user.groups.filter(name=MODERATOR_GROUP_NAME).exists()


def can_access_support_request(user, support_request):
    if not getattr(user, "is_authenticated", False):
        return False
    return support_request.user_id == user.pk or is_moderator(user)

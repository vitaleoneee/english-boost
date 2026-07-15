from apps.support.permissions import is_moderator


def support_permissions(request):
    return {"support_is_moderator": is_moderator(request.user)}

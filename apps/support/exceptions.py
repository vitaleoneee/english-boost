from django.utils.translation import gettext_lazy as _


class SupportServiceError(Exception):
    code = "SUPPORT_ERROR"
    default_message = _("Support operation failed")

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class AuthenticationRequired(SupportServiceError):
    code = "AUTHENTICATION_REQUIRED"
    default_message = _("Authentication is required")


class SupportAccessDenied(SupportServiceError):
    code = "ACCESS_DENIED"
    default_message = _("You do not have access to this support request")


class SupportRequestNotFound(SupportServiceError):
    code = "REQUEST_NOT_FOUND"
    default_message = _("Support request was not found")


class InvalidMessage(SupportServiceError):
    code = "INVALID_MESSAGE"
    default_message = _("Message text is invalid")


class MessagesNotAllowed(SupportServiceError):
    code = "MESSAGES_NOT_ALLOWED"
    default_message = _("Wait for a moderator to join the conversation")


class RequestClosed(SupportServiceError):
    code = "REQUEST_CLOSED"
    default_message = _("Support request is already closed")


class RequestNotInProgress(SupportServiceError):
    code = "REQUEST_NOT_IN_PROGRESS"
    default_message = _("Only an active support request can be closed")


class RequestNotClosed(SupportServiceError):
    code = "REQUEST_NOT_CLOSED"
    default_message = _("Only a closed support request can be rated")


class InvalidRating(SupportServiceError):
    code = "INVALID_RATING"
    default_message = _("Rating must be either helped or did not help")


class AlreadyRated(SupportServiceError):
    code = "ALREADY_RATED"
    default_message = _("This support request has already been rated")

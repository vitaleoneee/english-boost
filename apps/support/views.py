import json
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.support.exceptions import (
    AuthenticationRequired,
    InvalidMessage,
    InvalidRating,
    SupportAccessDenied,
    SupportRequestNotFound,
    SupportServiceError,
)
from apps.support.models import SupportRequest
from apps.support.permissions import can_access_support_request, is_moderator
from apps.support.realtime import broadcast_support_request_status
from apps.support.services import (
    close_support_request,
    create_support_request,
    rate_support_request,
)

ERROR_STATUS_CODES = {
    AuthenticationRequired: 401,
    SupportAccessDenied: 403,
    SupportRequestNotFound: 404,
    InvalidMessage: 400,
    InvalidRating: 400,
}


@require_GET
@login_required
def moderator_dashboard(request):
    if not is_moderator(request.user):
        raise PermissionDenied
    return render(
        request,
        "support/moderator_dashboard.html",
        {"selected": "support"},
    )


def api_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _error_response(AuthenticationRequired())
        return view_func(request, *args, **kwargs)

    return wrapper


def _error_response(error):
    status = next(
        (
            status_code
            for error_class, status_code in ERROR_STATUS_CODES.items()
            if isinstance(error, error_class)
        ),
        409,
    )
    return JsonResponse(
        {"error": {"code": error.code, "message": str(error.message)}},
        status=status,
    )


def _read_json(request):
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError from error

    if not isinstance(data, dict):
        raise ValueError
    return data


def _invalid_json_response():
    return JsonResponse(
        {"error": {"code": "INVALID_JSON", "message": "Invalid JSON body"}},
        status=400,
    )


def _serialize_request(
    support_request,
    viewer,
    *,
    include_messages=False,
    viewer_is_moderator=None,
):
    if viewer_is_moderator is None:
        viewer_is_moderator = is_moderator(viewer)
    viewer_is_owner = support_request.user_id == viewer.pk
    request_is_closed = support_request.status == SupportRequest.Status.CLOSED
    has_rating = (
        viewer_is_owner and request_is_closed and hasattr(support_request, "rating")
    )
    data = {
        "id": support_request.pk,
        "status": support_request.status,
        "user": {
            "id": support_request.user_id,
            "username": support_request.user.get_username(),
        },
        "created_at": support_request.created_at.isoformat(),
        "updated_at": support_request.updated_at.isoformat(),
        "started_at": (
            support_request.started_at.isoformat()
            if support_request.started_at
            else None
        ),
        "closed_at": (
            support_request.closed_at.isoformat() if support_request.closed_at else None
        ),
        "can_send_messages": (
            support_request.status == SupportRequest.Status.IN_PROGRESS
            or (
                support_request.status == SupportRequest.Status.WAITING_MODERATOR
                and viewer_is_moderator
            )
        ),
        "can_rate": (viewer_is_owner and request_is_closed and not has_rating),
        "rating": ({"helped": support_request.rating.helped} if has_rating else None),
    }

    if include_messages:
        data["messages"] = [
            {
                "id": message.pk,
                "author": (
                    "user"
                    if message.author_id == support_request.user_id
                    else "moderator"
                ),
                "author_name": message.author.get_username(),
                "text": message.text,
                "created_at": message.created_at.isoformat(),
            }
            for message in support_request.messages.all()
        ]

    return data


def _get_visible_request(request_id, user):
    try:
        support_request = (
            SupportRequest.objects.select_related("user", "rating")
            .prefetch_related("messages__author")
            .get(pk=request_id)
        )
    except SupportRequest.DoesNotExist as error:
        raise SupportRequestNotFound from error

    if not can_access_support_request(user, support_request):
        raise SupportAccessDenied
    return support_request


@require_http_methods(["GET", "POST"])
@api_login_required
def support_request_collection(request):
    if request.method == "POST":
        try:
            data = _read_json(request)
            support_request = create_support_request(request.user, data.get("text"))
        except ValueError:
            return _invalid_json_response()
        except SupportServiceError as error:
            return _error_response(error)

        support_request = SupportRequest.objects.select_related("user").get(
            pk=support_request.pk
        )
        return JsonResponse(
            {"request": _serialize_request(support_request, request.user)},
            status=201,
        )

    support_requests = SupportRequest.objects.select_related("user", "rating")
    viewer_is_moderator = is_moderator(request.user)
    if not viewer_is_moderator:
        support_requests = support_requests.filter(user=request.user)

    return JsonResponse(
        {
            "requests": [
                _serialize_request(
                    support_request,
                    request.user,
                    viewer_is_moderator=viewer_is_moderator,
                )
                for support_request in support_requests
            ]
        }
    )


@require_GET
@api_login_required
def support_request_detail(request, request_id):
    try:
        support_request = _get_visible_request(request_id, request.user)
    except SupportServiceError as error:
        return _error_response(error)

    return JsonResponse(
        {
            "request": _serialize_request(
                support_request,
                request.user,
                include_messages=True,
            )
        }
    )


@require_POST
@api_login_required
def support_request_close(request, request_id):
    try:
        support_request = close_support_request(request_id, request.user)
    except SupportServiceError as error:
        return _error_response(error)

    broadcast_support_request_status(support_request)
    return JsonResponse({"request": _serialize_request(support_request, request.user)})


@require_POST
@api_login_required
def support_request_rating(request, request_id):
    try:
        data = _read_json(request)
        rating = rate_support_request(request_id, request.user, data.get("helped"))
    except ValueError:
        return _invalid_json_response()
    except SupportServiceError as error:
        return _error_response(error)

    return JsonResponse(
        {
            "rating": {
                "request_id": rating.request_id,
                "helped": rating.helped,
                "created_at": rating.created_at.isoformat(),
            }
        },
        status=201,
    )

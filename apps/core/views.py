import os

from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.core.forms import ContactForm
from apps.progress.models import UserAchievement


class ToastView(TemplateView):
    template_name = "core/partials/toasts.html"


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "selected": "index",
                "form": ContactForm(),
            }
        )
        return context


@login_required
@require_POST
def mark_achievements_seen(request):
    UserAchievement.objects.filter(
        user=request.user,
        is_seen=False,
    ).update(is_seen=True)
    return HttpResponse(status=204)


@require_POST
def send_features_view(request):
    form = ContactForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "core/partials/send_form_btn.html",
            {"message": _("Form cannot be sent. Please try again later")},
        )

    full_name = form.cleaned_data["full_name"]
    email = form.cleaned_data["email"]
    message = form.cleaned_data["message"]
    from_email = f"{full_name} <{email}>"

    try:
        send_mail(
            subject=f"Message from {full_name} ({email})!",
            message=message,
            from_email=from_email,
            recipient_list=[os.environ.get("EMAIL_HOST_USER")],
        )
        return render(
            request,
            "core/partials/send_form_btn.html",
            {"message": _("Form sent successfully!")},
        )
    except Exception:
        return render(
            request,
            "core/partials/send_form_btn.html",
            {"message": _("Form cannot be sent. Please try again later")},
        )

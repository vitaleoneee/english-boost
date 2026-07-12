import itertools

import django_tables2 as tables
from django.utils.html import escapejs, format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.dictionary.models import Word


class DictionaryTable(tables.Table):
    # Checkbox column for bulk actions
    select = tables.Column(
        empty_values=(),
        orderable=False,
        verbose_name=mark_safe(
            '<input type="checkbox" id="select-all" class="form-check-input">'
        ),
        attrs={
            "td": {"class": "text-center align-middle select-cell"},
            "th": {"class": "text-center align-middle select-cell"},
        },
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name="#",
        orderable=False,
        attrs={
            "td": {"class": "text-center align-middle fw-semibold row-number-cell"},
            "th": {"class": "text-center align-middle row-number-cell"},
        },
    )
    english_name = tables.Column(
        verbose_name=_("English word"),
        attrs={
            "td": {"class": "text-center align-middle word-text-cell"},
            "th": {"class": "text-center align-middle"},
        },
    )
    russian_name = tables.Column(
        verbose_name=_("Translation"),
        attrs={
            "td": {"class": "text-center align-middle word-text-cell"},
            "th": {"class": "text-center align-middle"},
        },
    )
    topics = tables.Column(
        empty_values=(),
        verbose_name=_("Topics"),
        orderable=False,
        attrs={
            "td": {"class": "text-center align-middle"},
            "th": {"class": "text-center align-middle"},
        },
    )
    # accessor='pk' is required for virtual column rendering
    pronunciation = tables.Column(
        verbose_name=_("Pronunciation"),
        orderable=False,
        empty_values=(),
        accessor="pk",
        attrs={
            "td": {"class": "text-center align-middle pronunciation-cell"},
            "th": {"class": "text-center align-middle"},
        },
    )
    status = tables.Column(
        verbose_name=_("Status"),
        attrs={
            "td": {"class": "text-center align-middle status-cell"},
            "th": {"class": "text-center align-middle"},
        },
    )

    class Meta:
        model = Word
        template_name = "django_tables2/dictionary_bootstrap5.html"
        fields = (
            "select",
            "row_number",
            "english_name",
            "russian_name",
            "topics",
            "pronunciation",
            "status",
        )
        attrs = {
            "class": "table table-hover align-middle custom-table mb-0",
            "thead": {"class": "table-dark"},
        }

    def render_select(self, record):
        return format_html(
            '<input type="checkbox" name="selected_words" value="{}" class="form-check-input">',
            record.id,
        )

    def render_row_number(self):
        start_index = self.page.start_index() if hasattr(self, "page") else 1
        self.row_number = getattr(self, "row_number", itertools.count(start_index))
        return next(self.row_number)

    def render_pronunciation(self, value, record):
        word_js = escapejs(record.english_name)
        return format_html(
            '<button type="button" class="btn btn-sm btn-outline-secondary pronunciation-btn" '
            'onclick="playAudio(\'{}\')" data-bs-toggle="tooltip" data-bs-placement="top" title="Play pronunciation">'
            '<i class="bi bi-play-fill"></i>'
            "</button>",
            word_js,
        )

    def render_topics(self, record):
        topics = record.topics.all()
        if not topics:
            return "—"
        return format_html_join(
            " ",
            '<span class="badge text-bg-light border">{}</span>',
            ((topic.name,) for topic in topics),
        )

    def render_status(self, value, record):
        if record.status == "LEARNED":
            badge = "dictionary-status dictionary-status-learned"
            text = _("Learned")
        else:
            badge = "dictionary-status dictionary-status-process"
            text = _("In progress")
        return format_html('<span class="{}">{}</span>', badge, text)

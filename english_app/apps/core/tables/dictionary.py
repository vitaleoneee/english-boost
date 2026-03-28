import itertools
import django_tables2 as tables
from django.utils.html import format_html, escapejs

from english_app.apps.core.models import Word


class DictionaryTable(tables.Table):
    # Checkbox column for bulk actions
    select = tables.Column(
        empty_values=(),
        orderable=False,
        verbose_name=format_html(
            '<input type="checkbox" id="select-all" class="form-check-input">'
        ),
        attrs={
            "td": {"class": "text-center align-middle bg-dark"},
            "th": {"class": "text-center align-middle"},
        },
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name="#",
        orderable=False,
        attrs={
            "td": {"class": "text-center align-middle fw-bold"},
            "th": {"class": "text-center align-middle"},
        },
    )
    english_name = tables.Column(
        verbose_name="Слово на английском",
        attrs={
            "td": {"class": "text-center align-middle"},
            "th": {"class": "text-center align-middle"},
        },
    )
    russian_name = tables.Column(
        verbose_name="Перевод",
        attrs={
            "td": {"class": "text-center align-middle"},
            "th": {"class": "text-center align-middle"},
        },
    )
    # accessor='pk' is required for virtual column rendering
    pronunciation = tables.Column(
        verbose_name="Произношение",
        orderable=False,
        empty_values=(),
        accessor="pk",
        attrs={
            "td": {"class": "text-center align-middle"},
            "th": {"class": "text-center align-middle"},
        },
    )
    status = tables.Column(
        verbose_name="Статус",
        attrs={
            "td": {"class": "text-center align-middle"},
            "th": {"class": "text-center align-middle"},
        },
    )

    class Meta:
        model = Word
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = (
            "select",
            "row_number",
            "english_name",
            "russian_name",
            "pronunciation",
            "status",
        )
        attrs = {
            "class": "table table-bordered table-hover align-middle custom-table mb-0",
            "thead": {"class": "table-dark"},
        }

    def render_select(self, record):
        return format_html(
            '<input type="checkbox" name="selected_words" value="{}" class="form-check-input">',
            record.id,
        )

    def render_row_number(self):
        self.row_number = getattr(
            self, "row_number", itertools.count(self.page.start_index())
        )
        return next(self.row_number)

    def render_pronunciation(self, value, record):
        word_js = escapejs(record.english_name)
        return format_html(
            '<button type="button" class="btn btn-sm btn-outline-secondary" '
            'onclick="playAudio(\'{}\')" data-bs-toggle="tooltip" data-bs-placement="top" title="Play pronunciation">'
            '<i class="bi bi-play-fill"></i>'
            "</button>",
            word_js,
        )

    def render_status(self, value, record):
        if record.status == "LEARNED":
            badge = "success"
            text = "Изучено"
        else:
            badge = "warning text-dark"
            text = "В процессе"
        return format_html('<span class="badge bg-{}">{}</span>', badge, text)

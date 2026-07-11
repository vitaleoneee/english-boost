from django.db import migrations, models


ACHIEVEMENT_ICONS = {
    1: "bi-flower1",
    2: "bi-list-ol",
    3: "bi-bricks",
    4: "bi-book-half",
    5: "bi-collection-fill",
    6: "bi-sunrise-fill",
    7: "bi-calendar-week-fill",
    8: "bi-clock-fill",
    9: "bi-moon-stars-fill",
    10: "bi-arrow-repeat",
    11: "bi-lightning-charge-fill",
    12: "bi-trophy-fill",
    13: "bi-bullseye",
    14: "bi-patch-check-fill",
    15: "bi-eraser-fill",
}


def set_achievement_icons(apps, schema_editor):
    Achievement = apps.get_model("progress", "Achievement")
    for achievement_id, icon in ACHIEVEMENT_ICONS.items():
        Achievement.objects.filter(pk=achievement_id).update(icon=icon)


class Migration(migrations.Migration):
    dependencies = [("progress", "0018_alter_achievement_options_and_more")]

    operations = [
        migrations.AddField(
            model_name="achievement",
            name="icon",
            field=models.CharField(
                default="bi-award-fill",
                help_text="Bootstrap Icons class, for example: bi-book-fill",
                max_length=50,
                verbose_name="Icon",
            ),
        ),
        migrations.RunPython(set_achievement_icons, migrations.RunPython.noop),
    ]

from django.db import migrations


MODERATOR_GROUP_NAME = "moderators"


def create_moderators_group(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    group_model.objects.get_or_create(name=MODERATOR_GROUP_NAME)


def remove_moderators_group(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    group_model.objects.filter(name=MODERATOR_GROUP_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("support", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_moderators_group,
            remove_moderators_group,
        ),
    ]

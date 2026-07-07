from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("progress", "0013_update_word_fk"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                'ALTER TABLE IF EXISTS "games_achievement" RENAME TO "progress_achievement"',
                'ALTER TABLE IF EXISTS "games_userachievement" RENAME TO "progress_userachievement"',
                'ALTER TABLE IF EXISTS "games_usersrs" RENAME TO "progress_usersrs"',
            ],
            reverse_sql=[
                'ALTER TABLE IF EXISTS "progress_achievement" RENAME TO "games_achievement"',
                'ALTER TABLE IF EXISTS "progress_userachievement" RENAME TO "games_userachievement"',
                'ALTER TABLE IF EXISTS "progress_usersrs" RENAME TO "games_usersrs"',
            ],
        ),
    ]

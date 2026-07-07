from django.db import migrations


RENAME_CONSTRAINTS = """
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'games_achievement_pkey')
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'progress_achievement_pkey') THEN
        ALTER TABLE "progress_achievement" RENAME CONSTRAINT "games_achievement_pkey" TO "progress_achievement_pkey";
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'games_userachievement_pkey')
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'progress_userachievement_pkey') THEN
        ALTER TABLE "progress_userachievement" RENAME CONSTRAINT "games_userachievement_pkey" TO "progress_userachievement_pkey";
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'games_userachievemen_achievement_id_8619c28f_fk_games_ach')
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'progress_userachievement_achievement_id_fk') THEN
        ALTER TABLE "progress_userachievement" RENAME CONSTRAINT "games_userachievemen_achievement_id_8619c28f_fk_games_ach" TO "progress_userachievement_achievement_id_fk";
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'games_userachievement_user_id_52176570_fk_auth_user_id')
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'progress_userachievement_user_id_fk') THEN
        ALTER TABLE "progress_userachievement" RENAME CONSTRAINT "games_userachievement_user_id_52176570_fk_auth_user_id" TO "progress_userachievement_user_id_fk";
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'games_usersrs_pkey')
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'progress_usersrs_pkey') THEN
        ALTER TABLE "progress_usersrs" RENAME CONSTRAINT "games_usersrs_pkey" TO "progress_usersrs_pkey";
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'games_usersrs_word_id_key')
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'progress_usersrs_word_id_key') THEN
        ALTER TABLE "progress_usersrs" RENAME CONSTRAINT "games_usersrs_word_id_key" TO "progress_usersrs_word_id_key";
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'games_usersrs_user_id_f1020d36_fk_auth_user_id')
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'progress_usersrs_user_id_fk') THEN
        ALTER TABLE "progress_usersrs" RENAME CONSTRAINT "games_usersrs_user_id_f1020d36_fk_auth_user_id" TO "progress_usersrs_user_id_fk";
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'games_usersrs_word_id_85ea0009_fk_core_word_id')
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'progress_usersrs_word_id_fk') THEN
        ALTER TABLE "progress_usersrs" RENAME CONSTRAINT "games_usersrs_word_id_85ea0009_fk_core_word_id" TO "progress_usersrs_word_id_fk";
    END IF;
END $$;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("progress", "0014_rename_games_tables"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                RENAME_CONSTRAINTS,
                'ALTER INDEX IF EXISTS "games_userachievement_achievement_id_8619c28f" RENAME TO "progress_userachievement_achievement_id_idx"',
                'ALTER INDEX IF EXISTS "games_userachievement_user_id_52176570" RENAME TO "progress_userachievement_user_id_idx"',
                'ALTER INDEX IF EXISTS "games_usersrs_user_id_f1020d36" RENAME TO "progress_usersrs_user_id_idx"',
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

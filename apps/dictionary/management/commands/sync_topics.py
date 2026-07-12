from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.dictionary.models import Topic
from apps.dictionary.topic_catalog import SYSTEM_TOPICS


class Command(BaseCommand):
    help = "Synchronize system topics with the versioned topic catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show planned changes without modifying the database.",
        )
        parser.add_argument(
            "--delete-obsolete",
            action="store_true",
            help="Delete inactive system topics instead of keeping them archived.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Allow deletion of obsolete topics that are linked to words.",
        )

    def handle(self, *args, **options):
        if options["force"] and not options["delete_obsolete"]:
            raise CommandError("--force can only be used with --delete-obsolete.")

        catalog = {item["code"]: item for item in SYSTEM_TOPICS}
        if len(catalog) != len(SYSTEM_TOPICS):
            raise CommandError("SYSTEM_TOPICS contains duplicate codes.")

        with transaction.atomic():
            changes = self._synchronize(catalog, options)
            if options["dry_run"]:
                transaction.set_rollback(True)

        summary = ", ".join(f"{key}: {value}" for key, value in changes.items())
        prefix = "Dry run: " if options["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(f"{prefix}{summary}"))

    def _synchronize(self, catalog, options):
        changes = {
            "created": 0,
            "updated": 0,
            "reactivated": 0,
            "archived": 0,
            "deleted": 0,
            "unchanged": 0,
            "skipped": 0,
        }

        existing = {topic.code: topic for topic in Topic.objects.filter(is_system=True)}

        for code, data in catalog.items():
            topic = existing.get(code)
            if topic is None:
                Topic.objects.create(**data, is_active=True, is_system=True)
                changes["created"] += 1
                self.stdout.write(f"CREATE {code}")
                continue

            fields = []
            if topic.name != data["name"]:
                topic.name = data["name"]
                fields.append("name")
            if topic.description != data["description"]:
                topic.description = data["description"]
                fields.append("description")
            if not topic.is_active:
                topic.is_active = True
                fields.append("is_active")
                changes["reactivated"] += 1

            if fields:
                topic.save(update_fields=[*fields, "updated_at"])
                changes["updated"] += 1
                self.stdout.write(f"UPDATE {code}")
            else:
                changes["unchanged"] += 1

        obsolete = Topic.objects.filter(is_system=True).exclude(code__in=catalog)
        for topic in obsolete:
            if options["delete_obsolete"]:
                word_count = topic.words.count()
                if word_count and not options["force"]:
                    changes["skipped"] += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"SKIP {topic.code}: linked to {word_count} word(s); use --force"
                        )
                    )
                    continue
                self.stdout.write(f"DELETE {topic.code}")
                topic.delete()
                changes["deleted"] += 1
            elif topic.is_active:
                topic.is_active = False
                topic.save(update_fields=["is_active", "updated_at"])
                changes["archived"] += 1
                self.stdout.write(f"ARCHIVE {topic.code}")
            else:
                changes["unchanged"] += 1

        return changes

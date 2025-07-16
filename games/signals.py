from django.db.models.signals import post_migrate
from django.dispatch import receiver
from games.models import Achievement
from games.constants import DEFAULT_ACHIEVEMENTS


@receiver(post_migrate)
def create_default_achievements(sender, **kwargs):
    for category, achievements in DEFAULT_ACHIEVEMENTS.items():
        for threshold, name, description, secret in achievements:
            full_name = name if threshold else name
            Achievement.objects.get_or_create(
                name=full_name,
                defaults={
                    'description': description,
                    'secret': secret
                }
            )

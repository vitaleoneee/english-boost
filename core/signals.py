from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

from core.constants import DEFAULT_CATEGORIES


@receiver(post_migrate)
def create_default_categories(sender, app_config, **kwargs):
    Category = apps.get_model('core', 'Category')

    for name, description in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )

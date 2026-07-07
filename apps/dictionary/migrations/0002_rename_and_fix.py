from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("dictionary", "0001_move_from_core"),
    ]

    operations = [
        migrations.AlterModelTable(name="Category", table=None),
        migrations.AlterModelTable(name="Word", table=None),
    ]

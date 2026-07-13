import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('waiting_moderator', 'Waiting for moderator'), ('in_progress', 'In progress'), ('closed', 'Closed')], db_index=True, default='waiting_moderator', max_length=32, verbose_name='Status')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Started at')),
                ('closed_at', models.DateTimeField(blank=True, null=True, verbose_name='Closed at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('closed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='closed_support_requests', to=settings.AUTH_USER_MODEL, verbose_name='Closed by')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_requests', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Support request',
                'verbose_name_plural': 'Support requests',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='SupportRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('helped', models.BooleanField(verbose_name='Helped')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='support.supportrequest', verbose_name='Support request')),
            ],
            options={
                'verbose_name': 'Support rating',
                'verbose_name_plural': 'Support ratings',
            },
        ),
        migrations.CreateModel(
            name='SupportMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(validators=[django.core.validators.MaxLengthValidator(4000)], verbose_name='Text')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_messages', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='support.supportrequest', verbose_name='Support request')),
            ],
            options={
                'verbose_name': 'Support message',
                'verbose_name_plural': 'Support messages',
                'ordering': ('created_at', 'id'),
            },
        ),
        migrations.AddIndex(
            model_name='supportrequest',
            index=models.Index(fields=['user', 'status', '-created_at'], name='support_sup_user_id_d7b939_idx'),
        ),
        migrations.AddIndex(
            model_name='supportrequest',
            index=models.Index(fields=['status', '-created_at'], name='support_sup_status_2c5003_idx'),
        ),
        migrations.AddIndex(
            model_name='supportmessage',
            index=models.Index(fields=['request', 'created_at'], name='support_sup_request_7b12c6_idx'),
        ),
    ]

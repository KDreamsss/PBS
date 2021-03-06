# Generated by Django 4.0.4 on 2022-05-01 04:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0006_rename_user_photographer_photographer'),
    ]

    operations = [
        migrations.AddField(
            model_name='photographer',
            name='user',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='photographer',
            name='photographer',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]

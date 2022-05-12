# Generated by Django 4.0.4 on 2022-05-02 14:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0012_alter_photographer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photographer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photographer_user', to=settings.AUTH_USER_MODEL),
        ),
    ]

# Generated by Django 4.0.4 on 2022-05-08 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0020_remove_photographer_available_daytime_order_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(max_length=100),
        ),
    ]

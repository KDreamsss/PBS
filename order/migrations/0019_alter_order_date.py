# Generated by Django 4.0.4 on 2022-05-05 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0018_alter_order_date_alter_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.CharField(max_length=100),
        ),
    ]

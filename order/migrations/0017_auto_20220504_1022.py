# Generated by Django 3.1.7 on 2022-05-04 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0016_remove_photographer_photographer_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='photographer',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

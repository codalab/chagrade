# Generated by Django 2.1.1 on 2019-10-01 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0044_auto_20190930_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='definition',
            name='questions_only',
            field=models.BooleanField(default=False),
        ),
    ]

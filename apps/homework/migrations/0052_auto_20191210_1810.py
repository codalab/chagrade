# Generated by Django 2.1.11 on 2019-12-10 18:10

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0051_auto_20191204_0131'),
    ]

    operations = [
        migrations.AddField(
            model_name='definition',
            name='force_github',
            field=models.BooleanField(default=False),
        )
    ]

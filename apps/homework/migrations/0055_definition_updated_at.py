# Generated by Django 2.2.10 on 2020-04-24 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0054_auto_20200427_0136'),
    ]

    operations = [
        migrations.AddField(
            model_name='definition',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

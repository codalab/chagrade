# Generated by Django 2.1.1 on 2019-07-23 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0030_auto_20190701_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='definition',
            name='baseline_score',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='definition',
            name='target_score',
            field=models.FloatField(default=1.0),
        ),
    ]

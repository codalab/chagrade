# Generated by Django 2.2.10 on 2020-05-07 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('klasses', '0015_auto_20200326_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='klass',
            name='description',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
# Generated by Django 2.1.1 on 2019-11-28 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('klasses', '0013_auto_20191127_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='klass',
            name='course_number',
            field=models.SlugField(max_length=60),
        ),
    ]

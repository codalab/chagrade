# Generated by Django 2.1.1 on 2019-01-25 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0007_auto_20190125_0332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chauser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
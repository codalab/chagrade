# Generated by Django 2.1.1 on 2019-10-04 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0046_auto_20191001_1929'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionanswer',
            old_name='answer',
            new_name='answers',
        ),
    ]
# Generated by Django 2.1.1 on 2019-09-13 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0041_remove_submission_normalized_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionanswer',
            name='text',
            field=models.TextField(default=''),
        ),
    ]

# Generated by Django 2.1.1 on 2019-08-02 22:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0035_auto_20190802_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissiontracker',
            name='submission',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tracker', to='homework.Submission'),
        ),
    ]
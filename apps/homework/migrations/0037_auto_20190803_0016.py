# Generated by Django 2.1.1 on 2019-08-03 00:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0036_auto_20190802_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissiontracker',
            name='submission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tracked_submissions', to='homework.Submission'),
        ),
    ]
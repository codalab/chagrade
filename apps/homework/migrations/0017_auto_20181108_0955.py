# Generated by Django 2.1.1 on 2018-11-08 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0016_grade_overall_grade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='overall_grade',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]

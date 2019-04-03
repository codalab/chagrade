# Generated by Django 2.1.1 on 2019-04-02 20:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_passwordresetrequest_key'),
        ('groups', '0008_team_challenge_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='leader',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='led_teams', to='profiles.StudentMembership'),
        ),
        migrations.AlterField(
            model_name='group',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_template', to='klasses.Klass'),
        ),
        migrations.AlterField(
            model_name='team',
            name='klass',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='klasses.Klass'),
        ),
    ]

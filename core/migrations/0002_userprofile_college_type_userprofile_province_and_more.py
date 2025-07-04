# Generated by Django 5.0.6 on 2025-07-01 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='college_type',
            field=models.CharField(choices=[('Public', 'Public'), ('Private', 'Private')], default='Public', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='province',
            field=models.CharField(default='Punjab', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='year_of_study',
            field=models.CharField(choices=[('1st_year', '1st Year MBBS'), ('2nd_year', '2nd Year MBBS'), ('3rd_year', '3rd Year MBBS'), ('4th_year', '4th Year MBBS'), ('final_year', '5th Year MBBS (Final)'), ('graduate', 'Graduate')], max_length=20),
        ),
    ]

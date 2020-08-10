# Generated by Django 2.2.13 on 2020-08-10 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actorgoal',
            name='drawn_goal_1_img_path',
            field=models.CharField(max_length=127, null=True, verbose_name='Drawn Goal 1 Image Path'),
        ),
        migrations.AddField(
            model_name='actorgoal',
            name='drawn_goal_2_img_path',
            field=models.CharField(max_length=127, null=True, verbose_name='Drawn Goal 2 Image Path'),
        ),
    ]

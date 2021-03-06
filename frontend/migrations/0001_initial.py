# Generated by Django 2.2.13 on 2020-08-10 19:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('modified_at', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Modified At')),
                ('distributed', models.BooleanField(default=False, verbose_name='Distributed')),
                ('for_batch', models.PositiveIntegerField(verbose_name='For Batch')),
            ],
            options={
                'verbose_name': 'Goal State',
                'db_table': 'goal_state',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ActorGoal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('modified_at', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Modified At')),
                ('selected_goal_img_path', models.CharField(max_length=127, verbose_name='Selected Goal Image Path')),
                ('batch', models.PositiveIntegerField(verbose_name='Batch')),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Actor Goal',
                'db_table': 'actor_goal',
                'ordering': ['-created_at'],
                'managed': True,
            },
        ),
    ]

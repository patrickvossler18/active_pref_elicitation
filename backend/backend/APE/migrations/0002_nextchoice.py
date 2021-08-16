# Generated by Django 3.2.6 on 2021-08-16 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APE', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NextChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.JSONField()),
                ('previous_step', models.IntegerField()),
                ('current_step', models.IntegerField()),
                ('choice_topic', models.IntegerField()),
                ('left_choice', models.IntegerField()),
            ],
        ),
    ]

# Generated by Django 4.0 on 2022-08-29 12:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_task_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='parent',
        ),
    ]

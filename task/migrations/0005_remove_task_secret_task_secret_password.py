# Generated by Django 5.2.4 on 2025-07-30 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_remove_task_complete_remove_task_created_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='secret',
        ),
        migrations.AddField(
            model_name='task',
            name='secret_password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]

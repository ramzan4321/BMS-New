# Generated by Django 4.1.3 on 2022-11-15 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0010_project_task_title_alter_project_start_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='task_title',
        ),
    ]

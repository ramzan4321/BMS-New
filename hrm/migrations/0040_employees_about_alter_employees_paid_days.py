# Generated by Django 4.1.3 on 2022-12-08 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0039_employees_account_holder_name_employees_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='employees',
            name='about',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='employees',
            name='paid_days',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
# Generated by Django 4.1.3 on 2022-12-15 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0040_employees_about_alter_employees_paid_days'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=50)),
                ('message', models.CharField(max_length=500)),
            ],
        ),
    ]

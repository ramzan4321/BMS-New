# Generated by Django 4.1.3 on 2022-11-09 12:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hrm', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeesworkdetails',
            name='deduction',
        ),
        migrations.RemoveField(
            model_name='employeesworkdetails',
            name='leave_days',
        ),
        migrations.RemoveField(
            model_name='employeesworkdetails',
            name='leave_reason',
        ),
        migrations.AlterField(
            model_name='employeesworkdetails',
            name='employee_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_work', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='LeaveManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_reason', models.CharField(max_length=150)),
                ('leave_days', models.DateField()),
                ('leave_type', models.CharField(max_length=150)),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_leave', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
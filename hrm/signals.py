from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Employees,TaskTitle,Task

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Employees.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    usr = User.objects.get(username=instance)
    if usr.is_superuser == False:
        instance.employees.save()

@receiver(post_save, sender=TaskTitle)
def create_profile(sender, instance, created, **kwargs):
    print(instance)
    if created:
        Task.objects.create(task_title=instance,project_id=instance.project_id)

@receiver(post_save, sender=TaskTitle)
def save_profile(sender, instance, **kwargs):
    instance.project_id.save()
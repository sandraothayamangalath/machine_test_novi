# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
    ('superadmin', 'SuperAdmin'),
    ('admin', 'Admin'),
    ('user', 'User'),
    )
    ROLE_SUPERADMIN = 'superadmin'
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'
    # ROLE_SUPERADMIN = 'superadmin'
    # ROLE_ADMIN = 'admin'
    # ROLE_USER = 'user'
    # ROLE_CHOICES = (
    #     (ROLE_SUPERADMIN, 'SuperAdmin'),
    #     (ROLE_ADMIN, 'Admin'),
    #     (ROLE_USER, 'User'),
    # )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
    admin = models.ForeignKey('self', null=True, blank=True, related_name='assigned_users', on_delete=models.SET_NULL,
                              limit_choices_to={'role': ROLE_ADMIN})

    def __str__(self):
        return self.username

class Task(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks',
                                    limit_choices_to={'role': 'user'})
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    completion_report = models.TextField(blank=True)
    worked_hours = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
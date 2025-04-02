from django.db import models

class Manager(models.Model):
    user = models.OneToOneField(
        'accounts.User',  # Use string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='dashboard_manager'
    )
    # Add any additional fields you need for Manager

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Dashboard Manager'
        verbose_name_plural = 'Dashboard Managers'

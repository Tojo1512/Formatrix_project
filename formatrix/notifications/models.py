from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPES = [
        ('new_course', 'New course'),
        ('new_trainer', 'New trainer'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', 
                                   verbose_name="Recipient")
    message = models.TextField(verbose_name="Message")
    notification_type = models.CharField(max_length=20, choices=TYPES, verbose_name="Notification type")
    related_id = models.IntegerField(verbose_name="Related ID", help_text="ID of the course or trainer concerned")
    is_read = models.BooleanField(default=False, verbose_name="Read")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creation date")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        
    def __str__(self):
        type_display = dict(self.TYPES).get(self.notification_type, self.notification_type)
        created_at_str = str(self.created_at) if self.created_at else ''
        return f"{type_display} - {created_at_str}"

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPES = [
        ('new_course', 'Nouveau cours'),
        ('new_trainer', 'Nouveau formateur'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', 
                                   verbose_name="Destinataire")
    message = models.TextField(verbose_name="Message")
    notification_type = models.CharField(max_length=20, choices=TYPES, verbose_name="Type de notification")
    related_id = models.IntegerField(verbose_name="ID associé", help_text="ID du cours ou du formateur concerné")
    is_read = models.BooleanField(default=False, verbose_name="Lue")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        
    def __str__(self):
        type_display = dict(self.TYPES).get(self.notification_type, self.notification_type)
        created_at_str = str(self.created_at) if self.created_at else ''
        return f"{type_display} - {created_at_str}"

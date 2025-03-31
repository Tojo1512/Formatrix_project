from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Notification

# Create your views here.

@login_required
def notification_list(request):
    """Displays all notifications for the user"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    """Marks a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:notification_list')

@login_required
def mark_all_read(request):
    """Marks all notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:notification_list')

@login_required
def get_unread_count(request):
    """Returns the count of unread notifications for the current user"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})

def create_notification(message, notification_type, related_id):
    """Creates notifications for all administrators"""
    admin_users = User.objects.filter(is_staff=True)
    
    for user in admin_users:
        Notification.objects.create(
            recipient=user,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )

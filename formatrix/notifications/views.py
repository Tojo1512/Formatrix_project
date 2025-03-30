from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Notification

# Create your views here.

@login_required
def notification_list(request):
    """Affiche toutes les notifications de l'utilisateur"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    """Marque une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:notification_list')

@login_required
def mark_all_read(request):
    """Marque toutes les notifications comme lues"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:notification_list')

@login_required
def get_unread_count(request):
    """Retourne le nombre de notifications non lues pour l'utilisateur actuel"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})

def create_notification(message, notification_type, related_id):
    """Crée des notifications pour tous les administrateurs"""
    admin_users = User.objects.filter(is_staff=True)
    
    for user in admin_users:
        Notification.objects.create(
            recipient=user,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )

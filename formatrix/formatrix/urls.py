"""
URL configuration for formatrix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import register_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('formatrix/admin/', admin.site.urls),
    path('api/cours/', include('cours.urls')),
    path('api/modules/', include('modules.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/renouvellements/', include('renouvellements.urls')),
    path('api/seances/', include('seances.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/lieux/', include('lieux.urls')),
    path('api/apprenants/', include('apprenants.urls')),
    path('api/inscriptions/', include('inscriptions.urls')),
    path('api/evaluations/', include('evaluations.urls')),
    path('api/presences/', include('presences.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='auth/logged_out.html'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

"""business_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from hrm import views as hrm_views
from django.contrib.auth import views as auth_views
from hrm.api import views as api_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hrm_views.index, name='index'),
    path('profile/', hrm_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='hrm/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='hrm/logout.html'), name='logout'),
    path('getpdf/', hrm_views.generate_pdf , name='getpdf'),
    path('send_mail/', hrm_views.send_mail , name='send_mail'),
    path('api/leave/', api_view.LeaveAPI.as_view() , name='employee'),

    path('leave_approved/<int:pk>', hrm_views.leave_approved , name='leaveapproved'),
    path('leave_rejected/<int:pk>', hrm_views.leave_rejected , name='leaverejected'),
    
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

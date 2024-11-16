from django.urls import path, include

app_name = 'dashboard'
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('blog/', include('blog.urls', namespace='blog')),
    path('about/', views.about, name='about'),
]

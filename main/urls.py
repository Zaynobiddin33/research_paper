from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main, name='main'),
    path('about/', views.about, name='about'),
    path('creators/', views.creators, name='creators'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('check-username/', views.check_username, name='check_username'),
    path('upoad-file/', views.upload_paper, name='upload_paper'),
    path('my-papers/', views.my_papers, name='my_papers'),
    path('my-paper/<int:id>', views.my_paper, name='my_paper'),
    path('delete-paper/<int:id>', views.delete_paper, name='delete_paper'),
    path('detail-paper/<int:id>', views.detail_paper, name='detail_paper')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
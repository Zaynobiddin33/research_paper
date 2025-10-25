from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import *

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('about/', AboutView.as_view(), name='about'),
    path('creators/', CreatorsView.as_view(), name='creators'),

    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Papers
    path('upload-paper/', UploadPaperView.as_view(), name='upload_paper'),
    path('all-papers/', AllPapersView.as_view(), name='all_papers'),
    path('my-papers/', MyPapersView.as_view(), name='my_papers'),
    path('my-paper/<int:pk>/', MyPaperDetailView.as_view(), name='my_paper'),
    path('detail-paper/<int:id>/', PaperDetailView.as_view(), name='detail_paper'),
    path('delete-paper/<int:id>/', PaperDeleteView.as_view(), name='delete_paper'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

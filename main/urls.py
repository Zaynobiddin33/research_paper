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

    path('profile/', ProfileStatsView.as_view(), name='profile'),
    path('/profile/settings', ProfileUpdateView.as_view(), name='update_profile'),
    path('profile/password/', PasswordChangeView.as_view(), name='change_password'),
    path('apply-otp/<int:id>', apply_otp, name = 'apply_otp'),

    path('check-username/', check_username, name='check_username'),
    path('admin-waitlist/', admin_waitlist, name='admin_waitlist'),
    path('admin-detail/<int:id>', admin_paper_detail, name='admin_paper_detail'),

    path('paper-accept/<int:id>', accept_paper, name='accept_paper'),
    path('deny_paper/<int:id>', deny_paper, name='deny_paper'),
    path('success-payment/', success_payment, name='success_payment'),

    path('payments/', payments, name='payments'),
    path('payment-accept/<int:id>', accept_payment, name='accept_payment'),
    path('payment-deny/<int:id>', deny_payment, name='deny_payment'),
    path('payment-stats/', payments_stats, name='payments_stats'),

    path('paper-edit/<int:id>', edit_paper, name='edit_paper'),
    path('paper-resubmit/<int:id>', resubmit_paper, name='resubmit_paper'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

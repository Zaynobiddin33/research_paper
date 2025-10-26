from django import forms
from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Joriy parol",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Yangi parol",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Yangi parolni tasdiqlang",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'})
    )

    error_messages = {
        'password_mismatch': "Parollar mos kelmadi. Iltimos qaytadan kiriting.",
        'password_incorrect': "Joriy parol noto‘g‘ri kiritildi. Iltimos, qayta kiriting."
    }
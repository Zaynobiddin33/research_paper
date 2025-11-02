from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from main.forms import CustomPasswordChangeForm


class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'settings.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user = request.user

        # Update basic fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.username = request.POST.get('username', user.username)
        user.save()

        # Handle avatar upload
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save()

        messages.success(request, "Profil muvaffaqiyatli yangilandi ✅")
        return redirect('update_profile')


class PasswordChangeView(LoginRequiredMixin, View):
    template_name = 'settings.html'

    def get(self, request):
        form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {'password_form': form})

    def post(self, request):
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parol muvaffaqiyatli o`zgartirildi")  # Keep user logged in
            return redirect('change_password')
        return render(request, self.template_name, {'password_form': form})

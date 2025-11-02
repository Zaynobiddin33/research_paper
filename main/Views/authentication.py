from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from main.models import CustomUser


class RegisterView(View):
    template_name = 'register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        data = request.POST
        avatar = request.FILES.get('avatar')

        if data['password'] != data['check_password']:
            messages.error(request, "Parollar mos kelmadi!")
            return redirect('register')

        if CustomUser.objects.filter(username=data['username']).exists():
            messages.error(request, "Kechirasiz, bu foydalanuvchi nomi band!")
            return redirect('register')

        CustomUser.objects.create_user(
            first_name=data['name'],
            last_name=data['surname'],
            username=data['username'],
            password=data['password'],
            avatar=avatar
        )
        return redirect('login')


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('main')
        messages.error(request, "Noto'g'ri foydalanuvchi ismi yoki parol.")
        return redirect('login')


class LogoutView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        logout(request)
        return redirect('main')

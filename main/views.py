from PyPDF2 import PdfReader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.views.generic import TemplateView, DetailView

from . import models
from .models import CustomUser, Creator
from .models import Paper, Category


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


class MainView(ListView):
    model = Paper
    template_name = 'index.html'
    context_object_name = 'papers'

    def get_queryset(self):
        number = 6
        return Paper.objects.filter(status=4).order_by('-published_at')[:number]


class AboutView(TemplateView):
    template_name = 'about.html'


class CreatorsView(ListView):
    model = Creator
    template_name = 'owners.html'
    context_object_name = 'creators'

    def get_queryset(self):
        return Creator.objects.all()


class PaperDetailView(View):
    def get(self, request, id):
        paper = get_object_or_404(models.Paper, id=id)
        keywords = [kw.strip() for kw in paper.keywords.split(',')]
        return render(request, 'detail.html', {'paper': paper, 'tags': keywords})


class MyPapersView(LoginRequiredMixin, ListView):
    model = Paper
    template_name = 'papers.html'
    context_object_name = 'papers'
    login_url = 'login'

    def get_queryset(self):
        return Paper.objects.filter(owner=self.request.user).order_by('-id')


class MyPaperDetailView(LoginRequiredMixin, DetailView):
    model = Paper
    template_name = 'detail-owner.html'
    context_object_name = 'paper'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keywords'] = self.object.keywords.split(',')
        return context


class UploadPaperView(LoginRequiredMixin, View):
    template_name = 'upload.html'
    login_url = 'login'

    def get(self, request):
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories})

    def post(self, request):
        data = request.POST
        file = request.FILES['file']
        category = Category.objects.get(name=data['category'])
        pdf = PdfReader(file)
        pages = len(pdf.pages)

        Paper.objects.create(
            owner=request.user,
            title=data['title'],
            summary=data['summary'],
            intro=data['intro'],
            citations=data['citations'],
            file=file,
            category=category,
            keywords=data['keywords'],
            pages=pages,
            status=1
        )
        return redirect('my_papers')


class PaperDeleteView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, id):
        paper = get_object_or_404(models.Paper, id=id, owner=request.user)
        paper.delete()
        return redirect('my_papers')


class AllPapersView(ListView):
    model = Paper
    template_name = 'all_papers.html'
    context_object_name = 'papers'
    paginate_by = 9

    def get_queryset(self):
        queryset = Paper.objects.filter(status=4).order_by('-published_at')

        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(owner__first_name__icontains=query) |
                Q(keywords__icontains=query)
            )

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

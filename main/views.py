from PyPDF2 import PdfReader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import ListView, TemplateView, DetailView
from . import models
from .models import Paper, CustomUser, Category, Creator
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.functions import Concat
from django.db.models import F, Value
from django.utils import timezone


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
    extra_context = {'page_title': "So‘nggi maqolalar"}

    def get_queryset(self):
        queryset = Paper.objects.filter(status=4)
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.annotate(
                full_name=Concat(F('owner__first_name'), Value(' '), F('owner__last_name'))
            ).filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(intro__icontains=query) |
                Q(organization__icontains=query) |
                Q(keywords__icontains=query) |
                Q(full_name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("q"):
            context["page_title"] = "Qidiruv natijalari"
        else:
            context["page_title"] = "So‘nggi maqolalar"
        return context


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

@login_required(redirect_field_name='login')
def apply_otp(request, id):
    paper = models.Paper.objects.get(id = id)
    if request.method == "POST":
        otp = request.POST['otp']
        otp_obj = models.OTP.objects.filter(code = int(otp))
        if otp_obj.exists():
            otp_obj = otp_obj.first()
            otp_obj.paper = paper
            otp_obj.paid_at = timezone.now()
            otp_obj.save()
            return redirect('my_papers')
        messages.error(request, "Noto'g'ri OTP")
    return render(request, 'otp.html')


def check_username(request):
    username = request.GET.get('username', None)
    if username:
        exists = CustomUser.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'No username provided'}, status=400)

@login_required(redirect_field_name='login')
def admin_waitlist(request):
    context = {}
    if request.user.is_superuser:
        papers = models.Paper.objects.filter(status = 2).order_by('paid_at')
        context = {
            'papers':papers
        }
    else:
        return redirect('main')
    return render(request, 'admin-waitlist.html', context)

@login_required(redirect_field_name='login')
def admin_paper_detail(request, id):
    context = {}
    if request.user.is_superuser:
        paper = models.Paper.objects.get(id = id)
        context = {
            'paper':paper
        }
    else:
        return redirect('main')
    return render(request, 'detail-admin.html', context)


@login_required(redirect_field_name='login')
def accept_paper(request, id):
    if request.user.is_superuser:
        paper = models.Paper.objects.get(id = id)
        paper.status = 4
        paper.save()
        return redirect('admin_waitlist')
    else:
        return redirect('main')

@login_required(redirect_field_name='login')
def deny_paper(request, id):
    if request.user.is_superuser and request.method == 'POST':
        paper = models.Paper.objects.get(id = id)
        paper.status = 3
        paper.save()
        comment = request.POST['comment']
        models.Comment.objects.create(
            comment = comment,
            paper = paper
        )
        return redirect('admin_waitlist')
    else:
        return redirect('main')
    

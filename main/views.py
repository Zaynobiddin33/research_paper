from PyPDF2 import PdfReader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic import TemplateView, DetailView

from . import models
from .forms import CustomPasswordChangeForm
from .models import Paper, CustomUser, Category, Creator
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.functions import Concat
from django.db.models import F, Value
from django.utils import timezone
from .pdf_edit import give_certificate
from .wordify import *
from .convert import *
from django.conf import settings


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
    template_name = 'templates/main-page.html'
    context_object_name = 'papers'
    extra_context = {'page_title': "So‘nggi maqolalar"}

    def get_queryset(self):
        number = 6
        return Paper.objects.filter(status=4).order_by('-published_at')[:number]


class AboutView(TemplateView):
    template_name = 'about.html'


class CreatorsView(ListView):
    model = Creator
    template_name = 'templates/creators.html'
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
        paper = self.object
        context['keywords'] = paper.keywords.split(',')

        context['comments'] = models.Comment.objects.filter(paper=paper).order_by('-id')

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
        pages = 1

        Paper.objects.create(
            owner=request.user,
            title=data['title'],
            abstract=data['abstract'],
            intro=data['intro'],
            file=file,
            category=category,
            keywords=data['keywords'],
            organization = data['organization'],
            citations = data['citations'],
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
    template_name = 'templates/all-papers.html'
    context_object_name = 'papers'
    paginate_by = 9

    def get_queryset(self):
        queryset = Paper.objects.filter(status=4).order_by('-published_at')

        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(abstract__icontains=query) |
                Q(owner__first_name__icontains=query) |
                Q(organization__icontains=query) |
                Q(keywords__icontains=query)
            )

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProfileStatsView(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'profile.html'

    def get(self, request):
        user = request.user

        # Count papers by status
        draft_count = Paper.objects.filter(owner=user, status=1).count()
        on_process_count = Paper.objects.filter(owner=user, status=2).count()
        declined_count = Paper.objects.filter(owner=user, status=3).count()
        accepted_count = Paper.objects.filter(owner=user, status=4).count()

        context = {
            'draft_count': draft_count,
            'on_process_count': on_process_count,
            'declined_count': declined_count,
            'accepted_count': accepted_count,
        }

        return render(request, self.template_name, context)


class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'settings.html'

    def get(self, request):
        # Just render the page with user info
        return render(request, self.template_name)

    def post(self, request):
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.username = request.POST.get('username', user.username)
        user.save()
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
            messages.success(request, "Parol muvaffaqiyatli o`zgartirildi")# Keep user logged in
            return redirect('change_password')
        return render(request, self.template_name, {'password_form': form})

@login_required(redirect_field_name='login')
def apply_otp(request, id):
    paper = models.Paper.objects.get(id = id)
    if request.method == "POST":
        image = request.FILES['check']
        models.Payment.objects.create(
            paper = paper,
            check_image = image
        )
        paper.status = 5
        paper.save()
        return redirect('success_payment')
    return render(request, 'otp.html')


def check_username(request):
    username = request.GET.get('username', None)
    if username:
        exists = CustomUser.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'No username provided'}, status=400)

@login_required(login_url='login')
def admin_waitlist(request):
    if not request.user.is_superuser:
        return redirect('main')

    papers = models.Paper.objects.filter(
        payment__status=2,
        status=2
    ).distinct()

    return render(request, 'admin-waitlist.html', {'papers': papers})

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
    if not request.user.is_superuser:
        return redirect('main')

    paper = models.Paper.objects.get(id=id)
    paper.status = 4

    # Generate the certificate
    certificate = give_certificate(
        paper.owner.first_name,
        paper.owner.last_name,
        paper.title,
        f'http://127.0.0.1:8000/detail-paper/{paper.id}'
    )
    paper.certificate = certificate

    # Fill the Word template with paper info
    filled_template_path = f"word_templates/{paper.owner.first_name}-{paper.owner.last_name}.docx"
    template = fill_template(
        'temp.docx',
        {
            "publisher_name": f"{paper.owner.first_name} {paper.owner.last_name}",
            "num_years": str(datetime.now().year - 2024),
            "num_month": str(datetime.now().month),
            "current_year": str(datetime.now().year),
            "submitted_time": paper.published_at.strftime('%d/%m/%y'),
            "accepted_time": datetime.now().strftime('%d/%m/%y'),
            "published_time": datetime.now().strftime('%d/%m/%y'),
            "licence_url": f"http://127.0.0.1:8000/detail-paper/{paper.id}",
        },
        filled_template_path
    )

    # Combine the filled template and the existing paper
    combined_docx = add_template(template, paper.file.path, f"combined/{paper.owner.first_name}-{paper.owner.last_name}.docx")

    # Convert to PDF (works on Linux/macOS)
    pdf_path = f"pdfs/{paper.owner.first_name}-{paper.owner.last_name}.pdf"
    convert_to_pdf(combined_docx, f"media/{pdf_path}")
    reader = PdfReader(f"media/{pdf_path}")
    length = len(reader.pages)

    # Save the final PDF path to the paper model
    paper.file.name = pdf_path
    paper.pages = length
    paper.save()

    print(f"✅ Paper '{paper.title}' accepted and converted to PDF.")
    return redirect('admin_waitlist')

@login_required(redirect_field_name='login')
def deny_paper(request, id):
    if request.user.is_superuser and request.method == 'POST':
        paper = models.Paper.objects.get(id = id)
        paper.status = 3
        paper.reject_count+=1
        paper.save()
        comment = request.POST['comment']
        models.Comment.objects.create(
            comment = comment,
            paper = paper
        )
        return redirect('admin_waitlist')
    else:
        return redirect('main')

@login_required(redirect_field_name='login')
def success_payment(request):
    return render(request, 'success-payment.html')

@login_required(redirect_field_name='login')
def payments(request):
    context = {}
    if request.user.is_superuser and request.user.status == 1:
        payments = models.Payment.objects.filter(status = 1).order_by('id')
        context = {
            'payments': payments
        }
    else:
        return redirect('main')
    return render(request, 'payments-admin.html', context)

@login_required(redirect_field_name='login')
def accept_payment(request, id):
    if request.user.is_superuser and request.user.status == 1:
        check = models.Payment.objects.get(id = id)
        check.status = 2
        paper = check.paper
        paper.status = 2
        paper.save()
        check.save()
        return redirect('payments')
    else:
        return redirect('main')
    

@login_required(redirect_field_name='login')
def deny_payment(request, id):
    if request.user.is_superuser and request.user.status == 1:
        check = models.Payment.objects.get(id = id)
        check.status = 3
        paper = check.paper
        paper.status = 1
        paper.save()
        check.save()
        return redirect('payments')
    else:
        return redirect('main')
    

@login_required(redirect_field_name='login')
def payments_stats(request):
    if request.user.is_superuser and request.user.status == 1:
        now = timezone.now()
        total_payments = models.Payment.objects.filter(status = 2).count()
        total_sum = total_payments*20000
        monthly_payments = models.Payment.objects.filter(paid_at__year = now.year, paid_at__month = now.month, status = 2).count()
        monthly_sum = monthly_payments*20000
        payments = models.Payment.objects.filter(status = 2).order_by('-paid_at')

        context = {
            'total':total_payments,
            'total_sum':total_sum,
            'monthly':monthly_payments,
            'monthly_sum':monthly_sum,
            'payments':payments
        }
    else:
        return redirect('main')
    return render(request, 'payment-stats.html', context)

@login_required(redirect_field_name='login')
def edit_paper(request, id):
    paper = models.Paper.objects.filter(owner = request.user, id = id).first()
    categories = models.Category.objects.all()
    if paper.status in [1,3]:
        if request.method == 'POST':
            data = request.POST
            file = request.FILES.get('file')
            category = Category.objects.get(name=data['category'])
            if file:
                paper.pages = 1

            paper.title = data['title']
            paper.abstract = data['abstract']
            paper.intro = data['intro']
            paper.category = category
            paper.keywords = data['keywords']
            paper.organization = data['organization']
            paper.citations = data['citations']
            if paper.status == 3:
                paper.status = 2
            else:
                paper.status = 1

            paper.save()
            return redirect('my_paper', paper.id)
    else:
        return redirect('main')
    return render(request, 'edit-paper.html', {'paper': paper, 'categories': categories})

@login_required(redirect_field_name='login')
def resubmit_paper(request, id):
    paper = models.Paper.objects.get(id = id)
    if paper.reject_count<5:
        paper.status = 2
        paper.save()
    return redirect('my_paper', paper.id)

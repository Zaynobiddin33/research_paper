from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from PyPDF2 import PdfReader
from . import models

# Create your views here.

def check_username(request):
    username = request.GET.get('username', None)
    if username:
        exists = models.CustomUser.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'No username provided'}, status=400)

def main(request):
    papers = models.Paper.objects.filter(status = 4)
    return render(request, 'index.html', {'papers':papers})

def about(request):
    return render(request, 'about.html')

def creators(request):
    return render(request, 'owners.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main")  # redirect to home or dashboard
        else:
            messages.error(request, "Noto'g'ri login or parol.")
            return redirect("login")

    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        surname =request.POST['surname']
        username = request.POST['username']
        password = request.POST['password']
        check_password = request.POST['check_password']
        avatar = request.FILES.get('avatar')
        if password == check_password:
            if not models.CustomUser.objects.filter(username = username).exists():
                if avatar:
                    models.CustomUser.objects.create_user(
                        first_name = name,
                        last_name = surname,
                        username = username,
                        password = password,
                        avatar = avatar
                    )
                else:
                    models.CustomUser.objects.create_user(
                            first_name = name,
                            last_name = surname,
                            username = username,
                            password = password,
                            avatar = avatar
                        )
                return redirect('login')
        
    return render(request, 'register.html')

@login_required(redirect_field_name='login')
def logout_view(request):
    logout(request)
    return redirect('main')

@login_required(redirect_field_name='login')
def upload_paper(request):
    categories = models.Category.objects.all()
    if request.method == 'POST':
        title = request.POST['title']
        abstract = request.POST['abstract']
        intro = request.POST['intro']
        citation = request.POST['citations']
        file = request.FILES['file']
        category_name = request.POST['category']
        keywords = request.POST['keywords']
        category = models.Category.objects.get(name = category_name)
        pdf = PdfReader(file)
        length = len(pdf.pages)
        models.Paper.objects.create(
            owner = request.user,
            title = title,
            abstract = abstract,
            intro = intro,
            citations = citation,
            file = file,
            category = category,
            keywords = keywords,
            pages = length,
            status = 1
        )
        return redirect('my_papers')

    return render(request, 'upload.html', {'categories':categories})


@login_required(redirect_field_name='login')
def my_papers(request):
    papers = models.Paper.objects.filter(owner = request.user).order_by('-id')
    return render(request, 'papers.html', {'papers':papers})

@login_required(redirect_field_name='login')
def my_paper(request, id):
    paper = models.Paper.objects.get(id = id)
    keywords = paper.keywords.split(',')
    print(keywords)
    if paper.owner != request.user:
        return redirect('main')
    return render(request, 'detail-owner.html', {'paper':paper, 'keywords':keywords})


@login_required(redirect_field_name='login')
def delete_paper(request, id):
    paper = models.Paper.objects.get(id = id)
    paper.delete()
    return redirect('my_papers')


def detail_paper(request, id):
    paper = models.Paper.objects.get(id = id)
    print(paper.file.url)
    keywords = paper.keywords.split(',')
    return render(request, 'detail.html', {'paper':paper, 'tags':keywords})


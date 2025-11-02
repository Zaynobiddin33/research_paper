from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views import View

from main.models import Paper, Category


class PaperDetailView(View):
    def get(self, request, id):
        paper = get_object_or_404(Paper, id=id)
        keywords = [kw.strip() for kw in paper.keywords.split(',')]
        return render(request, 'detail.html', {'paper': paper, 'tags': keywords})


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
            organization=data['organization'],
            citations=data['citations'],
            pages=pages,
            status=1
        )
        return redirect('my_papers')


class PaperDeleteView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, id):
        paper = get_object_or_404(Paper, id=id, owner=request.user)
        paper.delete()
        return redirect('my_papers')

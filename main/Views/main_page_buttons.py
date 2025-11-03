from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic import TemplateView

from main.models import Paper, Category, Creator, Comment


class MainView(ListView):
    model = Paper
    template_name = 'templates/main-page.html'
    context_object_name = 'papers'
    extra_context = {'page_title': "So‘nggi maqolalar"}

    def get_queryset(self):
        number = 6
        return Paper.objects.filter(status=4).order_by('-id')[:number]


class AboutView(TemplateView):
    template_name = 'about.html'


class CreatorsView(ListView):
    model = Creator
    template_name = 'templates/creators.html'
    context_object_name = 'creators'

    def get_queryset(self):
        return Creator.objects.all()


class MyPapersView(LoginRequiredMixin, ListView):
    model = Paper
    template_name = 'papers.html'
    context_object_name = 'papers'
    login_url = 'login'

    def get_queryset(self):
        return Paper.objects.filter(owner=self.request.user).order_by('-id')


class AllPapersView(ListView):
    model = Paper
    template_name = 'templates/all-papers.html'
    context_object_name = 'papers'
    paginate_by = 9

    def get_queryset(self):
        queryset = Paper.objects.filter(status=4).order_by('-id')

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
        payment_process_count = Paper.objects.filter(owner=user, status=5).count()
        blocked_count = Paper.objects.filter(owner=user, status=6).count()

        context = {
            'draft_count': draft_count,
            'on_process_count': on_process_count,
            'declined_count': declined_count,
            'accepted_count': accepted_count,
            'payment_process_count': payment_process_count,
            'blocked_count': blocked_count,
        }

        return render(request, self.template_name, context)

class MyPaperDetailView(LoginRequiredMixin, DetailView):
    model = Paper
    template_name = 'detail-owner.html'
    context_object_name = 'paper'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paper = self.object
        context['keywords'] = paper.keywords.split(',')

        context['comments'] = Comment.objects.filter(paper=paper).order_by('-id')

        return context

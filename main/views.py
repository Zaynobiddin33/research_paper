from PyPDF2 import PdfReader
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from . import models
from .convert import *
from .models import CustomUser, Category
from .pdf_edit import give_certificate
from .wordify import *


@login_required(redirect_field_name='login')
def apply_otp(request, id):
    paper = models.Paper.objects.get(id=id)
    if request.method == "POST":
        image = request.FILES['check']
        models.Payment.objects.create(
            paper=paper,
            check_image=image
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
        paper = models.Paper.objects.get(id=id)
        context = {
            'paper': paper
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
    combined_docx = add_template(
        template,
        paper.file.path,
        f"combined/{paper.owner.first_name}-{paper.owner.last_name}.docx"
    )

    # Ensure directories exist
    os.makedirs("media/pdfs", exist_ok=True)

    # Convert to PDF
    pdf_path = f"pdfs/{paper.owner.first_name}-{paper.owner.last_name}-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.pdf"
    full_pdf_path = os.path.join("media", pdf_path)

    convert_to_pdf(combined_docx, full_pdf_path)

    # Count PDF pages
    reader = PdfReader(full_pdf_path)
    num_pages = len(reader.pages)

    # Save to database
    paper.file.name = pdf_path
    paper.pages = num_pages
    paper.save()

    print(f"✅ Paper '{paper.title}' accepted, converted to PDF, {num_pages} pages.")
    return redirect('admin_waitlist')

@login_required(redirect_field_name='login')
def deny_paper(request, id):
    if request.user.is_superuser and request.method == 'POST':
        paper = models.Paper.objects.get(id=id)
        paper.status = 3
        paper.reject_count += 1
        paper.save()
        comment = request.POST['comment']
        models.Comment.objects.create(
            comment=comment,
            paper=paper
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
        payments = models.Payment.objects.filter(status=1).order_by('id')
        context = {
            'payments': payments
        }
    else:
        return redirect('main')
    return render(request, 'payments-admin.html', context)


@login_required(redirect_field_name='login')
def accept_payment(request, id):
    if request.user.is_superuser and request.user.status == 1:
        check = models.Payment.objects.get(id=id)
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
        check = models.Payment.objects.get(id=id)
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
        total_payments = models.Payment.objects.filter(status=2).count()
        total_sum = total_payments * 20000
        monthly_payments = models.Payment.objects.filter(paid_at__year=now.year, paid_at__month=now.month,
                                                         status=2).count()
        monthly_sum = monthly_payments * 20000
        payments = models.Payment.objects.filter(status=2).order_by('-paid_at')

        context = {
            'total': total_payments,
            'total_sum': total_sum,
            'monthly': monthly_payments,
            'monthly_sum': monthly_sum,
            'payments': payments
        }
    else:
        return redirect('main')
    return render(request, 'payment-stats.html', context)


@login_required(redirect_field_name='login')
def edit_paper(request, id):
    paper = models.Paper.objects.filter(owner=request.user, id=id).first()
    categories = models.Category.objects.all()
    if paper.status in [1, 3]:
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

            paper.save()
            return redirect('my_paper', paper.id)
    else:
        return redirect('main')
    return render(request, 'edit-paper.html', {'paper': paper, 'categories': categories})


@login_required(redirect_field_name='login')
def resubmit_paper(request, id):
    paper = models.Paper.objects.get(id=id)
    if paper.reject_count < 5 and paper.status == 3:
        paper.status = 2
        paper.save()
    return redirect('my_paper', paper.id)

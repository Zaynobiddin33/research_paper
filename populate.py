from main.models import Category, Paper
from django.contrib.auth import get_user_model
from PyPDF2 import PdfReader
import random
import datetime

User = get_user_model()

# Create sample categories
categories = ["Kimyo", "Tabiatshunoslik", "Biologiya", "Fizika", "Matematika", "Texnologiya"]
for cat_name in categories:
    Category.objects.get_or_create(name=cat_name)

owner = User.objects.first()  # change to specific user if needed
sample_pdf_path = "/home/amirsaid/New_Projects/research_paper/media/pdfs/OQITUVCHI_FAOLIYATIDA_MUOMALA_MADANIYATI_VA_PSIXO.pdf"

for i in range(1, 21):
    category = Category.objects.order_by("?").first()
    with open(sample_pdf_path, "rb") as pdf_file:
        pdf = PdfReader(pdf_file)
        pages = len(pdf.pages)

        Paper.objects.create(
            owner=owner,
            category=category,
            title=f"Sample Paper {i} in {category.name}",
            summary=f"This is a summary for sample paper {i}. It explains the main points of the research in detail.",
            intro=f"This paper explores topic {i} in depth, providing insights and analysis.",
            citations=f"Author A, Author B. Citation example {i}.",
            file=pdf_file.name,
            status=random.choice([1, 2, 3, 4]),
            published_at=datetime.date.today() - datetime.timedelta(days=random.randint(0, 100)),
            keywords="sample, research, science",
            pages=pages,
            organization=f"Organization {i}"
        )

print("Categories and 20 sample papers have been created!")

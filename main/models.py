from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models


# Create your models here.

class Category(models.Model):
    name = models.CharField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='media/avatars/', null=True, blank=True)

    def __str__(self):
        return self.username


class Paper(models.Model):
    STATUS_CHOICES = [
        (1, 'draft'),
        (2, 'on_process'),
        (3, 'declined'),
        (4, 'accepted'),
    ]

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)

    title = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)],
        help_text="Sarlavha 10–255 belgidan iborat bo‘lishi kerak."
    )

    summary = models.TextField(
        max_length=500,
        validators=[MinLengthValidator(100)],
        help_text="Qisqacha mazmun kamida 100 ta belgidan iborat bo‘lishi kerak."
    )

    intro = models.TextField(
        max_length=500,
        validators=[MinLengthValidator(100)],
        help_text="Kirish qismi kamida 100 ta belgidan iborat bo‘lishi kerak."
    )

    file = models.FileField(upload_to='pdfs/')

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        help_text="Maqolaning joriy holatini tanlang."
    )

    published_at = models.DateField(auto_now=True)

    keywords = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(10)],
        help_text="Kalit so‘zlar 10–300 belgidan iborat bo‘lishi kerak."
    )

    pages = models.IntegerField(
        null=True,
        blank=True,
        help_text="Betlar soni 3–50 oralig‘ida bo‘lishi kerak."
    )

    organization = models.CharField(
        max_length=120,
        validators=[MinLengthValidator(1)],
        null=True,
        blank=True,
        help_text="Tashkilot nomi 5–120 belgidan iborat bo‘lishi kerak."
    )

    def __str__(self):
        return self.title


class Creator(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='creators/')
    instagram = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

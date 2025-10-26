from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
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
        (5, 'payment_process'),
        (6, 'blocked')
    ]

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)

    title = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(10)],
        help_text="Sarlavha 10–255 belgidan iborat bo‘lishi kerak."
    )

    summary = models.TextField(
        validators=[MinLengthValidator(100)],
        help_text="Qisqacha mazmun kamida 100 ta belgidan iborat bo‘lishi kerak."
    )

    intro = models.TextField(
        validators=[MinLengthValidator(300)],
        help_text="Kirish qismi kamida 300 ta belgidan iborat bo‘lishi kerak."
    )

    citations = models.TextField(
        validators=[MinLengthValidator(50)],
        help_text="Iqtiboslar ro‘yxati kamida 50 ta belgidan iborat bo‘lishi kerak."
    )

    file = models.FileField(upload_to='pdfs/')

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        help_text="Maqolaning joriy holatini tanlang."
    )

    published_at = models.DateField(auto_now=True)

    keywords = models.CharField(
        max_length=300,
        validators=[MinLengthValidator(10)],
        help_text="Kalit so‘zlar 10–300 belgidan iborat bo‘lishi kerak."
    )

    pages = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        null=True,
        blank=True,
        help_text="Betlar soni 3–50 oralig‘ida bo‘lishi kerak."
    )

    organization = models.CharField(
        max_length=120,
        validators=[MinLengthValidator(5)],
        null=True,
        blank=True,
        help_text="Tashkilot nomi 5–120 belgidan iborat bo‘lishi kerak."
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    reject_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.reject_count>=5:
            self.status = 6
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class OTP(models.Model):
    code = models.IntegerField(unique=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = "OTPs"


    def save(self, *args, **kwargs):
        if self.paper:
            paper = Paper.objects.get(id=self.paper.id)
            paper.status = 2
            paper.save()
        return super().save(*args, **kwargs)


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

class Comment(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    comment = models.TextField()
    written_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    check_image = models.ImageField('checks/')
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    status = models.IntegerField(choices=[(1, 'sent'), (2, 'approved'), (3, 'denied')], default=1)
    paid_at = models.DateTimeField(auto_now_add=True)

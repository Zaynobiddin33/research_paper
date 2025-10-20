from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.

class Category(models.Model):
    name = models.CharField(unique=True)

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='media/avatars/', null=True, blank=True)

    def __str__(self):
        return self.username

class Paper(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null = True)
    title = models.TextField()
    abstract = models.TextField()
    intro = models.TextField()
    citations = models.TextField()
    file = models.FileField(upload_to='pdfs/')
    status = models.IntegerField(choices=[(1, 'draft'),(2, 'on_process'), (3, 'declined'), (4, 'accepted')])
    published_at = models.DateField(auto_now=True)
    keywords = models.TextField()
    pages = models.IntegerField()
    organization = models.CharField(max_length=250)

class Otp(models.Model):
    code = models.IntegerField()
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, null=True)


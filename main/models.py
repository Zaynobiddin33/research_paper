from django.contrib.auth.models import User, AbstractUser

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
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Paper(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.TextField()
    summary = models.TextField()
    intro = models.TextField()
    citations = models.TextField()
    file = models.FileField(upload_to='pdfs/')
    status = models.IntegerField(choices=[(1, 'draft'), (2, 'on_process'), (3, 'declined'), (4, 'accepted')])
    published_at = models.DateField(auto_now=True)
    keywords = models.TextField()
    pages = models.IntegerField()
    organization = models.CharField(max_length=250)
    paid_at = models.DateTimeField(null=True, blank=True)

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
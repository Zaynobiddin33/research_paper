from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, CustomUser, Paper, OTP, Creator


# --- Custom User Admin ---
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "avatar")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active")
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        ("User Info", {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "avatar")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )


# --- Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


# --- Paper Admin ---
@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "category", "status", "published_at", "organization")
    list_filter = ("status", "category", "published_at")
    search_fields = ("title", "keywords", "organization", "owner__username")
    readonly_fields = ("published_at", "pages")
    ordering = ("-published_at",)
    list_per_page = 20

    fieldsets = (
        ("General Info", {
            "fields": ("title", "summary", "intro", "citations", "keywords", "organization")
        }),
        ("Relations", {
            "fields": ("owner", "category")
        }),
        ("File & Status", {
            "fields": ("file", "pages", "status", "published_at")
        }),
    )


# --- OTP Admin ---
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "paper")
    search_fields = ("code", "paper__title")
    list_filter = ("paper__status",)
    ordering = ("-id",)


# --- Creator Admin ---
@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "role", "instagram", "telegram", "github", "linkedin")
    search_fields = ("name", "role")
    list_filter = ("role",)
    ordering = ("name",)




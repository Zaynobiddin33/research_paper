from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, CustomUser, Paper, Creator, Comment, Payment
from django.utils.html import format_html


# ✅ Inline Comments in Paper Admin
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("comment", "written_at")


# ✅ Inline Payment in Paper Admin
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("paid_at", "check_image", "status")
    can_delete = False


# ✅ Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("avatar_preview", "username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active", "status")
    readonly_fields = ("last_login", "date_joined", "avatar_preview")

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(f'<img src="{obj.avatar.url}" width="35" style="border-radius: 50%;">')
        return "No Photo"

    avatar_preview.short_description = "Avatar"

    fieldsets = (
        ("Login info", {"fields": ("username", "password")}),
        ("Personal data", {"fields": ("first_name", "last_name", "email", "avatar", "avatar_preview", "status")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


# ✅ Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


# ✅ Paper Admin
@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ("id", "color_status", "title", "owner", "category", "published_at", "pages")
    list_filter = ("status", "category", "published_at", "reject_count")
    search_fields = ("title", "keywords", "organization", "owner__username")
    ordering = ("-published_at",)
    readonly_fields = ("published_at", "pages", "color_status")
    list_per_page = 25

    inlines = [CommentInline, PaymentInline]

    fieldsets = (
        ("📌 General Information", {
            "fields": ("title", "abstract", "intro", "keywords", "organization")
        }),
        ("✅ Owner & Category", {
            "fields": ("owner", "category")
        }),
        ("📄 File Information", {
            "fields": ("file", "pages", "citations")
        }),
        ("📡 Status Information", {
            "fields": ("status", "color_status", "published_at", "paid_at", "reject_count", "certificate")
        }),
    )

    def color_status(self, obj):
        status_colors = {
            1: ("Draft", "gray"),
            2: ("On Process", "orange"),
            3: ("Declined", "red"),
            4: ("Accepted", "green"),
            5: ("Payment Process", "blue"),
            6: ("Blocked", "black"),
        }
        label, color = status_colors.get(obj.status, ("Unknown", "black"))
        return format_html(f"<strong style='color:{color}'>{label}</strong>")

    color_status.short_description = "Status"


# ✅ Creator Admin
@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "name", "role")
    search_fields = ("name", "role")
    ordering = ("name",)

    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="50" height="50" style="border-radius: 50%;">')
        return "No Image"

    image_preview.short_description = "Photo"


# ✅ Comment Admin (Optional)
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("paper", "comment", "written_at")
    list_filter = ("written_at",)
    search_fields = ("comment", "paper__title")
    ordering = ("-written_at",)


# ✅ Payment Admin (Optional)
from django.utils.html import format_html

from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "paper", "status", "paid_at")
    list_filter = ("status", "paid_at")
    search_fields = ("paper__title",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # If payment approved → set paper status to 2 (on_process)
        if obj.status == 2:
            obj.paper.status = 2
            obj.paper.save(update_fields=["status"])

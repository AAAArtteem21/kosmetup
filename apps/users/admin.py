from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Client


@admin.register(Client)
class ClientAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("role", "created_at")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("email",)}),
    )
    readonly_fields = ("role", "created_at")
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_staff", "is_active", "is_superuser", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-created_at",)
    list_per_page = 50


admin.site.site_header = "GlowBook Administration"
admin.site.site_title = "GlowBook Admin"
admin.site.index_title = "User and booking management"

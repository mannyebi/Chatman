from django.contrib import admin
from users.models import User
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "first_name", "last_name", "email", "is_active", "is_staff")
    search_fields = ("user_id", "email")
    ordering = ("email",)

admin.site.register(User, CustomUserAdmin)
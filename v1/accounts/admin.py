from django.contrib import admin
from .models.user import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username', 'first_name', 'last_name')


admin.site.register(User)

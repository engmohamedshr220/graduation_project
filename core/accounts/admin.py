from django.contrib import admin
from .models import User 

# Register your models here.

admin.site.site_header = "My Project Admin"
admin.site.site_title = "My Project Admin Portal"
admin.site.index_title = "Welcome to My Project Admin"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'role', 'is_staff', 'is_superuser']
    search_fields = ['name', 'email']
    list_filter = ['role']




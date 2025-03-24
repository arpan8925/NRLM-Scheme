from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Manager, Employee

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'phone_number', 'employee_count')
    search_fields = ('user__email', 'user__first_name', 'department')
    list_filter = ('department',)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'position', 'department', 'manager', 'hire_date')
    search_fields = ('user__email', 'user__first_name', 'employee_id', 'position')
    list_filter = ('department', 'manager', 'hire_date')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(Employee, EmployeeAdmin)

from django.contrib import admin
from .models import Family, FamilyPatientBinding, FamilyInviteCode


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_name', 'phone', 'created_at']
    search_fields = ['user__username', 'user__name', 'user__phone', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    def get_name(self, obj):
        return obj.name or obj.user.name or obj.user.username
    get_name.short_description = '姓名'


@admin.register(FamilyPatientBinding)
class FamilyPatientBindingAdmin(admin.ModelAdmin):
    list_display = ['family', 'patient', 'relationship', 'created_at']
    list_filter = ['relationship', 'created_at']
    search_fields = ['family__user__username', 'patient__user__username', 'patient__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FamilyInviteCode)
class FamilyInviteCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'patient', 'created_by', 'created_at']
    search_fields = ['code', 'patient__name', 'patient__user__username', 'created_by__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

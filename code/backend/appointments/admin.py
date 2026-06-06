from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment_type', 'visit_date', 'status', 'created_at')
    list_filter = ('status', 'appointment_type', 'visit_date')
    search_fields = ('patient__name', 'doctor__name', 'symptoms', 'medical_history')
    readonly_fields = ('created_at', 'updated_at')

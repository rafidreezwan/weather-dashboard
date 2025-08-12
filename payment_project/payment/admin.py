# payment/admin.py
from django.contrib import admin
from .models import FileUpload, PaymentTransaction, ActivityLog

class ReadOnlyAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(FileUpload, ReadOnlyAdmin)
admin.site.register(PaymentTransaction, ReadOnlyAdmin)
admin.site.register(ActivityLog) # Staff can manage logs if needed
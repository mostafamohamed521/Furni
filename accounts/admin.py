from django.contrib import admin
from .models import Profile, OTPCode


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country')
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'purpose', 'code', 'is_used', 'created_at')
    list_filter = ('purpose', 'is_used')
    search_fields = ('user__username', 'user__email', 'code')
    readonly_fields = ('user', 'code', 'purpose', 'created_at')

    def has_add_permission(self, request):
        return False

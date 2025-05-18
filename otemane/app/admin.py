from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Helps, Rewards, User, Family

class RewardInline(admin.StackedInline): 
    model = Rewards
    extra = 1  

class HelpsAdmin(admin.ModelAdmin):
    inlines = [RewardInline]


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('id',)  

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('user_name', 'family', 'relationship')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', )}),
        ('Password reset', {'fields': ('password_token', 'password_expiry')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'family', 'relationship', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'user_name', 'family', 'relationship', 'is_staff', 'is_active')
    search_fields = ('email', 'user_name', 'family_id')
    ordering = ('email',)


admin.site.register(Helps, HelpsAdmin,)  # 管理画面に登録
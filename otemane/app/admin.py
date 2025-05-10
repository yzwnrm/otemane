from django.contrib import admin
from .models import Helps, Rewards


class RewardInline(admin.StackedInline): 
    model = Rewards
    extra = 1  

class HelpsAdmin(admin.ModelAdmin):
    inlines = [RewardInline]

admin.site.register(Helps, HelpsAdmin)  # 管理画面に登録

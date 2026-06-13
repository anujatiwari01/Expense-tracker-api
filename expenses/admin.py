from django.contrib import admin
from .models import Category, Expense

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0
    readonly_fields = ("created_at", "updated_at")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
    inlines = [ExpenseInline]

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "category", "amount", "spent_on", "created_at")
    search_fields = ("title", "note", "user__username", "category__name")
    list_filter = ("category", "spent_on", "created_at")
    readonly_fields = ("created_at", "updated_at")

# Register your models here.

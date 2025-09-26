from django.contrib import admin
from .models import *


class RecipeAdmin(admin.ModelAdmin):
    list_display=("recipe_name",)

# Register your models here.
admin.site.register(Category)
admin.site.register(Recipe,RecipeAdmin)
from django.contrib import admin
from .models import Categorie, Article


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'actif', 'date_creation', 'date_modification']
    list_filter = ['actif', 'date_creation']
    search_fields = ['libelle']
    ordering = ['libelle']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('libelle', 'actif')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['designation', 'categorie', 'actif', 'date_creation', 'date_modification']
    list_filter = ['categorie', 'actif', 'date_creation']
    search_fields = ['designation', 'categorie__libelle']
    ordering = ['designation']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('designation', 'categorie', 'actif')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
from django.contrib import admin
from .models import Auteur, Tag, Livre, Emprunt, ProfilLecteur


@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'nationalite', 'date_creation']
    search_fields = ['nom', 'nationalite']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ['nom']
    search_fields = ['nom']


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display      = ['titre', 'auteur', 'annee_publication', 'categorie', 'disponible']
    list_filter       = ['categorie', 'disponible']
    search_fields     = ['titre', 'isbn']
    filter_horizontal = ['tags']


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display  = ['utilisateur', 'livre', 'date_emprunt', 'rendu']
    list_filter   = ['rendu']


@admin.register(ProfilLecteur)
class ProfilLecteurAdmin(admin.ModelAdmin):
    list_display      = ['utilisateur', 'telephone']
    filter_horizontal = ['livres_favoris']
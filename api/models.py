from django.db import models
from django.contrib.auth.models import User


class Auteur(models.Model):
    nom = models.CharField(max_length=200, verbose_name='Nom complet')
    biographie = models.TextField(blank=True, null=True)
    nationalite = models.CharField(max_length=100, blank=True, default='')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = 'Auteur'
        verbose_name_plural = 'Auteurs'


class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


class Livre(models.Model):
    CATEGORIES = [
        ('roman',    'Roman'),
        ('essai',    'Essai'),
        ('poesie',   'Poésie'),
        ('bd',       'Bande dessinée'),
        ('science',  'Science'),
        ('histoire', 'Histoire'),
    ]

    titre = models.CharField(max_length=300)
    isbn = models.CharField(max_length=17, unique=True)
    annee_publication = models.IntegerField()
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='roman')
    auteur = models.ForeignKey(
        Auteur, on_delete=models.CASCADE, related_name='livres'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='livres')
    disponible = models.BooleanField(default=True)
    cree_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='livres_crees'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titre} ({self.annee_publication})'

    class Meta:
        ordering = ['-annee_publication', 'titre']


class Emprunt(models.Model):
    utilisateur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='emprunts'
    )
    livre = models.ForeignKey(
        Livre, on_delete=models.CASCADE, related_name='emprunts'
    )
    date_emprunt = models.DateField(auto_now_add=True)
    date_retour_prevue = models.DateField()
    rendu = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.utilisateur.username} — {self.livre.titre}'

    class Meta:
        ordering = ['-date_emprunt']


class ProfilLecteur(models.Model):
    utilisateur = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profil'
    )
    adresse = models.CharField(max_length=300, blank=True, default='')
    telephone = models.CharField(max_length=20, blank=True, default='')
    date_naissance = models.DateField(null=True, blank=True)
    livres_favoris = models.ManyToManyField(
        Livre, blank=True, related_name='lecteurs_favoris'
    )

    def __str__(self):
        return f'Profil de {self.utilisateur.username}'
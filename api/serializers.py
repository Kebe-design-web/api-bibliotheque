from rest_framework import serializers
from .models import Auteur, Tag, Livre, Emprunt, ProfilLecteur


class AuteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auteur
        fields = ['id', 'nom', 'nationalite', 'biographie', 'date_creation']
        read_only_fields = ['id', 'date_creation']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nom']


class LivreSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.SerializerMethodField()
    auteur = AuteurSerializer(read_only=True)
    auteur_id = serializers.PrimaryKeyRelatedField(
        queryset=Auteur.objects.all(), source='auteur', write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
        source='tags', write_only=True, required=False
    )

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'isbn', 'annee_publication', 'categorie',
            'disponible', 'auteur', 'auteur_id', 'auteur_nom',
            'tags', 'tag_ids', 'date_creation',
        ]
        read_only_fields = ['id', 'date_creation']

    def get_auteur_nom(self, obj):
        return obj.auteur.nom

    def validate_isbn(self, value):
        clean = value.replace('-', '')
        if not clean.isdigit() or len(clean) != 13:
            raise serializers.ValidationError(
                "L'ISBN doit contenir exactement 13 chiffres."
            )
        return value

    def validate_annee_publication(self, value):
        if value < 1000 or value > 2100:
            raise serializers.ValidationError(
                "L'année doit être entre 1000 et 2100."
            )
        return value


class LivreDetailSerializer(LivreSerializer):
    cree_par = serializers.StringRelatedField(read_only=True)

    class Meta(LivreSerializer.Meta):
        fields = LivreSerializer.Meta.fields + ['cree_par']


class EmpruntSerializer(serializers.ModelSerializer):
    utilisateur = serializers.StringRelatedField(read_only=True)
    livre_titre = serializers.SerializerMethodField()

    class Meta:
        model = Emprunt
        fields = [
            'id', 'utilisateur', 'livre', 'livre_titre',
            'date_emprunt', 'date_retour_prevue', 'rendu',
        ]
        read_only_fields = ['id', 'utilisateur', 'date_emprunt']

    def get_livre_titre(self, obj):
        return obj.livre.titre


class ProfilLecteurSerializer(serializers.ModelSerializer):
    utilisateur = serializers.StringRelatedField(read_only=True)
    livres_favoris = LivreSerializer(many=True, read_only=True)
    livres_favoris_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Livre.objects.all(),
        source='livres_favoris', write_only=True, required=False
    )

    class Meta:
        model = ProfilLecteur
        fields = [
            'id', 'utilisateur', 'adresse', 'telephone',
            'date_naissance', 'livres_favoris', 'livres_favoris_ids',
        ]
        read_only_fields = ['id', 'utilisateur']
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Auteur, Tag, Livre, Emprunt, ProfilLecteur
from .serializers import (
    AuteurSerializer, TagSerializer,
    LivreSerializer, LivreDetailSerializer,
    EmpruntSerializer, ProfilLecteurSerializer,
)
from .permissions import EstProprietaireOuReadOnly, EstAdminOuReadOnly
from .filters import LivreFilter, EmpruntFilter
from .pagination import StandardPagination


class AuteurViewSet(viewsets.ModelViewSet):
    queryset = Auteur.objects.all()
    serializer_class = AuteurSerializer
    permission_classes = [EstAdminOuReadOnly]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom', 'nationalite']
    ordering_fields = ['nom', 'date_creation']

    @action(detail=True, methods=['get'], url_path='livres')
    def livres(self, request, pk=None):
        auteur = self.get_object()
        livres = auteur.livres.all()
        serializer = LivreSerializer(livres, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        return Response({
            'total_auteurs': Auteur.objects.count(),
            'total_livres': Livre.objects.count(),
            'livres_disponibles': Livre.objects.filter(disponible=True).count(),
        })


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [EstAdminOuReadOnly]


class LivreViewSet(viewsets.ModelViewSet):
    queryset = (
        Livre.objects
        .select_related('auteur', 'cree_par')
        .prefetch_related('tags')
        .all()
    )
    permission_classes = [EstProprietaireOuReadOnly]
    pagination_class = StandardPagination
    filterset_class = LivreFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['titre', 'auteur__nom', 'isbn']
    ordering_fields = ['titre', 'annee_publication', 'date_creation']
    ordering = ['-date_creation']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LivreDetailSerializer
        return LivreSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(cree_par=self.request.user)

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        qs = self.get_queryset().filter(disponible=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def emprunter(self, request, pk=None):
        livre = self.get_object()
        if not livre.disponible:
            return Response(
                {'erreur': 'Ce livre n\'est pas disponible.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        livre.disponible = False
        livre.save()
        return Response({'message': f'"{livre.titre}" emprunté avec succès.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rendre(self, request, pk=None):
        livre = self.get_object()
        if livre.disponible:
            return Response(
                {'erreur': 'Ce livre est déjà disponible.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        livre.disponible = True
        livre.save()
        return Response({'message': f'"{livre.titre}" rendu avec succès.'})


class EmpruntViewSet(viewsets.ModelViewSet):
    serializer_class = EmpruntSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EmpruntFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Emprunt.objects.select_related('utilisateur', 'livre').all()
        return Emprunt.objects.select_related('utilisateur', 'livre').filter(
            utilisateur=user
        )

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)


class ProfilLecteurView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfilLecteurSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profil, _ = ProfilLecteur.objects.get_or_create(
            utilisateur=self.request.user
        )
        return profil
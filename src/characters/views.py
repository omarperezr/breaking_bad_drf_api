from typing import Any

from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response

from characters.models import Character
from characters.serializers import CharacterSerializer


class CharacterViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for all CRUD operations necessary for the characters endpoint
    """

    queryset = Character.objects.all()
    serializer_class = CharacterSerializer

    def get_queryset(self) -> Character.objects:
        queryset = self.queryset.all()

        # Getting optional query parameters
        name = self.request.query_params.get("name")
        is_suspect = self.request.query_params.get("suspect")
        occupation = self.request.query_params.get("occupation")

        if name or is_suspect or occupation:
            query = Q()
            if name:
                query |= Q(name__icontains=name)
            if is_suspect:
                query |= Q(is_suspect=is_suspect.lower() == "true")
            if occupation:
                query |= Q(occupation__icontains=occupation)

            queryset = queryset.filter(query)

        return queryset

    @staticmethod
    def validate_ordering_params(order_by: str, ascending: str):
        if not (order_by in ("name", "date_of_birth") and ascending in ("0", "1")):
            raise serializers.ValidationError(
                "The query parameters `orderBy` and `ascending` are obligatory. `orderBy` only accepts "
                "`name` and `date_of_birth`. `ascending` only accepts 0 or 1"
            )

    @swagger_auto_schema(
        responses={
            200: CharacterSerializer(many=True),
            422: "Error: Unprocessable Entity",
        },
        manual_parameters=[
            openapi.Parameter(
                "orderBy", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                "ascending", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter("name", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(
                "is_suspect", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter("occupation", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
    )
    def list(self, request: Any) -> Response:
        """
        Get a list of all characters, you can filter optionally by name, is_suspect and occupation
        and get partial and case-insensitive matches
        """
        order_by = request.query_params.get("orderBy")
        ascending = request.query_params.get("ascending")

        try:
            self.validate_ordering_params(order_by, ascending)
        except serializers.ValidationError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        filtered_queryset = self.get_queryset()

        # Sorting
        if order_by and ascending:
            order_by = order_by if ascending == "1" else f"-{order_by}"
            filtered_queryset = filtered_queryset.order_by(order_by)

        serializer = self.serializer_class(filtered_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

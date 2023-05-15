from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import F, FloatField
from django.db.models.functions import ACos, Cos, Least, Radians, Round, Sin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Location
from .serializers import LocationSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @staticmethod
    def validate_distance_params(coordinates: str, distance: str):
        if not (coordinates and "," in coordinates and distance.isdigit() and float(distance) >= 0):
            raise serializers.ValidationError(
                "The query parameters `coordinates` and `distance` are obligatory. `coordinates` accepts "
                "a `latitude,longitude` pair. `distance` accepts any value >= 0"
            )

    def filter_by_character(self, queryset):
        """
        Filter by character assigned to specific location entry
        """
        character_id = self.request.query_params.get("character")
        if character_id is not None:
            queryset = queryset.filter(character=character_id)
        return queryset

    def filter_by_date_range(self, queryset):
        """
        Filter by datetime range that they were recorded within
        """
        date_range = self.request.query_params.get("date_range")
        if date_range is not None:
            start_datetime, end_datetime = date_range.split(",")
            queryset = queryset.filter(timestamp__range=[start_datetime, end_datetime])
        return queryset

    def filter_by_distance(self, queryset, coordinates, distance):
        """
        Filtering by locations that are within the distance specified and ordering asc or desc
        """
        lat, lon = coordinates.split(",")
        lat = Decimal(lat)
        lon = Decimal(lon)
        ascending = self.request.query_params.get("ascending", "1")

        order_by = "distance" if ascending == "1" else f"-distance"

        # Calculating distance using the spherical law of cosines
        queryset = (
            queryset.annotate(
                distance=Round(
                    ACos(
                        Least(
                            Cos(Radians(lat))
                            * Cos(Radians(F("lat")))
                            * Cos(Radians(F("lon")) - Radians(lon))
                            + Sin(Radians(lat)) * Sin(Radians(F("lat"))),
                            1.0,
                        )
                    )
                    * 6_371_000,
                    precision=6,
                    output_field=FloatField(),
                )
            )
            .filter(distance__lte=distance)
            .order_by(order_by)
        )

        return queryset

    def get_filtered_queryset(self, coordinates: str, distance: float):
        queryset = self.queryset.all()

        queryset = self.filter_by_character(queryset)
        queryset = self.filter_by_date_range(queryset)
        queryset = self.filter_by_distance(queryset, coordinates, distance)

        return queryset

    @swagger_auto_schema(
        responses={200: LocationSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "coordinates", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                "distance", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter("ascending", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("character", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("date_range", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
    )
    @action(detail=False, methods=["get"])
    def near(self, request):
        """
        Gets all locations that are at a radius of 'distance' meters from the 'coordinates' specified,
        filters optionally by 'character' id, 'dater_ange' of timestamps and orders 'ascending' or descending based on
        the distance from the 'coordinates' specified and the coordinates in the database
        Distances are calculates using the spherical law of cosines
        """
        coordinates = request.query_params.get("coordinates")
        distance = request.query_params.get("distance", "")

        try:
            self.validate_distance_params(coordinates, distance)
            locations = self.get_filtered_queryset(coordinates, distance)
            serializer = self.serializer_class(locations, many=True)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

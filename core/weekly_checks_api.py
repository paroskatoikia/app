"""Additional water API ViewSets; add this file inside your existing Django app."""
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import HouseWaterReading, HouseWaterTank, HouseWaterTankReading


class PastReadingMixin:
    def validate_reading_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Reading date cannot be in the future.")
        return value


class HouseWaterReadingSerializer(PastReadingMixin, serializers.ModelSerializer):
    class Meta:
        model = HouseWaterReading
        fields = "__all__"
        read_only_fields = ["created_at"]


class HouseWaterTankSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseWaterTank
        fields = "__all__"


class HouseWaterTankReadingSerializer(PastReadingMixin, serializers.ModelSerializer):
    class Meta:
        model = HouseWaterTankReading
        fields = "__all__"


class HouseWaterReadingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HouseWaterReadingSerializer
    queryset = HouseWaterReading.objects.select_related("house").all()
    filterset_fields = ["house"]


class HouseWaterTankViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HouseWaterTankSerializer
    queryset = HouseWaterTank.objects.select_related("house").all()
    pagination_class = None  # All tanks are needed in the villa selector.
    filterset_fields = ["house"]


class HouseWaterTankReadingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HouseWaterTankReadingSerializer
    queryset = HouseWaterTankReading.objects.select_related("tank", "tank__house").all()
    filterset_fields = ["tank"]

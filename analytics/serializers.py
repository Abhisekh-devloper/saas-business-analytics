from rest_framework import serializers
from .models import Dataset, SaleRecord

class DatasetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'description', 'file_type', 'file_size_bytes',
            'row_count', 'column_count', 'is_active', 'created_at', 'updated_at'
        ]

class DatasetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'description', 'file_type', 'file_size_bytes',
            'row_count', 'column_count', 'columns_detected', 'validation_report',
            'summary_cache', 'is_active', 'created_at', 'updated_at'
        ]

class SaleRecordSerializer(serializers.ModelSerializer):
    revenue = serializers.FloatField()
    cost = serializers.FloatField()
    profit = serializers.FloatField()

    class Meta:
        model = SaleRecord
        fields = [
            'id', 'order_id', 'order_date', 'product_name', 'category',
            'region', 'quantity', 'revenue', 'cost', 'profit', 'profit_margin',
            'customer_name'
        ]

class UploadDatasetSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=True)


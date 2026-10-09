from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder

class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    file = models.FileField(upload_to='datasets/', blank=True, null=True)
    file_type = models.CharField(max_length=20, default='csv')  # 'csv', 'excel', 'sample'
    file_size_bytes = models.BigIntegerField(default=0)
    row_count = models.IntegerField(default=0)
    column_count = models.IntegerField(default=0)
    columns_detected = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    validation_report = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    summary_cache = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class SaleRecord(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='records')
    order_id = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    order_date = models.DateField(null=True, blank=True, db_index=True)
    product_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    category = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    region = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    quantity = models.IntegerField(default=1)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, db_index=True)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    profit = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, db_index=True)
    profit_margin = models.FloatField(default=0.0)  # Percentage %
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-order_date', '-id']
        indexes = [
            models.Index(fields=['dataset', 'order_date']),
            models.Index(fields=['dataset', 'category']),
            models.Index(fields=['dataset', 'region']),
        ]

    def __str__(self):
        return f"{self.order_id or 'Order'} - {self.product_name} (${self.revenue})"

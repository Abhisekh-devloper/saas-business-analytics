from django.contrib import admin
from .models import Dataset, SaleRecord

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'file_type', 'row_count', 'is_active', 'created_at')
    list_filter = ('file_type', 'is_active', 'created_at')
    search_fields = ('name', 'user__username', 'description')
    readonly_fields = ('created_at', 'updated_at', 'row_count', 'column_count', 'file_size_bytes')

@admin.register(SaleRecord)
class SaleRecordAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_date', 'product_name', 'category', 'region', 'revenue', 'profit', 'profit_margin', 'dataset')
    list_filter = ('category', 'region', 'order_date')
    search_fields = ('order_id', 'product_name', 'customer_name')
    date_hierarchy = 'order_date'
    list_per_page = 50

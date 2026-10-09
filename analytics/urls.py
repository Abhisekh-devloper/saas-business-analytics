from django.urls import path
from .views import (
    DatasetListView, UploadDatasetView, LoadSampleDatasetView,
    DatasetDetailView, SetActiveDatasetView, DashboardAnalyticsView,
    SmartInsightsView, DataTablePaginationView, ExportCsvView,
    ExportExcelView, ExportPdfView, DownloadSampleTemplateView
)

urlpatterns = [
    # Datasets Management
    path('datasets/', DatasetListView.as_view(), name='dataset-list'),
    path('datasets/upload/', UploadDatasetView.as_view(), name='dataset-upload'),
    path('datasets/load-sample/', LoadSampleDatasetView.as_view(), name='dataset-load-sample'),
    path('datasets/<int:pk>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('datasets/<int:pk>/set-active/', SetActiveDatasetView.as_view(), name='dataset-set-active'),
    
    # Analytics & Insights
    path('dashboard/', DashboardAnalyticsView.as_view(), name='analytics-dashboard'),
    path('insights/', SmartInsightsView.as_view(), name='analytics-insights'),
    path('data-table/', DataTablePaginationView.as_view(), name='analytics-data-table'),
    
    # Exports & Downloads
    path('export/csv/', ExportCsvView.as_view(), name='export-csv'),
    path('export/excel/', ExportExcelView.as_view(), name='export-excel'),
    path('export/pdf/', ExportPdfView.as_view(), name='export-pdf'),
    path('sample-template/', DownloadSampleTemplateView.as_view(), name='download-sample-template'),
]


import os
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Dataset, SaleRecord
from .serializers import (
    DatasetListSerializer, DatasetDetailSerializer,
    SaleRecordSerializer, UploadDatasetSerializer
)
from .engine.cleaner import load_and_clean_data
from .engine.analyzer import calculate_dashboard_metrics
from .engine.insights import generate_automated_insights
from .engine.exporter import export_records_to_csv, export_executive_excel, export_executive_pdf
from .sample_data import seed_sample_dataset_for_user, generate_sample_sales_data


class DatasetListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datasets = Dataset.objects.filter(user=request.user)
        serializer = DatasetListSerializer(datasets, many=True)
        return Response(serializer.data)


class UploadDatasetView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = UploadDatasetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['file']
        filename = uploaded_file.name
        name = serializer.validated_data.get('name') or os.path.splitext(filename)[0].replace('_', ' ').title()
        description = serializer.validated_data.get('description', '')

        # Determine file type
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.xlsx', '.xls']:
            file_type = 'excel'
        elif ext == '.csv':
            file_type = 'csv'
        else:
            return Response(
                {'error': 'Unsupported file format. Please upload a .csv or .xlsx / .xls file.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Process & Clean using Pandas Engine
            cleaned_df, report, detected_mappings = load_and_clean_data(uploaded_file)
            
            if len(cleaned_df) == 0:
                return Response(
                    {'error': 'Could not extract valid sales records from file. Please ensure columns include date and sales/revenue amounts.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deactivate previous active datasets
            Dataset.objects.filter(user=request.user, is_active=True).update(is_active=False)

            # Create Dataset
            uploaded_file.seek(0)
            dataset = Dataset.objects.create(
                user=request.user,
                name=name,
                description=description,
                file=uploaded_file,
                file_type=file_type,
                file_size_bytes=uploaded_file.size,
                row_count=len(cleaned_df),
                column_count=report['total_raw_cols'],
                columns_detected=detected_mappings,
                validation_report=report,
                is_active=True
            )

            # Bulk insert records
            records_to_create = []
            for _, row in cleaned_df.iterrows():
                records_to_create.append(
                    SaleRecord(
                        dataset=dataset,
                        order_id=row.get('order_id'),
                        order_date=row.get('order_date'),
                        product_name=row.get('product_name'),
                        category=row.get('category'),
                        region=row.get('region'),
                        quantity=row.get('quantity', 1),
                        revenue=Decimal(str(row.get('revenue', 0))),
                        cost=Decimal(str(row.get('cost', 0))),
                        profit=Decimal(str(row.get('profit', 0))),
                        profit_margin=float(row.get('profit_margin', 0)),
                        customer_name=row.get('customer_name')
                    )
                )

            SaleRecord.objects.bulk_create(records_to_create, batch_size=1000)

            # Cache metrics
            metrics = calculate_dashboard_metrics(dataset.records.all())
            dataset.summary_cache = metrics
            dataset.save(update_fields=['summary_cache'])

            return Response({
                'dataset': DatasetDetailSerializer(dataset).data,
                'validation_report': report,
                'message': f"Successfully cleaned and ingested {len(cleaned_df):,} records!"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f"Data ingestion failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoadSampleDatasetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            dataset = seed_sample_dataset_for_user(request.user)
            return Response({
                'dataset': DatasetDetailSerializer(dataset).data,
                'message': 'Demo E-Commerce dataset loaded successfully with 1,200 records!'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
        return Response(DatasetDetailSerializer(dataset).data)

    def delete(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
        was_active = dataset.is_active
        dataset.delete()
        if was_active:
            # Set newest remaining dataset as active
            latest = Dataset.objects.filter(user=request.user).first()
            if latest:
                latest.is_active = True
                latest.save(update_fields=['is_active'])
        return Response({'message': 'Dataset deleted successfully.'})


class SetActiveDatasetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
        Dataset.objects.filter(user=request.user).update(is_active=False)
        dataset.is_active = True
        dataset.save(update_fields=['is_active'])
        return Response({'message': f"'{dataset.name}' is now active.", 'dataset': DatasetDetailSerializer(dataset).data})


def get_filtered_records_queryset(user, request):
    """Helper to resolve dataset and apply query parameters."""
    dataset_id = request.query_params.get('dataset_id')
    if dataset_id:
        dataset = get_object_or_404(Dataset, pk=dataset_id, user=user)
    else:
        dataset = Dataset.objects.filter(user=user, is_active=True).first()
        if not dataset:
            dataset = Dataset.objects.filter(user=user).first()

    if not dataset:
        return None, SaleRecord.objects.none()

    qs = dataset.records.all()

    # Date range filters
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    if start_date:
        qs = qs.filter(order_date__gte=start_date)
    if end_date:
        qs = qs.filter(order_date__lte=end_date)

    # Category filter
    category = request.query_params.get('category')
    if category and category.lower() != 'all':
        qs = qs.filter(category=category)

    # Region filter
    region = request.query_params.get('region')
    if region and region.lower() != 'all':
        qs = qs.filter(region=region)

    # Search filter
    search = request.query_params.get('search')
    if search:
        qs = qs.filter(
            Q(product_name__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(order_id__icontains=search)
        )

    return dataset, qs


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dataset, qs = get_filtered_records_queryset(request.user, request)
        if not dataset:
            return Response({
                'has_dataset': False,
                'message': 'No dataset found. Please upload a dataset or load the demo sample.'
            })

        metrics = calculate_dashboard_metrics(qs)

        # Get overall dataset bounds and filter choices
        all_records = dataset.records.all()
        categories = list(all_records.values_list('category', flat=True).distinct().order_by('category'))
        regions = list(all_records.values_list('region', flat=True).distinct().order_by('region'))
        
        # Min/max dates
        dates_agg = all_records.filter(order_date__isnull=False).order_by('order_date')
        min_date = dates_agg.first().order_date.isoformat() if dates_agg.exists() else None
        max_date = dates_agg.last().order_date.isoformat() if dates_agg.exists() else None

        return Response({
            'has_dataset': True,
            'dataset_id': dataset.id,
            'dataset_name': dataset.name,
            'metrics': metrics,
            'filter_options': {
                'categories': [c for c in categories if c],
                'regions': [r for r in regions if r],
                'date_bounds': {'min': min_date, 'max': max_date}
            }
        })


class SmartInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dataset, qs = get_filtered_records_queryset(request.user, request)
        if not dataset:
            return Response({'has_dataset': False, 'message': 'No dataset available.'})

        metrics = calculate_dashboard_metrics(qs)
        insights = generate_automated_insights(metrics, dataset.name)
        return Response({
            'has_dataset': True,
            'dataset_id': dataset.id,
            'dataset_name': dataset.name,
            'insights': insights
        })


class DataTablePaginationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dataset, qs = get_filtered_records_queryset(request.user, request)
        if not dataset:
            return Response({'count': 0, 'results': []})

        # Ordering
        ordering = request.query_params.get('ordering', '-order_date')
        valid_order_fields = [
            'order_date', '-order_date', 'revenue', '-revenue',
            'profit', '-profit', 'profit_margin', '-profit_margin',
            'quantity', '-quantity', 'product_name', '-product_name',
            'category', '-category', 'region', '-region', 'order_id', '-order_id'
        ]
        if ordering in valid_order_fields:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by('-order_date')

        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        total_count = qs.count()

        start = (page - 1) * page_size
        end = start + page_size
        page_records = qs[start:end]

        serializer = SaleRecordSerializer(page_records, many=True)
        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size if page_size else 1,
            'results': serializer.data
        })


class ExportCsvView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dataset, qs = get_filtered_records_queryset(request.user, request)
        if not dataset:
            return Response({'error': 'No dataset found'}, status=404)

        csv_bytes = export_records_to_csv(qs)
        response = HttpResponse(csv_bytes, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{dataset.name.replace(" ", "_")}_filtered_records.csv"'
        return response


class ExportExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dataset, qs = get_filtered_records_queryset(request.user, request)
        if not dataset:
            return Response({'error': 'No dataset found'}, status=404)

        metrics = calculate_dashboard_metrics(qs)
        excel_bytes = export_executive_excel(dataset, metrics, qs)
        response = HttpResponse(excel_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{dataset.name.replace(" ", "_")}_Executive_Report.xlsx"'
        return response


class ExportPdfView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dataset, qs = get_filtered_records_queryset(request.user, request)
        if not dataset:
            return Response({'error': 'No dataset found'}, status=404)

        metrics = calculate_dashboard_metrics(qs)
        insights = generate_automated_insights(metrics, dataset.name)
        pdf_bytes = export_executive_pdf(dataset, metrics, insights)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{dataset.name.replace(" ", "_")}_Executive_Brief.pdf"'
        return response


class DownloadSampleTemplateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        df = generate_sample_sales_data(300)
        csv_data = df.to_csv(index=False)
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Sample_Sales_Data_Template.csv"'
        return response

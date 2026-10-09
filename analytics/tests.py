import os
import io
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Dataset, SaleRecord
from .sample_data import seed_sample_dataset_for_user

class AnalyticsPlatformTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Password123!'
        )
        # Login and obtain token
        login_res = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'Password123!'
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.token = login_res.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

    def test_demo_login_flow(self):
        anon_client = APIClient()
        res = anon_client.post('/api/auth/demo-login/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertEqual(res.data['user']['username'], 'demo_executive')

    def test_load_sample_dataset(self):
        res = self.client.post('/api/analytics/datasets/load-sample/')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('dataset', res.data)
        self.assertEqual(res.data['dataset']['row_count'], 1200)

        # Check records were created in DB
        dataset_id = res.data['dataset']['id']
        records_count = SaleRecord.objects.filter(dataset_id=dataset_id).count()
        self.assertEqual(records_count, 1200)

    def test_dashboard_analytics_kpis_and_charts(self):
        seed_sample_dataset_for_user(self.user)
        res = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['has_dataset'])

        metrics = res.data['metrics']
        self.assertIn('kpis', metrics)
        self.assertGreater(metrics['kpis']['total_revenue'], 0)
        self.assertGreater(metrics['kpis']['total_profit'], 0)
        self.assertGreater(metrics['kpis']['total_orders'], 0)

        # Chart datasets checks
        self.assertIn('monthly_trends', metrics)
        self.assertIn('category_performance', metrics)
        self.assertIn('region_performance', metrics)
        self.assertIn('top_products', metrics)

    def test_dashboard_filters(self):
        dataset = seed_sample_dataset_for_user(self.user)
        # Test category filter
        res = self.client.get('/api/analytics/dashboard/', {'category': 'Electronics'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        cat_labels = res.data['metrics']['category_performance']['labels']
        self.assertEqual(cat_labels, ['Electronics'])

        # Test region filter
        res = self.client.get('/api/analytics/dashboard/', {'region': 'North America'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        reg_labels = res.data['metrics']['region_performance']['labels']
        self.assertEqual(reg_labels, ['North America'])

    def test_smart_ai_insights(self):
        seed_sample_dataset_for_user(self.user)
        res = self.client.get('/api/analytics/insights/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['has_dataset'])
        
        insights = res.data['insights']
        self.assertIn('executive_summary', insights)
        self.assertIn('highlights', insights)
        self.assertIn('recommendations', insights)
        self.assertGreater(len(insights['highlights']), 0)

    def test_csv_upload_and_cleaning(self):
        csv_content = (
            "Order_Date,Order_ID,Product,Category,Region,Sales,Profit,Quantity\n"
            "2025-01-15,ORD-101,Ultra Keyboard,Electronics,North,250.00,75.00,2\n"
            "2025-01-16,ORD-102,Office Desk,Furniture,West,800.00,220.00,1\n"
            "2025-01-17,ORD-103,Pen Set,Supplies,East,45.00,15.00,3\n"
        ).encode('utf-8')

        file_obj = io.BytesIO(csv_content)
        file_obj.name = 'test_sales.csv'

        res = self.client.post('/api/analytics/datasets/upload/', {
            'file': file_obj,
            'name': 'Test Upload'
        }, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['dataset']['row_count'], 3)
        self.assertEqual(res.data['validation_report']['cleaned_rows'], 3)

    def test_export_endpoints(self):
        seed_sample_dataset_for_user(self.user)

        # CSV Export
        csv_res = self.client.get('/api/analytics/export/csv/')
        self.assertEqual(csv_res.status_code, status.HTTP_200_OK)
        self.assertEqual(csv_res['Content-Type'], 'text/csv')

        # Excel Export
        xlsx_res = self.client.get('/api/analytics/export/excel/')
        self.assertEqual(xlsx_res.status_code, status.HTTP_200_OK)
        self.assertIn('spreadsheetml', xlsx_res['Content-Type'])

        # PDF Export
        pdf_res = self.client.get('/api/analytics/export/pdf/')
        self.assertEqual(pdf_res.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_res['Content-Type'], 'application/pdf')

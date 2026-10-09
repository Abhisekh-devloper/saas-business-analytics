import os
import random
import datetime
import pandas as pd
import numpy as np
from decimal import Decimal
from django.conf import settings
from .models import Dataset, SaleRecord
from .engine.cleaner import load_and_clean_data
from .engine.analyzer import calculate_dashboard_metrics

SAMPLE_PRODUCTS = [
    # Category: Electronics
    ("MacBook Pro M3 Max 16\"", "Electronics", 2499.00, 1850.00),
    ("Dell XPS 15 OLED", "Electronics", 1799.00, 1350.00),
    ("Sony WH-1000XM5 Wireless Headphones", "Electronics", 399.00, 240.00),
    ("Logitech MX Master 3S Mouse", "Electronics", 99.00, 48.00),
    ("Keychron Q1 Pro Mechanical Keyboard", "Electronics", 199.00, 110.00),
    ("Samsung 34\" Curved Ultrawide Monitor", "Electronics", 899.00, 620.00),
    ("Anker 100W USB-C GaN Charger", "Electronics", 59.00, 24.00),
    
    # Category: Office Furniture
    ("Herman Miller Aeron Chair", "Office Furniture", 1250.00, 890.00),
    ("Jarvis Dual-Motor Standing Desk", "Office Furniture", 750.00, 520.00),
    ("Steelcase Gesture Ergonomic Stool", "Office Furniture", 980.00, 710.00),
    ("Oak Solid Wood Executive Desk", "Office Furniture", 1450.00, 1050.00),
    ("Mobile 3-Drawer File Cabinet", "Office Furniture", 189.00, 135.00),
    
    # Category: Office Supplies
    ("Ergonomic Gel Wrist Rest Pad", "Office Supplies", 28.00, 9.00),
    ("High-Grade Whiteboard 48x36\"", "Office Supplies", 145.00, 80.00),
    ("Moleskine Classic Leather Journal", "Office Supplies", 24.00, 8.50),
    ("Heavy-Duty Desktop Stapler", "Office Supplies", 35.00, 14.00),
    ("Recycled Laser Printer Paper (10 Reams)", "Office Supplies", 65.00, 52.00), # Lower margin
    
    # Category: Fashion & Apparel
    ("Premium Merino Wool Blazer", "Fashion & Apparel", 280.00, 120.00),
    ("All-Weather Waterproof Commuter Parka", "Fashion & Apparel", 220.00, 95.00),
    ("Breathable Tech Polo Shirt", "Fashion & Apparel", 68.00, 22.00),
    ("Italian Full-Grain Leather Briefcase", "Fashion & Apparel", 340.00, 150.00),
    ("Everyday Canvas Laptop Backpack", "Fashion & Apparel", 85.00, 36.00),
    
    # Category: Home & Lifestyle
    ("Nespresso VertuoPlus Coffee Machine", "Home & Lifestyle", 199.00, 130.00),
    ("Smart LED Ambient Desk Light Bar", "Home & Lifestyle", 89.00, 38.00),
    ("Ceramic Self-Heating Smart Mug", "Home & Lifestyle", 129.00, 60.00),
    ("HEPA Air Purifier Pro Tower", "Home & Lifestyle", 260.00, 175.00),
]

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
CUSTOMERS = [
    "Apex Global Logistics", "Quantum Innovations Inc", "Starlight Media Group",
    "Horizon Financial Partners", "BluePeak Systems", "Vanguard Health Technologies",
    "Nexus Cloud Solutions", "Ironclad Cyber Security", "Summit Ventures Ltd",
    "Alpha Core Dynamics", "Pinnacle Capital", "Echo Interactive Labs",
    "Hyperion Energy", "Omni Retail Networks", "Synergy Design Co"
]

def generate_sample_sales_data(num_rows=1200):
    random.seed(42)
    np.random.seed(42)
    
    # Span past 14 months up to current date
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=420)
    
    records = []
    
    for i in range(1, num_rows + 1):
        prod_name, category, unit_price, unit_cost = random.choice(SAMPLE_PRODUCTS)
        region = random.choices(REGIONS, weights=[0.40, 0.28, 0.18, 0.08, 0.06])[0]
        customer = random.choice(CUSTOMERS)
        
        # Random date with slight monthly upward trend
        days_offset = random.randint(0, 420)
        order_date = start_date + datetime.timedelta(days=days_offset)
        
        # Quantity
        qty = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[0.50, 0.25, 0.12, 0.06, 0.04, 0.02, 0.01])[0]
        
        # Small random discount or price variation (+- 5%)
        discount_factor = random.choice([1.0, 1.0, 0.95, 0.90, 1.05])
        actual_price = round(unit_price * discount_factor, 2)
        
        revenue = round(actual_price * qty, 2)
        total_cost = round(unit_cost * qty, 2)
        profit = round(revenue - total_cost, 2)
        margin = round((profit / revenue * 100.0), 2) if revenue > 0 else 0.0
        
        records.append({
            'Order ID': f"INV-{20250000 + i}",
            'Order Date': order_date.isoformat(),
            'Product Name': prod_name,
            'Category': category,
            'Region': region,
            'Quantity': qty,
            'Revenue': revenue,
            'Cost': total_cost,
            'Profit': profit,
            'Customer Name': customer
        })
        
    return pd.DataFrame(records)

def seed_sample_dataset_for_user(user, name="Global Enterprise Sales (Demo)"):
    """
    Creates and ingests the comprehensive demo sales dataset for a user.
    """
    df = generate_sample_sales_data(1200)
    
    # Save to media/datasets/
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'datasets'), exist_ok=True)
    file_rel_path = f"datasets/sample_{user.id}_{int(datetime.datetime.now().timestamp())}.csv"
    full_path = os.path.join(settings.MEDIA_ROOT, file_rel_path)
    df.to_csv(full_path, index=False)

    # Process and clean
    cleaned_df, report, detected_mappings = load_and_clean_data(full_path)

    # Deactivate existing datasets
    Dataset.objects.filter(user=user, is_active=True).update(is_active=False)

    dataset = Dataset.objects.create(
        user=user,
        name=name,
        description="Comprehensive 14-month multi-regional e-commerce & retail sales analytics dataset.",
        file=file_rel_path,
        file_type='sample',
        file_size_bytes=os.path.getsize(full_path),
        row_count=len(cleaned_df),
        column_count=len(df.columns),
        columns_detected=detected_mappings,
        validation_report=report,
        is_active=True
    )

    # Bulk insert SaleRecords for high performance
    records_to_create = []
    for _, row in cleaned_df.iterrows():
        records_to_create.append(
            SaleRecord(
                dataset=dataset,
                order_id=row['order_id'],
                order_date=row['order_date'],
                product_name=row['product_name'],
                category=row['category'],
                region=row['region'],
                quantity=row['quantity'],
                revenue=Decimal(str(row['revenue'])),
                cost=Decimal(str(row['cost'])),
                profit=Decimal(str(row['profit'])),
                profit_margin=float(row['profit_margin']),
                customer_name=row['customer_name']
            )
        )

    SaleRecord.objects.bulk_create(records_to_create, batch_size=1000)

    # Pre-cache summary KPIs
    metrics = calculate_dashboard_metrics(dataset.records.all())
    dataset.summary_cache = metrics
    dataset.save(update_fields=['summary_cache'])

    return dataset


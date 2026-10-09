import re
import datetime
import pandas as pd
import numpy as np

COLUMN_SYNONYMS = {
    'order_date': ['order_date', 'orderdate', 'date', 'transaction_date', 'trans_date', 'sale_date', 'purchase_date', 'invoice_date', 'time'],
    'order_id': ['order_id', 'orderid', 'order_no', 'invoice_no', 'invoice_id', 'transaction_id', 'trans_id', 'id'],
    'product_name': ['product_name', 'product', 'productname', 'item', 'item_name', 'item_description', 'title', 'sku_name'],
    'category': ['category', 'product_category', 'sub_category', 'subcategory', 'segment', 'department', 'type', 'group', 'genre'],
    'region': ['region', 'market', 'territory', 'country', 'state', 'city', 'zone', 'location', 'area'],
    'revenue': ['revenue', 'sales', 'sale_amount', 'total_sales', 'total_amount', 'amount', 'turnover', 'gross_sales', 'total_price', 'price'],
    'cost': ['cost', 'cogs', 'unit_cost', 'total_cost', 'expense', 'cost_price'],
    'profit': ['profit', 'net_profit', 'margin', 'gross_profit', 'earnings', 'gain'],
    'quantity': ['quantity', 'qty', 'units', 'volume', 'count', 'items_sold'],
    'customer_name': ['customer_name', 'customer', 'customername', 'client', 'buyer', 'account_name']
}

def clean_currency_str(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    # Check for parentheses indicating negative: (100) -> -100
    is_negative = False
    if s.startswith('(') and s.endswith(')'):
        is_negative = True
        s = s[1:-1]
    # Remove symbols like $, €, £, ₹, commas, and whitespace
    s = re.sub(r'[^\d.-]', '', s)
    if not s or s == '-' or s == '.':
        return np.nan
    try:
        num = float(s)
        return -num if is_negative else num
    except ValueError:
        return np.nan

def detect_column_mappings(df_columns):
    mappings = {}
    normalized_cols = {col: re.sub(r'[\s_\-.]+', '_', str(col).strip().lower()) for col in df_columns}
    
    for canonical, synonyms in COLUMN_SYNONYMS.items():
        found = None
        # Exact normalized match
        for col, norm in normalized_cols.items():
            if norm in synonyms:
                found = col
                break
        
        # Substring / partial match if not found
        if not found:
            for col, norm in normalized_cols.items():
                for syn in synonyms:
                    if syn in norm or norm in syn:
                        found = col
                        break
                if found:
                    break
        
        if found:
            mappings[canonical] = found

    return mappings

def load_and_clean_data(file_source, custom_mappings=None):
    """
    Reads CSV or Excel file, validates structure, standardizes columns,
    cleans missing/invalid data, and generates a validation report.
    Returns: (cleaned_df, validation_report, detected_mappings)
    """
    # 1. Read file into DataFrame
    if isinstance(file_source, str):
        if file_source.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_source)
        else:
            try:
                df = pd.read_csv(file_source, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_source, encoding='latin1')
    else:
        # File-like object (e.g. Django UploadedFile)
        filename = getattr(file_source, 'name', '')
        if filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_source)
        else:
            try:
                df = pd.read_csv(file_source, encoding='utf-8')
            except UnicodeDecodeError:
                file_source.seek(0)
                df = pd.read_csv(file_source, encoding='latin1')

    total_raw_rows = len(df)
    total_raw_cols = len(df.columns)
    
    # Strip whitespace from column headers
    df.columns = [str(c).strip() for c in df.columns]
    
    # Detect or apply mappings
    detected_mappings = detect_column_mappings(df.columns)
    if custom_mappings:
        detected_mappings.update(custom_mappings)
        
    # Check duplicate rows
    initial_dupes = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Create canonical DataFrame
    canonical_df = pd.DataFrame(index=df.index)
    
    # 1. Order ID
    if 'order_id' in detected_mappings:
        canonical_df['order_id'] = df[detected_mappings['order_id']].astype(str).str.strip()
    else:
        canonical_df['order_id'] = [f"ORD-{i+10001}" for i in range(len(df))]

    # 2. Order Date
    if 'order_date' in detected_mappings:
        raw_dates = df[detected_mappings['order_date']]
        parsed_dates = pd.to_datetime(raw_dates, errors='coerce', dayfirst=False)
        # If too many NaTs, try dayfirst=True
        if parsed_dates.isna().sum() > len(df) * 0.5:
            alt_dates = pd.to_datetime(raw_dates, errors='coerce', dayfirst=True)
            if alt_dates.isna().sum() < parsed_dates.isna().sum():
                parsed_dates = alt_dates
        canonical_df['order_date'] = parsed_dates
    else:
        # Default fallback dates (e.g. past year)
        base_date = datetime.date.today() - datetime.timedelta(days=365)
        canonical_df['order_date'] = [pd.to_datetime(base_date + datetime.timedelta(days=i % 365)) for i in range(len(df))]

    # 3. Product Name
    if 'product_name' in detected_mappings:
        canonical_df['product_name'] = df[detected_mappings['product_name']].fillna('General Product').astype(str).str.strip()
    else:
        canonical_df['product_name'] = 'General Merchandise'

    # 4. Category
    if 'category' in detected_mappings:
        canonical_df['category'] = df[detected_mappings['category']].fillna('Uncategorized').astype(str).str.strip()
    else:
        canonical_df['category'] = 'General'

    # 5. Region
    if 'region' in detected_mappings:
        canonical_df['region'] = df[detected_mappings['region']].fillna('Standard Region').astype(str).str.strip()
    else:
        canonical_df['region'] = 'Global'

    # 6. Customer Name
    if 'customer_name' in detected_mappings:
        canonical_df['customer_name'] = df[detected_mappings['customer_name']].fillna('Anonymous').astype(str).str.strip()
    else:
        canonical_df['customer_name'] = 'Direct Customer'

    # 7. Quantity
    if 'quantity' in detected_mappings:
        raw_qty = df[detected_mappings['quantity']].apply(clean_currency_str)
        canonical_df['quantity'] = pd.to_numeric(raw_qty, errors='coerce').fillna(1).astype(int)
        canonical_df.loc[canonical_df['quantity'] <= 0, 'quantity'] = 1
    else:
        canonical_df['quantity'] = 1

    # 8. Revenue / Sales
    if 'revenue' in detected_mappings:
        raw_rev = df[detected_mappings['revenue']].apply(clean_currency_str)
        canonical_df['revenue'] = pd.to_numeric(raw_rev, errors='coerce')
    else:
        canonical_df['revenue'] = np.nan

    # 9. Cost
    if 'cost' in detected_mappings:
        raw_cost = df[detected_mappings['cost']].apply(clean_currency_str)
        canonical_df['cost'] = pd.to_numeric(raw_cost, errors='coerce')
    else:
        canonical_df['cost'] = np.nan

    # 10. Profit
    if 'profit' in detected_mappings:
        raw_profit = df[detected_mappings['profit']].apply(clean_currency_str)
        canonical_df['profit'] = pd.to_numeric(raw_profit, errors='coerce')
    else:
        canonical_df['profit'] = np.nan

    # Intelligently infer missing financial values
    # If revenue is missing but we have profit & cost: revenue = cost + profit
    need_rev = canonical_df['revenue'].isna()
    canonical_df.loc[need_rev & canonical_df['cost'].notna() & canonical_df['profit'].notna(), 'revenue'] = (
        canonical_df['cost'] + canonical_df['profit']
    )

    # If profit is missing but we have revenue & cost: profit = revenue - cost
    need_profit = canonical_df['profit'].isna()
    canonical_df.loc[need_profit & canonical_df['revenue'].notna() & canonical_df['cost'].notna(), 'profit'] = (
        canonical_df['revenue'] - canonical_df['cost']
    )

    # If cost is missing but we have revenue & profit: cost = revenue - profit
    need_cost = canonical_df['cost'].isna()
    canonical_df.loc[need_cost & canonical_df['revenue'].notna() & canonical_df['profit'].notna(), 'cost'] = (
        canonical_df['revenue'] - canonical_df['profit']
    )

    # If revenue is still missing, estimate or fallback
    if canonical_df['revenue'].isna().all():
        canonical_df['revenue'] = 100.0 * canonical_df['quantity']
    else:
        canonical_df['revenue'] = canonical_df['revenue'].fillna(canonical_df['revenue'].median())

    # If cost is still missing, default cost = 65% of revenue
    if canonical_df['cost'].isna().all():
        canonical_df['cost'] = (canonical_df['revenue'] * 0.65).round(2)
    else:
        canonical_df['cost'] = canonical_df['cost'].fillna((canonical_df['revenue'] * 0.65).round(2))

    # If profit is still missing: profit = revenue - cost
    if canonical_df['profit'].isna().all():
        canonical_df['profit'] = (canonical_df['revenue'] - canonical_df['cost']).round(2)
    else:
        canonical_df['profit'] = canonical_df['profit'].fillna((canonical_df['revenue'] - canonical_df['cost']).round(2))

    # Calculate profit margin %
    canonical_df['profit_margin'] = np.where(
        canonical_df['revenue'] > 0,
        ((canonical_df['profit'] / canonical_df['revenue']) * 100).round(2),
        0.0
    )

    # Filter out completely invalid records (e.g. invalid dates, negative/zero revenue where meaningless)
    valid_mask = canonical_df['order_date'].notna() & canonical_df['revenue'].notna()
    dropped_rows = int((~valid_mask).sum())
    cleaned_df = canonical_df[valid_mask].copy()

    # Convert date to standard ISO string and Python date object
    cleaned_df['order_date'] = pd.to_datetime(cleaned_df['order_date']).dt.date

    # Round numeric values for clean database insertion
    cleaned_df['revenue'] = cleaned_df['revenue'].round(2)
    cleaned_df['cost'] = cleaned_df['cost'].round(2)
    cleaned_df['profit'] = cleaned_df['profit'].round(2)
    cleaned_df['profit_margin'] = cleaned_df['profit_margin'].round(2)

    # Calculate Data Quality Score
    cleaned_count = len(cleaned_df)
    quality_score = 100.0 if total_raw_rows == 0 else round((cleaned_count / total_raw_rows) * 100.0, 1)

    # Date range
    min_date = str(cleaned_df['order_date'].min()) if cleaned_count > 0 else None
    max_date = str(cleaned_df['order_date'].max()) if cleaned_count > 0 else None

    # Distinct counts
    unique_categories = int(cleaned_df['category'].nunique()) if cleaned_count > 0 else 0
    unique_regions = int(cleaned_df['region'].nunique()) if cleaned_count > 0 else 0
    unique_products = int(cleaned_df['product_name'].nunique()) if cleaned_count > 0 else 0

    preview_df = cleaned_df.head(5).copy()
    if 'order_date' in preview_df.columns:
        preview_df['order_date'] = preview_df['order_date'].astype(str)

    validation_report = {
        'total_raw_rows': total_raw_rows,
        'total_raw_cols': total_raw_cols,
        'cleaned_rows': cleaned_count,
        'dropped_rows': dropped_rows,
        'duplicates_removed': initial_dupes,
        'data_quality_score': quality_score,
        'date_range': {'min': min_date, 'max': max_date},
        'distinct_counts': {
            'categories': unique_categories,
            'regions': unique_regions,
            'products': unique_products
        },
        'detected_columns': detected_mappings,
        'preview_rows': preview_df.to_dict(orient='records')
    }

    return cleaned_df, validation_report, detected_mappings

import datetime
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth, TruncDate
import pandas as pd
import numpy as np

def calculate_dashboard_metrics(records_qs):
    """
    Computes all analytical metrics, chart series, and breakdowns
    from a filtered SaleRecord queryset.
    """
    total_records = records_qs.count()
    if total_records == 0:
        return {
            'kpis': {
                'total_revenue': 0.0,
                'total_profit': 0.0,
                'profit_margin': 0.0,
                'total_orders': 0,
                'total_units': 0,
                'avg_order_value': 0.0,
                'mom_growth': 0.0
            },
            'monthly_trends': {'labels': [], 'revenue': [], 'profit': [], 'orders': [], 'margin': []},
            'category_performance': {'labels': [], 'revenue': [], 'profit': [], 'margin': [], 'shares': []},
            'region_performance': {'labels': [], 'revenue': [], 'profit': [], 'orders': []},
            'top_products': [],
            'least_profitable_products': [],
            'summary_count': 0
        }

    # Aggregate core KPIs
    aggregates = records_qs.aggregate(
        tot_rev=Sum('revenue'),
        tot_prof=Sum('profit'),
        tot_qty=Sum('quantity'),
        distinct_orders=Count('order_id', distinct=True)
    )

    tot_rev = float(aggregates['tot_rev'] or 0.0)
    tot_prof = float(aggregates['tot_prof'] or 0.0)
    tot_qty = int(aggregates['tot_qty'] or 0)
    tot_orders = int(aggregates['distinct_orders'] or total_records)
    
    margin_pct = round((tot_prof / tot_rev * 100.0), 2) if tot_rev > 0 else 0.0
    aov = round(tot_rev / tot_orders, 2) if tot_orders > 0 else 0.0

    # 1. Monthly Trends
    # Group by month
    monthly_data = (
        records_qs
        .filter(order_date__isnull=False)
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(
            rev=Sum('revenue'),
            prof=Sum('profit'),
            orders=Count('id')
        )
        .order_by('month')
    )

    trend_labels = []
    trend_rev = []
    trend_prof = []
    trend_orders = []
    trend_margin = []

    for item in monthly_data:
        if item['month']:
            m_label = item['month'].strftime('%b %Y')
            m_r = round(float(item['rev'] or 0.0), 2)
            m_p = round(float(item['prof'] or 0.0), 2)
            m_o = int(item['orders'] or 0)
            m_m = round((m_p / m_r * 100.0), 2) if m_r > 0 else 0.0

            trend_labels.append(m_label)
            trend_rev.append(m_r)
            trend_prof.append(m_p)
            trend_orders.append(m_o)
            trend_margin.append(m_m)

    # MoM Revenue Growth
    mom_growth = 0.0
    if len(trend_rev) >= 2 and trend_rev[-2] > 0:
        mom_growth = round(((trend_rev[-1] - trend_rev[-2]) / trend_rev[-2]) * 100.0, 2)

    # 2. Category Performance
    cat_data = (
        records_qs
        .values('category')
        .annotate(
            rev=Sum('revenue'),
            prof=Sum('profit'),
            orders=Count('id')
        )
        .order_by('-rev')
    )

    cat_labels = []
    cat_rev = []
    cat_prof = []
    cat_margin = []
    cat_shares = []

    for c in cat_data:
        c_name = c['category'] or 'Uncategorized'
        c_r = round(float(c['rev'] or 0.0), 2)
        c_p = round(float(c['prof'] or 0.0), 2)
        c_m = round((c_p / c_r * 100.0), 2) if c_r > 0 else 0.0
        c_share = round((c_r / tot_rev * 100.0), 2) if tot_rev > 0 else 0.0

        cat_labels.append(c_name)
        cat_rev.append(c_r)
        cat_prof.append(c_p)
        cat_margin.append(c_m)
        cat_shares.append(c_share)

    # 3. Region Performance
    reg_data = (
        records_qs
        .values('region')
        .annotate(
            rev=Sum('revenue'),
            prof=Sum('profit'),
            orders=Count('id')
        )
        .order_by('-rev')
    )

    reg_labels = []
    reg_rev = []
    reg_prof = []
    reg_orders = []

    for r in reg_data:
        r_name = r['region'] or 'Other'
        r_r = round(float(r['rev'] or 0.0), 2)
        r_p = round(float(r['prof'] or 0.0), 2)
        r_o = int(r['orders'] or 0)

        reg_labels.append(r_name)
        reg_rev.append(r_r)
        reg_prof.append(r_p)
        reg_orders.append(r_o)

    # 4. Top Selling Products (Top 10)
    top_prods_qs = (
        records_qs
        .values('product_name', 'category')
        .annotate(
            rev=Sum('revenue'),
            prof=Sum('profit'),
            units=Sum('quantity'),
            orders=Count('id')
        )
        .order_by('-rev')[:10]
    )

    top_products = []
    for p in top_prods_qs:
        p_rev = round(float(p['rev'] or 0.0), 2)
        p_prof = round(float(p['prof'] or 0.0), 2)
        p_margin = round((p_prof / p_rev * 100.0), 2) if p_rev > 0 else 0.0
        top_products.append({
            'name': p['product_name'] or 'Product',
            'category': p['category'] or 'General',
            'revenue': p_rev,
            'profit': p_prof,
            'units': int(p['units'] or 0),
            'margin': p_margin
        })

    # 5. Bottom / Underperforming Products (lowest profit or loss makers)
    bottom_prods_qs = (
        records_qs
        .values('product_name', 'category')
        .annotate(
            rev=Sum('revenue'),
            prof=Sum('profit'),
            units=Sum('quantity')
        )
        .order_by('prof')[:5]
    )
    least_profitable_products = []
    for p in bottom_prods_qs:
        least_profitable_products.append({
            'name': p['product_name'] or 'Product',
            'category': p['category'] or 'General',
            'revenue': round(float(p['rev'] or 0.0), 2),
            'profit': round(float(p['prof'] or 0.0), 2),
            'units': int(p['units'] or 0)
        })

    return {
        'kpis': {
            'total_revenue': round(tot_rev, 2),
            'total_profit': round(tot_prof, 2),
            'profit_margin': margin_pct,
            'total_orders': tot_orders,
            'total_units': tot_qty,
            'avg_order_value': aov,
            'mom_growth': mom_growth
        },
        'monthly_trends': {
            'labels': trend_labels,
            'revenue': trend_rev,
            'profit': trend_prof,
            'orders': trend_orders,
            'margin': trend_margin
        },
        'category_performance': {
            'labels': cat_labels,
            'revenue': cat_rev,
            'profit': cat_prof,
            'margin': cat_margin,
            'shares': cat_shares
        },
        'region_performance': {
            'labels': reg_labels,
            'revenue': reg_rev,
            'profit': reg_prof,
            'orders': reg_orders
        },
        'top_products': top_products,
        'least_profitable_products': least_profitable_products,
        'summary_count': total_records
    }


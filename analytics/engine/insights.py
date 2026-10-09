import numpy as np

def generate_automated_insights(metrics, dataset_name="Business Dataset"):
    """
    Analyzes calculated metrics and automatically synthesizes:
    - Executive Narrative Summary
    - Highlight badges (Top Product, Top Category, Growth rate, Peak Month)
    - Actionable Business Recommendations
    - Risk & Anomaly Warnings
    """
    kpis = metrics.get('kpis', {})
    tot_rev = kpis.get('total_revenue', 0.0)
    tot_prof = kpis.get('total_profit', 0.0)
    margin = kpis.get('profit_margin', 0.0)
    tot_orders = kpis.get('total_orders', 0)
    aov = kpis.get('avg_order_value', 0.0)
    mom_growth = kpis.get('mom_growth', 0.0)

    trends = metrics.get('monthly_trends', {})
    categories = metrics.get('category_performance', {})
    regions = metrics.get('region_performance', {})
    top_products = metrics.get('top_products', [])
    least_profitable = metrics.get('least_profitable_products', [])

    if tot_rev == 0:
        return {
            'executive_summary': 'No sales records were found matching the selected filters. Please adjust your date range or category filters.',
            'highlights': [],
            'recommendations': [],
            'anomalies': [],
            'overall_health': 'Neutral'
        }

    # 1. Best Month identification
    months = trends.get('labels', [])
    revs = trends.get('revenue', [])
    best_month = None
    best_month_rev = 0
    if months and revs:
        max_idx = int(np.argmax(revs))
        best_month = months[max_idx]
        best_month_rev = revs[max_idx]

    # 2. Top Category identification
    cat_labels = categories.get('labels', [])
    cat_revs = categories.get('revenue', [])
    cat_margins = categories.get('margin', [])
    top_cat = cat_labels[0] if cat_labels else 'N/A'
    top_cat_rev = cat_revs[0] if cat_revs else 0
    top_cat_share = round((top_cat_rev / tot_rev * 100.0), 1) if tot_rev > 0 else 0

    # Highest margin category
    highest_margin_cat = 'N/A'
    highest_margin_val = 0
    if cat_labels and cat_margins:
        h_idx = int(np.argmax(cat_margins))
        highest_margin_cat = cat_labels[h_idx]
        highest_margin_val = cat_margins[h_idx]

    # 3. Top Product
    top_prod_name = top_products[0]['name'] if top_products else 'N/A'
    top_prod_rev = top_products[0]['revenue'] if top_products else 0
    top_prod_share = round((top_prod_rev / tot_rev * 100.0), 1) if tot_rev > 0 else 0

    # 4. Top Region
    reg_labels = regions.get('labels', [])
    reg_revs = regions.get('revenue', [])
    top_reg = reg_labels[0] if reg_labels else 'N/A'
    top_reg_rev = reg_revs[0] if reg_revs else 0
    top_reg_share = round((top_reg_rev / tot_rev * 100.0), 1) if tot_rev > 0 else 0

    # Executive narrative synthesis
    health_status = 'Excellent' if margin >= 20 else ('Healthy' if margin >= 10 else 'Needs Attention')
    
    summary_paragraph = (
        f"Across the analyzed timeframe, {dataset_name} generated a cumulative revenue of ${tot_rev:,.2f} "
        f"with a net profit of ${tot_prof:,.2f}, resulting in an overall profit margin of {margin:.1f}%. "
        f"A total of {tot_orders:,} customer transactions were completed with an Average Order Value (AOV) of ${aov:,.2f}. "
        f"The primary revenue engine is '{top_cat}' contributing {top_cat_share}% of total turnover, "
        f"while '{top_prod_name}' stands as the standout flagship SKU generating ${top_prod_rev:,.2f} ({top_prod_share}%). "
    )
    if best_month:
        summary_paragraph += f"Performance reached its peak in {best_month} with monthly sales reaching ${best_month_rev:,.2f}. "
    if mom_growth != 0.0:
        summary_paragraph += f"The latest Month-over-Month (MoM) revenue trend trajectory reflects a {mom_growth:+.1f}% shift."

    # Highlight Cards
    highlights = [
        {
            'title': 'Flagship Performer',
            'value': top_prod_name,
            'subtitle': f"${top_prod_rev:,.2f} ({top_prod_share}% of Total Revenue)",
            'icon': 'award',
            'color': 'indigo'
        },
        {
            'title': 'Category Leader',
            'value': top_cat,
            'subtitle': f"${top_cat_rev:,.2f} ({top_cat_share}% volume share)",
            'icon': 'folder-check',
            'color': 'blue'
        },
        {
            'title': 'Highest Margin Segment',
            'value': highest_margin_cat,
            'subtitle': f"{highest_margin_val:.1f}% Profit Margin",
            'icon': 'trending-up',
            'color': 'emerald'
        },
        {
            'title': 'Prime Regional Market',
            'value': top_reg,
            'subtitle': f"${top_reg_rev:,.2f} ({top_reg_share}% regional share)",
            'icon': 'map-pin',
            'color': 'purple'
        }
    ]

    # Recommendations
    recommendations = []
    if highest_margin_cat != 'N/A' and highest_margin_cat != top_cat:
        recommendations.append({
            'category': 'Margin Optimization',
            'text': f"'{highest_margin_cat}' enjoys an impressive {highest_margin_val:.1f}% profit margin but is outpaced in volume by '{top_cat}'. Increasing promotional allocation toward this segment will boost blended EBITDA margins.",
            'priority': 'High'
        })
    else:
        recommendations.append({
            'category': 'Sales Expansion',
            'text': f"Continue scaling inventory for '{top_cat}', while testing bundled accessory packages to increase the average ticket size beyond ${aov:,.2f}.",
            'priority': 'Medium'
        })

    if top_reg != 'N/A' and len(reg_labels) > 1:
        lowest_reg = reg_labels[-1]
        recommendations.append({
            'category': 'Geographic Growth',
            'text': f"Market concentration is heavy in '{top_reg}' ({top_reg_share}%). Regional sales in '{lowest_reg}' represent untapped expansion potential through localized marketing and targeted distributor partnerships.",
            'priority': 'Medium'
        })

    if margin < 12.0:
        recommendations.append({
            'category': 'Cost Structure',
            'text': f"Overall profit margin sits at {margin:.1f}%. Review supplier agreements and freight overhead to recover at least 300 basis points in gross margin.",
            'priority': 'Critical'
        })
    else:
        recommendations.append({
            'category': 'Customer Retention',
            'text': f"With healthy margins of {margin:.1f}%, deploy a loyalty or recurring subscription discount program to sustain customer lifetime value (LTV).",
            'priority': 'Low'
        })

    # Anomalies and Risk Alerts
    anomalies = []
    # Check for loss-making products
    loss_makers = [p for p in least_profitable if p['profit'] < 0]
    if loss_makers:
        names = ", ".join([p['name'] for p in loss_makers[:3]])
        anomalies.append({
            'type': 'Negative Profit Alert',
            'severity': 'High',
            'message': f"Negative profit detected on: {names}. Investigate whether pricing discounts or shipping subsidies are eroding gross returns."
        })

    # Check for category with low margin
    low_margin_cats = [
        cat_labels[i] for i, m in enumerate(cat_margins) if m < 5.0
    ]
    if low_margin_cats:
        anomalies.append({
            'type': 'Thin Margin Warning',
            'severity': 'Medium',
            'message': f"Categories with margins under 5%: {', '.join(low_margin_cats)}. Consider price adjustments or cost-of-goods re-negotiation."
        })

    # Check for single product over-reliance
    if top_prod_share > 35.0:
        anomalies.append({
            'type': 'Revenue Concentration Risk',
            'severity': 'Medium',
            'message': f"'{top_prod_name}' represents {top_prod_share}% of all revenue. Over-reliance on a single product poses supply-chain and competitor exposure."
        })

    return {
        'executive_summary': summary_paragraph,
        'highlights': highlights,
        'recommendations': recommendations,
        'anomalies': anomalies,
        'overall_health': health_status
    }


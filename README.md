# 📊 SaaS Business Analytics Platform

![Python](https://img.shields.io/badge/Python-3.14%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.1-green?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.18-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Engine-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visuals-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Dark_Theme-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

An enterprise-grade, multi-tenant **SaaS Business Intelligence & Analytics Web Platform** that bridges full-stack web development with deep data analytics. Businesses can upload raw sales datasets (CSV & Excel) to instantly unlock interactive visual dashboards, profit analysis, slice-and-dice filters, automated executive narratives, and multi-format reports.

---

## 📑 Table of Contents

- [Concept & Architecture](#-concept--architecture)
- [Key Features](#-key-features)
- [Tech Stack Details](#-tech-stack-details)
- [Project Directory Structure](#-project-directory-structure)
- [Quick Start Guide](#-quick-start-guide)
- [PostgreSQL Database Setup](#-postgresql-database-setup)
- [Default Login Credentials](#-default-login-credentials)
- [Core Application Modules](#-core-application-modules)
- [REST API Endpoints Reference](#-rest-api-endpoints-reference)
- [Automated Testing Suite](#-automated-testing-suite)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 💡 Concept & Architecture

Small and medium businesses often have sales data scattered across messy spreadsheets (CSV, Excel) with dirty numbers, currency symbols, and inconsistent columns. 

**SaaS Business Analytics Platform** automatically ingests, validates, and cleans this data using a robust **Pandas pipeline**, calculates financial metrics (Revenue, Profit, Margins, Orders, AOV), and renders a sleek, interactive executive dashboard powered by **Django REST Framework**, **Chart.js**, and **Plotly**.

```
[User CSV/Excel Upload] 
         │
         ▼
[Pandas Ingestion & Cleaning Engine] 
  ├── Fuzzy Column Detection (Synonyms)
  ├── Currency & Symbol Sanitizer
  ├── Missing Profit/Revenue Imputation
  └── Data Quality Score Report
         │
         ▼
[Database Storage & Aggregation] 
  ├── PostgreSQL (or SQLite Zero-Setup Default)
  └── Fast Indexed SQL Aggregations
         │
         ▼
[Django REST Framework APIs] (Token Auth)
  ├── Dashboard Analytics Endpoint
  ├── Automated Smart AI Insights
  ├── Paginated Records Explorer
  └── Report Generators (CSV, Excel, PDF)
         │
         ▼
[Modern SPA Frontend] (HTML, CSS, Vanilla JS, Tailwind)
  ├── Real-time Interactive Filters
  ├── Dual Visualizer (Chart.js & Plotly)
  └── Multi-Format Export Center
```

---

## 🚀 Key Features

### 1. 🔐 Multi-Tenant User Authentication & Data Isolation
- **Tenant Isolation**: Har user sirf apna uploaded data dekh sakta hai. Ek user doosre ka business data kabhi access nahi kar sakta.
- **Token-Based Authentication**: Secure DRF token authentication (`TokenAuthentication`) with session fallback.
- **1-Click Instant Demo Login**: Bina kisi manual form registration ke **1 click** me pre-loaded 1,200 records ke sath dashboard test drive kar sakte hain.
- **User Profile Header**: Displays user initials, display name, and active dataset badge.

### 2. 📁 Multi-Format Upload (CSV & Excel)
- Drag-and-drop file upload zone supporting **`.csv`**, **`.xlsx`**, and **`.xls`** formats.
- Pre-packaged demo datasets included in the root folder (`sample_sales_data.csv` and `sample_sales_data.xlsx`).
- Built-in "Download Sample CSV Template" button on the UI for quick custom testing.

### 3. 🧼 Automated Data Validation & Cleaning (Pandas Engine)
- **Fuzzy Column Mapper**: Automatically maps synonymous columns:
  - `Order_Date` / `Date` / `Transaction_Date` / `Time`
  - `Revenue` / `Sales` / `Amount` / `Total_Amount` / `Turnover`
  - `Profit` / `Net_Profit` / `Margin` / `Earnings`
  - `Category` / `Segment` / `Department` / `Product_Category`
  - `Region` / `Market` / `Country` / `State` / `Territory`
  - `Quantity` / `Units` / `Qty` / `Volume`
  - `Product_Name` / `Product` / `Item` / `SKU`
- **Currency Cleaning**: Cleans `$`, `€`, `₹`, `£`, commas (`,`), and negative brackets like `(150.00)` into pure numeric values.
- **Financial Inference**: Missing profit ya cost ko automatically calculate karta hai (`Profit = Revenue - Cost`).
- **Validation Modal**: Ingestion ke baad Data Quality Score (%), Total Rows, Cleaned Rows, Dropped Rows, and Mapped Columns display karta hai.

### 4. 📊 Interactive Visualizations (Dual-Engine: Chart.js & Plotly)
- **Monthly Sales & Profit Trends**: Dual-axis smooth area curves showing monthly revenue vs. net retained profit.
- **Category Revenue Share**: Interactive doughnut chart with percentage volume share.
- **Sales vs. Profit by Category**: Grouped bar chart comparing top-line revenue against bottom-line margin.
- **Region-wise Performance**: Geographic market revenue contributions.
- **Top 10 Selling Products Leaderboard**: Ranked horizontal bar chart.
- **Profit Margin % Distribution**: Color-coded margin efficiency bar chart (Emerald: >25%, Cyan: >12%, Amber: <12%).
- **Engine Switcher**: Top bar me ek click se **Chart.js** aur **Plotly** me switch kar sakte hain.

### 5. 💰 Sales & Profit Analysis (KPI Cards)
- **Total Revenue**: Formatted aggregate currency (`$1,046,372.80`).
- **Total Net Profit**: Total EBITDA bottom-line dollars (`$323,877.30`).
- **Profit Margin %**: Blended efficiency percentage (`31.0%`).
- **Total Orders**: Distinct completed invoices (`1,200`).
- **Average Order Value (AOV)**: Revenue per invoice ticket (`$871.98`).
- **Month-over-Month (MoM) Growth**: % change with color-coded positive/negative badges.

### 6. 🔍 Dynamic Slice-and-Dice Filters
- Date range picker (`From` & `To` date inputs).
- Category dropdown filter.
- Geographic Region dropdown filter.
- Global search box (Product SKU, Customer, or Order ID).
- **Instant Client-Side Recalculation**: All KPI cards, charts, and tables update instantly without full page reload.

### 7. 🧠 Advanced Feature: Automated Smart AI Insights & Executive Narrative
- **Executive Summary Paragraph**: Dataset ke empirical analysis par based naturally synthesized narrative.
- **Performance Highlight Badges**:
  - 🏆 *Flagship Performer* (Top revenue SKU and % contribution)
  - 📁 *Category Leader* (Highest revenue volume segment)
  - 📈 *Highest Margin Segment* (Best EBITDA margin %)
  - 🗺️ *Prime Regional Market* (Top geographical revenue driver)
- **Strategic Action Recommendations**: Concrete suggestions with priority tags (*Critical*, *High*, *Medium*, *Low*).
- **Anomaly & Risk Warnings**: Negative profit products detection, thin margin warnings (<5%), and revenue concentration risks.

### 8. 📋 Cleaned Records Data Explorer
- Paginated table showing individual normalized sales records.
- Live keyword search and multi-column sorting.
- Color-coded profit margin badges on each row.

### 9. 📑 Multi-Format Report Downloads
- **Cleaned Data CSV**: Full normalized records with calculated margins.
- **Executive Excel (.xlsx)**: Multi-sheet styled workbook generated via `openpyxl` (*Executive Summary*, *Category Performance*, *Regional Performance*, *Top Products*).
- **Executive Brief PDF**: Printable, publication-ready PDF report generated dynamically using `reportlab`.

### 10. 🗂️ User-Specific Datasets Management
- Manage multiple datasets per business account.
- Switch active dataset, delete obsolete datasets, and view metadata (row count, file size, upload timestamp).

---

## 🛠️ Tech Stack Details

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **Django 6.1** | Core web framework, ORM, models, security |
| **API Framework** | **Django REST Framework 3.18** | REST endpoints, serializers, token authentication |
| **Database** | **PostgreSQL / SQLite** | High performance relational storage with `psycopg 3.3` |
| **Data Engine** | **Pandas 3.0 & NumPy** | Ingestion, data cleaning, date standardizing, aggregations |
| **Spreadsheet Engine** | **OpenPyXL 3.1** | Reading `.xlsx` uploads and generating styled multi-sheet Excel reports |
| **PDF Generation** | **ReportLab 5.0** | Building styled Executive Brief PDF reports |
| **Visualizations** | **Chart.js 4.4 & Plotly.js 2.27** | Responsive, interactive HTML5 charts with tooltips and dual axes |
| **Frontend UI** | **HTML5, CSS3, Vanilla JS** | Zero-bloat, ultra-fast responsive Single Page Application (SPA) |
| **Styling** | **Tailwind CSS & Lucide Icons** | Glassmorphic dark SaaS UI, custom badges, and SVG icons |

---

## 📂 Project Directory Structure

```
d:\saas project\
│
├── manage.py                         # Django management CLI script
├── requirements.txt                  # Python dependencies
├── setup_postgres.py                 # Interactive PostgreSQL setup helper
├── sample_sales_data.csv             # 1,200-row demo sales CSV file
├── sample_sales_data.xlsx            # 1,200-row demo sales Excel file
├── .env                              # Environment variables (DB, Secret Key)
├── .env.example                      # Template for environment configuration
├── db.sqlite3                        # SQLite database (pre-seeded with demo data)
│
├── analytics_saas/                   # Project Configuration
│   ├── __init__.py
│   ├── settings.py                   # DRF, Database, Static, Media & CORS settings
│   ├── urls.py                       # Main routing & SPA entry point
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                         # Authentication & Tenant App
│   ├── models.py                     # User profile bindings
│   ├── serializers.py                # Register, Login & User serializers
│   ├── views.py                      # Register, Login, DemoLogin, Profile, Logout
│   └── urls.py                       # /api/auth/ routes
│
├── analytics/                        # Analytics & BI App
│   ├── models.py                     # Dataset & SaleRecord models
│   ├── serializers.py                # Dataset and SaleRecord DRF serializers
│   ├── views.py                      # Ingestion, Dashboard, Insights, Table, Exports
│   ├── urls.py                       # /api/analytics/ routes
│   ├── admin.py                      # Django Admin model registrations & filters
│   ├── authentication.py             # CsrfExemptSessionAuthentication handler
│   ├── sample_data.py                # Demo dataset generator (1,200 rows across categories)
│   ├── tests.py                      # Comprehensive automated test suite (7 tests)
│   │
│   └── engine/                       # Core Analytics Processing Engine
│       ├── __init__.py
│       ├── cleaner.py                # Pandas data cleaning, currency & column detection
│       ├── analyzer.py               # KPIs, monthly trends, category & regional metrics
│       ├── insights.py               # Automated executive narrative & anomaly engine
│       └── exporter.py               # CSV, Multi-sheet Excel & ReportLab PDF generator
│
├── templates/
│   └── index.html                    # Modern SaaS SPA dashboard template
│
├── static/                           # Static Assets
│   ├── css/
│   │   └── app.css                   # Glassmorphic dark styling, animations, toasts
│   └── js/
│       ├── api.js                    # DRF API client with Token & CSRF handling
│       ├── charts.js                 # Chart.js & Plotly visualization engine
│       └── app.js                    # SPA state machine, upload handler, filter controller
│
└── media/                            # Media storage for uploaded datasets
    └── datasets/
```

---

## ⚡ Quick Start Guide

### Step 1: Open Terminal in Project Directory
```powershell
cd "d:\saas project"
```

### Step 2: Install Dependencies (if not already installed)
```powershell
pip install -r requirements.txt
```

### Step 3: Run Database Migrations
```powershell
python manage.py migrate
```

### Step 4: Start the Django Server
```powershell
python manage.py runserver 127.0.0.1:8000
```

### Step 5: Open in Your Browser
Navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🐘 PostgreSQL Database Setup

The platform is designed to run seamlessly on **PostgreSQL** or **SQLite**. 

By default, it uses SQLite so anyone can start the app with zero setup. You can connect PostgreSQL anytime using either method:

### Option A: Interactive Setup Helper (Recommended)
Run the built-in helper script in your terminal:
```powershell
python setup_postgres.py
```
Yeh script aapke PostgreSQL host, port, username aur password pooch kar:
1. Target database (`saas_analytics`) create karega.
2. `.env` file ko update karega.
3. Automatically Django migrations run karega.

### Option B: Manual Configuration
Create or edit the `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=saas-analytics-secret-key-super-secure-change-in-prod-2026
DB_ENGINE=postgresql
DB_NAME=saas_analytics
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
DB_HOST=localhost
DB_PORT=5432
```
Then run migrations:
```powershell
python manage.py migrate
```

---

## 🔑 Default Login Credentials

### 1. Instant 1-Click Demo Login
- Click the button on the sign-in modal: **"1-Click Instant Demo Login (Pre-loaded Data)"**.
- **User**: `demo_executive`
- Preloaded with **1,200 real transactions**, 14 months of history, 6 product categories, and 5 global regions.

### 2. Django Admin Panel Access
- **URL**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Username**: `admin`
- **Password**: `admin123`
- *(Note: Your custom user `abhisekh` is also configured as a Staff Superuser)*.

### 3. Custom User Registration
- Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Click **"Register"** tab, enter any username, email, and password.
- Registration creates a clean, private tenant dashboard where you can upload your own datasets.

---

## 🧩 Core Application Modules

### 1. Data Cleaning Engine (`analytics/engine/cleaner.py`)
- Accepts file streams or file paths (`.csv`, `.xlsx`, `.xls`).
- Uses fuzzy matching to map canonical columns (`order_date`, `order_id`, `product_name`, `category`, `region`, `revenue`, `cost`, `profit`, `quantity`, `customer_name`).
- Detects encoding (UTF-8, Latin-1, ISO-8859-1).
- Converts date formats into ISO `YYYY-MM-DD`.
- Generates a **Validation Report** with quality score and dropped row statistics.

### 2. Analytical Calculation Engine (`analytics/engine/analyzer.py`)
- Aggregates core KPIs (Total Revenue, Net Profit, Blended Margin %, Orders, AOV, MoM Growth).
- Groups monthly trends using `TruncMonth('order_date')`.
- Groups category and regional performance by revenue and profit.
- Ranks top 10 products and flags low-margin items.

### 3. Smart AI Insights Engine (`analytics/engine/insights.py`)
- Synthesizes a human-readable **Executive Summary** paragraph.
- Identifies peak performance periods and flagship products.
- Generates categorized **Strategic Recommendations** (*Margin Optimization*, *Geographic Growth*, *Cost Structure*).
- Detects **Anomalies & Risks** (Negative profit SKUs, thin margin categories <5%, single-product revenue concentration >35%).

### 4. Multi-Format Exporter (`analytics/engine/exporter.py`)
- `export_records_to_csv()`: Generates raw normalized CSV stream.
- `export_executive_excel()`: Builds styled multi-sheet `.xlsx` workbook using `openpyxl`.
- `export_executive_pdf()`: Generates publication-ready Executive Brief PDF with tables and narrative using `reportlab`.

---

## 📡 REST API Endpoints Reference

### Authentication Endpoints (`/api/auth/`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Register a new business account and obtain token |
| `POST` | `/api/auth/login/` | Sign in with username and password |
| `POST` | `/api/auth/demo-login/` | Instant 1-click login into demo executive workspace |
| `GET` | `/api/auth/user/` | Fetch authenticated user profile details |
| `POST` | `/api/auth/logout/` | Invalidate and delete user authentication token |

### Datasets Management (`/api/analytics/`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/analytics/datasets/` | List all datasets owned by the authenticated user |
| `POST` | `/api/analytics/datasets/upload/` | Upload, validate, and clean CSV or Excel file |
| `POST` | `/api/analytics/datasets/load-sample/` | Seed and ingest the 1,200-row demo sales dataset |
| `GET` | `/api/analytics/datasets/{id}/` | Get dataset details, row counts, and validation report |
| `POST` | `/api/analytics/datasets/{id}/set-active/` | Set dataset as the active dashboard view |
| `DELETE`| `/api/analytics/datasets/{id}/` | Delete dataset and all associated transaction records |

### Analytics & Reports (`/api/analytics/`)
| Method | Endpoint | Query Parameters | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/analytics/dashboard/` | `dataset_id`, `start_date`, `end_date`, `category`, `region`, `search` | Core KPI metrics, trends, category, and regional data |
| `GET` | `/api/analytics/insights/` | `dataset_id`, `start_date`, `end_date`, `category`, `region` | Automated executive narrative, highlights, and risks |
| `GET` | `/api/analytics/data-table/`| `page`, `page_size`, `ordering`, `category`, `region`, `search` | Paginated cleaned records table |
| `GET` | `/api/analytics/export/csv/` | *(Filter parameters)* | Download filtered dataset as CSV |
| `GET` | `/api/analytics/export/excel/`| *(Filter parameters)* | Download formatted multi-sheet Excel report |
| `GET` | `/api/analytics/export/pdf/` | *(Filter parameters)* | Download executive brief PDF report |
| `GET` | `/api/analytics/sample-template/`| None | Download blank/sample CSV template |

---

## 🧪 Automated Testing Suite

The project includes an end-to-end automated unit and integration test suite ([analytics/tests.py](file:///d:/saas%20project/analytics/tests.py)).

To run all tests:
```powershell
python manage.py test
```

### Tests Covered:
- `test_demo_login_flow`: Tests instant demo account creation and token generation.
- `test_load_sample_dataset`: Verifies 1,200-row demo dataset generation and database bulk insertion.
- `test_dashboard_analytics_kpis_and_charts`: Verifies all financial KPIs (Revenue, Profit, Orders, AOV) and chart series calculations.
- `test_dashboard_filters`: Verifies dynamic category and regional filtering.
- `test_smart_ai_insights`: Verifies narrative synthesis, highlight badges, and recommendations generation.
- `test_csv_upload_and_cleaning`: Tests multipart CSV file upload, Pandas cleaning, column mapping, and validation score.
- `test_export_endpoints`: Tests CSV stream, Excel (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`), and PDF (`application/pdf`) generation.

**All 7 tests pass with 100% success.**

---

## ❓ Troubleshooting & FAQs

#### Q1: "CSRF Failed: CSRF token missing or incorrect" error aa raha hai?
**Solution**: Humne `CsrfExemptSessionAuthentication` implement kar diya hai jo Token-based API calls ke liye session cookie CSRF conflicts ko eliminate karta hai, aur homepage par `@ensure_csrf_cookie` set kiya hai. Agar purana browser session cached ho, toh page ko **`Ctrl + F5`** se refresh karein.

#### Q2: Main custom CSV upload karta hoon lekin columns match nahi ho rahe?
**Solution**: Cleaner engine me fuzzy matching built-in hai. Agar aapke CSV me columns `Date`, `Sales`, `Profit`, `Category`, `Region` naam se hain, toh cleaner unhe automatically detect kar lega. Ek baar UI me **"Download Sample CSV Template"** button dabakar sample column structure dekh sakte hain.

#### Q3: Admin panel me login kaise karein?
**Solution**: Navigate to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) with:
- Username: `admin`
- Password: `admin123`

#### Q4: Plotly mode me charts kaise switch karein?
**Solution**: Top navigation bar me **"Engine: Chart.js"** button par click karein. Yeh instantly Plotly visualizer mode me toggle ho jayega.

---

## 📜 License & Credits

- Developed for **SaaS Business Analytics Platform**.
- Built with **Django REST Framework**, **PostgreSQL**, **Pandas**, **Chart.js**, **Plotly**, and **Tailwind CSS**.
- © 2026 SaaS Business Analytics Platform. All rights reserved.

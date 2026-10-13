# 🛒 ShopAI — E-Commerce Recommendation System
> **MCA Final Year Capstone Project**  
> Full-Stack E-Commerce Platform with Real-Time Machine Learning Recommendation Engine

---

## 📌 Executive Summary

**ShopAI** is a production-grade full-stack e-commerce web application powered by **Python, Django, Scikit-Learn, Pandas, NumPy, Bootstrap 5, and Chart.js**. Beyond standard catalog browsing and checkout, the system features a **Real-Time Hybrid Recommendation Engine** combining:

1. **Content-Based Filtering**: TF-IDF vectorization with Cosine Similarity across categories, brands, specifications, and descriptions.
2. **Collaborative Filtering**: User-Item interaction matrix factorization based on customer interaction telemetry (Views, Clicks, Wishlist, Cart additions, Purchases, and Ratings).
3. **Adaptive Hybrid Scoring Model**: Dynamic multi-factor weighting ($40\%$ Content Similarity, $30\%$ User Category/Brand Affinity, $20\%$ Collaborative co-occurrence, and $10\%$ Global popularity/ratings) with **transparent explanations** ("*Recommended because you viewed...*").
4. **Cold-Start Handler**: Zero-latency fallback for new users and guest shoppers using velocity trending items and declared category preferences.
5. **Business & ML Analytics Dashboard**: Interactive Chart.js visualizations for revenue timelines, category distribution, user telemetry, and conversion funnels, plus on-demand model retraining.
6. **Automated PDF Invoice Generation**: Commercial-grade tax invoices generated dynamically via ReportLab.
7. **Cross-Platform Intelligence & Price Comparison**: Live product comparisons and recommendations across **Amazon**, **Flipkart**, **Croma**, **Reliance Digital**, **Myntra**, and **Tata CLiQ** with similarity matching, price difference tracking, and direct deal links.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla CSS Design System, Bootstrap 5.3, Bootstrap Icons, JavaScript (AJAX) |
| **Backend** | Python 3.12, Django 6.0 |
| **Machine Learning** | Scikit-learn, Pandas, NumPy, Joblib |
| **Analytics & Charts** | Chart.js 4.4 |
| **PDF Reporting** | ReportLab 5.0 |
| **Database** | SQLite3 (Development) / PostgreSQL & MySQL ready |

---

## 📐 Machine Learning Architecture

```
                    ┌────────────────────────┐
                    │    User Interaction    │
                    │ Views, Carts, Orders   │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  UserActivity Telemetry│
                    │   Database Logging     │
                    └───────────┬────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           ▼                    ▼                    ▼
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│   Content-Based    │ │   Collaborative    │ │   User Affinity    │
│   TF-IDF + Cosine  │ │ Interaction Matrix │ │ Category Frequency │
└──────────┬─────────┘ └────────┬───────────┘ └─────────┬──────────┘
           │                    │                       │
           └────────────────────┼───────────────────────┘
                                ▼
                    ┌────────────────────────┐
                    │   Hybrid Scoring Model │
                    │ 0.40 C + 0.30 A +      │
                    │ 0.20 CF + 0.10 P       │
                    └───────────┬────────────┘
                                ▼
                    ┌────────────────────────┐
                    │ Transparent Explanation│
                    │ & Personalized Display │
                    └────────────────────────┘
```

### The Hybrid Mathematical Formula:
$$S_{\text{hybrid}}(u, i) = 0.40 \times S_{\text{content}}(i) + 0.30 \times S_{\text{affinity}}(u, c_i) + 0.20 \times S_{\text{collab}}(u, i) + 0.10 \times S_{\text{popularity}}(i)$$

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Make sure **Python 3.10+** is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Rich Catalog & Pre-Train ML Models
Run the automated seeder command to populate categories, brands, 20+ realistic products with images, demo users, user telemetry, and fit the ML models:
```bash
python manage.py seed_data
```

### 5. Launch the Application Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your web browser.

---

## 🔑 Demo & Evaluation Credentials

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Superuser / Staff** | `admin` | `admin123` | Full Django Admin & ML Analytics Dashboard access |
| **Customer User 1** | `vinay` | `user123` | Pre-trained Audiophile & Tech preference profile |
| **Customer User 2** | `priya` | `user123` | Pre-trained Fitness & Fashion preference profile |
| **Customer User 3** | `rahul` | `user123` | Pre-trained Computer enthusiast profile |

---

## 📁 Project Directory Structure

```text
ecommerce_recommendation_system/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── ecommerce/                   # Django Project Core
│   ├── settings.py              # Configuration & Context Processors
│   ├── urls.py                  # Master URL Router
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                    # User Authentication & Profiles
│   ├── models.py                # Profile Model & Signals
│   ├── forms.py                 # Registration & Profile Forms
│   ├── views.py                 # Login, Register, Profile Views
│   └── urls.py
│
├── products/                    # Catalog, Search, Filtering
│   ├── models.py                # Category, Brand, Product, ProductImage
│   ├── views.py                 # Home, Catalog, Detail Views
│   ├── urls.py
│   ├── admin.py
│   └── management/commands/
│       └── seed_data.py         # Realistic Catalog & Activity Generator
│
├── cart/                        # Shopping Bag & Session Management
│   ├── models.py                # Cart & CartItem Models
│   ├── views.py                 # AJAX Add, Update, Remove
│   ├── urls.py
│   └── context_processors.py    # Global Navbar Cart Count
│
├── orders/                      # Checkout, Orders, PDF Invoice
│   ├── models.py                # Order & OrderItem Models
│   ├── forms.py                 # Shipping & Payment Selection
│   ├── views.py                 # Checkout, Tracking, ReportLab PDF Invoice
│   └── urls.py
│
├── reviews/                     # Ratings & Customer Feedback
│   ├── models.py                # Review Model & Rating Aggregation
│   ├── forms.py                 # Review Submission Form
│   ├── views.py                 # Verified Buyer Reviews
│   └── urls.py
│
├── recommendations/             # ML Recommendation Engines
│   ├── models.py                # UserActivity & Wishlist Models
│   ├── content_based.py         # TF-IDF + Cosine Similarity Engine
│   ├── collaborative.py         # Interaction Matrix Co-occurrence Engine
│   ├── hybrid.py                # Multi-Factor Hybrid Ranking
│   ├── engine.py                # Unified Recommendation Facade
│   ├── views.py                 # Wishlist & ML Showcase Views
│   └── urls.py
│
├── dashboard/                   # Admin & ML Analytics
│   ├── analytics.py             # KPIs, Funnel, Chart.js Aggregations
│   ├── views.py                 # Dashboard View & Model Retrain
│   └── urls.py
│
├── static/                      # Static Assets
│   ├── css/style.css            # Custom CSS Design System
│   ├── js/main.js               # AJAX Wishlist, Cart & Toasts
│   └── images/placeholder.svg   # Vector Graphics
│
├── templates/                   # Semantic HTML Templates
│   ├── base.html                # Master Layout with Navigation
│   ├── products/                # home.html, product_list.html, product_detail.html
│   ├── cart/                    # cart_detail.html
│   ├── orders/                  # checkout.html, order_success.html, order_list.html, order_detail.html
│   ├── accounts/                # login.html, register.html, profile.html
│   ├── recommendations/         # wishlist.html, showcase.html
│   └── dashboard/               # dashboard.html (Chart.js)
│
├── ml_models/                   # Pickled ML Artifacts
│   ├── tfidf_vectorizer.pkl
│   ├── content_based_matrix.pkl
│   └── collaborative_matrix.pkl
│
└── datasets/                    # Exported Interaction CSV Datasets
    └── user_product_interactions.csv
```

---

## 🎯 Key MCA Viva Features to Highlight

1. **How does Content-Based Filtering work?**
   - Products are processed through `sklearn.feature_extraction.text.TfidfVectorizer(ngram_range=(1,2))` on combined metadata (Name, Category, Brand, Specifications, Description). Pairwise Cosine Similarity identifies matching attributes regardless of user purchase history.

2. **How does Collaborative Filtering work?**
   - Interaction weights are assigned per event: View ($1.0\times$), Click ($1.5\times$), Wishlist ($3.0\times$), Cart ($4.0\times$), Purchase ($6.0\times$). A User-Item matrix is constructed and Item-Item Cosine Similarity identifies co-occurrence patterns ("*Customers who bought this also bought...*").

3. **How does the system resolve the Cold-Start problem?**
   - Brand-new shoppers without interaction history receive popular and trending products filtered by their declared profile preferences. Once they click or view a single item, real-time activity logging immediately updates the candidate pool.

4. **Is the system real-time or batch?**
   - Every product view, cart add, and order immediately logs a `UserActivity` database row. The Hybrid Recommender dynamically queries the latest activity profile upon page render, providing instantaneous adaptation.

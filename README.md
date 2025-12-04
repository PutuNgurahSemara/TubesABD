# 📊 Dashboard Superstore - PostgreSQL Analytics

Dashboard interaktif untuk analisis data penjualan Superstore menggunakan PostgreSQL, Streamlit, dan Plotly.

## 🚀 Features

- 📉 **Loss Products Analysis** - Analisis produk dengan penjualan tinggi tapi rugi
- 🏪 **Seller Analytics** - Performa penjual berdasarkan sales dan rating
- 📅 **Yearly Sales** - Tren penjualan per tahun
- 📈 **YTD Comparison** - Perbandingan Year-to-Date vs tahun sebelumnya
- 🔵 **Profitability Analysis** - Scatter plot sales vs profit per sub-category
- 📊 **Interactive Visualizations** - Charts interaktif dengan Plotly

## 🛠️ Tech Stack

- **Database:** PostgreSQL
- **Backend:** Python 3.x
- **Frontend:** Streamlit
- **Visualization:** Plotly
- **Data Processing:** Pandas, psycopg2, SQLAlchemy

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Conda atau pip untuk package management

## 🔧 Installation

### 1. Clone repository
```bash
git clone https://github.com/yourusername/TubesABD.git
cd TubesABD
```

### 2. Install dependencies
```bash
# Menggunakan conda (recommended)
conda create -n superstore python=3.10
conda activate superstore
conda install pandas psycopg2 plotly streamlit sqlalchemy xlrd openpyxl -y

# Atau menggunakan pip
pip install -r requirement.txt
```

### 3. Setup Database

**Create PostgreSQL Database:**
```bash
psql -U postgres
CREATE DATABASE superstore;
\q
```

**Create Tables:**
```bash
psql -U postgres -d superstore -f create_tables.sql
```

**Import Data:**
```bash
python config.py
```

### 4. Configure Database Connection

Edit `config.py` dengan kredensial database Anda:
```python
conn = psycopg2.connect(
    dbname="superstore",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)
```

## 🚀 Running the Application

```bash
streamlit run app.py
```

Dashboard akan terbuka di browser pada `http://localhost:8501`

## 📁 Project Structure

```
TubesABD/
├── app.py                      # Main Streamlit application
├── config.py                   # Database connection & queries
├── create_tables.sql           # Database schema
├── add_sellers.py             # Script untuk generate seller data
├── optimize_indexes.sql        # Index optimization
├── Superstore.xls             # Source data (500 rows)
├── requirement.txt            # Python dependencies
├── INDEX_DOCUMENTATION.md     # Index documentation
└── README.md                  # This file
```

## 📊 Database Schema

### Tables:
1. **customers** - Customer information
2. **products** - Product catalog
3. **orders** - Order header
4. **order_details** - Order line items
5. **sellers** - Seller information

### Optimizations:
- 13 indexes untuk query performance
- Foreign key constraints
- Cached queries dengan Streamlit

## 📸 Screenshots

### Overview Dashboard
![Overview](screenshots/overview.png)

### Loss Products Analysis
![Loss Products](screenshots/loss-products.png)

### Seller Analytics
![Sellers](screenshots/sellers.png)

## 🔍 Features Detail

### 1. Loss Products Analysis
- Top 15 produk dengan quantity tinggi tapi profit negatif
- Stacked bar chart by category
- Summary metrics per kategori

### 2. Seller Analytics
- Top 10 sellers by total sales
- Rating vs Profit correlation
- Regional performance comparison

### 3. YTD Comparison
- Sales, Profit, Margin metrics
- Growth rate vs last year
- Visual comparison charts

### 4. Profitability Analysis
- Scatter plot: Sales vs Profit
- Bubble size: Sales volume
- Color: Profit/Loss indicator
- Break-even line visualization

## 🎯 Performance Optimization

- **Caching:** `@st.cache_data` untuk data loading
- **Indexes:** 13 optimized indexes (turun dari 21)
- **Query Optimization:** INNER JOIN dengan indexed columns
- **Lazy Loading:** Load data hanya saat dibutuhkan

## 📚 Documentation

- [Index Documentation](INDEX_DOCUMENTATION.md) - Detailed index strategy
- [Database Setup Guide](docs/database-setup.md) - Step-by-step setup
- [API Documentation](docs/api.md) - Config.py functions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Dataset: Superstore Sales Data
- Streamlit Community
- PostgreSQL Documentation
- Plotly Documentation

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/TubesABD](https://github.com/yourusername/TubesABD)

---

⭐ Star this repo if you find it helpful!

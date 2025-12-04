import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================
# CONFIGURATION
# ==============================
COLORS = {
    'Furniture': '#e67e22',
    'Office Supplies': '#27ae60',
    'Technology': '#2980b9',
    'Central': '#c0392b'
}

CATEGORIES = ['Furniture', 'Office Supplies', 'Technology']

# ==============================
# DATA LOADING FUNCTIONS
# ==============================
@st.cache_data
def load_data():
    """Load data from CSV file"""
    data = pd.read_csv('superstore_data.csv')
    data['order_date'] = pd.to_datetime(data['order_date'])
    data['ship_date'] = pd.to_datetime(data['ship_date'])
    data['year'] = data['order_date'].dt.year
    data['month'] = data['order_date'].dt.month
    return data

@st.cache_data
def get_high_qty_loss_products(top_n=15):
    """Get products dengan high quantity tapi negative profit"""
    df = load_data()
    
    # Filter: Produk dengan profit negatif
    loss_products = df[df['profit'] < 0].copy()
    
    # Agregasi per product dan category
    product_summary = loss_products.groupby(
        ['product_name', 'category'], 
        as_index=False
    ).agg({
        'quantity': 'sum',
        'profit': 'sum'
    })
    
    # Sort dan ambil top N
    return product_summary.nlargest(top_n, 'quantity')

@st.cache_data
def get_seller_stats(top_n=10):
    """Get seller statistics dan sort by sales"""
    df = load_data()
    
    seller_stats = df.groupby(
        ['seller_name', 'seller_region', 'seller_rating']
    ).agg({
        'sales': 'sum',
        'profit': 'sum',
        'order_id': 'count',
        'quantity': 'sum'
    }).reset_index()
    
    seller_stats.columns = [
        'Seller', 'Region', 'Rating', 
        'Total Sales', 'Total Profit', 'Total Orders', 'Total Quantity'
    ]
    
    return seller_stats.nlargest(top_n, 'Total Sales')

@st.cache_data
def get_yearly_comparison(df):
    """Calculate YTD metrics vs last year"""
    current_year = df['year'].max()
    last_year = current_year - 1
    current_month = df[df['year'] == current_year]['month'].max()
    
    # Filter YTD data
    ytd_current = df[
        (df['year'] == current_year) & 
        (df['month'] <= current_month)
    ]
    ytd_last = df[
        (df['year'] == last_year) & 
        (df['month'] <= current_month)
    ]
    
    # Calculate metrics
    metrics = {
        'current_year': current_year,
        'sales_current': ytd_current['sales'].sum(),
        'profit_current': ytd_current['profit'].sum(),
        'sales_last': ytd_last['sales'].sum(),
        'profit_last': ytd_last['profit'].sum()
    }
    
    # Calculate margins
    metrics['margin_current'] = (
        metrics['profit_current'] / metrics['sales_current'] * 100 
        if metrics['sales_current'] > 0 else 0
    )
    metrics['margin_last'] = (
        metrics['profit_last'] / metrics['sales_last'] * 100 
        if metrics['sales_last'] > 0 else 0
    )
    
    # Calculate growth
    metrics['sales_growth'] = (
        (metrics['sales_current'] - metrics['sales_last']) / metrics['sales_last'] * 100
        if metrics['sales_last'] > 0 else 0
    )
    metrics['profit_growth'] = (
        (metrics['profit_current'] - metrics['profit_last']) / metrics['profit_last'] * 100
        if metrics['profit_last'] > 0 else 0
    )
    metrics['margin_growth'] = metrics['margin_current'] - metrics['margin_last']
    
    return metrics

# ==============================
# CHART CREATION FUNCTIONS
# ==============================
def create_loss_products_chart(product_loss):
    """Create stacked bar chart untuk loss products"""
    fig = go.Figure()
    
    for cat in CATEGORIES:
        cat_data = product_loss[product_loss['category'] == cat]
        
        if not cat_data.empty:
            fig.add_trace(go.Bar(
                name=cat,
                x=cat_data['product_name'],
                y=cat_data['quantity'],
                marker=dict(
                    color=COLORS[cat], 
                    line=dict(color='white', width=2)
                ),
                text=cat_data['quantity'],
                textposition='inside',
                textfont=dict(size=12, color='white', family='Arial Black'),
                hovertemplate=(
                    '<b>%{x}</b><br>'
                    f'Category: {cat}<br>'
                    'Quantity: %{y}<br>'
                    'Loss: $%{customdata:,.2f}<br>'
                    '<extra></extra>'
                ),
                customdata=cat_data['profit']
            ))
    
    fig.update_layout(
        barmode='stack',
        title=dict(
            text='Products with High Quantity but Negative Profit<br><sub>Stacked by Category</sub>',
            font=dict(size=18, family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Product Name',
            title_font=dict(size=14, family='Arial Black'),
            tickfont=dict(size=10),
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            title='Total Quantity Sold',
            title_font=dict(size=14, family='Arial Black'),
            tickfont=dict(size=11),
            gridcolor='lightgray'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=12, family='Arial')
        ),
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=120, b=150, l=80, r=40),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(38,39,48,0.9)',
            font_size=12,
            font_family='Arial',
            font_color='white'
        )
    )
    
    return fig

def create_seller_sales_chart(seller_stats):
    """Create bar chart untuk top sellers"""
    fig = px.bar(
        seller_stats,
        x='Seller',
        y='Total Sales',
        color='Region',
        title='Top 10 Sellers by Total Sales',
        labels={'Total Sales': 'Total Sales ($)', 'Seller': 'Seller Name'},
        text='Total Sales',
        color_discrete_map=COLORS
    )
    
    fig.update_traces(
        texttemplate='$%{text:.2f}', 
        textposition='outside'
    )
    
    fig.update_layout(
        xaxis_title='Seller Name',
        yaxis_title='Total Sales ($)',
        showlegend=True,
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_seller_rating_chart(seller_stats):
    """Create scatter plot untuk seller rating vs profit"""
    fig = px.scatter(
        seller_stats,
        x='Rating',
        y='Total Profit',
        size='Total Orders',
        color='Region',
        hover_data=['Seller', 'Total Sales'],
        title='Correlation: Seller Rating vs Profit',
        labels={'Rating': 'Seller Rating', 'Total Profit': 'Total Profit ($)'},
        color_discrete_map=COLORS
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_yearly_sales_chart(df):
    """Create bar chart untuk yearly sales"""
    yearly_sales = df.groupby('year')['sales'].sum().reset_index()
    
    fig = px.bar(
        yearly_sales,
        x='year',
        y='sales',
        title='Total Penjualan per Tahun',
        labels={'year': 'Tahun', 'sales': 'Total Sales'},
        text='sales'
    )
    
    fig.update_traces(
        texttemplate='%{text:.2s}', 
        textposition='outside'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_ytd_comparison_chart(metrics):
    """Create comparison chart YTD vs Last Year"""
    chart_df = pd.DataFrame({
        "Metric": ["Sales", "Profit", "Margin %"],
        "Current Year": [
            metrics['sales_current'],
            metrics['profit_current'],
            metrics['margin_current']
        ],
        "Last Year": [
            metrics['sales_last'],
            metrics['profit_last'],
            metrics['margin_last']
        ]
    })
    
    fig = px.bar(
        chart_df,
        x="Metric",
        y=["Current Year", "Last Year"],
        barmode="group",
        title="📊 Comparison: YTD vs Last Year"
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# ==============================
# UI COMPONENTS
# ==============================
def display_loss_products_section(product_loss):
    """Display section untuk loss products"""
    st.subheader("📉 Top 15 Products: High Quantity Sold but Loss")
    st.markdown("*Products dengan penjualan tinggi tetapi mengalami kerugian, dikelompokkan per kategori*")
    
    # Chart
    fig = create_loss_products_chart(product_loss)
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
    })
    
    # Detail table
    with st.expander("📋 View Detailed Data"):
        detail_df = product_loss[['product_name', 'category', 'quantity', 'profit']].copy()
        detail_df.columns = ['Product Name', 'Category', 'Quantity', 'Loss (Profit)']
        detail_df['Loss (Profit)'] = detail_df['Loss (Profit)'].apply(lambda x: f'${x:,.2f}')
        st.dataframe(detail_df, use_container_width=True, hide_index=True)
    
    # Summary metrics
    st.markdown("---")
    st.subheader("📊 Summary by Category")
    col1, col2, col3 = st.columns(3)
    
    for idx, cat in enumerate(CATEGORIES):
        cat_summary = product_loss[product_loss['category'] == cat]
        with [col1, col2, col3][idx]:
            st.metric(
                label=cat,
                value=f"{cat_summary['quantity'].sum():,} units",
                delta=f"Loss: ${cat_summary['profit'].sum():,.2f}",
                delta_color="inverse"
            )

def display_seller_analytics_section(seller_stats):
    """Display section untuk seller analytics"""
    st.markdown("---")
    st.subheader("🏪 Top 10 Sellers by Sales")
    
    # Bar chart
    fig_sellers = create_seller_sales_chart(seller_stats)
    st.plotly_chart(fig_sellers, use_container_width=True)
    
    # Performance table
    st.dataframe(seller_stats, use_container_width=True, hide_index=True)
    
    # Scatter plot
    st.subheader("⭐ Seller Rating vs Total Profit")
    fig_rating = create_seller_rating_chart(seller_stats)
    st.plotly_chart(fig_rating, use_container_width=True)

def display_overview_section(df):
    """Display section untuk data overview"""
    st.title("📊 Dashboard Superstore Analytics")
    st.write("Total Records:", len(df))
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"${df['sales'].sum():,.2f}")
    with col2:
        st.metric("Total Profit", f"${df['profit'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['order_id'].nunique():,}")
    with col4:
        st.metric("Avg Order Value", f"${df['sales'].mean():,.2f}")
    
    st.markdown("---")
    st.dataframe(df.head(20), use_container_width=True)

def display_yearly_sales_section(df):
    """Display section untuk yearly sales"""
    st.subheader("📅 Penjualan per Tahun")
    fig = create_yearly_sales_chart(df)
    st.plotly_chart(fig, use_container_width=True)

def display_ytd_comparison_section(df):
    """Display section untuk YTD comparison"""
    st.subheader("📈 Total Sales, Profit & Margin YTD vs Last Year")
    
    metrics = get_yearly_comparison(df)
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"Sales YTD {metrics['current_year']}",
            value=f"${metrics['sales_current']:,.2f}",
            delta=f"{metrics['sales_growth']:.2f}% vs LY"
        )
    
    with col2:
        st.metric(
            label=f"Profit YTD {metrics['current_year']}",
            value=f"${metrics['profit_current']:,.2f}",
            delta=f"{metrics['profit_growth']:.2f}% vs LY"
        )
    
    with col3:
        st.metric(
            label=f"Margin YTD {metrics['current_year']}",
            value=f"{metrics['margin_current']:.2f}%",
            delta=f"{metrics['margin_growth']:.2f} pts"
        )
    
    # Comparison chart
    fig = create_ytd_comparison_chart(metrics)
    st.plotly_chart(fig, use_container_width=True)

def display_profitability_analysis_section(df):
    """Display section untuk scatter plot sales vs profit"""
    st.markdown("---")
    st.subheader("🔵 Analisis Profitabilitas: Sales vs Profit")
    
    # Kelompokkan data berdasarkan Sub-Category
    scatter_data = df.groupby('sub_category')[['sales', 'profit']].sum().reset_index()
    
    # Buat Scatter Plot
    fig_scatter = px.scatter(
        scatter_data,
        x='sales',
        y='profit',
        text='sub_category',
        hover_name='sub_category',
        title='Total Penjualan vs Total Profit berdasarkan Sub-Category',
        labels={'sales': 'Total Sales', 'profit': 'Total Profit'},
        size='sales',
        color='profit',
        color_continuous_scale='RdYlGn'
    )
    
    # Pindahkan posisi text label
    fig_scatter.update_traces(textposition='top center')
    
    # Tambahkan garis horizontal di angka 0
    fig_scatter.add_hline(
        y=0, 
        line_dash="dash", 
        line_color="red", 
        annotation_text="Batas Impas (Break Even)"
    )
    
    # Transparent background
    fig_scatter.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)

# ==============================
# MAIN APPLICATION
# ==============================
def main():
    """Main application entry point"""
    
    # Set page config
    st.set_page_config(
        page_title="Dashboard Superstore",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar navigation
    st.sidebar.title("📊 Dashboard Navigation")
    st.sidebar.markdown("---")
    
    # Menu options
    menu_options = {
        "🏠 Overview": "overview",
        "📉 Loss Products Analysis": "loss_products",
        "🏪 Seller Analytics": "seller_analytics",
        "📅 Yearly Sales": "yearly_sales",
        "📈 YTD Comparison": "ytd_comparison",
        "🔵 Profitability Analysis": "profitability"
    }
    
    # Create radio buttons for menu selection
    selected_menu = st.sidebar.radio(
        "Select Analysis:",
        list(menu_options.keys()),
        index=0
    )
    
    # Get the selected page
    selected_page = menu_options[selected_menu]
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info(
        "📌 **Tip:** Pilih menu di atas untuk navigasi antar halaman analisis."
    )
    
    # Load data
    df = load_data()
    product_loss = get_high_qty_loss_products()
    seller_stats = get_seller_stats()
    
    # Display data info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.metric("Total Records", f"{len(df):,}")
    st.sidebar.metric("Date Range", f"{df['year'].min()} - {df['year'].max()}")
    
    # Display selected section
    if selected_page == "overview":
        display_overview_section(df)
    elif selected_page == "loss_products":
        display_loss_products_section(product_loss)
    elif selected_page == "seller_analytics":
        display_seller_analytics_section(seller_stats)
    elif selected_page == "yearly_sales":
        display_yearly_sales_section(df)
    elif selected_page == "ytd_comparison":
        display_ytd_comparison_section(df)
    elif selected_page == "profitability":
        display_profitability_analysis_section(df)

if __name__ == "__main__":
    main()

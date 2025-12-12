import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import (
    load_data as config_load_data,
    get_top_sellers,
    get_seller_performance,
    get_sales_by_category,
    get_profit_by_category,
    get_categories,
    get_subcategories,
    get_sellers,
    get_customers,
    get_products,
    get_orders,
    get_order_details,
    get_order_invoice,  
    search_orders,
    get_rfm_analysis,
    get_rfm_segment_summary  
)

# ==============================
# CONFIGURATION
# ==============================
COLORS = {
    'Furniture': '#e67e22',
    'Office Supplies': '#27ae60',
    'Technology': '#2980b9',
    'Central': '#c0392b',
    'East': '#3498db',
    'West': '#9b59b6',
    'South': '#e74c3c'
}

CATEGORIES = ['Furniture', 'Office Supplies', 'Technology']

# ==============================
# DATA LOADING FUNCTIONS
# ==============================
@st.cache_data
def load_data():
    """Load all data from database menggunakan config.py"""
    data = config_load_data()
    data['order_date'] = pd.to_datetime(data['order_date'])
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
    """Get seller statistics dari database (optimized query)"""
    seller_data = get_top_sellers(limit=top_n)
    
    # Rename columns untuk konsistensi dengan UI
    seller_data.columns = [
        'Seller', 'Region', 'Rating', 
        'Total Orders', 'Total Quantity', 'Total Sales', 'Total Profit', 'Avg Profit'
    ]
    
    # Reorder columns
    return seller_data[['Seller', 'Region', 'Rating', 'Total Sales', 'Total Profit', 'Total Orders', 'Total Quantity']]

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
        texttemplate='$%{text:.2s}', 
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
        texttemplate='$%{text:.2s}', 
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

def display_all_tables_section():
    """Display section untuk all database tables"""
    st.title("📚 All Database Tables")
    st.markdown("*Viewing all normalized tables from the database*")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📦 Customers",
        "📋 Subcategories",
        "🏪 Sellers",
        "👥 Categories",
        "📦 Products",
        "📝 Orders",
        "📊 Order Details"
    ])

    with tab1:
        st.subheader("Customers Table")
        customers_df = get_customers()
        st.dataframe(customers_df, use_container_width=True, hide_index=True)
        st.info(f"Total Customers: {len(customers_df)}")
       
    with tab2:
        st.subheader("Subcategories Table")
        subcategories_df = get_subcategories()
        st.dataframe(subcategories_df, use_container_width=True, hide_index=True)
        st.info(f"Total Subcategories: {len(subcategories_df)}")

    with tab3:
        st.subheader("Sellers Table")
        sellers_df = get_sellers()
        st.dataframe(sellers_df, use_container_width=True, hide_index=True)
        st.info(f"Total Sellers: {len(sellers_df)}")

    with tab4:
        st.subheader("Categories Table")
        categories_df = get_categories()
        st.dataframe(categories_df, use_container_width=True, hide_index=True)
        st.info(f"Total Categories: {len(categories_df)}")


    with tab5:
        st.subheader("Products Table")
        products_df = get_products()
        st.dataframe(products_df, use_container_width=True, hide_index=True)
        st.info(f"Total Products: {len(products_df)}")

    with tab6:
        st.subheader("Orders Table")
        orders_df = get_orders()
        st.dataframe(orders_df, use_container_width=True, hide_index=True)
        st.info(f"Total Orders: {len(orders_df)}")

    with tab7:
        st.subheader("Order Details Table")
        order_details_df = get_order_details()
        st.dataframe(order_details_df, use_container_width=True, hide_index=True)
        st.info(f"Total Order Details: {len(order_details_df)}")

def display_invoice_section():
    """Display section untuk invoice/nota search & detail"""
    st.title("📜 Invoice / Nota Detail View")
    st.markdown("*Search and view detailed invoice information*")
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            "🔍 Search by Order ID or Customer Name:",
            placeholder="e.g., CA-2017-152156 or Sean Miller",
            help="Search akan mencari di Order ID dan Customer Name"
        )
    
    with col2:
        search_button = st.button("🔎 Search", type="primary", use_container_width=True)
    
    # Show results if search
    if search_button or search_term:
        with st.spinner("Searching orders..."):
            search_results = search_orders(search_term)
        
        if len(search_results) > 0:
            st.success(f"Found {len(search_results)} order(s)")
            
            # Display search results
            st.subheader("Search Results:")
            
            # Format dataframe
            display_results = search_results.copy()
            display_results['order_date'] = pd.to_datetime(display_results['order_date']).dt.strftime('%Y-%m-%d')
            display_results['total_sales'] = display_results['total_sales'].apply(lambda x: f'${x:,.2f}')
            display_results['total_profit'] = display_results['total_profit'].apply(lambda x: f'${x:,.2f}')
            
            st.dataframe(
                display_results,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "order_id": "Order ID",
                    "order_date": "Order Date",
                    "customer_name": "Customer",
                    "city": "City",
                    "state": "State",
                    "total_items": st.column_config.NumberColumn("Items", format="%d"),
                    "total_sales": "Total Sales",
                    "total_profit": "Total Profit"
                }
            )
            
            # Select order untuk detail
            st.markdown("---")
            selected_order = st.selectbox(
                "Select Order ID to view detailed invoice:",
                options=search_results['order_id'].tolist()
            )
            
            if selected_order:
                display_invoice_detail(selected_order)
        else:
            st.warning("No orders found. Try different search term.")
    else:
        st.info("👆 Enter Order ID or Customer Name to search")


def display_invoice_detail(order_id):
    """Display detailed invoice for selected order"""
    st.markdown("---")
    st.subheader(f"📋 Invoice Detail: {order_id}")
    
    # Get invoice data
    invoice_data = get_order_invoice(order_id)
    
    if len(invoice_data) == 0:
        st.error("Order not found!")
        return
    
    # Header Info (ambil baris pertama karena info customer sama)
    header = invoice_data.iloc[0]
    
    # === CUSTOMER INFO ===
    st.markdown("### 👤 Customer Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Customer:** {header['customer_name']}")
        st.markdown(f"**Customer ID:** {header['customer_id']}")
        st.markdown(f"**Segment:** {header['segment']}")
    
    with col2:
        st.markdown(f"**City:** {header['city']}")
        st.markdown(f"**State:** {header['state']}")
        st.markdown(f"**Region:** {header['region']}")
    
    with col3:
        st.markdown(f"**Order Date:** {header['order_date']}")
        st.markdown(f"**Ship Date:** {header['ship_date']}")
        st.markdown(f"**Ship Mode:** {header['ship_mode']}")
    
    st.markdown("---")
    
    # === PRODUCTS TABLE ===
    st.markdown("### 📦 Products Ordered")
    
    products_df = invoice_data[[
        'product_name', 'category_name', 'subcategory_name', 
        'seller_name', 'quantity', 'sales', 'discount', 'profit'
    ]].copy()
    
    # Format columns
    products_df['sales'] = products_df['sales'].apply(lambda x: f'${x:,.2f}')
    products_df['profit'] = products_df['profit'].apply(lambda x: f'${x:,.2f}')
    products_df['discount'] = products_df['discount'].apply(lambda x: f'{x*100:.0f}%')
    
    products_df.columns = [
        'Product Name', 'Category', 'Subcategory', 
        'Seller', 'Qty', 'Sales', 'Discount', 'Profit'
    ]
    
    st.dataframe(products_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # === SUMMARY ===
    st.markdown("### 💰 Invoice Summary")
    
    total_items = invoice_data['quantity'].sum()
    subtotal = invoice_data['sales'].sum()
    total_discount = (invoice_data['discount'] * invoice_data['sales']).sum()
    total_profit = invoice_data['profit'].sum()
    profit_margin = (total_profit / subtotal * 100) if subtotal > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Items", f"{total_items:,.0f}")
    
    with col2:
        st.metric("Subtotal", f"${subtotal:,.2f}")
    
    with col3:
        st.metric("Total Discount", f"${total_discount:,.2f}")
    
    with col4:
        st.metric("Total Profit", f"${total_profit:,.2f}")
    
    with col5:
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    # Download button (optional)
    st.markdown("---")
    csv = invoice_data.to_csv(index=False)
    st.download_button(
        label="📥 Download Invoice CSV",
        data=csv,
        file_name=f"invoice_{order_id}.csv",
        mime="text/csv"
    )

@st.cache_data
def load_rfm_data():
    """Load RFM analysis data"""
    return get_rfm_analysis()

@st.cache_data
def load_rfm_summary():
    """Load RFM segment summary"""
    return get_rfm_segment_summary()


def display_rfm_analysis_section():
    """Display RFM Analysis section"""
    st.title("🎯 RFM Analysis - Customer Segmentation")
    st.markdown("*Recency, Frequency, Monetary Analysis untuk segmentasi customer*")
    
    # Load data
    with st.spinner("Loading RFM data..."):
        rfm_data = load_rfm_data()
        rfm_summary = load_rfm_summary()
    
    # === OVERVIEW METRICS ===
    st.markdown("---")
    st.subheader("📊 RFM Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", f"{len(rfm_data):,}")
    
    with col2:
        avg_recency = rfm_data['recency_days'].mean()
        st.metric("Avg Recency", f"{avg_recency:.0f} days")
    
    with col3:
        avg_frequency = rfm_data['frequency'].mean()
        st.metric("Avg Frequency", f"{avg_frequency:.1f} orders")
    
    with col4:
        avg_monetary = rfm_data['monetary'].mean()
        st.metric("Avg Monetary", f"${avg_monetary:,.2f}")
    
    # === SEGMENT DISTRIBUTION ===
    st.markdown("---")
    st.subheader("🎨 Customer Segment Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        segment_counts = rfm_data['customer_segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        
        fig_pie = px.pie(
            segment_counts,
            values='Count',
            names='Segment',
            title='Customer Distribution by Segment',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart
        fig_bar = px.bar(
            segment_counts.sort_values('Count', ascending=False),
            x='Segment',
            y='Count',
            title='Customer Count by Segment',
            text='Count',
            color='Segment',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # === SEGMENT SUMMARY TABLE ===
    st.markdown("---")
    st.subheader("📋 Segment Summary Statistics")
    
    # Format summary table
    summary_display = rfm_summary.copy()
    summary_display['avg_monetary'] = summary_display['avg_monetary'].apply(lambda x: f'${x:,.2f}')
    summary_display['total_revenue'] = summary_display['total_revenue'].apply(lambda x: f'${x:,.2f}')
    summary_display.columns = ['Segment', 'Customers', 'Avg Recency (days)', 'Avg Frequency', 'Avg Monetary', 'Total Revenue']
    
    st.dataframe(summary_display, use_container_width=True, hide_index=True)
    
    # === RFM SCATTER PLOTS ===
    st.markdown("---")
    st.subheader("📈 RFM Scatter Analysis")
    
    tab1, tab2, tab3 = st.tabs(["💰 Monetary vs Frequency", "⏰ Recency vs Monetary", "🔄 Recency vs Frequency"])
    
    with tab1:
        fig_mf = px.scatter(
            rfm_data,
            x='frequency',
            y='monetary',
            color='customer_segment',
            size='rfm_score',
            hover_data=['customer_name', 'recency_days'],
            title='Monetary vs Frequency by Segment',
            labels={'frequency': 'Frequency (Orders)', 'monetary': 'Monetary (Sales)'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_mf.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        st.plotly_chart(fig_mf, use_container_width=True)
    
    with tab2:
        fig_rm = px.scatter(
            rfm_data,
            x='recency_days',
            y='monetary',
            color='customer_segment',
            size='rfm_score',
            hover_data=['customer_name', 'frequency'],
            title='Monetary vs Recency by Segment',
            labels={'recency_days': 'Recency (Days)', 'monetary': 'Monetary (Sales)'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_rm.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        st.plotly_chart(fig_rm, use_container_width=True)
    
    with tab3:
        fig_rf = px.scatter(
            rfm_data,
            x='recency_days',
            y='frequency',
            color='customer_segment',
            size='monetary',
            hover_data=['customer_name', 'monetary'],
            title='Frequency vs Recency by Segment',
            labels={'recency_days': 'Recency (Days)', 'frequency': 'Frequency (Orders)'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_rf.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        st.plotly_chart(fig_rf, use_container_width=True)
    
    # === SEGMENT FILTER & DETAIL ===
    st.markdown("---")
    st.subheader("🔍 Filter by Segment")
    
    selected_segment = st.selectbox(
        "Select Customer Segment:",
        options=['All'] + sorted(rfm_data['customer_segment'].unique().tolist())
    )
    
    if selected_segment == 'All':
        filtered_data = rfm_data
    else:
        filtered_data = rfm_data[rfm_data['customer_segment'] == selected_segment]
    
    st.info(f"Showing {len(filtered_data)} customers")
    
    # Format display
    display_data = filtered_data[[
        'customer_name', 'segment', 'region', 'customer_segment',
        'recency_days', 'frequency', 'monetary', 'rfm_score'
    ]].copy()
    
    display_data['monetary'] = display_data['monetary'].apply(lambda x: f'${x:,.2f}')
    display_data.columns = [
        'Customer Name', 'Business Segment', 'Region', 'RFM Segment',
        'Recency (days)', 'Frequency', 'Monetary', 'RFM Score'
    ]
    
    st.dataframe(
        display_data.sort_values('RFM Score', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    st.markdown("---")
    csv = rfm_data.to_csv(index=False)
    st.download_button(
        label="📥 Download Full RFM Analysis CSV",
        data=csv,
        file_name="rfm_analysis.csv",
        mime="text/csv"
    )
    
    # === SEGMENT EXPLANATION ===
    with st.expander("ℹ️ RFM Segment Explanation"):
        st.markdown("""
        ### Customer Segment Definitions:
        
        - **Champions** 🏆: Best customers - bought recently, buy often, and spend the most
        - **Loyal Customers** 💎: Consistent customers with good engagement
        - **Big Spenders** 💰: High monetary value customers
        - **Potential Loyalists** 🌟: Recent customers with good spending, may become loyal
        - **New Customers** 🆕: Recent buyers, need nurturing
        - **At Risk** ⚠️: Used to be good customers, haven't bought recently
        - **Lost Customers** 😢: Haven't bought in a long time, need win-back campaigns
        - **Regular Customers** 👥: Average engagement across all metrics
        
        ### RFM Scores:
        - **R (Recency)**: How recently did they purchase? (1-5, 5 = most recent)
        - **F (Frequency)**: How often do they purchase? (1-5, 5 = most frequent)
        - **M (Monetary)**: How much do they spend? (1-5, 5 = highest spender)
        """)

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
        "📚 All Tables": "all_tables",
        "📜 Invoice Detail": "invoice",
        "🎯 RFM Analysis": "rfm",
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
    if selected_page == "loss_products":
        display_loss_products_section(product_loss)
    elif selected_page == "seller_analytics":
        display_seller_analytics_section(seller_stats)
    elif selected_page == "yearly_sales":
        display_yearly_sales_section(df)
    elif selected_page == "ytd_comparison":
        display_ytd_comparison_section(df)
    elif selected_page == "profitability":
        display_profitability_analysis_section(df)
    elif selected_page == "all_tables":
        display_all_tables_section()
    elif selected_page == "invoice":
        display_invoice_section()
    elif selected_page == "rfm":
        display_rfm_analysis_section()

if __name__ == "__main__":
    main()

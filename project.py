
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ELECTROMART",
    page_icon="",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #022c22, #065f46, #134e4a);
    color: white;
}
h1, h2, h3, p, label {
    color: white !important;
}
/* TITLE FONT STYLE */
.dashboard-title {
    font-family: Verdana, sans-serif;
    font-size: 46px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #38bdf8;
    text-shadow: 0 0 15px rgba(56, 189, 248, 0.35);
    margin-bottom: 5px;
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
}
div[data-testid="stMetricValue"] {
    color: #38bdf8;
}
section[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv("Sales_transactions_2022_2025.csv")
    data["Order_Date"] = pd.to_datetime(
        data["Order_Date"], errors="coerce"
    )
    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "CSV file not found. Place "
        "Sales_transactions_2022_2025.csv "
        "in the same folder as app.py."
    )
    st.stop()

# Convert numeric columns safely
for col in [
    "Sales_Amount", "Profit", "Quantity",
    "Cost_Amount", "Customer_Rating",
    "Discount_Percentage"
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------- TITLE ----------------
# ---------------- CENTERED ELECTRO MART LOGO & TITLE ----------------

logo_left, logo_center, logo_right = st.columns([1, 2, 1])

with logo_center:
    st.image("Electro Mart Energy Logo.png", width=420)

st.markdown(
    """
        <h1 class="dashboard-title"></h1>
        <p class="dashboard-subtitle">
            
        </p>
        """,
    unsafe_allow_html=True
)

st.caption("Sales performance analysis | 2022–2025")
st.divider()

# ---------------- TOP FILTER PANEL ----------------
st.markdown("### 🎛️ Sales Filters")

with st.container(border=True):
    f1, f2, f3 = st.columns(3)

    years = sorted(df["Order_Year"].dropna().unique())
    regions = sorted(df["Region"].dropna().unique())
    categories = sorted(df["Product_Category"].dropna().unique())

    with f1:
        selected_years = st.multiselect(
            "📅 Select Year",
            options=years,
            default=years,
            key="filter_year"
        )

    with f2:
        selected_regions = st.multiselect(
            "🌍 Select Region",
            options=regions,
            default=regions,
            key="filter_region"
        )

    with f3:
        selected_categories = st.multiselect(
            "📦 Product Category",
            options=categories,
            default=categories,
            key="filter_category"
        )

# ---------------- APPLY FILTERS ----------------
filtered = df[
    df["Order_Year"].isin(selected_years)
    & df["Region"].isin(selected_regions)
    & df["Product_Category"].isin(selected_categories)
].copy()

st.caption(f"Showing {len(filtered):,} transactions")
st.divider()


# ---------------- KPI CARD STYLING ----------------
st.markdown("""
<style>
/* Common KPI card design */
div[data-testid="stMetric"] {
    padding: 22px 18px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    transition: transform 0.25s ease;
    min-height: 125px;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
}

/* Gradient backgrounds */
div[data-testid="stHorizontalBlock"]:has(
    div[data-testid="stMetric"]
) > div:nth-child(1) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1d4ed8, #06b6d4);
}

div[data-testid="stHorizontalBlock"]:has(
    div[data-testid="stMetric"]
) > div:nth-child(2) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #047857, #34d399);
}

div[data-testid="stHorizontalBlock"]:has(
    div[data-testid="stMetric"]
) > div:nth-child(3) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #6d28d9, #c084fc);
}

div[data-testid="stHorizontalBlock"]:has(
    div[data-testid="stMetric"]
) > div:nth-child(4) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #c2410c, #fbbf24);
}

/* Text colours */
div[data-testid="stMetricLabel"],
div[data-testid="stMetricValue"],
div[data-testid="stMetricDelta"] {
    color: #ffffff !important;
}

div[data-testid="stMetricLabel"] {
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)


# ---------------- KPI CARDS ----------------
total_sales = filtered["Sales_Amount"].sum()
total_profit = filtered["Profit"].sum()
total_orders = filtered["Order_ID"].nunique()
avg_rating = filtered["Customer_Rating"].mean()
total_quantity = filtered["Quantity"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Total Sales", f"₹{total_sales:,.2f}")
c2.metric("📈 Total Profit", f"₹{total_profit:,.2f}")
c3.metric("🛒 Unique Orders", f"{total_orders:,}")
c4.metric(
    "⭐ Average Rating",
    f"{avg_rating:.2f}/5" if pd.notna(avg_rating) else "N/A"
)

st.divider()




# ---------------- GAUGE CHARTS ----------------
st.subheader("🎯 Performance Indicators")

g1, g2 = st.columns(2)

# Profit margin = total profit / total sales
profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

# Average customer rating, maximum 5
with g1:
    fig_rating = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(avg_rating) if pd.notna(avg_rating) else 0,
        title={"text": "Average Customer Rating"},
        gauge={
            "axis": {"range": [0, 5]},
            "bar": {"color": "#38bdf8"},
            "steps": [
                {"range": [0, 2.5], "color": "#334155"},
                {"range": [2.5, 4], "color": "#475569"},
                {"range": [4, 5], "color": "#166534"}
            ]
        }
    ))
    fig_rating.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_rating, use_container_width=True)

with g2:
    fig_margin = go.Figure(go.Indicator(
        mode="gauge+number",
        value=profit_margin,
        title={"text": "Profit Margin (%)"},
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#fb923c"}
        }
    ))
    fig_margin.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_margin, use_container_width=True)
# ---------------- MONTHLY SALES TREND ----------------
st.subheader("📈 Monthly Sales Trend")

monthly = (
    filtered.dropna(subset=["Order_Date"])
    .groupby(pd.Grouper(key="Order_Date", freq="MS"))["Sales_Amount"]
    .sum()
    .reset_index()
)

if not monthly.empty:
    fig_line = px.line(
        monthly,
        x="Order_Date",
        y="Sales_Amount",
        markers=True,
        title="Monthly Sales Performance",
        labels={
            "Order_Date": "Month",
            "Sales_Amount": "Sales Amount"
        },
        template="plotly_dark"
    )
    fig_line.update_traces(
        line=dict(color="#38bdf8", width=3)
    )
    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ---------------- CATEGORY & REGION ----------------
left, right = st.columns(2)

with left:
    st.subheader("📦 Sales by Product Category")

    category_sales = (
        filtered.groupby("Product_Category", as_index=False)
        ["Sales_Amount"].sum()
        .sort_values("Sales_Amount", ascending=False)
    )

    fig_bar = px.bar(
        category_sales,
        x="Product_Category",
        y="Sales_Amount",
        color="Product_Category",
        text_auto=".2s",
        title="Category-wise Sales",
        template="plotly_dark"
    )
    fig_bar.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    st.subheader("🌍 Sales by Region")

    region_sales = (
        filtered.groupby("Region", as_index=False)
        ["Sales_Amount"].sum()
        .sort_values("Sales_Amount", ascending=False)
    )

    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Sales_Amount",
        color="Region",
        text_auto=".2s",
        title="Regional Sales Comparison",
        template="plotly_dark"
    )
    fig_region.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_region, use_container_width=True)

# ---------------- PROFIT ANALYSIS ----------------
left, right = st.columns(2)

with left:
    st.subheader("💹 Profit by Category")

    profit_category = (
        filtered.groupby("Product_Category", as_index=False)
        ["Profit"].sum()
        .sort_values("Profit", ascending=False)
    )

    fig_profit = px.bar(
        profit_category,
        x="Product_Category",
        y="Profit",
        color="Profit",
        title="Category-wise Profit",
        template="plotly_dark"
    )
    fig_profit.update_layout(
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_profit, use_container_width=True)

with right:
    st.subheader("💳 Payment Methods")

    payment = filtered["Payment_Method"].value_counts().reset_index()
    payment.columns = ["Payment_Method", "Transactions"]

    fig_pie = px.pie(
        payment,
        names="Payment_Method",
        values="Transactions",
        hole=0.45,
        title="Transactions by Payment Method",
        template="plotly_dark"
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ---------------- ORDER STATUS ----------------
st.subheader("📋 Order Status Analysis")

status_data = (
    filtered["Order_Status"]
    .value_counts()
    .rename_axis("Order_Status")
    .reset_index(name="Transactions")
)

fig_status = px.bar(
    status_data,
    x="Order_Status",
    y="Transactions",
    color="Order_Status",
    text_auto=True,
    title="Transactions by Order Status",
    template="plotly_dark"
)
fig_status.update_layout(
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig_status, use_container_width=True)



# ---------------- TOP PRODUCTS ----------------
st.subheader("🏆 Top 10 Products by Sales")

top_products = (
    filtered.groupby("Product_Name", as_index=False)
    ["Sales_Amount"].sum()
    .sort_values("Sales_Amount", ascending=False)
    .head(10)
)

fig_products = px.bar(
    top_products.sort_values("Sales_Amount"),
    x="Sales_Amount",
    y="Product_Name",
    orientation="h",
    title="Top Products",
    text_auto=".2s",
    template="plotly_dark"
)
fig_products.update_layout(
    paper_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig_products, use_container_width=True)

# ---------------- DATA TABLE ----------------
st.subheader("🧾 Transaction Details")

search = st.text_input(
    "Search by Product Name, Order ID, or Customer ID"
)

table_data = filtered.copy()

if search.strip():
    mask = (
        table_data["Product_Name"].astype(str).str.contains(
            search, case=False, na=False
        )
        | table_data["Order_ID"].astype(str).str.contains(
            search, case=False, na=False
        )
        | table_data["Customer_ID"].astype(str).str.contains(
            search, case=False, na=False
        )
    )
    table_data = table_data[mask]

st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True
)

csv_data = table_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Transactions",
    data=csv_data,
    file_name="filtered_sales_transactions.csv",
    mime="text/csv"
)

st.caption("Sales Transactions Dashboard | Built with Python and Streamlit")



import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ELECTROMART",
    page_icon="🛒",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg, #022c22, #065f46, #134e4a
    );
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

.dashboard-title {
    font-family: Verdana, sans-serif;
    font-size: 46px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #38bdf8;
    text-align: center;
}

.dashboard-subtitle {
    text-align: center;
    color: #d1fae5 !important;
    font-size: 16px;
}

div[data-testid="stMetric"] {
    padding: 22px 18px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    min-height: 125px;
    background: rgba(255,255,255,0.08);
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricValue"],
div[data-testid="stMetricDelta"] {
    color: #ffffff !important;
}

div[data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 800;
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
    data.columns = data.columns.str.strip()

    # Convert order date
    if "Order_Date" in data.columns:
        data["Order_Date"] = pd.to_datetime(
            data["Order_Date"], errors="coerce"
        )

    # Standardize text columns to remove duplicate-looking values
    text_columns = [
        "Product_Category",
        "Payment_Method",
        "Region",
        "Order_Status",
        "Product_Name"
    ]

    for col in text_columns:
        if col in data.columns:
            values = data[col].astype("string").str.strip()
            values = values.str.replace(
                r"\s+", " ", regex=True
            )
            values = values.str.casefold().str.title()
            data[col] = values

    # Restore common payment method capitalization
    if "Payment_Method" in data.columns:
        data["Payment_Method"] = data["Payment_Method"].replace({
            "Upi": "UPI",
            "Paypal": "PayPal"
        })

    # Create Order_Year if missing
    if (
        "Order_Year" not in data.columns
        and "Order_Date" in data.columns
    ):
        data["Order_Year"] = data["Order_Date"].dt.year

    return data


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "CSV file not found. Please keep "
        "Sales_transactions_2022_2025.csv "
        "in the same folder as project.py."
    )
    st.stop()

except Exception as e:
    st.error(f"Could not load CSV file: {e}")
    st.stop()


# ---------------- NUMERIC CONVERSION ----------------
numeric_columns = [
    "Sales_Amount",
    "Profit",
    "Quantity",
    "Cost_Amount",
    "Customer_Rating",
    "Discount_Percentage"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )


# ---------------- VALIDATE DATA ----------------
required_columns = [
    "Order_Year",
    "Region",
    "Product_Category"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "Missing required CSV columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ---------------- CENTERED LOGO ----------------
logo_left, logo_center, logo_right = st.columns([1, 2, 1])

with logo_center:
    try:
        st.image(
            "Electro Mart Energy Logo.png",
            use_container_width=True
        )
    except Exception:
        st.markdown(
            '<h1 class="dashboard-title">ELECTROMART</h1>',
            unsafe_allow_html=True
        )

st.markdown(
    '<p class="dashboard-subtitle">'
    'Sales Performance Analysis | 2022–2025'
    '</p>',
    unsafe_allow_html=True
)

st.divider()


# ---------------- FILTERS ----------------
st.markdown("### 🎛️ Sales Filters")

with st.container(border=True):
    f1, f2, f3 = st.columns(3)

    years = sorted(
        df["Order_Year"].dropna().unique().tolist()
    )

    regions = sorted(
        df["Region"].dropna().astype(str).unique().tolist()
    )

    categories = sorted(
        df["Product_Category"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with f1:
        selected_years = st.multiselect(
            "📅 Select Year",
            options=years,
            default=years
        )

    with f2:
        selected_regions = st.multiselect(
            "🌍 Select Region",
            options=regions,
            default=regions
        )

    with f3:
        selected_categories = st.multiselect(
            "📦 Product Category",
            options=categories,
            default=categories
        )


# ---------------- APPLY FILTERS ----------------
filtered = df[
    df["Order_Year"].isin(selected_years)
    & df["Region"].isin(selected_regions)
    & df["Product_Category"].isin(selected_categories)
].copy()

st.caption(f"Showing {len(filtered):,} transactions")
st.divider()


# ---------------- KPI CARDS ----------------
total_sales = (
    filtered["Sales_Amount"].sum()
    if "Sales_Amount" in filtered.columns else 0
)

total_profit = (
    filtered["Profit"].sum()
    if "Profit" in filtered.columns else 0
)

total_orders = (
    filtered["Order_ID"].nunique()
    if "Order_ID" in filtered.columns else 0
)

avg_rating = (
    filtered["Customer_Rating"].mean()
    if "Customer_Rating" in filtered.columns else float("nan")
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Total Sales", f"₹{total_sales:,.2f}")
c2.metric("📈 Total Profit", f"₹{total_profit:,.2f}")
c3.metric("🛒 Unique Orders", f"{total_orders:,}")

c4.metric(
    "⭐ Average Rating",
    f"{avg_rating:.2f}/5"
    if pd.notna(avg_rating) else "N/A"
)

st.divider()


# ---------------- PERFORMANCE INDICATORS ----------------
st.subheader("🎯 Performance Indicators")

g1, g2 = st.columns(2)

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

with g1:
    fig_rating = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=(
                float(avg_rating)
                if pd.notna(avg_rating) else 0
            ),
            title={"text": "Average Customer Rating"},
            gauge={
                "axis": {"range": [0, 5]},
                "bar": {"color": "#38bdf8"},
                "steps": [
                    {
                        "range": [0, 2.5],
                        "color": "#334155"
                    },
                    {
                        "range": [2.5, 4],
                        "color": "#475569"
                    },
                    {
                        "range": [4, 5],
                        "color": "#166534"
                    }
                ]
            }
        )
    )

    fig_rating.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_rating, use_container_width=True
    )


with g2:
    fig_margin = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=profit_margin,
            title={"text": "Profit Margin (%)"},
            number={"suffix": "%"},
            gauge={
                "axis": {
                    "range": [0, max(100, profit_margin)]
                },
                "bar": {"color": "#fb923c"}
            }
        )
    )

    fig_margin.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_margin, use_container_width=True
    )


# ---------------- MONTHLY SALES TREND ----------------
st.subheader("📈 Monthly Sales Trend")

if (
    "Order_Date" in filtered.columns
    and "Sales_Amount" in filtered.columns
):
    monthly = (
        filtered.dropna(subset=["Order_Date"])
        .groupby(
            pd.Grouper(key="Order_Date", freq="MS")
        )["Sales_Amount"]
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

        st.plotly_chart(
            fig_line, use_container_width=True
        )
    else:
        st.info("No valid order dates for these filters.")


# ---------------- CATEGORY AND REGION ----------------
left, right = st.columns(2)

with left:
    st.subheader("📦 Sales by Product Category")

    if "Sales_Amount" in filtered.columns:
        category_sales = (
            filtered.groupby(
                "Product_Category", as_index=False
            )["Sales_Amount"]
            .sum()
            .sort_values(
                "Sales_Amount", ascending=False
            )
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

        st.plotly_chart(
            fig_bar, use_container_width=True
        )


with right:
    st.subheader("🌍 Sales by Region")

    if "Sales_Amount" in filtered.columns:
        region_sales = (
            filtered.groupby(
                "Region", as_index=False
            )["Sales_Amount"]
            .sum()
            .sort_values(
                "Sales_Amount", ascending=False
            )
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

        st.plotly_chart(
            fig_region, use_container_width=True
        )


# ---------------- PROFIT AND PAYMENT ANALYSIS ----------------
left, right = st.columns(2)

with left:
    st.subheader("💹 Profit by Category")

    if "Profit" in filtered.columns:
        profit_category = (
            filtered.groupby(
                "Product_Category", as_index=False
            )["Profit"]
            .sum()
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

        st.plotly_chart(
            fig_profit, use_container_width=True
        )


with right:
    st.subheader("💳 Payment Methods")

    if "Payment_Method" in filtered.columns:
        payment = (
            filtered["Payment_Method"]
            .value_counts()
            .reset_index()
        )

        payment.columns = [
            "Payment_Method", "Transactions"
        ]

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

        st.plotly_chart(
            fig_pie, use_container_width=True
        )


# ---------------- ORDER STATUS ----------------
st.subheader("📋 Order Status Analysis")

if "Order_Status" in filtered.columns:
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

    st.plotly_chart(
        fig_status, use_container_width=True
    )


# ---------------- TOP PRODUCTS ----------------
st.subheader("🏆 Top 10 Products by Sales")

if (
    "Product_Name" in filtered.columns
    and "Sales_Amount" in filtered.columns
):
    top_products = (
        filtered.groupby(
            "Product_Name", as_index=False
        )["Sales_Amount"]
        .sum()
        .sort_values("Sales_Amount", ascending=False)
        .head(10)
    )

    if not top_products.empty:
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

        st.plotly_chart(
            fig_products, use_container_width=True
        )


# ---------------- TRANSACTION DETAILS ----------------
st.subheader("🧾 Transaction Details")

search = st.text_input(
    "Search by Product Name, Order ID, or Customer ID"
)

table_data = filtered.copy()

if search.strip():
    search_value = search.strip()

    search_columns = [
        col for col in [
            "Product_Name", "Order_ID", "Customer_ID"
        ]
        if col in table_data.columns
    ]

    if search_columns:
        mask = pd.Series(
            False, index=table_data.index
        )

        for col in search_columns:
            mask |= table_data[col].astype(str).str.contains(
                search_value,
                case=False,
                na=False,
                regex=False
            )

        table_data = table_data[mask]


st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True
)

csv_data = table_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Transactions",
    data=csv_data,
    file_name="filtered_sales_transactions.csv",
    mime="text/csv"
)

st.caption(
    "Sales Transactions Dashboard | Built with Python and Streamlit"
)

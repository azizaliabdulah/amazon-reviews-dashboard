import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(
    page_title="Amazon Reviews Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Amazon Products & Reviews Dashboard")
st.markdown("تحليل المنتجات، التقييمات، المشاعر، والأسعار بشكل تفاعلي")


@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_dataset.csv")

    df["brand"] = df["brand"].fillna("Unknown")
    df["sentiment"] = df["sentiment"].fillna("Unknown")

    df["discount_percentage"] = (
        (df["actual_price"] - df["discount_price"]) / df["actual_price"]
    ) * 100

    df["discount_percentage"] = df["discount_percentage"].clip(lower=0)

    df["short_name"] = df["name"].astype(str).str[:40] + "..."

    return df


df = load_data()

st.sidebar.header("🔎 Filters")

brands = sorted(df["brand"].dropna().unique().tolist())
selected_brands = st.sidebar.multiselect(
    "Select Brand",
    options=brands,
    default=[]
)

sentiments = sorted(df["sentiment"].dropna().unique().tolist())
selected_sentiments = st.sidebar.multiselect(
    "Select Sentiment",
    options=sentiments,
    default=sentiments
)

min_rating = float(df["rating"].min())
max_rating = float(df["rating"].max())

rating_range = st.sidebar.slider(
    "Select Rating Range",
    min_value=min_rating,
    max_value=max_rating,
    value=(min_rating, max_rating)
)


filtered_df = df.copy()

if selected_brands:
    filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)]

filtered_df = filtered_df[
    (filtered_df["sentiment"].isin(selected_sentiments)) &
    (filtered_df["rating"] >= rating_range[0]) &
    (filtered_df["rating"] <= rating_range[1])
]


total_products = len(filtered_df)
avg_rating = filtered_df["rating"].mean() if not filtered_df.empty else 0
positive_count = (filtered_df["sentiment"] == "Positive").sum()
negative_count = (filtered_df["sentiment"] == "Negative").sum()
avg_discount = filtered_df["discount_percentage"].mean() if not filtered_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Products", f"{total_products:,}")
col2.metric("Average Rating", f"{avg_rating:.2f}")
col3.metric("Positive Reviews", f"{positive_count:,}")
col4.metric("Negative Reviews", f"{negative_count:,}")
col5.metric("Avg Discount %", f"{avg_discount:.2f}")

st.markdown("---")


col1, col2 = st.columns(2)

with col1:
    st.subheader("Sentiment Distribution")
    sentiment_counts = filtered_df["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]

    fig_sentiment = px.bar(
        sentiment_counts,
        x="sentiment",
        y="count",
        text="count",
        title="Positive vs Negative Reviews"
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

with col2:
    st.subheader("Top Brands")
    top_brands = filtered_df["brand"].value_counts().head(10).reset_index()
    top_brands.columns = ["brand", "count"]

    fig_brands = px.bar(
        top_brands,
        x="brand",
        y="count",
        text="count",
        title="Top 10 Brands by Product Count"
    )
    st.plotly_chart(fig_brands, use_container_width=True)


col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Products with Negative Reviews")
    negative_reviews = filtered_df[filtered_df["sentiment"] == "Negative"]

    top_negative = (
        negative_reviews["short_name"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_negative.columns = ["product_name", "negative_count"]

    fig_negative = px.bar(
        top_negative,
        x="product_name",
        y="negative_count",
        text="negative_count",
        title="Top 10 Products with Negative Reviews"
    )
    fig_negative.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_negative, use_container_width=True)

with col2:
    st.subheader("Price vs Rating")
    fig_scatter = px.scatter(
        filtered_df,
        x="actual_price",
        y="rating",
        color="sentiment",
        hover_data=["name", "brand"],
        title="Relationship Between Price and Rating",
        opacity=0.5
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


col1, col2 = st.columns(2)

with col1:
    st.subheader("Discount Distribution")
    fig_discount = px.histogram(
        filtered_df,
        x="discount_percentage",
        nbins=30,
        title="Discount Percentage Distribution"
    )
    st.plotly_chart(fig_discount, use_container_width=True)

with col2:
    st.subheader("Top Rated Brands")

    brand_stats = (
        filtered_df.groupby("brand")
        .agg(
            avg_rating=("rating", "mean"),
            product_count=("rating", "count")
        )
        .reset_index()
    )

    brand_stats = brand_stats[brand_stats["product_count"] >= 20]

    top_rated_brands = brand_stats.sort_values(
        "avg_rating", ascending=False
    ).head(10)

    fig_brand_rating = px.bar(
        top_rated_brands,
        x="brand",
        y="avg_rating",
        text="avg_rating",
        title="Top 10 Brands by Average Rating (Min 20 Products)"
    )
    st.plotly_chart(fig_brand_rating, use_container_width=True)


st.markdown("---")
st.subheader("Filtered Data Preview")

display_columns = [
    "name",
    "brand",
    "actual_price",
    "discount_price",
    "discount_percentage",
    "rating",
    "sentiment"
]

if not filtered_df.empty:
    st.dataframe(
        filtered_df[display_columns].sort_values(by="rating", ascending=False),
        use_container_width=True
    )
else:
    st.warning("No data available for the selected filters.")


st.markdown("---")
st.subheader("Quick Insights")

if not filtered_df.empty:
    top_brand_name = filtered_df["brand"].value_counts().idxmax()
    top_brand_count = filtered_df["brand"].value_counts().max()

    st.write(f"- أكثر براند ظهورًا: **{top_brand_name}** بعدد **{top_brand_count}** منتج.")
    st.write(f"- متوسط التقييم العام: **{avg_rating:.2f}**.")
    st.write(f"- عدد المنتجات ذات المراجعات الإيجابية: **{positive_count:,}**.")
    st.write(f"- عدد المنتجات ذات المراجعات السلبية: **{negative_count:,}**.")
    st.write(f"- متوسط نسبة الخصم: **{avg_discount:.2f}%**.")
else:
    st.write("لا توجد بيانات مطابقة للفلاتر الحالية.")
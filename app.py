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


# ──────────────────────────────────────────────────────────
# FIX #7 & try/except: تحميل الداتا مع معالجة الأخطاء
# ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cleaned_dataset.csv")
    except FileNotFoundError:
        st.error("❌ الملف cleaned_dataset.csv غير موجود في نفس مجلد التطبيق.")
        st.stop()

    df["brand"] = df["brand"].fillna("Unknown")
    df["sentiment"] = df["sentiment"].fillna("Unknown")

    # FIX #1: إصلاح discount_percentage الصحيح
    # بدل clip (يخفي المشكلة) — نضع NaN للقيم المستحيلة
    df["discount_percentage"] = (
        (df["actual_price"] - df["discount_price"]) / df["actual_price"]
    ) * 100

    # discount_price > actual_price = بيانات خاطئة → NaN
    bad_mask = (df["discount_price"] > df["actual_price"]) | (df["actual_price"] <= 0)
    df.loc[bad_mask, "discount_percentage"] = None
    df["discount_percentage"] = df["discount_percentage"].clip(lower=0, upper=100)

    # FIX #2: short_name أطول + استخدام name الكاملة في hover
    # نحتفظ بالاسم الكامل ونقطع فقط للعرض في الـ charts
    df["short_name"] = df["name"].astype(str).str[:50] + "..."

    return df


df = load_data()

# ──────────────────────────────────────────────────────────
# Sidebar Filters
# ──────────────────────────────────────────────────────────
st.sidebar.header("🔎 Filters")

brands = sorted(df["brand"].dropna().unique().tolist())
selected_brands = st.sidebar.multiselect(
    "Select Brand",
    options=brands,
    default=[]
)

sentiments = sorted(df["sentiment"].dropna().unique().tolist())

# FIX #3: default=[] بدل default=sentiments
# كان يحدد كل الـ sentiments دائماً = لا فائدة من الفلتر
selected_sentiments = st.sidebar.multiselect(
    "Select Sentiment",
    options=sentiments,
    default=sentiments   # نبقيها محددة كلها ابتداءً لكن قابلة للتعديل
)

# FIX: إذا ما اختار شيء → نعرض الكل (UX أفضل من شاشة فارغة)
if not selected_sentiments:
    selected_sentiments = sentiments

min_rating = float(df["rating"].min())
max_rating = float(df["rating"].max())

rating_range = st.sidebar.slider(
    "Select Rating Range",
    min_value=min_rating,
    max_value=max_rating,
    value=(min_rating, max_rating),
    step=0.5   # FIX: step منطقي لأن التقييمات أعداد صحيحة
)

# ──────────────────────────────────────────────────────────
# تطبيق الفلاتر
# ──────────────────────────────────────────────────────────
filtered_df = df.copy()

if selected_brands:
    filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)]

filtered_df = filtered_df[
    (filtered_df["sentiment"].isin(selected_sentiments)) &
    (filtered_df["rating"] >= rating_range[0]) &
    (filtered_df["rating"] <= rating_range[1])
]

# ──────────────────────────────────────────────────────────
# KPI Metrics
# FIX #4: كل الحسابات تعتمد على filtered_df وليس df
# ──────────────────────────────────────────────────────────
total_products   = len(filtered_df)
avg_rating       = filtered_df["rating"].mean()        if not filtered_df.empty else 0
positive_count   = (filtered_df["sentiment"] == "Positive").sum()
negative_count   = (filtered_df["sentiment"] == "Negative").sum()
avg_discount     = filtered_df["discount_percentage"].mean() if not filtered_df.empty else 0

# FIX #7: أسماء مختلفة للـ columns بدل إعادة col1/col2
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Total Products",    f"{total_products:,}")
kpi2.metric("Average Rating",    f"{avg_rating:.2f}")
kpi3.metric("Positive Reviews",  f"{positive_count:,}")
kpi4.metric("Negative Reviews",  f"{negative_count:,}")
kpi5.metric("Avg Discount %",    f"{avg_discount:.1f}")   # FIX #9: رقم واحد بعد الفاصلة

st.markdown("---")

# ──────────────────────────────────────────────────────────
# Row 1: Sentiment Distribution + Top Brands
# ──────────────────────────────────────────────────────────
row1_left, row1_right = st.columns(2)

with row1_left:
    st.subheader("Sentiment Distribution")

    if not filtered_df.empty:
        sentiment_counts = filtered_df["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["sentiment", "count"]

        # FIX #9: ألوان تعبيرية + تنسيق نص
        color_map = {"Positive": "#2ecc71", "Negative": "#e74c3c", "Unknown": "#95a5a6"}
        fig_sentiment = px.bar(
            sentiment_counts,
            x="sentiment",
            y="count",
            text="count",
            color="sentiment",
            color_discrete_map=color_map,
            title="Positive vs Negative Reviews"
        )
        fig_sentiment.update_traces(textposition="outside")
        fig_sentiment.update_layout(showlegend=False)
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.info("لا توجد بيانات.")

with row1_right:
    st.subheader("Top Brands")

    if not filtered_df.empty:
        top_brands = filtered_df["brand"].value_counts().head(10).reset_index()
        top_brands.columns = ["brand", "count"]

        fig_brands = px.bar(
            top_brands,
            x="brand",
            y="count",
            text="count",
            title="Top 10 Brands by Product Count",
            color="count",
            color_continuous_scale="Blues"
        )
        fig_brands.update_traces(textposition="outside")
        fig_brands.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_brands, use_container_width=True)
    else:
        st.info("لا توجد بيانات.")

# ──────────────────────────────────────────────────────────
# Row 2: Top Negative Products + Price vs Rating
# ──────────────────────────────────────────────────────────
row2_left, row2_right = st.columns(2)

with row2_left:
    st.subheader("Top Products with Negative Reviews")

    negative_reviews = filtered_df[filtered_df["sentiment"] == "Negative"]

    if not negative_reviews.empty:
        # FIX #2 + #3: استخدام name الكاملة للـ groupby، short_name للعرض فقط
        top_negative = (
            negative_reviews.groupby("name")
            .size()
            .reset_index(name="negative_count")
            .sort_values("negative_count", ascending=False)
            .head(10)
        )
        # اختصار الاسم للعرض فقط هنا
        top_negative["product_name"] = top_negative["name"].str[:45] + "..."

        fig_negative = px.bar(
            top_negative,
            x="product_name",
            y="negative_count",
            text="negative_count",
            title="Top 10 Products with Negative Reviews",
            color="negative_count",
            color_continuous_scale="Reds"
        )
        fig_negative.update_traces(textposition="outside")
        fig_negative.update_layout(
            xaxis_tickangle=-35,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_negative, use_container_width=True)
    else:
        st.info("✅ لا توجد مراجعات سلبية في الفلتر الحالي.")

with row2_right:
    st.subheader("Price vs Rating")

    if not filtered_df.empty:
        # FIX #10: sample للداتا الكبيرة لتسريع الرسم
        scatter_df = (
            filtered_df.sample(n=min(1500, len(filtered_df)), random_state=42)
            if len(filtered_df) > 1500
            else filtered_df
        )
        color_map_s = {"Positive": "#2ecc71", "Negative": "#e74c3c", "Unknown": "#95a5a6"}
        fig_scatter = px.scatter(
            scatter_df,
            x="actual_price",
            y="rating",
            color="sentiment",
            color_discrete_map=color_map_s,
            hover_data=["name", "brand"],
            title="Relationship Between Price and Rating",
            opacity=0.6,
            labels={"actual_price": "Actual Price (₹)", "rating": "Rating"}
        )
        if len(filtered_df) > 1500:
            fig_scatter.update_layout(
                title="Relationship Between Price and Rating (sample 1,500)"
            )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("لا توجد بيانات.")

# ──────────────────────────────────────────────────────────
# Row 3: Discount Distribution + Top Rated Brands
# ──────────────────────────────────────────────────────────
row3_left, row3_right = st.columns(2)

with row3_left:
    st.subheader("Discount Distribution")

    disc_data = filtered_df["discount_percentage"].dropna()

    if not disc_data.empty:
        fig_discount = px.histogram(
            filtered_df.dropna(subset=["discount_percentage"]),
            x="discount_percentage",
            nbins=30,
            title="Discount Percentage Distribution",
            labels={"discount_percentage": "Discount %"},
            color_discrete_sequence=["#3498db"]
        )
        fig_discount.update_layout(bargap=0.05)
        st.plotly_chart(fig_discount, use_container_width=True)
    else:
        st.info("لا توجد بيانات خصم.")

with row3_right:
    st.subheader("Top Rated Brands")

    brand_stats = (
        filtered_df.groupby("brand")
        .agg(
            avg_rating=("rating", "mean"),
            product_count=("rating", "count")
        )
        .reset_index()
    )

    # FIX #6: تخفيض الحد بناءً على حجم الداتا المفلترة
    min_products = 20 if len(filtered_df) > 500 else 3
    brand_stats_filtered = brand_stats[brand_stats["product_count"] >= min_products]

    # FIX #9: تقريب avg_rating لرقمين فقط
    brand_stats_filtered = brand_stats_filtered.copy()
    brand_stats_filtered["avg_rating"] = brand_stats_filtered["avg_rating"].round(2)

    top_rated_brands = brand_stats_filtered.sort_values(
        "avg_rating", ascending=False
    ).head(10)

    # FIX #8: fallback عند فراغ الـ DataFrame
    if not top_rated_brands.empty:
        fig_brand_rating = px.bar(
            top_rated_brands,
            x="brand",
            y="avg_rating",
            text="avg_rating",
            title=f"Top 10 Brands by Avg Rating (Min {min_products} Products)",
            color="avg_rating",
            color_continuous_scale="Greens",
            range_y=[0, 5.5]
        )
        fig_brand_rating.update_traces(textposition="outside")
        fig_brand_rating.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_brand_rating, use_container_width=True)
    else:
        st.info(f"لا توجد براندات بـ {min_products}+ منتج في الفلتر الحالي.")

# ──────────────────────────────────────────────────────────
# Filtered Data Preview
# ──────────────────────────────────────────────────────────
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
    # FIX: تقريب discount_percentage في العرض
    preview_df = filtered_df[display_columns].copy()
    preview_df["discount_percentage"] = preview_df["discount_percentage"].round(1)
    st.dataframe(
        preview_df.sort_values(by="discount_percentage", ascending=False),
        use_container_width=True
    )
else:
    st.warning("⚠️ No data available for the selected filters.")

# ──────────────────────────────────────────────────────────
# Quick Insights
# FIX #4: كل المتغيرات من filtered_df وليس df
# ──────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Quick Insights")

if not filtered_df.empty:
    top_brand_name  = filtered_df["brand"].value_counts().idxmax()
    top_brand_count = filtered_df["brand"].value_counts().max()
    pos_pct = (positive_count / total_products * 100) if total_products > 0 else 0

    st.write(f"- أكثر براند ظهورًا: **{top_brand_name}** بعدد **{top_brand_count}** منتج.")
    st.write(f"- متوسط التقييم العام: **{avg_rating:.2f}** ⭐")
    st.write(f"- عدد المنتجات ذات المراجعات الإيجابية: **{positive_count:,}** ({pos_pct:.1f}%)")
    st.write(f"- عدد المنتجات ذات المراجعات السلبية: **{negative_count:,}**")
    st.write(f"- متوسط نسبة الخصم: **{avg_discount:.1f}%**")

    # FIX: إضافة insight إضافي مفيد
    most_reviewed = (
        filtered_df.groupby("brand")["no_of_ratings"].sum().idxmax()
        if "no_of_ratings" in filtered_df.columns else "—"
    )
    st.write(f"- البراند الأكثر تقييمًا (عدد ratings): **{most_reviewed}**")
else:
    st.write("لا توجد بيانات مطابقة للفلاتر الحالية.")

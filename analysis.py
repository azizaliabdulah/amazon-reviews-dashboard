"""
Amazon Reviews - Data Analysis Script
تحليل بيانات مراجعات Amazon
"""

# ── Imports (مرة واحدة فقط) ───────────────────────────────
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # FIX #4: يمنع plt.show() من تجميد البرنامج
import matplotlib.pyplot as plt


# ── FIX #5: دوال منظمة بدل كود مبعثر ─────────────────────

def load_data(path: str) -> pd.DataFrame:
    """FIX #5 + try/except: تحميل الداتا مع معالجة الأخطاء"""
    try:
        df = pd.read_csv(path)
        print(f"✅ تم تحميل الداتا: {len(df):,} صف | {df.shape[1]} عمود")
        return df
    except FileNotFoundError:
        print(f"❌ الملف '{path}' غير موجود!")
        raise


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """تنظيف الداتا وإضافة الأعمدة المشتقة"""
    df = df.copy()
    df["brand"]     = df["brand"].fillna("Unknown")
    df["sentiment"] = df["sentiment"].fillna("Unknown")

    # FIX #3: discount_percentage مع معالجة القيم الخاطئة
    df["discount_percentage"] = (
        (df["actual_price"] - df["discount_price"]) / df["actual_price"]
    ) * 100

    # discount_price > actual_price = بيانات خاطئة → NaN
    bad_mask = (df["discount_price"] > df["actual_price"]) | (df["actual_price"] <= 0)
    df.loc[bad_mask, "discount_percentage"] = None
    df["discount_percentage"] = df["discount_percentage"].clip(lower=0, upper=100)

    return df


def print_summary(df: pd.DataFrame):
    """FIX #2 + #5: طباعة الملخص مرة واحدة فقط"""
    sep = "=" * 50

    print(f"\n{sep}")
    print("  📊 نظرة عامة على الداتا")
    print(sep)
    print(df.info())
    print(f"\nالأعمدة: {df.columns.tolist()}")

    print(f"\n{sep}")
    print("  ⭐ إحصائيات التقييم")
    print(sep)
    print(f"  متوسط التقييم  : {df['rating'].mean():.2f}")   # FIX #2: مرة واحدة
    print(f"  أعلى تقييم     : {df['rating'].max():.1f}")
    print(f"  أدنى تقييم     : {df['rating'].min():.1f}")

    print(f"\n{sep}")
    print("  💬 توزيع المشاعر (Sentiment)")
    print(sep)
    print(df["sentiment"].value_counts().to_string())         # FIX #2: مرة واحدة

    print(f"\n{sep}")
    print("  🏷️  أكثر البراندات (Top 10)")
    print(sep)
    print(df["brand"].value_counts().head(10).to_string())

    print(f"\n{sep}")
    print("  ❌ أكثر المنتجات مراجعات سلبية (Top 10)")
    print(sep)
    neg = df[df["sentiment"] == "Negative"]                   # FIX #2: تعريف مرة واحدة
    print(neg["name"].value_counts().head(10).to_string())

    print(f"\n{sep}")
    print("  💰 إحصائيات الخصم")
    print(sep)
    valid_disc = df["discount_percentage"].dropna()
    print(f"  متوسط الخصم   : {valid_disc.mean():.1f}%")
    print(f"  أعلى خصم      : {valid_disc.max():.1f}%")
    print(f"  صفوف بخصم خاطئ: {df['discount_percentage'].isna().sum()}")


def save_charts(df: pd.DataFrame):
    """FIX #4: حفظ الرسوم في ملفات بدل plt.show()"""

    neg = df[df["sentiment"] == "Negative"]   # FIX #2: تعريف مرة واحدة هنا

    # ── Chart 1: Sentiment Distribution ──────────────────
    fig, ax = plt.subplots(figsize=(6, 4))
    counts = df["sentiment"].value_counts()
    colors = ["#2ecc71" if s == "Positive" else "#e74c3c"
              for s in counts.index]
    counts.plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Sentiment Distribution")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Count")
    ax.bar_label(ax.containers[0])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("chart_sentiment.png", dpi=150)
    plt.close()
    print("✅ حُفظ: chart_sentiment.png")

    # ── Chart 2: Top Brands ───────────────────────────────
    top_brands = df["brand"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    top_brands.plot(kind="bar", ax=ax, color="#3498db")
    ax.set_title("Top 10 Brands by Product Count")
    ax.set_xlabel("Brand")
    ax.set_ylabel("Number of Products")
    ax.bar_label(ax.containers[0])
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("chart_top_brands.png", dpi=150)
    plt.close()
    print("✅ حُفظ: chart_top_brands.png")

    # ── Chart 3: Top Negative Products ───────────────────
    top_negative = neg["name"].value_counts().head(10)
    short_names  = top_negative.index.str[:40] + "..."
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(range(len(top_negative)), top_negative.values, color="#e74c3c")
    ax.set_xticks(range(len(top_negative)))
    ax.set_xticklabels(short_names, rotation=45, ha="right")
    ax.set_title("Top 10 Products with Negative Reviews")
    ax.set_xlabel("Product")
    ax.set_ylabel("Negative Reviews Count")
    for i, v in enumerate(top_negative.values):
        ax.text(i, v + 0.1, str(v), ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig("chart_negative_products.png", dpi=150)
    plt.close()
    print("✅ حُفظ: chart_negative_products.png")

    # ── Chart 4: Price vs Rating ──────────────────────────
    # FIX: sample للداتا الكبيرة
    scatter_df = df.sample(n=min(1500, len(df)), random_state=42)
    colors_map  = scatter_df["sentiment"].map(
        {"Positive": "#2ecc71", "Negative": "#e74c3c", "Unknown": "#95a5a6"}
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(scatter_df["actual_price"], scatter_df["rating"],
               alpha=0.4, c=colors_map, s=15)
    ax.set_title("Price vs Rating")
    ax.set_xlabel("Actual Price (₹)")
    ax.set_ylabel("Rating")
    plt.tight_layout()
    plt.savefig("chart_price_vs_rating.png", dpi=150)
    plt.close()
    print("✅ حُفظ: chart_price_vs_rating.png")

    # ── Chart 5: Discount Distribution ───────────────────
    valid_disc = df["discount_percentage"].dropna()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(valid_disc, bins=30, color="#9b59b6", edgecolor="white")
    ax.set_title("Discount Percentage Distribution")
    ax.set_xlabel("Discount %")
    ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig("chart_discount_distribution.png", dpi=150)
    plt.close()
    print("✅ حُفظ: chart_discount_distribution.png")


# ── FIX #5: if __name__ == "__main__" ─────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  🚀 Amazon Reviews Analysis - Started")
    print("=" * 50)

    df = load_data("cleaned_dataset.csv")
    df = clean_data(df)

    print_summary(df)
    save_charts(df)

    print("\n" + "=" * 50)
    print("  ✅ Analysis Complete!")
    print("=" * 50)

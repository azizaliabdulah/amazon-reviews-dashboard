print("program started")

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("cleaned_dataset.csv")

print(df.head())

print(df.info())

print(df.columns)

print("\nAverage rating:")
print(df["rating"].mean())

print("\nSentiment distribution:")
print(df["sentiment"].value_counts())

print("\nTop brands:")
print(df["brand"].value_counts().head(10))

import matplotlib.pyplot as plt

sentiment_counts = df["sentiment"].value_counts()

sentiment_counts.plot(kind="bar")
plt.title("Sentiment Distribution")
plt.xlabel("Sentiment")
plt.ylabel("Count")
plt.show()

negative_reviews = df[df["sentiment"] == "Negative"]

print("\nTop products with negative reviews:")
print(negative_reviews["name"].value_counts().head(10))

top_negative = negative_reviews["name"].value_counts().head(10)

plt.figure(figsize=(12,6))
top_negative.plot(kind="bar", color="red")
plt.title("Top Products with Negative Reviews")
plt.xlabel("Product")
plt.ylabel("Negative Reviews Count")
plt.xticks(rotation=60)
plt.tight_layout()
plt.show()


print("\nAverage rating:")
print(df["rating"].mean())

print("\nHighest rating:")
print(df["rating"].max())

print("\nLowest rating:")
print(df["rating"].min())



print("\nSentiment distribution:")
print(df["sentiment"].value_counts())

sentiment_counts = df["sentiment"].value_counts()

plt.figure(figsize=(6,4))
sentiment_counts.plot(kind="bar")
plt.title("Sentiment Distribution")
plt.xlabel("Sentiment")
plt.ylabel("Count")
plt.show()




print("\nTop brands:")
print(df["brand"].value_counts().head(10))

top_brands = df["brand"].value_counts().head(10)

plt.figure(figsize=(10,5))
top_brands.plot(kind="bar")
plt.title("Top Brands")
plt.xlabel("Brand")
plt.ylabel("Number of Products")
plt.xticks(rotation=45)
plt.show()




negative_reviews = df[df["sentiment"] == "Negative"]

print("\nTop products with negative reviews:")
print(negative_reviews["name"].value_counts().head(10))

top_negative = negative_reviews["name"].value_counts().head(10)

plt.figure(figsize=(10,5))
top_negative.plot(kind="bar", color="red")
plt.title("Top Products with Negative Reviews")
plt.xlabel("Product")
plt.ylabel("Negative Reviews Count")
plt.xticks(rotation=60)
plt.show()




plt.figure(figsize=(8,5))
plt.scatter(df["actual_price"], df["rating"], alpha=0.3)
plt.title("Price vs Rating")
plt.xlabel("Actual Price")
plt.ylabel("Rating")
plt.show()



df["discount_percentage"] = (
    (df["actual_price"] - df["discount_price"]) / df["actual_price"]
) * 100

print("\nAverage discount percentage:")
print(df["discount_percentage"].mean())

plt.figure(figsize=(8,5))
plt.hist(df["discount_percentage"], bins=30)
plt.title("Discount Distribution")
plt.xlabel("Discount %")
plt.ylabel("Count")
plt.show()
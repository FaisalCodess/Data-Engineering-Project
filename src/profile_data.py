import pandas as pd

df = pd.read_csv("data/raw/countries_flat.csv", keep_default_na=False, na_values=[""])

print("1. SHAPE")
print(f"{df.shape[0]} rows, {df.shape[1]} columns\n")

print("2. DATA TYPES")
print(df.dtypes, "\n")

print("3. MISSING VALUES")
missing = pd.DataFrame({
    "missing_count": df.isnull().sum(),
    "missing_percent": (df.isnull().sum() / len(df) * 100).round(2),
})
print(missing.sort_values("missing_percent", ascending=False), "\n")

print("4. DUPLICATES")
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate uuid:", df["uuid"].duplicated().sum())
print("Duplicate alpha3:", df["alpha3"].dropna().duplicated().sum(), "\n")

print("5. SUMMARY STATISTICS")
print(df.describe(), "\n")

print("6. REGION COUNTS")
print(df["region"].value_counts(), "\n")

print("7. OUTLIERS")
Q1_area = df["area_km2"].quantile(0.25)
Q2_area = df["area_km2"].quantile(0.50)
Q3_area = df["area_km2"].quantile(0.75)

Q1_pop = df["population"].quantile(0.25)
Q2_pop = df["population"].quantile(0.50)
Q3_pop = df["population"].quantile(0.75)

IQR_area = Q3_area - Q1_area
IQR_pop = Q3_pop - Q1_pop

upperBoundary_area = Q3_area + 1.5 * IQR_area
upperBoundary_pop = Q3_pop + 1.5 * IQR_pop
lowerBoundary_area = Q1_area - 1.5 * IQR_area
lowerBoundary_pop = Q1_pop - 1.5 * IQR_pop

df_outliers_area = df[(df["area_km2"] > upperBoundary_area) | (df["area_km2"] < lowerBoundary_area)]
df_outliers_pop = df[(df["population"] > upperBoundary_pop) | (df["population"] < lowerBoundary_pop)]

print("Outliers in area_km2:", len(df_outliers_area))
print("Outliers in population:", len(df_outliers_pop))

print("\n8. SUSPICIOUS VALUES")
print("Population == 0:", (df["population"] == 0).sum())
print("Area <= 0:", (df["area_km2"] <= 0).sum())
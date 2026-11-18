import pandas as pd

RAW_PATH = "data/raw/countries_flat.csv"
CLEAN_PATH = "data/clean/countries_clean.csv"

SKIP_WORDS = {"north", "northern", "south", "southern", "east", "eastern",
              "west", "western", "the", "of", "and"}

CODE_OVERRIDES = {
    "Northern Cyprus": "NCY",
    "Somaliland": "SML",
}

CAPITAL_OVERRIDES = {"Macau": "Macau"}

def make_code(name):
    words = [w for w in name.replace("-", " ").split() if w.lower() not in SKIP_WORDS]
    word = words[0] if words else name
    return word[:3].upper()

def fill_gini(df):
    df["gini_imputed"] = df["gini"].isnull()
    region_mean = df.groupby("region").aggregate({"gini": "mean"})
    df["gini"] = df["gini"].fillna(region_mean).round(2)
    return df

def fill_alpha3(df):
    df["code_is_synthetic"] = df["alpha3"].isnull()
    for i in df.index[df["alpha3"].isnull()]: # explain this line : This line gets the indices of rows where 'alpha3' is null
        name = df[i, "name_common"] # explain this line : This line retrieves the value of the 'name_common' column for the row at index 'i'.
        df[i, "alpha3"] = CODE_OVERRIDES.get(name, make_code(name)) # explain this line : This line sets the 'alpha3' value for the row at index 'i'. It first checks if there is an override in the CODE_OVERRIDES dictionary for the country name. If there is, it uses that value; if not, it generates a synthetic code using the make_code function based on the country name.
    return df

def fill_text_columns(df):
    df["capital"] = df["capital"].fillna(df["name_common"].map(CAPITAL_OVERRIDES)) # explain this line : This line fills missing values in the 'capital' column. It uses the 'name_common' column to look up any overrides in the CAPITAL_OVERRIDES dictionary. If a country name has an override, it fills the 'capital' with that value; otherwise, it leaves it as NaN. 
    df["capital"] = df["capital"].fillna("None")
    df["subregion"] = df["subregion"].fillna(df["region"])
    df["currencies"] = df["currencies"].fillna("None")
    df["languages"] = df["languages"].fillna("None")
    return df

def check(df):
    assert df["uuid"].is_unique, "duplicate uuid"
    assert df["alpha3"].notnull().all(), "alpha3 still has missing values"
    assert df["alpha3"].is_unique, "alpha3 codes are not unique"
    assert df["name_common"].is_unique, "duplicate country names"
    for col in ["capital", "subregion", "currencies", "languages"]:
        assert df[col].notnull().all(), f"{col} still has missing values"

if __name__ == "__main__":
    df = pd.read_csv(RAW_PATH)
    n_rows = len(df)
    
    df = fill_gini(df)
    df = fill_alpha3(df)
    df = fill_text_columns(df)
    check(df)
    assert len(df) == n_rows, "rows were lost"
    
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False, encoding="utf-8-sig")
    
    print(f"Saved {len(df)} rows, {df.shape[1]} columns -> {CLEAN_PATH}")
    print(f"gini imputed:        {int(df['gini_imputed'].sum())} rows")
    print(f"gini still missing:  {int(df['gini'].isnull().sum())} rows")
    print(f"synthetic alpha3:    {int(df['code_is_synthetic'].sum())} rows")
    print(f"alpha2 still empty:  {int(df['alpha2'].isnull().sum())} rows")

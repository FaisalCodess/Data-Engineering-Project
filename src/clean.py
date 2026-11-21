from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/countries_flat.csv")
CLEAN_PATH = Path("data/clean/countries_clean.csv")

SKIP_WORDS = {"north", "northern", "south", "southern", "east", "eastern",
              "west", "western", "the", "of", "and"}

CODE_OVERRIDES = {
    "Northern Cyprus": "NCY",
    "Somaliland": "SML",
}

ALPHA2_OVERRIDES = {
    "Abkhazia": "XA",
    "Northern Cyprus": "XC",
    "Somaliland": "XS",
    "South Ossetia": "XO",
}


def make_code(name):
    words = [w for w in name.replace("-", " ").split() if w.lower() not in SKIP_WORDS]
    word = words[0] if len(words) > 1 else name
    return word[:3].upper()


def fill_gini(df):
    df["gini_imputed"] = df["gini"].isnull()
    region_mean = df.groupby("region")["gini"].transform("mean")
    df["gini"] = df["gini"].fillna(region_mean).round(2)
    df["gini"] = df["gini"].fillna(df["gini"].mean().round(2))
    return df


def fill_alpha2(df):
    df["alpha2_is_synthetic"] = df["alpha2"].isnull()
    for i in df.index[df["alpha2"].isnull()]:
        df.loc[i, "alpha2"] = ALPHA2_OVERRIDES[df.loc[i, "name_common"]]
    return df


def fill_alpha3(df):
    df["alpha3_is_synthetic"] = df["alpha3"].isnull()
    for i in df.index[df["alpha3"].isnull()]:
        name = df.loc[i, "name_common"]
        df.loc[i, "alpha3"] = CODE_OVERRIDES.get(name, make_code(name))
    return df


def fill_text_columns(df):
    df["capital"] = df["capital"].fillna(df["name_common"])
    df["borders"] = df["borders"].fillna("No borders")
    df["subregion"] = df["subregion"].fillna(df["region"])
    df["currencies"] = df["currencies"].fillna(df["currencies"].mode()[0])
    df["languages"] = df["languages"].fillna(df["languages"].mode()[0])
    return df


def check(df):
    assert df["uuid"].is_unique, "duplicate uuid"
    assert df["alpha2"].notnull().all(), "alpha2 still has missing values"
    assert df["alpha2"].is_unique, "alpha2 codes are not unique"
    assert df["alpha3"].notnull().all(), "alpha3 still has missing values"
    assert df["alpha3"].is_unique, "alpha3 codes are not unique"
    assert df["name_common"].is_unique, "duplicate country names"
    for col in ["capital", "subregion", "currencies", "languages"]:
        assert df[col].notnull().all(), f"{col} still has missing values"


if __name__ == "__main__":
    df = pd.read_csv(RAW_PATH, keep_default_na=False, na_values=[""])
    n_rows = len(df)

    df = fill_gini(df)
    df = fill_alpha3(df)
    df = fill_alpha2(df)
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